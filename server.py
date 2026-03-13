"""
Oaktree Capital GPT 301 Workshop — Mock Enterprise API Server

Simulates financial services workflows for demonstrating how ChatGPT
Custom GPTs connect to enterprise systems via API Actions.

Endpoints match the GPT 301 Checklist specification exactly.
All data is synthetic. No real Oaktree data is used.
"""

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

app = FastAPI(
    title="Oaktree GPT 301 Demo API",
    description="Mock enterprise API for ChatGPT Actions workshop — financial services workflows",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth ---
API_KEY = "demo-key-2026"
api_key_header = APIKeyHeader(name="X-API-Key")


def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


# =============================================================================
# MOCK DATA — CLIENTS
# =============================================================================

CLIENTS = {
    "CLI-001": {
        "id": "CLI-001",
        "name": "Northshore Pension Fund",
        "type": "Defined Benefit Pension",
        "sector": "Public Pension",
        "aum": 3_800_000_000,
        "relationship_manager": "Sarah Chen",
        "status": "Active",
        "inception_date": "2014-06-15",
        "last_review": "2026-01-22",
        "next_meeting": "2026-03-14",
        "investment_mandate": "Long-term growth with income, 60/40 target with 20% alternatives allocation",
        "risk_tolerance": "Moderate",
        "benchmark": "60% MSCI ACWI / 40% Bloomberg Aggregate",
        "key_contacts": [
            {"name": "Margaret Torres", "title": "CIO", "email": "mtorres@northshore-pension.example.com"},
            {"name": "David Huang", "title": "Investment Director", "email": "dhuang@northshore-pension.example.com"},
        ],
        "notes": "Board meeting in April — will need updated performance attribution. CIO flagged interest in expanding alternatives sleeve to 25%.",
    },
    "CLI-002": {
        "name": "Cascade Family Office",
        "id": "CLI-002",
        "type": "Single Family Office",
        "sector": "Family Office",
        "aum": 620_000_000,
        "relationship_manager": "James Morrison",
        "status": "Active",
        "inception_date": "2019-03-01",
        "last_review": "2026-02-10",
        "next_meeting": "2026-03-28",
        "investment_mandate": "Capital preservation with opportunistic growth, heavy real assets tilt",
        "risk_tolerance": "Conservative",
        "benchmark": "CPI + 4%",
        "key_contacts": [
            {"name": "Richard Cascade III", "title": "Principal", "email": "rc3@cascade-fo.example.com"},
            {"name": "Anna Liu", "title": "Family CFO", "email": "aliu@cascade-fo.example.com"},
        ],
        "notes": "Generational transition underway. Next-gen family members want more ESG integration. Current principal still focused on downside protection.",
    },
}

# =============================================================================
# MOCK DATA — POSITIONS / HOLDINGS
# =============================================================================

POSITIONS = {
    "CLI-001": [
        {"security": "Oaktree Distressed Debt Fund V", "asset_class": "Alternatives — Credit", "market_value": 285_000_000, "allocation_pct": 7.5, "inception": "2023-01-15", "ytd_return": 8.2, "status": "Active"},
        {"security": "Oaktree Real Estate Opportunity IV", "asset_class": "Alternatives — Real Estate", "market_value": 190_000_000, "allocation_pct": 5.0, "inception": "2022-06-01", "ytd_return": 4.1, "status": "Active"},
        {"security": "Oaktree Strategic Income Fund", "asset_class": "Fixed Income — High Yield", "market_value": 380_000_000, "allocation_pct": 10.0, "inception": "2020-09-15", "ytd_return": 5.7, "status": "Active"},
        {"security": "MSCI ACWI Index Fund", "asset_class": "Equity — Global", "market_value": 1_140_000_000, "allocation_pct": 30.0, "inception": "2014-06-15", "ytd_return": 7.3, "status": "Active"},
        {"security": "S&P 500 Index Fund", "asset_class": "Equity — US Large Cap", "market_value": 570_000_000, "allocation_pct": 15.0, "inception": "2014-06-15", "ytd_return": 8.9, "status": "Active"},
        {"security": "Bloomberg Aggregate Bond Fund", "asset_class": "Fixed Income — Investment Grade", "market_value": 760_000_000, "allocation_pct": 20.0, "inception": "2014-06-15", "ytd_return": 2.1, "status": "Active"},
        {"security": "Oaktree Infrastructure Co-Invest II", "asset_class": "Alternatives — Infrastructure", "market_value": 152_000_000, "allocation_pct": 4.0, "inception": "2024-03-01", "ytd_return": 6.8, "status": "Active"},
        {"security": "TIPS Fund", "asset_class": "Fixed Income — Inflation Protected", "market_value": 171_000_000, "allocation_pct": 4.5, "inception": "2021-01-10", "ytd_return": 1.9, "status": "Active"},
        {"security": "Emerging Markets Equity Fund", "asset_class": "Equity — EM", "market_value": 114_000_000, "allocation_pct": 3.0, "inception": "2018-07-01", "ytd_return": 3.4, "status": "Active"},
        {"security": "Cash & Equivalents", "asset_class": "Cash", "market_value": 38_000_000, "allocation_pct": 1.0, "inception": "2014-06-15", "ytd_return": 4.8, "status": "Active"},
    ],
    "CLI-002": [
        {"security": "Oaktree Real Estate Opportunity IV", "asset_class": "Alternatives — Real Estate", "market_value": 93_000_000, "allocation_pct": 15.0, "inception": "2022-06-01", "ytd_return": 4.1, "status": "Active"},
        {"security": "Oaktree Strategic Income Fund", "asset_class": "Fixed Income — High Yield", "market_value": 62_000_000, "allocation_pct": 10.0, "inception": "2021-04-15", "ytd_return": 5.7, "status": "Active"},
        {"security": "US Treasury Bond Ladder", "asset_class": "Fixed Income — Government", "market_value": 186_000_000, "allocation_pct": 30.0, "inception": "2019-03-01", "ytd_return": 2.8, "status": "Active"},
        {"security": "Gold & Precious Metals Fund", "asset_class": "Commodities", "market_value": 62_000_000, "allocation_pct": 10.0, "inception": "2020-11-01", "ytd_return": 12.4, "status": "Active"},
        {"security": "S&P 500 Index Fund", "asset_class": "Equity — US Large Cap", "market_value": 124_000_000, "allocation_pct": 20.0, "inception": "2019-03-01", "ytd_return": 8.9, "status": "Active"},
        {"security": "Oaktree Infrastructure Co-Invest II", "asset_class": "Alternatives — Infrastructure", "market_value": 62_000_000, "allocation_pct": 10.0, "inception": "2024-03-01", "ytd_return": 6.8, "status": "Active"},
        {"security": "Cash & Equivalents", "asset_class": "Cash", "market_value": 31_000_000, "allocation_pct": 5.0, "inception": "2019-03-01", "ytd_return": 4.8, "status": "Active"},
    ],
}

# =============================================================================
# MOCK DATA — RESEARCH NOTES
# =============================================================================

RESEARCH = {
    "oaktree-distressed-debt-v": [
        {"id": "RES-001", "issuer": "Oaktree Distressed Debt Fund V", "date": "2026-03-08", "analyst": "Karen Wu", "title": "Q4 2025 Performance Review", "summary": "Fund returned 3.1% in Q4, outperforming benchmark by 140bps. Key drivers: restructuring gains in energy sector holdings and early recovery in commercial real estate debt. Pipeline of new opportunities remains strong as regional bank stress creates dislocated credit.", "rating": "Overweight", "conviction": "High"},
        {"id": "RES-002", "issuer": "Oaktree Distressed Debt Fund V", "date": "2026-02-15", "analyst": "Karen Wu", "title": "Sector Outlook: Distressed Credit 2026", "summary": "Expect elevated default cycle in commercial real estate and mid-market leveraged loans through H1 2026. Fund well-positioned with dry powder of $1.2B. Regional banking stress creating opportunities in performing but dislocated credits.", "rating": "Overweight", "conviction": "High"},
    ],
    "oaktree-strategic-income": [
        {"id": "RES-003", "issuer": "Oaktree Strategic Income Fund", "date": "2026-03-05", "analyst": "Michael Torres", "title": "Strategic Income: Yield Compression Watch", "summary": "Spreads have tightened 45bps since December. Fund maintaining shorter duration positioning. Recommend monitoring for rotation opportunity if spreads widen in Q2. Current yield: 7.2%, duration: 3.4 years.", "rating": "Neutral", "conviction": "Medium"},
        {"id": "RES-004", "issuer": "Oaktree Strategic Income Fund", "date": "2026-01-20", "analyst": "Michael Torres", "title": "Annual Strategy Review", "summary": "Fund outperformed benchmark by 210bps in 2025. Manager alpha primarily from security selection in BB-rated credits. Recommend maintaining current allocation. Key risk: rapid rate cuts could compress yields faster than expected.", "rating": "Overweight", "conviction": "High"},
    ],
    "oaktree-re-opportunity-iv": [
        {"id": "RES-005", "issuer": "Oaktree Real Estate Opportunity IV", "date": "2026-02-28", "analyst": "Jennifer Park", "title": "Real Estate Fund Update: Office Repositioning", "summary": "Three office-to-mixed-use conversions on track. Chicago asset 60% leased (ahead of plan). NYC asset permitting delayed 2 months but economics still attractive. Fund overall: 1.15x MOIC, 9.2% net IRR. Distributions expected to accelerate H2 2026.", "rating": "Overweight", "conviction": "Medium"},
    ],
}

# =============================================================================
# MOCK DATA — MARKET EVENTS
# =============================================================================

EVENTS = {
    "oaktree-distressed-debt-v": [
        {"date": "2026-03-10", "type": "Market Event", "headline": "Regional Bank CRE Losses Widen", "detail": "Three mid-size regional banks reported higher-than-expected CRE loan losses in Q4 filings. Distressed debt funds positioned to acquire performing loans at discount.", "impact": "Positive — expands fund's opportunity set", "relevance": "High"},
        {"date": "2026-03-03", "type": "Fund Update", "headline": "New Investment: Redstone Energy Restructuring", "detail": "Fund acquired $180M of senior secured debt in Redstone Energy at 72 cents on the dollar. Company entering consensual restructuring. Expected recovery: 90-95 cents.", "impact": "Positive — high-conviction position", "relevance": "High"},
        {"date": "2026-02-20", "type": "Regulatory", "headline": "SEC Proposes New Distressed Fund Reporting Requirements", "detail": "Proposed rule would require quarterly position-level reporting for funds over $500M in distressed assets. Comment period open through April 15.", "impact": "Neutral — operational cost increase, no investment impact", "relevance": "Medium"},
    ],
    "oaktree-strategic-income": [
        {"date": "2026-03-11", "type": "Market Event", "headline": "Fed Holds Rates Steady, Signals June Cut", "detail": "Federal Reserve held fed funds rate at 4.25-4.50%. Dot plot suggests two cuts in 2026, likely starting June. Bond markets rallied on the news.", "impact": "Positive — supports credit valuations", "relevance": "High"},
        {"date": "2026-03-01", "type": "Fund Update", "headline": "Distribution: $0.042/unit for February", "detail": "Monthly distribution of $0.042/unit, annualized yield of 7.2%. Distribution covered 1.1x by earnings.", "impact": "Neutral — in line with expectations", "relevance": "Medium"},
    ],
    "oaktree-re-opportunity-iv": [
        {"date": "2026-03-07", "type": "Market Event", "headline": "Office Vacancy Rate Stabilizes at 18.2%", "detail": "National office vacancy rate held steady for second consecutive quarter. Conversion economics increasingly favorable as new supply drops. Fund's repositioning thesis gaining traction.", "impact": "Positive — validates fund strategy", "relevance": "High"},
        {"date": "2026-02-14", "type": "Fund Update", "headline": "Chicago Mixed-Use Asset: Phase 1 Leasing Complete", "detail": "215 Wacker Drive conversion reached 60% leased milestone, 3 months ahead of schedule. Anchor tenant: Midwest Regional Health System (12-year lease).", "impact": "Positive — de-risks largest position", "relevance": "High"},
    ],
}

# =============================================================================
# MOCK DATA — ONBOARDING CASES
# =============================================================================

ONBOARDING = {
    "ONB-2001": {
        "case_id": "ONB-2001",
        "client_name": "Lakeview Municipal Retirement System",
        "type": "New Client Onboarding",
        "status": "In Progress",
        "opened": "2026-02-15",
        "target_completion": "2026-03-31",
        "assigned_to": "David Park",
        "investment_amount": 250_000_000,
        "products": ["Oaktree Strategic Income Fund", "Oaktree Distressed Debt Fund V"],
        "documents": {
            "received": [
                {"name": "Investment Policy Statement", "date_received": "2026-02-20", "status": "Approved"},
                {"name": "Board Resolution", "date_received": "2026-02-22", "status": "Approved"},
                {"name": "W-9 / Tax Documentation", "date_received": "2026-02-25", "status": "Approved"},
                {"name": "Subscription Agreement — Strategic Income", "date_received": "2026-03-01", "status": "Under Review"},
                {"name": "Anti-Money Laundering (AML) Documentation", "date_received": "2026-03-05", "status": "Approved"},
            ],
            "missing": [
                {"name": "Subscription Agreement — Distressed Debt Fund V", "required_by": "2026-03-15", "status": "Not Received", "notes": "Sent to client counsel on 2/28, awaiting signature"},
                {"name": "Custody Agreement", "required_by": "2026-03-15", "status": "Not Received", "notes": "Client's custodian (State Street) has template in review"},
                {"name": "Side Letter (if applicable)", "required_by": "2026-03-20", "status": "Pending", "notes": "Client requested MFN clause — legal reviewing"},
            ],
        },
        "exceptions": [
            {"type": "Concentration Limit", "detail": "Proposed 40% allocation to alternatives exceeds standard 25% guideline. Requires Investment Committee approval.", "status": "Pending Approval", "raised_by": "Maria Lopez", "date": "2026-03-02"},
            {"type": "Minimum Investment", "detail": "Distressed Debt Fund V subscription at $100M is below the $150M institutional minimum. GP discretion waiver requested.", "status": "Approved", "raised_by": "Sarah Chen", "date": "2026-02-28"},
        ],
        "next_steps": "Follow up with client counsel on Distressed Debt subscription agreement. Escalate concentration limit exception to Investment Committee (next meeting: March 18).",
    },
    "ONB-2002": {
        "case_id": "ONB-2002",
        "client_name": "Pacific Teachers Retirement",
        "type": "New Product Onboarding",
        "status": "Complete",
        "opened": "2026-01-10",
        "target_completion": "2026-02-28",
        "assigned_to": "James Morrison",
        "investment_amount": 175_000_000,
        "products": ["Oaktree Infrastructure Co-Invest II"],
        "documents": {
            "received": [
                {"name": "Investment Policy Statement", "date_received": "2026-01-15", "status": "Approved"},
                {"name": "Subscription Agreement", "date_received": "2026-01-22", "status": "Approved"},
                {"name": "Side Letter", "date_received": "2026-02-05", "status": "Approved"},
                {"name": "AML Documentation", "date_received": "2026-01-18", "status": "Approved"},
                {"name": "Custody Agreement", "date_received": "2026-02-10", "status": "Approved"},
            ],
            "missing": [],
        },
        "exceptions": [],
        "next_steps": "Onboarding complete. First capital call scheduled for April 1, 2026.",
    },
}

# =============================================================================
# MOCK DATA — SCREENING / COMPLIANCE
# =============================================================================

SCREENING = {
    "SCR-3001": {
        "case_id": "SCR-3001",
        "client_name": "Lakeview Municipal Retirement System",
        "related_onboarding": "ONB-2001",
        "type": "KYC / AML Screening",
        "status": "Cleared",
        "completed": "2026-03-06",
        "analyst": "Maria Lopez",
        "results": {
            "sanctions_check": "Clear — no matches on OFAC, EU, or UN sanctions lists",
            "pep_screening": "Clear — no Politically Exposed Persons identified among authorized signatories",
            "adverse_media": "Clear — no adverse media hits for entity or key personnel",
            "source_of_funds": "Verified — municipal pension contributions, audited financial statements reviewed",
            "risk_rating": "Low",
        },
        "notes": "Standard municipal pension fund with transparent funding sources. Annual re-screening scheduled for March 2027.",
    },
    "SCR-3002": {
        "case_id": "SCR-3002",
        "client_name": "Meridian Offshore Fund Ltd",
        "related_onboarding": None,
        "type": "Enhanced Due Diligence",
        "status": "Under Review",
        "completed": None,
        "analyst": "Maria Lopez",
        "results": {
            "sanctions_check": "Clear",
            "pep_screening": "Flag — one beneficial owner previously served as government minister in a high-risk jurisdiction",
            "adverse_media": "Flag — 2024 media reports regarding tax authority inquiry (resolved, no charges)",
            "source_of_funds": "Under Review — awaiting audited financials and fund flow documentation",
            "risk_rating": "Elevated",
        },
        "notes": "Enhanced due diligence triggered by PEP flag and offshore jurisdiction. Awaiting additional documentation from fund administrator. Escalated to Compliance Committee.",
    },
}

# =============================================================================
# MOCK DATA — RISK / PORTFOLIO
# =============================================================================

RISK = {
    "STRAT-INCOME": {
        "portfolio_id": "STRAT-INCOME",
        "portfolio_name": "Strategic Income Composite",
        "as_of_date": "2026-03-07",
        "aum": 4_200_000_000,
        "benchmark": "ICE BofA US High Yield Index",
        "performance": {
            "mtd": 0.8,
            "qtd": 2.1,
            "ytd": 5.7,
            "one_year": 9.4,
            "three_year_ann": 7.8,
            "since_inception_ann": 8.1,
            "benchmark_ytd": 4.9,
            "excess_return_ytd": 0.8,
        },
        "risk_metrics": {
            "duration": 3.4,
            "yield_to_worst": 7.2,
            "spread_duration": 3.1,
            "average_credit_quality": "BB+",
            "sharpe_ratio": 1.42,
            "max_drawdown_12m": -2.1,
            "var_95_1day": -0.18,
            "tracking_error": 1.8,
        },
        "sector_exposure": [
            {"sector": "Energy", "weight": 18.2, "change_1m": 1.5},
            {"sector": "Healthcare", "weight": 14.8, "change_1m": -0.3},
            {"sector": "Technology", "weight": 12.1, "change_1m": 0.8},
            {"sector": "Financials", "weight": 11.5, "change_1m": -1.2},
            {"sector": "Industrials", "weight": 10.3, "change_1m": 0.4},
            {"sector": "Real Estate", "weight": 8.7, "change_1m": -0.5},
            {"sector": "Consumer Cyclical", "weight": 7.9, "change_1m": 0.2},
            {"sector": "Communications", "weight": 6.4, "change_1m": -0.1},
            {"sector": "Utilities", "weight": 5.2, "change_1m": 0.3},
            {"sector": "Cash", "weight": 4.9, "change_1m": -1.1},
        ],
        "top_holdings": [
            {"name": "Redstone Energy 8.5% 2029", "weight": 2.8, "rating": "B+"},
            {"name": "Crestview Health 7.25% 2028", "weight": 2.4, "rating": "BB-"},
            {"name": "Pinnacle Telecom 6.875% 2030", "weight": 2.1, "rating": "BB"},
            {"name": "Atlas Industrial 7.75% 2027", "weight": 1.9, "rating": "BB+"},
            {"name": "Meridian CRE 9.0% 2028", "weight": 1.7, "rating": "B"},
        ],
        "risk_flags": [
            {"flag": "Concentration", "detail": "Energy sector at 18.2% — approaching 20% internal limit. Monitor for further increases.", "severity": "Watch"},
            {"flag": "Liquidity", "detail": "3 positions (combined 4.1% of portfolio) have bid-ask spreads >200bps. Below threshold but trending wider.", "severity": "Watch"},
            {"flag": "Credit Migration", "detail": "2 holdings (1.8% of portfolio) downgraded in February. Both from BB to BB-. No action required per IPS.", "severity": "Informational"},
        ],
        "weekly_commentary": "Spreads tightened 12bps on dovish Fed signal. Portfolio outperformed benchmark by 15bps on the week, driven by energy overweight. Reduced cash position by 110bps to fund new Redstone Energy position. Monitoring energy concentration as it approaches internal limit. No material credit events during the week.",
    },
    "INFRA-COINVEST": {
        "portfolio_id": "INFRA-COINVEST",
        "portfolio_name": "Infrastructure Co-Investment Composite",
        "as_of_date": "2026-03-07",
        "aum": 1_800_000_000,
        "benchmark": "CPI + 5%",
        "performance": {
            "mtd": 0.5,
            "qtd": 1.8,
            "ytd": 6.8,
            "one_year": 11.2,
            "three_year_ann": None,
            "since_inception_ann": 10.4,
            "benchmark_ytd": 3.2,
            "excess_return_ytd": 3.6,
        },
        "risk_metrics": {
            "irr_net": 10.4,
            "moic": 1.22,
            "dpi": 0.15,
            "tvpi": 1.22,
            "sharpe_ratio": None,
            "max_drawdown_12m": None,
            "var_95_1day": None,
            "tracking_error": None,
        },
        "sector_exposure": [
            {"sector": "Renewable Energy", "weight": 35.2, "change_1m": 2.1},
            {"sector": "Digital Infrastructure", "weight": 24.8, "change_1m": 0.0},
            {"sector": "Transportation", "weight": 18.5, "change_1m": -0.8},
            {"sector": "Water & Waste", "weight": 12.3, "change_1m": 0.0},
            {"sector": "Unfunded Commitments", "weight": 9.2, "change_1m": -1.3},
        ],
        "top_holdings": [
            {"name": "SunBridge Solar Portfolio", "weight": 14.1, "rating": "N/A — Private"},
            {"name": "NorthLink Data Centers", "weight": 12.7, "rating": "N/A — Private"},
            {"name": "Pacific Gateway Ports", "weight": 10.3, "rating": "N/A — Private"},
            {"name": "CleanWater Municipal Systems", "weight": 8.8, "rating": "N/A — Private"},
            {"name": "Midwest Wind Holdings", "weight": 7.2, "rating": "N/A — Private"},
        ],
        "risk_flags": [
            {"flag": "Concentration", "detail": "Renewable energy at 35.2% — above 30% target. Driven by SunBridge valuation mark-up. Will rebalance naturally as new commitments fund.", "severity": "Watch"},
            {"flag": "Regulatory", "detail": "IRA clean energy tax credit extension under Congressional review. Potential impact to SunBridge and Midwest Wind valuations if credits reduced.", "severity": "Elevated"},
        ],
        "weekly_commentary": "Quiet week for private infrastructure. SunBridge Solar received updated independent valuation reflecting completed Phase 2 construction — mark-up of 8% driving renewable concentration higher. NorthLink Data Centers signed new hyperscaler tenant (10-year lease). No material risk events.",
    },
}

# =============================================================================
# IN-MEMORY STORES FOR WRITE OPERATIONS
# =============================================================================

CRM_NOTES: list[dict] = []
COMPLIANCE_CASES: list[dict] = []
TASKS: list[dict] = []


# =============================================================================
# REQUEST MODELS
# =============================================================================


class CRMNoteCreate(BaseModel):
    client_id: str
    content: str
    author: str
    confirmation: str  # Must be "CONFIRMED"


class ComplianceCaseCreate(BaseModel):
    client_name: str
    case_type: str
    description: str
    severity: str
    author: str
    confirmation: str  # Must be "CONFIRMED"


class TaskCreate(BaseModel):
    title: str
    assigned_to: str
    due_date: str
    related_to: str
    priority: str
    description: str
    confirmation: str  # Must be "CONFIRMED"


# =============================================================================
# READ ENDPOINTS — CLIENT DATA (Salesforce-like)
# =============================================================================


@app.get("/client/{client_id}", tags=["Client Data (e.g. Salesforce CRM)"])
def get_client(client_id: str, _: str = Depends(verify_key)):
    """Get client profile including contacts, investment mandate, and relationship details."""
    if client_id not in CLIENTS:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found. Available: {', '.join(CLIENTS.keys())}")
    return CLIENTS[client_id]


@app.get("/client/{client_id}/positions", tags=["Client Data (e.g. Salesforce CRM)"])
def get_client_positions(client_id: str, _: str = Depends(verify_key)):
    """Get client's current holdings/positions with allocation, returns, and status."""
    if client_id not in POSITIONS:
        raise HTTPException(status_code=404, detail=f"No positions found for {client_id}")
    holdings = POSITIONS[client_id]
    total_value = sum(p["market_value"] for p in holdings)
    return {
        "client_id": client_id,
        "client_name": CLIENTS.get(client_id, {}).get("name", "Unknown"),
        "total_market_value": total_value,
        "positions_count": len(holdings),
        "positions": holdings,
    }


@app.get("/clients", tags=["Client Data (e.g. Salesforce CRM)"])
def list_clients(_: str = Depends(verify_key)):
    """List all clients with summary info."""
    return {
        "clients": [
            {"id": c["id"], "name": c["name"], "type": c["type"], "aum": c["aum"], "status": c["status"], "relationship_manager": c["relationship_manager"]}
            for c in CLIENTS.values()
        ],
        "total": len(CLIENTS),
    }


# =============================================================================
# READ ENDPOINTS — RESEARCH
# =============================================================================


@app.get("/research/{issuer_slug}", tags=["Research (e.g. Internal Research Platform)"])
def get_research(issuer_slug: str, _: str = Depends(verify_key)):
    """Get research notes for an issuer. Use slugs like 'oaktree-distressed-debt-v', 'oaktree-strategic-income', 'oaktree-re-opportunity-iv'."""
    if issuer_slug not in RESEARCH:
        raise HTTPException(
            status_code=404,
            detail=f"No research found for '{issuer_slug}'. Available: {', '.join(RESEARCH.keys())}",
        )
    return {"issuer": issuer_slug, "notes": RESEARCH[issuer_slug], "total": len(RESEARCH[issuer_slug])}


@app.get("/research", tags=["Research (e.g. Internal Research Platform)"])
def list_research(_: str = Depends(verify_key)):
    """List all available research by issuer."""
    return {
        "issuers": [
            {"slug": slug, "notes_count": len(notes), "latest": notes[0]["date"] if notes else None}
            for slug, notes in RESEARCH.items()
        ]
    }


# =============================================================================
# READ ENDPOINTS — EVENTS
# =============================================================================


@app.get("/events/{issuer_slug}", tags=["Market Events (e.g. Bloomberg / Market Data Feed)"])
def get_events(issuer_slug: str, _: str = Depends(verify_key)):
    """Get recent market events, fund updates, and regulatory news for an issuer."""
    if issuer_slug not in EVENTS:
        raise HTTPException(
            status_code=404,
            detail=f"No events found for '{issuer_slug}'. Available: {', '.join(EVENTS.keys())}",
        )
    return {"issuer": issuer_slug, "events": EVENTS[issuer_slug], "total": len(EVENTS[issuer_slug])}


# =============================================================================
# READ ENDPOINTS — ONBOARDING
# =============================================================================


@app.get("/onboarding/{case_id}", tags=["Onboarding (e.g. Workday / Client Lifecycle)"])
def get_onboarding(case_id: str, _: str = Depends(verify_key)):
    """Get onboarding case details including documents received, missing documents, and exceptions."""
    if case_id not in ONBOARDING:
        raise HTTPException(
            status_code=404,
            detail=f"Onboarding case {case_id} not found. Available: {', '.join(ONBOARDING.keys())}",
        )
    return ONBOARDING[case_id]


@app.get("/onboarding", tags=["Onboarding (e.g. Workday / Client Lifecycle)"])
def list_onboarding(status: Optional[str] = None, _: str = Depends(verify_key)):
    """List all onboarding cases. Optionally filter by status."""
    cases = list(ONBOARDING.values())
    if status:
        cases = [c for c in cases if c["status"].lower() == status.lower()]
    return {
        "cases": [
            {"case_id": c["case_id"], "client_name": c["client_name"], "status": c["status"], "target_completion": c["target_completion"]}
            for c in cases
        ],
        "total": len(cases),
    }


# =============================================================================
# READ ENDPOINTS — SCREENING / COMPLIANCE
# =============================================================================


@app.get("/screening/{case_id}", tags=["KYC / AML Screening (e.g. Compliance System)"])
def get_screening(case_id: str, _: str = Depends(verify_key)):
    """Get KYC/AML screening results for a case."""
    if case_id not in SCREENING:
        raise HTTPException(
            status_code=404,
            detail=f"Screening case {case_id} not found. Available: {', '.join(SCREENING.keys())}",
        )
    return SCREENING[case_id]


# =============================================================================
# READ ENDPOINTS — RISK / PORTFOLIO
# =============================================================================


@app.get("/risk/{portfolio_id}", tags=["Risk & Portfolio (e.g. Portfolio Management System)"])
def get_risk(portfolio_id: str, _: str = Depends(verify_key)):
    """Get risk summary, performance, sector exposure, and risk flags for a portfolio composite."""
    if portfolio_id not in RISK:
        raise HTTPException(
            status_code=404,
            detail=f"Portfolio {portfolio_id} not found. Available: {', '.join(RISK.keys())}",
        )
    return RISK[portfolio_id]


@app.get("/risk", tags=["Risk & Portfolio (e.g. Portfolio Management System)"])
def list_portfolios(_: str = Depends(verify_key)):
    """List all portfolio composites with summary info."""
    return {
        "portfolios": [
            {"id": r["portfolio_id"], "name": r["portfolio_name"], "aum": r["aum"], "ytd": r["performance"]["ytd"]}
            for r in RISK.values()
        ]
    }


# =============================================================================
# WRITE ENDPOINTS — APPROVAL-GATED
# =============================================================================


@app.post("/crm/note", tags=["Write-Back Operations (e.g. Salesforce / Compliance / Task System)"])
def create_crm_note(note: CRMNoteCreate, _: str = Depends(verify_key)):
    """Create a CRM note on a client. REQUIRES confirmation='CONFIRMED' — always ask user before calling."""
    if note.confirmation != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Write operations require confirmation='CONFIRMED'. Ask the user to confirm before proceeding.")
    new_note = {
        "id": f"NOTE-{uuid.uuid4().hex[:8].upper()}",
        "client_id": note.client_id,
        "content": note.content,
        "author": note.author,
        "created_at": datetime.utcnow().isoformat(),
        "status": "created",
    }
    CRM_NOTES.append(new_note)
    return new_note


@app.post("/compliance/case", tags=["Write-Back Operations (e.g. Salesforce / Compliance / Task System)"])
def create_compliance_case(case: ComplianceCaseCreate, _: str = Depends(verify_key)):
    """Open a new compliance case. REQUIRES confirmation='CONFIRMED' — always ask user before calling."""
    if case.confirmation != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Write operations require confirmation='CONFIRMED'. Ask the user to confirm before proceeding.")
    new_case = {
        "id": f"COMP-{uuid.uuid4().hex[:8].upper()}",
        "client_name": case.client_name,
        "case_type": case.case_type,
        "description": case.description,
        "severity": case.severity,
        "author": case.author,
        "created_at": datetime.utcnow().isoformat(),
        "status": "opened",
    }
    COMPLIANCE_CASES.append(new_case)
    return new_case


@app.post("/tasks/create", tags=["Write-Back Operations (e.g. Salesforce / Compliance / Task System)"])
def create_task(task: TaskCreate, _: str = Depends(verify_key)):
    """Create a new task. REQUIRES confirmation='CONFIRMED' — always ask user before calling."""
    if task.confirmation != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Write operations require confirmation='CONFIRMED'. Ask the user to confirm before proceeding.")
    new_task = {
        "id": f"TASK-{uuid.uuid4().hex[:8].upper()}",
        "title": task.title,
        "assigned_to": task.assigned_to,
        "due_date": task.due_date,
        "related_to": task.related_to,
        "priority": task.priority,
        "description": task.description,
        "created_at": datetime.utcnow().isoformat(),
        "status": "open",
    }
    TASKS.append(new_task)
    return new_task


# =============================================================================
# HEALTH CHECK
# =============================================================================


@app.get("/health", tags=["System"])
def health():
    """Health check — no auth required."""
    return {"status": "ok", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}
