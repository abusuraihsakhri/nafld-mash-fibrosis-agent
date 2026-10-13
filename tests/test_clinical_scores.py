"""Regression tests for independent MASLD risk-score calculations and API safety."""
import math

import pytest

from nafld_mash_fibrosis_agent.fibrosis import assess_fibrosis
from agents.base import AuditTrail
from cli import parse_csv_bool


def test_fib4_formula_and_low_risk():
    result = assess_fibrosis(age=60, ast=30, alt=40, platelets=250)
    expected = 60 * 30 / (250 * math.sqrt(40))
    assert result["fib4"] == pytest.approx(expected, abs=0.00005)
    assert result["fib4_category"] == "low"
    assert result["nfs"] is None


def test_high_risk_and_age_adjustment():
    high = assess_fibrosis(age=55, ast=90, alt=35, platelets=120)
    assert high["fib4"] > 2.67
    assert high["fib4_category"] == "high"

    older = assess_fibrosis(age=70, ast=40, alt=40, platelets=240)
    assert 1.3 < older["fib4"] < 2
    assert older["fib4_low_risk_cutoff"] == 2
    assert older["fib4_category"] == "low"


def test_below_35_warning_and_boundary():
    younger = assess_fibrosis(age=34, ast=20, alt=40, platelets=250)
    assert any("below age 35" in item for item in younger["cautions"])
    assert younger["fib4_category"] == "low"


def test_nfs_formula():
    result = assess_fibrosis(
        age=52, ast=40, alt=50, platelets=230,
        bmi=29, albumin=4.2,
        impaired_fasting_glucose_or_diabetes=True,
    )
    expected = -1.675 + 0.037 * 52 + 0.094 * 29 + 1.13 + (
        0.99 * (40 / 50)
    ) - 0.013 * 230 - 0.66 * 4.2
    assert result["nfs"] == pytest.approx(expected, abs=0.00005)
    assert result["nfs_category"] in {"low", "indeterminate", "high"}


@pytest.mark.parametrize("kwargs", [
    {"age": 40, "ast": 30, "alt": 0, "platelets": 200},
    {"age": 40, "ast": 30, "alt": 20, "platelets": 0},
    {"age": 40, "ast": float("nan"), "alt": 20, "platelets": 200},
    {"age": 40, "ast": float("inf"), "alt": 20, "platelets": 200},
    {"age": True, "ast": 30, "alt": 20, "platelets": 200},
    {"age": 150, "ast": 30, "alt": 20, "platelets": 200},
    {"age": 45.5, "ast": 30, "alt": 20, "platelets": 200},
    {"age": 40, "ast": 30, "alt": 20, "platelets": 200, "bmi": 30},
    {"age": 40, "ast": 30, "alt": 20, "platelets": 200,
     "bmi": 30, "albumin": 4, "impaired_fasting_glucose_or_diabetes": "False"},
])
def test_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        assess_fibrosis(**kwargs)


def test_csv_boolean_values():
    assert parse_csv_bool("False") is False
    assert parse_csv_bool("0") is False
    assert parse_csv_bool("No") is False
    assert parse_csv_bool("TRUE") is True
    with pytest.raises(ValueError):
        parse_csv_bool("perhaps")


def test_hmac_detects_tampering():
    trail = AuditTrail(secret_key="test-integrity-key-that-is-long")
    first = trail.log("operator", "test", "event", {"status": "OK"})
    assert trail.verify_integrity()
    first["payload_hash"] = "tampered"
    assert trail.verify_integrity()  # Caller cannot mutate internal logs.
    copy = trail.get_trail()
    copy[0]["actor"] = "someone else"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "someone else"
    assert not trail.verify_integrity()


def test_api_scores_and_restricts_logs(monkeypatch):
    from fastapi.testclient import TestClient
    from agents.api import app

    client = TestClient(app)
    resp = client.post("/api/fibrosis", json={
        "age": 60, "ast": 30, "alt": 40, "platelets": 250
    })
    assert resp.status_code == 200
    assert resp.json()["fib4_category"] == "low"

    invalid = client.post("/api/fibrosis", json={
        "age": 60, "ast": 30, "alt": 0, "platelets": 250
    })
    assert invalid.status_code == 422

    monkeypatch.delenv("AUDIT_LOG_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 403
    monkeypatch.setenv("AUDIT_LOG_READ_TOKEN", "test-read-token-with-sufficient-length-2026")
    assert client.get("/api/audit/logs").status_code == 403
    authorized = client.get("/api/audit/logs", headers={
        "Authorization": "Bearer test-read-token-with-sufficient-length-2026"
    })
    assert authorized.status_code == 200
    assert authorized.json()["verified"] is True



def test_batch_honors_original_schema_and_boolean_flags(tmp_path):
    import csv
    from cli import main

    source = tmp_path / "input.csv"
    target = tmp_path / "out.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "CASE-01,SYNTH-01,10,2,False,NOMINAL\n"
        "CASE-02,SYNTH-02,10,2,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
