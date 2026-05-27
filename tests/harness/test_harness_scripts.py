"""O harness a validar-se a si próprio.

Cobre a lógica de decisão dos sensores — classificação de risco, budgets/kill
switch, scoring do eval, métricas do dashboard e deteção de regressão. São as
peças cujo bug passa silencioso (como o do classify_risk que rebentou no CI).

Os módulos importam-se via pythonpath=scripts (ver pyproject.toml).
"""

import json

import budget_check
import classify_risk
import dashboard
import eval as eval_runner
import pytest
import sync_activity

# ── classify_risk ──────────────────────────────────────────────────────────
POLICY = {
    "risk_classification": {
        "critical": {"paths": ["config/**", "database/migrations/**"]},
        "high": {"paths": ["app/Http/Middleware/**", "routes/**"]},
        "low": {"paths": ["docs/**", "*.md"]},
    }
}


def test_classify_file_critical():
    assert classify_risk.classify_file("config/auth.php", POLICY) == "critical"
    assert classify_risk.classify_file("database/migrations/2026_x.php", POLICY) == "critical"


def test_classify_file_high():
    assert classify_risk.classify_file("app/Http/Middleware/Auth.php", POLICY) == "high"
    assert classify_risk.classify_file("routes/api.php", POLICY) == "high"


def test_classify_file_low_and_default():
    assert classify_risk.classify_file("docs/adr/0001.md", POLICY) == "low"
    assert classify_risk.classify_file("README.md", POLICY) == "low"
    # Sem match em nenhum nível → default "medium".
    assert classify_risk.classify_file("app/Services/Pricing.php", POLICY) == "medium"


def test_matches_any_globstar():
    assert classify_risk.matches_any("app/Http/Middleware/X.php", ["app/Http/Middleware/**"])
    assert not classify_risk.matches_any("app/Models/Y.php", ["app/Http/Middleware/**"])


def test_changed_files_resilient_to_empty_base_ref():
    # O bug que rebentou (exit 128): base ref vazio ou SHA nulo → [] em vez de crashar.
    assert classify_risk.changed_files("") == []
    assert classify_risk.changed_files("origin/" + "0" * 40) == []


# ── budget_check ───────────────────────────────────────────────────────────
@pytest.fixture
def no_kill_file(monkeypatch, tmp_path):
    """Garante que nenhum ficheiro KILL_SWITCH real interfere nos testes."""
    monkeypatch.setattr(budget_check, "KILL_SWITCH_FILE", tmp_path / "ABSENT")


def test_kill_switch_disabled_in_policy(no_kill_file):
    with pytest.raises(SystemExit) as exc:
        budget_check.check_kill_switch({"enabled": False})
    assert exc.value.code == 2


def test_kill_switch_enabled_passes(no_kill_file):
    budget_check.check_kill_switch({"enabled": True})  # não deve sair


def test_task_budget_exceeded():
    policy = {"budgets": {"max_tokens_per_task": 100}}
    with pytest.raises(SystemExit) as exc:
        budget_check.check_task_budget(policy, "t1", tokens=200, calls=1, duration=1)
    assert exc.value.code == 4


def test_task_budget_within_limits():
    policy = {"budgets": {
        "max_tokens_per_task": 1000,
        "max_tool_calls_per_task": 80,
        "max_duration_seconds": 1800,
    }}
    budget_check.check_task_budget(policy, "t1", tokens=10, calls=2, duration=5)  # ok


# ── dashboard ──────────────────────────────────────────────────────────────
def test_compute_metrics_real_cost_and_source_split():
    events = [
        {"type": "task_completed", "tokens": 100, "calls": 5, "duration": 10,
         "cost_usd": 0.05, "source": "eval"},
        {"type": "task_completed", "tokens": 0, "calls": 0, "duration": 30,
         "cost_usd": 0.0, "source": "agent"},
        {"type": "pr_opened", "source": "agent"},
    ]
    m = dashboard.compute_metrics(events)
    assert m["tasks_total"] == 2
    assert m["prs_opened"] == 1
    assert m["cost_usd_real"] == 0.05  # custo real somado, não estimado
    assert m["tasks_by_source"] == {"eval": 1, "agent": 1}


def test_compute_metrics_empty():
    assert dashboard.compute_metrics([]) == {"empty": True}


# ── sync_activity ──────────────────────────────────────────────────────────
def test_duration_parsing():
    assert sync_activity._duration("2026-05-28T10:00:00Z", "2026-05-28T10:01:30Z") == 90.0


def test_duration_bad_input_is_zero():
    assert sync_activity._duration(None, None) == 0.0
    assert sync_activity._duration("garbage", "x") == 0.0


# ── eval: scoring + regressão ──────────────────────────────────────────────
def _task(scoring=None):
    return {"expected": {"scoring": scoring or {}}}


def _run():
    return {"tool_calls": 5, "duration_seconds": 10,
            "files_created": [], "files_modified": [], "files_deleted": []}


def _clean_file_check():
    return {"required_created_missing": [], "required_modified_missing": [],
            "forbidden_touched": []}


def test_score_run_all_pass():
    gates = {"pest_passes": {"ran": True, "passed": True}}
    score = eval_runner.score_run(_task(), _run(), gates, _clean_file_check(), [])
    assert score["passed"] is True


def test_score_run_fails_on_red_gate():
    gates = {"pest_passes": {"ran": True, "passed": False}}
    score = eval_runner.score_run(_task(), _run(), gates, _clean_file_check(), [])
    assert score["passed"] is False


def test_check_file_expectations_missing_and_forbidden():
    task = {"expected": {
        "required_files_created": ["app/Models/Thing.php"],
        "forbidden_changes": ["config/*"],
    }}
    run = {"files_created": ["app/Models/Other.php"],
           "files_modified": ["config/app.php"], "files_deleted": []}
    res = eval_runner.check_file_expectations(task, run)
    assert "app/Models/Thing.php" in res["required_created_missing"]
    assert any("config/app.php" in f for f in res["forbidden_touched"])


def test_regression_detection(tmp_path, monkeypatch):
    baseline = {"results": [{"task_id": "t1", "score": {"passed": True}}]}
    bf = tmp_path / "baseline.json"
    bf.write_text(json.dumps(baseline))
    monkeypatch.setattr(eval_runner, "BASELINE_FILE", bf)

    regressed = {"passed": 0, "total": 1,
                 "results": [{"task_id": "t1", "score": {"passed": False}}]}
    assert eval_runner.check_regression(regressed) == 1

    ok = {"passed": 1, "total": 1,
          "results": [{"task_id": "t1", "score": {"passed": True}}]}
    assert eval_runner.check_regression(ok) == 0


def test_regression_no_baseline_does_not_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "BASELINE_FILE", tmp_path / "absent.json")
    summary = {"passed": 1, "total": 1,
               "results": [{"task_id": "t1", "score": {"passed": True}}]}
    assert eval_runner.check_regression(summary) == 0
