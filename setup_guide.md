# Enterprise GPT 301 Workshop — Demo Setup Guide

## What This Is

A Dockerized mock API server that simulates enterprise financial services data (client profiles, holdings, research, events, onboarding, compliance screening, portfolio risk). It powers a Custom GPT that demonstrates three core workflows:

1. **Client Meeting Prep** — pulls client data, holdings, research, and events to generate a meeting brief
2. **Onboarding Review** — pulls case details, missing documents, exceptions, and screening results
3. **Risk Memo** — pulls portfolio metrics, performance, sector exposure, and risk flags

All data is synthetic. No real client data is used.

## Quick Start

```bash
docker compose up --build -d
```

Server runs at `http://localhost:8000`.
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Test it:
```bash
curl -H "X-API-Key: demo-key-2026" http://localhost:8000/clients
```

## Making It Accessible to ChatGPT

ChatGPT Actions need a publicly accessible HTTPS URL.

### Option A: ngrok (quickest for demo)
```bash
ngrok http 8000
```
Copy the `https://xxxxx.ngrok-free.app` URL.

### Option B: Cloud deploy
Push to Railway, Render, or Fly.io. Set the Dockerfile as the build target. No environment variables needed.

## Creating the Custom GPT

1. ChatGPT → Explore GPTs → Create
2. **Name:** Financial Services Workflow Assistant
3. **Description:** Prepare client meeting briefs, review onboarding cases, and generate risk memos using live enterprise data.
4. **Instructions:** Paste contents of `system_prompt.txt`
5. **Configure → Actions → Create new action**
6. Paste contents of `openapi.yaml`
7. Update the `servers` URL to your ngrok/deployed URL
8. **Authentication:**
   - Type: API Key
   - Auth Type: Custom
   - Header Name: `X-API-Key`
   - API Key: `demo-key-2026`
9. Save and test

## Demo Prompts (from the 301 Checklist)

### Demo 1: Client Meeting Prep
```
Prepare me for tomorrow's Northshore Pension meeting.
```
Expected: pulls client profile, 10 holdings, research notes on key funds, recent events. Produces meeting summary, talking points, likely questions, and follow-up actions.

### Demo 2: Onboarding Review
```
Review onboarding case ONB-2001 and summarize missing documents and exceptions.
```
Expected: shows 5 received docs, 3 missing docs with deadlines, 2 exceptions (one pending approval), and related KYC/AML screening results.

### Demo 3: Risk Memo
```
Generate this week's risk memo for Strategic Income Composite.
```
Expected: $4.2B portfolio, YTD +5.7% (80bps over benchmark), 3 risk flags, sector exposure with changes, top holdings, weekly commentary.

### Bonus: Write Operations
```
Add a CRM note to the Northshore account: Met with CIO, board meeting in April, wants updated attribution.
```
Expected: GPT shows preview, asks for confirmation, then creates the note.

```
Create a task: Prepare Q4 performance attribution for Northshore board. Assign to Michael Torres, due April 1, high priority.
```
Expected: same confirmation flow, then creates the task.

## API Endpoints

### Client Data (Salesforce-like)
- `GET /clients` — List all clients
- `GET /client/{id}` — Client profile
- `GET /client/{id}/positions` — Holdings/positions

### Research
- `GET /research` — List available research
- `GET /research/{issuer_slug}` — Research notes for a fund

### Events
- `GET /events/{issuer_slug}` — Market events, fund updates

### Onboarding
- `GET /onboarding` — List onboarding cases
- `GET /onboarding/{case_id}` — Case details

### Screening
- `GET /screening/{case_id}` — KYC/AML results

### Risk
- `GET /risk` — List portfolio composites
- `GET /risk/{portfolio_id}` — Risk summary

### Write Operations (approval-gated)
- `POST /crm/note` — Create CRM note
- `POST /compliance/case` — Open compliance case
- `POST /tasks/create` — Create task

## Files

| File | Purpose |
|------|---------|
| `server.py` | FastAPI server with all endpoints and synthetic data |
| `openapi.yaml` | OpenAPI 3.0 schema for ChatGPT Actions |
| `system_prompt.txt` | GPT system prompt |
| `mcp_server.py` | MCP server for Claude Code testing |
| `.mcp.json` | MCP config for Claude Code |
| `Dockerfile` | Container build |
| `docker-compose.yml` | One-command startup |
| `requirements.txt` | Python dependencies |
| `setup_guide.md` | This file |

## API Key

Default: `demo-key-2026` (header: `X-API-Key`)

## Synthetic Data Inventory

| Data Type | Records | Details |
|-----------|---------|---------|
| Clients | 2 | Northshore Pension ($3.8B), Cascade Family Office ($620M) |
| Positions | 17 | 10 for Northshore, 7 for Cascade |
| Research Notes | 5 | Across 3 funds |
| Market Events | 7 | Across 3 funds |
| Onboarding Cases | 2 | 1 in progress (with missing docs), 1 complete |
| Screening Cases | 2 | 1 cleared, 1 under review (with flags) |
| Portfolios | 2 | Strategic Income ($4.2B), Infrastructure ($1.8B) |
