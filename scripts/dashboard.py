#!/usr/bin/env python3
"""
Dashboard do harness — gera relatório de saúde para visualização.

Uso:
    python scripts/dashboard.py                 # texto no terminal
    python scripts/dashboard.py --html > out.html
    python scripts/dashboard.py --metrics       # JSON para Prometheus/Grafana
"""

import argparse
import json
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).parent.parent
STATE_DIR = ROOT / ".harness" / "state"
TRACE_DIR = ROOT / ".harness" / "traces"
EVAL_RESULTS = ROOT / "tests" / "harness" / "eval-set" / "results"


def load_events(days: int = 7) -> list:
    f = STATE_DIR / "usage.jsonl"
    if not f.exists():
        return []
    cutoff = datetime.now(UTC) - timedelta(days=days)
    events = []
    for line in f.read_text().splitlines():
        try:
            e = json.loads(line)
            if datetime.fromisoformat(e["timestamp"]) > cutoff:
                events.append(e)
        except (json.JSONDecodeError, KeyError):
            pass
    return events


def compute_metrics(events: list) -> dict:
    tasks = [e for e in events if e["type"] == "task_completed"]
    prs = [e for e in events if e["type"] == "pr_opened"]
    kills = [e for e in events if e["type"] == "kill_switch_activated"]

    if not tasks:
        return {"empty": True}

    durations = [t.get("duration", 0) for t in tasks]
    token_counts = [t.get("tokens", 0) for t in tasks]
    call_counts = [t.get("calls", 0) for t in tasks]
    # Custo real quando o evento o traz (eval headless); senão estima por tokens.
    real_cost = round(sum(t.get("cost_usd", 0) or 0 for t in tasks), 2)
    by_source = Counter(t.get("source", "?") for t in tasks)

    return {
        "tasks_total": len(tasks),
        "tasks_by_source": dict(by_source),
        "prs_opened": len(prs),
        "pr_per_task_ratio": round(len(prs) / max(len(tasks), 1), 2),
        "kill_switch_events": len(kills),
        "duration_median_s": round(median(durations) if durations else 0, 1),
        "duration_mean_s": round(mean(durations) if durations else 0, 1),
        "tokens_median": int(median(token_counts) if token_counts else 0),
        "tokens_total": sum(token_counts),
        "calls_median": int(median(call_counts) if call_counts else 0),
        "cost_usd_real": real_cost,
        "estimated_total_cost_usd": round(sum(token_counts) * 9 / 1_000_000, 2),
    }


def latest_eval_summary() -> dict:
    if not EVAL_RESULTS.exists():
        return {"no_evals": True}
    files = sorted(EVAL_RESULTS.glob("*.json"), reverse=True)
    if not files:
        return {"no_evals": True}
    latest = json.loads(files[0].read_text())
    return {
        "timestamp": latest.get("timestamp"),
        "passed": latest.get("passed"),
        "total": latest.get("total"),
        "pass_rate": round(latest.get("passed", 0) / max(latest.get("total", 1), 1) * 100, 1),
    }


def trace_health() -> dict:
    """Olhada rápida nas traces recentes para warnings."""
    if not TRACE_DIR.exists():
        return {"no_traces": True}

    recent = sorted(TRACE_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]
    loop_count = 0
    high_churn_count = 0

    for t in recent:
        events = []
        for line in t.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass

        tool_calls = [e for e in events if e.get("type") == "tool_call"]
        if not tool_calls:
            continue

        # Detecção rápida de loop
        last_hash = None
        repeat = 0
        for e in tool_calls:
            h = e.get("params_hash")
            if h == last_hash:
                repeat += 1
                if repeat >= 3:
                    loop_count += 1
                    break
            else:
                repeat = 0
                last_hash = h

        file_changes = [e for e in events if e.get("type") == "file_change"]
        if file_changes:
            by_path = Counter(fc["path"] for fc in file_changes)
            if max(by_path.values()) > 3:
                high_churn_count += 1

    return {
        "recent_traces": len(recent),
        "tasks_with_loops": loop_count,
        "tasks_with_high_churn": high_churn_count,
    }


def render_text(metrics: dict, evals: dict, traces: dict) -> str:
    lines = ["=" * 60, "HARNESS DASHBOARD", "=" * 60, ""]

    lines.append("📊 ACTIVIDADE (últimos 7 dias)")
    lines.append("-" * 60)
    if metrics.get("empty"):
        lines.append("  (sem dados)")
    else:
        src = ", ".join(f"{k}:{v}" for k, v in metrics["tasks_by_source"].items())
        lines.append(f"  Tasks completadas:       {metrics['tasks_total']}  ({src})")
        lines.append(f"  PRs abertos:             {metrics['prs_opened']}")
        lines.append(f"  PRs por task:            {metrics['pr_per_task_ratio']}")
        lines.append(f"  Kill switch activações:  {metrics['kill_switch_events']}")
        lines.append(f"  Duração mediana:         {metrics['duration_median_s']:.0f}s")
        lines.append(f"  Tokens total:            {metrics['tokens_total']:,}")
        if metrics["cost_usd_real"] > 0:
            lines.append(f"  Custo real (eval):       ${metrics['cost_usd_real']}")
        else:
            lines.append(f"  Custo estimado:          ${metrics['estimated_total_cost_usd']}")

    lines.append("")
    lines.append("🧪 EVAL SET")
    lines.append("-" * 60)
    if evals.get("no_evals"):
        lines.append("  (nenhum eval run encontrado)")
    else:
        lines.append(f"  Último run:              {evals['timestamp']}")
        lines.append(f"  Pass rate:               {evals['pass_rate']}% ({evals['passed']}/{evals['total']})")

    lines.append("")
    lines.append("🔍 TRAJECTORY HEALTH")
    lines.append("-" * 60)
    if traces.get("no_traces"):
        lines.append("  (sem traces)")
    else:
        lines.append(f"  Traces analisadas:       {traces['recent_traces']}")
        lines.append(f"  Com loops detectados:    {traces['tasks_with_loops']}")
        lines.append(f"  Com churn alto:          {traces['tasks_with_high_churn']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", action="store_true", help="Output JSON para monitoring")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    events = load_events(args.days)
    metrics = compute_metrics(events)
    evals = latest_eval_summary()
    traces = trace_health()

    if args.metrics:
        print(json.dumps({"activity": metrics, "evals": evals, "traces": traces}, indent=2))
    else:
        print(render_text(metrics, evals, traces))


if __name__ == "__main__":
    main()
