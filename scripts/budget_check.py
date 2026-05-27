#!/usr/bin/env python3
"""
Budget enforcer e kill switch.

Corre no início de cada task do agente (via hook ou wrapper) e bloqueia
execução se o kill switch estiver activo ou se os budgets foram excedidos.

Uso:
    python scripts/budget_check.py --task-id <id>
    python scripts/budget_check.py --check-pr-rate
    python scripts/budget_check.py --record-usage --tokens 1234 --calls 5
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

POLICY_FILE = Path(__file__).parent.parent / "config" / "harness" / "policy.yml"
STATE_DIR = Path(__file__).parent.parent / ".harness" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

USAGE_FILE = STATE_DIR / "usage.jsonl"
KILL_SWITCH_FILE = STATE_DIR / "KILL_SWITCH"


def load_policy() -> dict:
    return yaml.safe_load(POLICY_FILE.read_text())


def check_kill_switch(policy: dict) -> None:
    """Falha se o kill switch estiver activo."""
    # Manual override por ficheiro (para emergências sem editar yml)
    if KILL_SWITCH_FILE.exists():
        reason = KILL_SWITCH_FILE.read_text().strip() or "(sem motivo registado)"
        print(f"🛑 Kill switch ACTIVE: {reason}", file=sys.stderr)
        print(f"   To re-enable: rm {KILL_SWITCH_FILE}", file=sys.stderr)
        sys.exit(2)

    if not policy.get("enabled", True):
        print("🛑 Harness disabled in policy.yml (enabled: false)", file=sys.stderr)
        sys.exit(2)


def check_rate_limits(policy: dict) -> None:
    """Verifica se ultrapassámos PRs/hora ou PRs/dia."""
    if not USAGE_FILE.exists():
        return

    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    pr_events_hour = 0
    pr_events_day = 0

    for line in USAGE_FILE.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "pr_opened":
            continue
        ts = datetime.fromisoformat(event["timestamp"])
        if ts > one_hour_ago:
            pr_events_hour += 1
        if ts > one_day_ago:
            pr_events_day += 1

    limits = policy.get("rate_limits", {})
    if pr_events_hour >= limits.get("max_prs_per_hour", 999):
        print(f"🛑 Rate limit: {pr_events_hour} PRs in the last hour "
              f"(limit {limits['max_prs_per_hour']})", file=sys.stderr)
        sys.exit(3)

    if pr_events_day >= limits.get("max_prs_per_day", 9999):
        print(f"🛑 Rate limit: {pr_events_day} PRs in the last 24h "
              f"(limit {limits['max_prs_per_day']})", file=sys.stderr)
        sys.exit(3)


def check_task_budget(policy: dict, task_id: str, tokens: int, calls: int, duration: float) -> None:
    """Verifica budgets de uma task específica."""
    b = policy.get("budgets", {})
    violations = []

    if tokens > b.get("max_tokens_per_task", 1e9):
        violations.append(f"tokens: {tokens} > {b['max_tokens_per_task']}")
    if calls > b.get("max_tool_calls_per_task", 1e9):
        violations.append(f"tool_calls: {calls} > {b['max_tool_calls_per_task']}")
    if duration > b.get("max_duration_seconds", 1e9):
        violations.append(f"duration: {duration:.0f}s > {b['max_duration_seconds']}s")

    if violations:
        print(f"🛑 Task {task_id} exceeded budget:", file=sys.stderr)
        for v in violations:
            print(f"   {v}", file=sys.stderr)
        sys.exit(4)


def record_event(event_type: str, **payload) -> None:
    """Regista evento em log estruturado."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        **payload,
    }
    with USAGE_FILE.open("a") as f:
        f.write(json.dumps(event) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", help="ID da task actual")
    parser.add_argument("--check-pr-rate", action="store_true")
    parser.add_argument("--record-usage", action="store_true")
    parser.add_argument("--record-pr", action="store_true")
    parser.add_argument("--tokens", type=int, default=0)
    parser.add_argument("--calls", type=int, default=0)
    parser.add_argument("--duration", type=float, default=0)
    parser.add_argument("--trigger-kill-switch", help="Activa kill switch com este motivo")
    args = parser.parse_args()

    if args.trigger_kill_switch:
        KILL_SWITCH_FILE.write_text(args.trigger_kill_switch)
        print(f"🛑 Kill switch activated: {args.trigger_kill_switch}")
        record_event("kill_switch_activated", reason=args.trigger_kill_switch)
        return

    policy = load_policy()

    # Sempre verifica kill switch primeiro
    check_kill_switch(policy)

    if args.check_pr_rate:
        check_rate_limits(policy)

    if args.task_id and (args.tokens or args.calls or args.duration):
        check_task_budget(policy, args.task_id, args.tokens, args.calls, args.duration)
        record_event("task_completed",
                     task_id=args.task_id,
                     tokens=args.tokens,
                     calls=args.calls,
                     duration=args.duration)

    if args.record_pr:
        record_event("pr_opened", task_id=args.task_id or "unknown")

    print("✓ Budget check OK")


if __name__ == "__main__":
    main()
