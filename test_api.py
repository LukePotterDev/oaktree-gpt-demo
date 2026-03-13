"""
Automated test suite for the Crestmark GPT 301 Demo API.

Tests every endpoint against expected data, validates response structures,
and runs the 3 demo workflow sequences end-to-end.

Run: pytest test_api.py -v
Requires: the API server running on localhost:8000
"""

import json
import urllib.request
import urllib.error
import pytest

BASE = "http://localhost:8000"
API_KEY = "demo-key-2026"
BAD_KEY = "wrong-key"


def api_get(path: str, key: str = API_KEY) -> tuple[int, dict]:
    req = urllib.request.Request(f"{BASE}{path}", headers={"X-API-Key": key})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else "{}"
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body}


def api_post(path: str, data: dict, key: str = API_KEY) -> tuple[int, dict]:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"X-API-Key": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else "{}"
        try:
            return e.code, json.loads(err_body)
        except json.JSONDecodeError:
            return e.code, {"error": err_body}


# ═══════════════════════════════════════════════════════════════
# HEALTH & AUTH
# ═══════════════════════════════════════════════════════════════


class TestHealthAndAuth:
    def test_health_no_auth_required(self):
        req = urllib.request.Request(f"{BASE}/health")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"

    def test_reject_bad_api_key(self):
        status, data = api_get("/clients", key=BAD_KEY)
        assert status == 401
        assert "Invalid API key" in data.get("detail", "")

    def test_reject_missing_api_key(self):
        req = urllib.request.Request(f"{BASE}/clients")
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req)
        assert exc_info.value.code in (401, 403, 422)


# ═══════════════════════════════════════════════════════════════
# CLIENT DATA
# ═══════════════════════════════════════════════════════════════


class TestClients:
    def test_list_clients(self):
        status, data = api_get("/clients")
        assert status == 200
        assert data["total"] == 2
        names = [c["name"] for c in data["clients"]]
        assert "Northshore Pension Fund" in names
        assert "Cascade Family Office" in names

    def test_get_client_northshore(self):
        status, data = api_get("/client/CLI-001")
        assert status == 200
        assert data["name"] == "Northshore Pension Fund"
        assert data["aum"] == 3_800_000_000
        assert data["relationship_manager"] == "Sarah Chen"
        assert data["risk_tolerance"] == "Moderate"
        assert data["next_meeting"] == "2026-03-14"
        assert len(data["key_contacts"]) == 2
        assert data["key_contacts"][0]["name"] == "Margaret Torres"
        assert data["key_contacts"][0]["title"] == "CIO"

    def test_get_client_cascade(self):
        status, data = api_get("/client/CLI-002")
        assert status == 200
        assert data["name"] == "Cascade Family Office"
        assert data["aum"] == 620_000_000
        assert data["risk_tolerance"] == "Conservative"

    def test_get_client_not_found(self):
        status, data = api_get("/client/CLI-999")
        assert status == 404

    def test_northshore_positions(self):
        status, data = api_get("/client/CLI-001/positions")
        assert status == 200
        assert data["client_name"] == "Northshore Pension Fund"
        assert data["total_market_value"] == 3_800_000_000
        assert data["positions_count"] == 10
        securities = [p["security"] for p in data["positions"]]
        assert "Crestmark Distressed Debt Fund V" in securities
        assert "Crestmark Strategic Income Fund" in securities
        # Verify allocations sum to ~100%
        total_alloc = sum(p["allocation_pct"] for p in data["positions"])
        assert 99.5 <= total_alloc <= 100.5

    def test_cascade_positions(self):
        status, data = api_get("/client/CLI-002/positions")
        assert status == 200
        assert data["positions_count"] == 7
        total_alloc = sum(p["allocation_pct"] for p in data["positions"])
        assert 99.5 <= total_alloc <= 100.5

    def test_positions_not_found(self):
        status, data = api_get("/client/CLI-999/positions")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# RESEARCH
# ═══════════════════════════════════════════════════════════════


class TestResearch:
    def test_list_research(self):
        status, data = api_get("/research")
        assert status == 200
        slugs = [i["slug"] for i in data["issuers"]]
        assert "crestmark-distressed-debt-v" in slugs
        assert "crestmark-strategic-income" in slugs
        assert "crestmark-re-opportunity-iv" in slugs

    def test_distressed_debt_research(self):
        status, data = api_get("/research/crestmark-distressed-debt-v")
        assert status == 200
        assert data["total"] == 2
        assert data["notes"][0]["analyst"] == "Karen Wu"
        assert data["notes"][0]["rating"] == "Overweight"
        assert data["notes"][0]["conviction"] == "High"

    def test_strategic_income_research(self):
        status, data = api_get("/research/crestmark-strategic-income")
        assert status == 200
        assert data["total"] == 2
        # Verify yield mentioned in research
        assert "7.2%" in data["notes"][0]["summary"]

    def test_research_not_found(self):
        status, data = api_get("/research/nonexistent-fund")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════


class TestEvents:
    def test_distressed_debt_events(self):
        status, data = api_get("/events/crestmark-distressed-debt-v")
        assert status == 200
        assert data["total"] == 3
        types = [e["type"] for e in data["events"]]
        assert "Market Event" in types
        assert "Fund Update" in types
        assert "Regulatory" in types

    def test_strategic_income_events(self):
        status, data = api_get("/events/crestmark-strategic-income")
        assert status == 200
        assert data["total"] == 2
        # Fed rate decision should be in events
        headlines = [e["headline"] for e in data["events"]]
        assert any("Fed" in h for h in headlines)

    def test_events_not_found(self):
        status, data = api_get("/events/nonexistent")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# ONBOARDING
# ═══════════════════════════════════════════════════════════════


class TestOnboarding:
    def test_list_onboarding(self):
        status, data = api_get("/onboarding")
        assert status == 200
        assert data["total"] == 2

    def test_list_onboarding_filter_in_progress(self):
        status, data = api_get("/onboarding?status=In%20Progress")
        assert status == 200
        assert data["total"] == 1
        assert data["cases"][0]["case_id"] == "ONB-2001"

    def test_onb_2001_details(self):
        status, data = api_get("/onboarding/ONB-2001")
        assert status == 200
        assert data["client_name"] == "Lakeview Municipal Retirement System"
        assert data["status"] == "In Progress"
        assert data["investment_amount"] == 250_000_000
        # Documents
        assert len(data["documents"]["received"]) == 5
        assert len(data["documents"]["missing"]) == 3
        # Exceptions
        assert len(data["exceptions"]) == 2
        exception_types = [e["type"] for e in data["exceptions"]]
        assert "Concentration Limit" in exception_types
        assert "Minimum Investment" in exception_types

    def test_onb_2001_missing_docs(self):
        status, data = api_get("/onboarding/ONB-2001")
        missing = data["documents"]["missing"]
        missing_names = [d["name"] for d in missing]
        assert "Subscription Agreement — Distressed Debt Fund V" in missing_names
        assert "Custody Agreement" in missing_names
        assert "Side Letter (if applicable)" in missing_names

    def test_onb_2002_complete(self):
        status, data = api_get("/onboarding/ONB-2002")
        assert status == 200
        assert data["status"] == "Complete"
        assert len(data["documents"]["missing"]) == 0
        assert len(data["exceptions"]) == 0

    def test_onboarding_not_found(self):
        status, data = api_get("/onboarding/ONB-9999")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# SCREENING / COMPLIANCE
# ═══════════════════════════════════════════════════════════════


class TestScreening:
    def test_scr_3001_cleared(self):
        status, data = api_get("/screening/SCR-3001")
        assert status == 200
        assert data["status"] == "Cleared"
        assert data["related_onboarding"] == "ONB-2001"
        assert data["results"]["risk_rating"] == "Low"
        assert "Clear" in data["results"]["sanctions_check"]
        assert "Clear" in data["results"]["pep_screening"]

    def test_scr_3002_flagged(self):
        status, data = api_get("/screening/SCR-3002")
        assert status == 200
        assert data["status"] == "Under Review"
        assert data["results"]["risk_rating"] == "Elevated"
        assert "Flag" in data["results"]["pep_screening"]
        assert "Flag" in data["results"]["adverse_media"]

    def test_screening_not_found(self):
        status, data = api_get("/screening/SCR-9999")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# RISK / PORTFOLIO
# ═══════════════════════════════════════════════════════════════


class TestRisk:
    def test_list_portfolios(self):
        status, data = api_get("/risk")
        assert status == 200
        ids = [p["id"] for p in data["portfolios"]]
        assert "STRAT-INCOME" in ids
        assert "INFRA-COINVEST" in ids

    def test_strategic_income_risk(self):
        status, data = api_get("/risk/STRAT-INCOME")
        assert status == 200
        assert data["portfolio_name"] == "Strategic Income Composite"
        assert data["aum"] == 4_200_000_000
        # Performance
        assert data["performance"]["ytd"] == 5.7
        assert data["performance"]["benchmark_ytd"] == 4.9
        assert data["performance"]["excess_return_ytd"] == 0.8
        # Risk metrics
        assert data["risk_metrics"]["yield_to_worst"] == 7.2
        assert data["risk_metrics"]["average_credit_quality"] == "BB+"
        assert data["risk_metrics"]["sharpe_ratio"] == 1.42
        # Sector exposure
        sectors = [s["sector"] for s in data["sector_exposure"]]
        assert "Energy" in sectors
        # Risk flags
        assert len(data["risk_flags"]) == 3
        flag_types = [f["flag"] for f in data["risk_flags"]]
        assert "Concentration" in flag_types
        assert "Liquidity" in flag_types
        # Weekly commentary exists
        assert len(data["weekly_commentary"]) > 50

    def test_infrastructure_risk(self):
        status, data = api_get("/risk/INFRA-COINVEST")
        assert status == 200
        assert data["aum"] == 1_800_000_000
        assert data["performance"]["ytd"] == 6.8
        assert len(data["risk_flags"]) == 2

    def test_risk_not_found(self):
        status, data = api_get("/risk/NONEXISTENT")
        assert status == 404


# ═══════════════════════════════════════════════════════════════
# WRITE OPERATIONS
# ═══════════════════════════════════════════════════════════════


class TestWriteOperations:
    def test_crm_note_success(self):
        status, data = api_post("/crm/note", {
            "client_id": "CLI-001",
            "content": "Test note from automated suite",
            "author": "Test Runner",
            "confirmation": "CONFIRMED",
        })
        assert status == 200
        assert data["status"] == "created"
        assert data["client_id"] == "CLI-001"
        assert data["content"] == "Test note from automated suite"
        assert "id" in data
        assert data["id"].startswith("NOTE-")

    def test_crm_note_requires_confirmation(self):
        status, data = api_post("/crm/note", {
            "client_id": "CLI-001",
            "content": "Should fail",
            "author": "Test",
            "confirmation": "NOPE",
        })
        assert status == 400

    def test_compliance_case_success(self):
        status, data = api_post("/compliance/case", {
            "client_name": "Test Client",
            "case_type": "KYC Review",
            "description": "Automated test case",
            "severity": "Low",
            "author": "Test Runner",
            "confirmation": "CONFIRMED",
        })
        assert status == 200
        assert data["status"] == "opened"
        assert data["id"].startswith("COMP-")

    def test_compliance_case_requires_confirmation(self):
        status, data = api_post("/compliance/case", {
            "client_name": "Test",
            "case_type": "Test",
            "description": "Should fail",
            "severity": "Low",
            "author": "Test",
            "confirmation": "NO",
        })
        assert status == 400

    def test_task_create_success(self):
        status, data = api_post("/tasks/create", {
            "title": "Test task",
            "assigned_to": "Test User",
            "due_date": "2026-04-01",
            "related_to": "CLI-001",
            "priority": "Medium",
            "description": "Automated test task",
            "confirmation": "CONFIRMED",
        })
        assert status == 200
        assert data["status"] == "open"
        assert data["id"].startswith("TASK-")

    def test_task_requires_confirmation(self):
        status, data = api_post("/tasks/create", {
            "title": "Should fail",
            "assigned_to": "Test",
            "due_date": "2026-04-01",
            "related_to": "CLI-001",
            "priority": "Low",
            "description": "Should fail",
            "confirmation": "NOPE",
        })
        assert status == 400


# ═══════════════════════════════════════════════════════════════
# END-TO-END DEMO WORKFLOW TESTS
# ═══════════════════════════════════════════════════════════════


class TestDemo1_ClientMeetingPrep:
    """
    Demo 1: "Prepare me for tomorrow's Northshore Pension meeting."
    Validates that all data needed for a meeting brief is available and correct.
    """

    def test_client_profile_available(self):
        status, data = api_get("/client/CLI-001")
        assert status == 200
        assert data["next_meeting"] == "2026-03-14"
        assert len(data["key_contacts"]) >= 1

    def test_holdings_available_with_returns(self):
        status, data = api_get("/client/CLI-001/positions")
        assert status == 200
        assert data["positions_count"] >= 5
        for pos in data["positions"]:
            assert "ytd_return" in pos
            assert "allocation_pct" in pos

    def test_research_available_for_key_holdings(self):
        # Get positions first
        _, positions = api_get("/client/CLI-001/positions")
        crestmark_holdings = [
            p for p in positions["positions"]
            if "Crestmark" in p["security"]
        ]
        assert len(crestmark_holdings) >= 3, "Northshore should have 3+ Crestmark fund holdings"

        # Research should exist for key funds
        status, data = api_get("/research/crestmark-distressed-debt-v")
        assert status == 200
        assert len(data["notes"]) >= 1

    def test_events_available_for_holdings(self):
        status, data = api_get("/events/crestmark-distressed-debt-v")
        assert status == 200
        assert len(data["events"]) >= 1
        # Events should be recent
        for event in data["events"]:
            assert event["date"] >= "2026-02-01"

    def test_can_create_followup_note(self):
        status, data = api_post("/crm/note", {
            "client_id": "CLI-001",
            "content": "Meeting prep complete. Key topics: alternatives expansion, Q4 attribution.",
            "author": "Sarah Chen",
            "confirmation": "CONFIRMED",
        })
        assert status == 200


class TestDemo2_OnboardingReview:
    """
    Demo 2: "Review onboarding case ONB-2001 and summarize missing documents and exceptions."
    Validates all onboarding data is present and correctly structured.
    """

    def test_case_exists_with_correct_status(self):
        status, data = api_get("/onboarding/ONB-2001")
        assert status == 200
        assert data["status"] == "In Progress"
        assert data["investment_amount"] == 250_000_000

    def test_received_docs_tracked(self):
        _, data = api_get("/onboarding/ONB-2001")
        received = data["documents"]["received"]
        assert len(received) == 5
        for doc in received:
            assert "name" in doc
            assert "date_received" in doc
            assert "status" in doc

    def test_missing_docs_with_deadlines(self):
        _, data = api_get("/onboarding/ONB-2001")
        missing = data["documents"]["missing"]
        assert len(missing) == 3
        for doc in missing:
            assert "name" in doc
            assert "required_by" in doc
            assert "notes" in doc

    def test_exceptions_flagged(self):
        _, data = api_get("/onboarding/ONB-2001")
        exceptions = data["exceptions"]
        assert len(exceptions) == 2
        # One should be pending
        statuses = [e["status"] for e in exceptions]
        assert "Pending Approval" in statuses

    def test_related_screening_available(self):
        status, data = api_get("/screening/SCR-3001")
        assert status == 200
        assert data["related_onboarding"] == "ONB-2001"
        assert data["status"] == "Cleared"

    def test_next_steps_defined(self):
        _, data = api_get("/onboarding/ONB-2001")
        assert len(data["next_steps"]) > 20


class TestDemo3_RiskMemo:
    """
    Demo 3: "Generate this week's risk memo for Strategic Income Composite."
    Validates all risk data is present for memo generation.
    """

    def test_portfolio_exists(self):
        status, data = api_get("/risk/STRAT-INCOME")
        assert status == 200
        assert data["portfolio_name"] == "Strategic Income Composite"

    def test_performance_vs_benchmark(self):
        _, data = api_get("/risk/STRAT-INCOME")
        perf = data["performance"]
        assert perf["ytd"] > perf["benchmark_ytd"], "Fund should be outperforming benchmark"
        assert perf["excess_return_ytd"] > 0

    def test_risk_metrics_complete(self):
        _, data = api_get("/risk/STRAT-INCOME")
        metrics = data["risk_metrics"]
        required_fields = ["duration", "yield_to_worst", "average_credit_quality", "sharpe_ratio", "var_95_1day"]
        for field in required_fields:
            assert field in metrics, f"Missing risk metric: {field}"
            assert metrics[field] is not None, f"Risk metric {field} is None"

    def test_sector_exposure_sums_to_100(self):
        _, data = api_get("/risk/STRAT-INCOME")
        total = sum(s["weight"] for s in data["sector_exposure"])
        assert 99.5 <= total <= 100.5, f"Sector weights sum to {total}, expected ~100"

    def test_risk_flags_present(self):
        _, data = api_get("/risk/STRAT-INCOME")
        assert len(data["risk_flags"]) >= 1
        for flag in data["risk_flags"]:
            assert "flag" in flag
            assert "detail" in flag
            assert "severity" in flag
            assert flag["severity"] in ("Watch", "Elevated", "Informational", "Critical")

    def test_weekly_commentary_exists(self):
        _, data = api_get("/risk/STRAT-INCOME")
        assert len(data["weekly_commentary"]) > 100, "Weekly commentary should be substantive"

    def test_top_holdings_present(self):
        _, data = api_get("/risk/STRAT-INCOME")
        assert len(data["top_holdings"]) == 5
        for holding in data["top_holdings"]:
            assert "name" in holding
            assert "weight" in holding
            assert "rating" in holding


# ═══════════════════════════════════════════════════════════════
# DATA INTEGRITY
# ═══════════════════════════════════════════════════════════════


class TestDataIntegrity:
    """Cross-system data consistency checks."""

    def test_client_positions_match_aum(self):
        """Total position values should equal reported AUM."""
        _, client = api_get("/client/CLI-001")
        _, positions = api_get("/client/CLI-001/positions")
        assert positions["total_market_value"] == client["aum"]

    def test_onboarding_screening_linked(self):
        """Screening case should reference the correct onboarding case."""
        _, screening = api_get("/screening/SCR-3001")
        _, onboarding = api_get("/onboarding/ONB-2001")
        assert screening["client_name"] == onboarding["client_name"]
        assert screening["related_onboarding"] == onboarding["case_id"]

    def test_research_dates_are_recent(self):
        """All research notes should be from 2026."""
        _, data = api_get("/research/crestmark-distressed-debt-v")
        for note in data["notes"]:
            assert note["date"].startswith("2026-"), f"Research note dated {note['date']} is not from 2026"

    def test_events_have_impact_assessment(self):
        """Every event should have an impact assessment."""
        for slug in ["crestmark-distressed-debt-v", "crestmark-strategic-income", "crestmark-re-opportunity-iv"]:
            _, data = api_get(f"/events/{slug}")
            for event in data["events"]:
                assert "impact" in event
                assert "relevance" in event
                assert event["relevance"] in ("High", "Medium", "Low")
