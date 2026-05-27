#!/usr/bin/env python3
"""
Sincroniza a atividade real do agente no GitHub para o usage.jsonl local.

Sem isto, o dashboard só vê os evals locais. Aqui puxamos via `gh` o que o
`@claude` faz mesmo:
- runs do workflow `claude.yml` (invocações do agente) → task_completed
- PRs do agente (branch `claude/*`) → pr_opened

A action é uma caixa-preta: não expõe tokens/custo por run (esses vês no
Anthropic Console). O que conseguimos — frequência, desfecho, duração, PRs — já
chega para deixar de voar às cegas.

Idempotente: não re-regista runs/PRs já vistos (dedup por run_id / número de PR).

Uso:
    python scripts/sync_activity.py            # últimos 20 runs + PRs do agente
    python scripts/sync_activity.py --limit 50
    python scripts/dashboard.py                # ver o resultado
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(__file__).parent.parent / ".harness" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
USAGE_FILE = STATE_DIR / "usage.jsonl"

AGENT_WORKFLOW = "claude.yml"   # implementação conduzida pelo @claude
AGENT_BRANCH_PREFIX = "claude/"  # branches abertas pelo agente


def _gh_json(args: list) -> list:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"gh failed: {' '.join(args)}\n{r.stderr.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return []


def _seen() -> set:
    """Chaves (run/pr) já registadas, para idempotência."""
    if not USAGE_FILE.exists():
        return set()
    seen = set()
    for line in USAGE_FILE.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "run_id" in e:
            seen.add(("run", e["run_id"]))
        if e.get("type") == "pr_opened" and "pr" in e:
            seen.add(("pr", e["pr"]))
    return seen


def _append(event: dict) -> None:
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with USAGE_FILE.open("a") as f:
        f.write(json.dumps(event) + "\n")


def _duration(created: str, updated: str) -> float:
    try:
        c = datetime.fromisoformat(created.replace("Z", "+00:00"))
        u = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return round((u - c).total_seconds(), 1)
    except (ValueError, AttributeError, TypeError):
        return 0.0


def sync_runs(limit: int, seen: set) -> int:
    runs = _gh_json(["run", "list", "--workflow", AGENT_WORKFLOW, "-L", str(limit),
                     "--json", "databaseId,conclusion,status,createdAt,updatedAt,displayTitle"])
    n = 0
    for run in runs:
        rid = run.get("databaseId")
        if rid is None or ("run", rid) in seen or run.get("status") != "completed":
            continue
        _append({
            "type": "task_completed",
            "source": "agent",
            "run_id": rid,
            "conclusion": run.get("conclusion"),
            "passed": run.get("conclusion") == "success",
            "duration": _duration(run.get("createdAt"), run.get("updatedAt")),
            "tokens": 0, "calls": 0, "cost_usd": 0.0,  # ver Console para custo
            "timestamp": run.get("createdAt"),
            "title": run.get("displayTitle", ""),
        })
        n += 1
    return n


def sync_prs(seen: set) -> int:
    prs = _gh_json(["pr", "list", "--state", "all", "-L", "50",
                    "--json", "number,headRefName,createdAt,title"])
    n = 0
    for pr in prs:
        if not pr.get("headRefName", "").startswith(AGENT_BRANCH_PREFIX):
            continue
        num = pr.get("number")
        if num is None or ("pr", num) in seen:
            continue
        _append({
            "type": "pr_opened",
            "source": "agent",
            "pr": num,
            "task_id": pr.get("headRefName"),
            "timestamp": pr.get("createdAt"),
            "title": pr.get("title", ""),
        })
        n += 1
    return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20, help="Quantos runs recentes ler")
    args = parser.parse_args()

    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        print("gh not authenticated — run `gh auth login`", file=sys.stderr)
        sys.exit(1)

    seen = _seen()
    runs = sync_runs(args.limit, seen)
    prs = sync_prs(seen)
    print(f"✓ synced {runs} agent run(s) and {prs} PR(s) into {USAGE_FILE}")
    if runs or prs:
        print("  view: python scripts/dashboard.py")


if __name__ == "__main__":
    main()
