#!/usr/bin/env python3
"""
Trajectory logger e analyzer.

Regista cada tool call do agente em formato estruturado, e produz análises:
- Sequência de acções
- Detecção de loops (mesma tool call repetida)
- Ficheiros tocados/revertidos
- Heatmap de erros
- Custo estimado

Uso pelo wrapper do agente:
    logger = TrajectoryLogger(task_id="abc123")
    logger.log_tool_call("bash", {"command": "ls"}, result="...", success=True)
    logger.finalize()

Uso pelo analyzer (post-task):
    python trajectory.py analyze .harness/traces/abc123.jsonl
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

TRACE_DIR = Path(__file__).parent.parent / ".harness" / "traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)


class TrajectoryLogger:
    """Regista trajectória de um agente em ficheiro JSONL."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.trace_file = TRACE_DIR / f"{task_id}.jsonl"
        self.start_time = datetime.now(UTC)
        self._log({
            "type": "task_started",
            "task_id": task_id,
        })

    def _log(self, event: dict) -> None:
        event["timestamp"] = datetime.now(UTC).isoformat()
        with self.trace_file.open("a") as f:
            f.write(json.dumps(event) + "\n")

    def log_tool_call(self, tool: str, params: dict, result: str = "",
                      success: bool = True, tokens: int = 0) -> None:
        # Hash dos parâmetros para detectar repetições exactas
        params_hash = hashlib.sha256(
            json.dumps(params, sort_keys=True).encode()
        ).hexdigest()[:12]

        self._log({
            "type": "tool_call",
            "tool": tool,
            "params": params,
            "params_hash": params_hash,
            "result_preview": result[:500] if result else "",
            "result_length": len(result),
            "success": success,
            "tokens": tokens,
        })

    def log_file_change(self, path: str, operation: str, before_hash: str = "",
                         after_hash: str = "") -> None:
        """Regista criação/edição/reversão de ficheiro."""
        self._log({
            "type": "file_change",
            "path": path,
            "operation": operation,   # create | edit | delete | revert
            "before_hash": before_hash,
            "after_hash": after_hash,
        })

    def log_thinking(self, summary: str) -> None:
        self._log({"type": "thinking", "summary": summary[:1000]})

    def finalize(self, status: str = "completed") -> None:
        self._log({
            "type": "task_finished",
            "status": status,
            "duration_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
        })


def load_trace(path: Path) -> list[dict]:
    events = []
    for line in path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events


def analyze(trace_path: Path) -> dict:
    """Produz relatório de uma trajectória."""
    events = load_trace(trace_path)
    if not events:
        return {"error": "trace vazia"}

    tool_calls = [e for e in events if e.get("type") == "tool_call"]
    file_changes = [e for e in events if e.get("type") == "file_change"]

    # Contadores básicos
    tool_counts = Counter(e["tool"] for e in tool_calls)
    failed_calls = [e for e in tool_calls if not e.get("success", True)]

    # Detecção de loops (mesma tool call repetida em sequência)
    loops = []
    last_hash = None
    repeat_count = 0
    for e in tool_calls:
        h = e.get("params_hash")
        if h == last_hash:
            repeat_count += 1
        else:
            if repeat_count >= 3:
                loops.append({
                    "tool": e["tool"],
                    "params_hash": last_hash,
                    "repetitions": repeat_count + 1,
                })
            repeat_count = 0
            last_hash = h

    # Ficheiros tocados / revertidos
    files_by_path = defaultdict(list)
    for fc in file_changes:
        files_by_path[fc["path"]].append(fc["operation"])

    churned_files = {
        path: ops for path, ops in files_by_path.items()
        if len(ops) > 3 or "revert" in ops
    }

    # Custo estimado (Claude Sonnet 4.6 ~ $3 input / $15 output por 1M tokens — média $9)
    total_tokens = sum(e.get("tokens", 0) for e in tool_calls)
    estimated_cost = total_tokens * 9 / 1_000_000

    return {
        "task_id": events[0].get("task_id"),
        "total_events": len(events),
        "total_tool_calls": len(tool_calls),
        "failed_tool_calls": len(failed_calls),
        "tool_distribution": dict(tool_counts.most_common()),
        "total_file_changes": len(file_changes),
        "churned_files": churned_files,
        "detected_loops": loops,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
        "warnings": _warnings(loops, churned_files, failed_calls, tool_calls),
    }


def _warnings(loops, churned, failed, all_calls) -> list[str]:
    w = []
    if loops:
        w.append(f"LOOP detectado: {len(loops)} sequência(s) de tool calls repetidas")
    if churned:
        w.append(f"CHURN: {len(churned)} ficheiro(s) editado(s) >3x ou revertido(s)")
    if all_calls and len(failed) / len(all_calls) > 0.3:
        w.append(f"FALHA ALTA: {len(failed)}/{len(all_calls)} tool calls falharam (>30%)")
    if len(all_calls) > 80:
        w.append(f"VOLUME ALTO: {len(all_calls)} tool calls (budget típico: 80)")
    return w


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["analyze", "summary"])
    parser.add_argument("path", nargs="?", help="Caminho para a trace ou directório")
    args = parser.parse_args()

    if args.command == "analyze":
        if not args.path:
            print("Especifica caminho da trace", file=sys.stderr)
            sys.exit(1)
        report = analyze(Path(args.path))
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == "summary":
        # Sumário de todas as traces dos últimos dias
        traces = sorted(TRACE_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]
        print(f"{'task_id':<20} {'calls':>6} {'failed':>7} {'tokens':>8} {'cost':>8} warnings")
        print("-" * 80)
        for t in traces:
            r = analyze(t)
            task = (r.get("task_id") or t.stem)[:18]
            warn = ",".join(w.split(":")[0] for w in r.get("warnings", []))
            print(f"{task:<20} {r['total_tool_calls']:>6} {r['failed_tool_calls']:>7} "
                  f"{r['total_tokens']:>8} ${r['estimated_cost_usd']:>6.2f} {warn}")


if __name__ == "__main__":
    main()
