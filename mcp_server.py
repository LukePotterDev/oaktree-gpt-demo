"""
MCP Server wrapping the Oaktree GPT 301 Demo API.

Gives Claude the same tool-calling capabilities that ChatGPT Actions would provide.
"""

import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

API_BASE = "http://localhost:8000"
API_KEY = "demo-key-2026"

mcp = FastMCP(
    "Oaktree Deal Intelligence",
    instructions=(
        "You are a Financial Services Workflow Assistant for an investment firm. "
        "Use these tools to prepare client meeting briefs, review onboarding cases, "
        "generate risk memos, and manage tasks. Always query the API before answering. "
        "Never guess or fabricate data. For write operations, always confirm with the user first. "
        "Structure outputs as: Summary, Evidence, Risks, Recommended Next Steps."
    ),
)


def _api_get(path: str) -> dict:
    req = urllib.request.Request(f"{API_BASE}{path}", headers={"X-API-Key": API_KEY})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.reason, "status": e.code}


def _api_post(path: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=body,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else e.reason
        return {"error": error_body, "status": e.code}


# ── Client Data ──


@mcp.tool()
def list_clients() -> str:
    """List all clients with summary info (name, type, AUM, status)."""
    return json.dumps(_api_get("/clients"), indent=2)


@mcp.tool()
def get_client(client_id: str) -> str:
    """Get full client profile including contacts, investment mandate, and relationship notes. Use IDs like CLI-001, CLI-002."""
    return json.dumps(_api_get(f"/client/{client_id}"), indent=2)


@mcp.tool()
def get_client_positions(client_id: str) -> str:
    """Get client's current holdings/positions with allocation, market value, and YTD returns."""
    return json.dumps(_api_get(f"/client/{client_id}/positions"), indent=2)


# ── Research ──


@mcp.tool()
def list_research() -> str:
    """List all available research by issuer/fund."""
    return json.dumps(_api_get("/research"), indent=2)


@mcp.tool()
def get_research(issuer_slug: str) -> str:
    """Get analyst research notes for a fund/issuer. Slugs: oaktree-distressed-debt-v, oaktree-strategic-income, oaktree-re-opportunity-iv."""
    return json.dumps(_api_get(f"/research/{issuer_slug}"), indent=2)


# ── Events ──


@mcp.tool()
def get_events(issuer_slug: str) -> str:
    """Get recent market events, fund updates, and regulatory news for a fund/issuer."""
    return json.dumps(_api_get(f"/events/{issuer_slug}"), indent=2)


# ── Onboarding ──


@mcp.tool()
def list_onboarding(status: str = "") -> str:
    """List all onboarding cases. Optionally filter by status (In Progress, Complete)."""
    path = "/onboarding"
    if status:
        path += f"?status={status}"
    return json.dumps(_api_get(path), indent=2)


@mcp.tool()
def get_onboarding(case_id: str) -> str:
    """Get onboarding case details including documents, missing items, and exceptions. Cases: ONB-2001, ONB-2002."""
    return json.dumps(_api_get(f"/onboarding/{case_id}"), indent=2)


# ── Screening ──


@mcp.tool()
def get_screening(case_id: str) -> str:
    """Get KYC/AML screening results for a compliance case. Cases: SCR-3001, SCR-3002."""
    return json.dumps(_api_get(f"/screening/{case_id}"), indent=2)


# ── Risk ──


@mcp.tool()
def list_portfolios() -> str:
    """List all portfolio composites with AUM and YTD performance."""
    return json.dumps(_api_get("/risk"), indent=2)


@mcp.tool()
def get_risk(portfolio_id: str) -> str:
    """Get portfolio risk summary: metrics, performance, sectors, holdings, flags, commentary. Portfolios: STRAT-INCOME, INFRA-COINVEST."""
    return json.dumps(_api_get(f"/risk/{portfolio_id}"), indent=2)


# ── Write Operations ──


@mcp.tool()
def create_crm_note(client_id: str, content: str, author: str) -> str:
    """Create a CRM note on a client record. ONLY call after user explicitly confirms."""
    return json.dumps(_api_post("/crm/note", {
        "client_id": client_id, "content": content, "author": author, "confirmation": "CONFIRMED",
    }), indent=2)


@mcp.tool()
def create_compliance_case(client_name: str, case_type: str, description: str, severity: str, author: str) -> str:
    """Open a new compliance case. ONLY call after user explicitly confirms."""
    return json.dumps(_api_post("/compliance/case", {
        "client_name": client_name, "case_type": case_type, "description": description,
        "severity": severity, "author": author, "confirmation": "CONFIRMED",
    }), indent=2)


@mcp.tool()
def create_task(title: str, assigned_to: str, due_date: str, related_to: str, priority: str, description: str) -> str:
    """Create a new task. ONLY call after user explicitly confirms."""
    return json.dumps(_api_post("/tasks/create", {
        "title": title, "assigned_to": assigned_to, "due_date": due_date,
        "related_to": related_to, "priority": priority, "description": description,
        "confirmation": "CONFIRMED",
    }), indent=2)


if __name__ == "__main__":
    mcp.run()
