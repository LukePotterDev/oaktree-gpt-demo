# ChatGPT Custom GPT Setup Guide

Connect the Enterprise GPT Demo API to a Custom GPT so it can query simulated financial services data in real time.

**API URL:** `https://oaktree-gpt-demo-production.up.railway.app`
**API Key:** `demo-key-2026`
**Web Dashboard (to show data visually):** `https://oaktree-gpt-web-production.up.railway.app`

---

## Step 1: Open the GPT Editor

1. Go to **https://chatgpt.com**
2. Click your name/avatar (bottom-left) → **My GPTs**
3. Click **+ Create a GPT** (top right)
4. You'll land on the GPT Builder. Click the **Configure** tab at the top.

---

## Step 2: Set the Name and Description

| Field | Value |
|-------|-------|
| **Name** | `Financial Services Assistant` |
| **Description** | `Queries enterprise systems to prepare meeting briefs, review onboarding cases, and generate risk memos.` |

---

## Step 3: Paste the System Prompt (Instructions)

In the **Instructions** box, paste the entire contents below:

```
You are a Financial Services Workflow Assistant built for investment professionals at an asset management firm.

You help prepare client meeting briefs, review onboarding cases, generate risk memos, and manage follow-up tasks.

## Your Data Sources

You have access to enterprise systems via API:
- Client Data — client profiles, holdings/positions, CRM notes
- Research — analyst research notes by fund/issuer
- Events — market events, fund updates, regulatory news
- Onboarding — new client/product onboarding cases with document tracking
- Screening — KYC/AML compliance screening results
- Risk — portfolio risk metrics, performance, sector exposure, risk flags

## Rules

1. Always query the API first. Never guess or fabricate data. If the user asks about a client, fund, or case — call the appropriate endpoint.

2. Separate facts from recommendations. Present data clearly, then offer analysis or suggestions separately.

3. Be concise and executive-ready. Use this output structure:
   - Summary — Key facts in 2-3 sentences
   - Evidence — Supporting data points
   - Risks — What could go wrong or needs attention
   - Recommended Next Steps — Actionable items

4. Write operations require explicit confirmation. Before creating a CRM note, compliance case, or task:
   - Show the user exactly what will be written
   - Ask: "Should I go ahead and save this?"
   - Only proceed when they confirm

5. Cross-reference when useful. A meeting prep request should pull client profile, positions, research on their holdings, AND recent events. An onboarding review should also check screening results.

6. If information is missing, say what is missing. Don't fill gaps with assumptions.

## Three Core Workflows

### 1. Client Meeting Prep
When asked to prepare for a client meeting:
- Pull client profile (contacts, mandate, notes)
- Pull current positions/holdings
- Pull research notes on their key holdings
- Pull recent events for those holdings
- Synthesize into a meeting brief with talking points and likely questions

### 2. Onboarding Review
When asked to review an onboarding case:
- Pull onboarding case details
- Highlight missing documents and deadlines
- Surface any exceptions that need approval
- Check related screening/compliance status
- Recommend next steps with owners and dates

### 3. Risk Memo
When asked to generate a risk memo:
- Pull portfolio risk metrics and performance
- Highlight risk flags and their severity
- Show sector exposure changes
- Include weekly commentary
- Format as a professional risk memo

## Limitations
- You can READ all data sources freely
- You can WRITE to CRM notes, compliance cases, and tasks — but only with user confirmation
- Do not provide investment advice or recommendations on specific securities
- All data comes from the connected API — you have no other data sources
```

---

## Step 4: Add the API Action (this is the key part)

1. Scroll down to **Actions** and click **Create new action**
2. You'll see three sections: **Authentication**, **Schema**, and a test area

### 4a: Set Authentication

1. Click **Authentication** (gear icon or link)
2. Choose **API Key**
3. Set these values:

| Field | Value |
|-------|-------|
| **API Key** | `demo-key-2026` |
| **Auth Type** | `API Key` |
| **Custom Header Name** | `X-API-Key` |

4. Click **Save**

### 4b: Paste the OpenAPI Schema

In the **Schema** box, delete anything there and paste this entire YAML:

```yaml
openapi: 3.0.0
info:
  title: Enterprise GPT 301 Demo API
  description: |
    Mock enterprise API for financial services workflows.
    Simulates client data (Salesforce), research, events, onboarding,
    compliance screening, and portfolio risk for ChatGPT Actions demo.
  version: 2.0.0
servers:
  - url: https://oaktree-gpt-demo-production.up.railway.app
    description: Railway-hosted demo API

paths:
  /clients:
    get:
      operationId: listClients
      summary: List all clients
      description: Returns all clients with summary info (name, type, AUM, status, relationship manager).
      responses:
        "200":
          description: List of clients
      security:
        - apiKey: []

  /client/{client_id}:
    get:
      operationId: getClient
      summary: Get client profile
      description: Returns full client profile including contacts, investment mandate, risk tolerance, benchmark, and relationship notes. Use IDs like CLI-001, CLI-002.
      parameters:
        - name: client_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Client profile
        "404":
          description: Client not found
      security:
        - apiKey: []

  /client/{client_id}/positions:
    get:
      operationId: getClientPositions
      summary: Get client holdings/positions
      description: Returns all current positions for a client including asset class, market value, allocation percentage, and YTD return.
      parameters:
        - name: client_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Client positions
        "404":
          description: No positions found
      security:
        - apiKey: []

  /research/{issuer_slug}:
    get:
      operationId: getResearch
      summary: Get research notes for an issuer
      description: "Returns analyst research notes for a specific fund/issuer. Available slugs: crestmark-distressed-debt-v, crestmark-strategic-income, crestmark-re-opportunity-iv"
      parameters:
        - name: issuer_slug
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Research notes
        "404":
          description: No research found
      security:
        - apiKey: []

  /research:
    get:
      operationId: listResearch
      summary: List all available research by issuer
      description: Returns a list of all issuers with research notes available.
      responses:
        "200":
          description: Research index
      security:
        - apiKey: []

  /events/{issuer_slug}:
    get:
      operationId: getEvents
      summary: Get recent events for an issuer
      description: "Returns recent market events, fund updates, and regulatory news for a fund/issuer. Available slugs: crestmark-distressed-debt-v, crestmark-strategic-income, crestmark-re-opportunity-iv"
      parameters:
        - name: issuer_slug
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Recent events
        "404":
          description: No events found
      security:
        - apiKey: []

  /onboarding/{case_id}:
    get:
      operationId: getOnboarding
      summary: Get onboarding case details
      description: "Returns full onboarding case including documents received, missing documents, exceptions, and next steps. Available cases: ONB-2001, ONB-2002."
      parameters:
        - name: case_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Onboarding case details
        "404":
          description: Case not found
      security:
        - apiKey: []

  /onboarding:
    get:
      operationId: listOnboarding
      summary: List onboarding cases
      description: List all onboarding cases. Optionally filter by status.
      parameters:
        - name: status
          in: query
          required: false
          schema:
            type: string
      responses:
        "200":
          description: List of onboarding cases
      security:
        - apiKey: []

  /screening/{case_id}:
    get:
      operationId: getScreening
      summary: Get KYC/AML screening results
      description: "Returns compliance screening results including sanctions, PEP, adverse media, and source of funds checks. Available cases: SCR-3001, SCR-3002."
      parameters:
        - name: case_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Screening results
        "404":
          description: Screening case not found
      security:
        - apiKey: []

  /risk/{portfolio_id}:
    get:
      operationId: getRisk
      summary: Get portfolio risk summary
      description: "Returns risk metrics, performance, sector exposure, top holdings, risk flags, and weekly commentary. Available portfolios: STRAT-INCOME, INFRA-COINVEST."
      parameters:
        - name: portfolio_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Portfolio risk summary
        "404":
          description: Portfolio not found
      security:
        - apiKey: []

  /risk:
    get:
      operationId: listPortfolios
      summary: List portfolio composites
      description: Returns all portfolio composites with AUM and YTD performance.
      responses:
        "200":
          description: List of portfolios
      security:
        - apiKey: []

  /crm/note:
    post:
      operationId: createCRMNote
      summary: Create a CRM note
      description: "Add a note to a client record. IMPORTANT: requires confirmation='CONFIRMED'. Always show the user what will be written and get explicit approval before calling."
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [client_id, content, author, confirmation]
              properties:
                client_id:
                  type: string
                  description: Client ID (e.g., CLI-001)
                content:
                  type: string
                  description: Note content
                author:
                  type: string
                  description: Author name
                confirmation:
                  type: string
                  description: "Must be 'CONFIRMED' to proceed"
      responses:
        "200":
          description: Note created
        "400":
          description: Missing confirmation
      security:
        - apiKey: []

  /compliance/case:
    post:
      operationId: createComplianceCase
      summary: Open a compliance case
      description: "Open a new compliance case. IMPORTANT: requires confirmation='CONFIRMED'. Always show the user what will be filed and get explicit approval before calling."
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [client_name, case_type, description, severity, author, confirmation]
              properties:
                client_name:
                  type: string
                description:
                  type: string
                case_type:
                  type: string
                  description: "e.g., KYC Review, AML Flag, Policy Violation"
                severity:
                  type: string
                  description: "Low, Medium, High, Critical"
                author:
                  type: string
                confirmation:
                  type: string
                  description: "Must be 'CONFIRMED' to proceed"
      responses:
        "200":
          description: Case opened
        "400":
          description: Missing confirmation
      security:
        - apiKey: []

  /tasks/create:
    post:
      operationId: createTask
      summary: Create a task
      description: "Create a new task assignment. IMPORTANT: requires confirmation='CONFIRMED'. Always show the user what will be created and get explicit approval before calling."
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [title, assigned_to, due_date, related_to, priority, description, confirmation]
              properties:
                title:
                  type: string
                assigned_to:
                  type: string
                due_date:
                  type: string
                  description: "YYYY-MM-DD format"
                related_to:
                  type: string
                  description: "Client ID or case ID this task relates to"
                priority:
                  type: string
                  description: "Low, Medium, High, Urgent"
                description:
                  type: string
                confirmation:
                  type: string
                  description: "Must be 'CONFIRMED' to proceed"
      responses:
        "200":
          description: Task created
        "400":
          description: Missing confirmation
      security:
        - apiKey: []

components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
```

### 4c: Verify It Loaded

After pasting, you should see a list of **Available Actions** appear below the schema box:

- listClients
- getClient
- getClientPositions
- getResearch
- listResearch
- getEvents
- getOnboarding
- listOnboarding
- getScreening
- getRisk
- listPortfolios
- createCRMNote
- createComplianceCase
- createTask

If you see all 14, you're good. If you see errors, check for copy/paste issues (extra whitespace, truncated text).

---

## Step 5: Set Privacy Policy (required)

In the Action editor, there's a **Privacy policy URL** field at the bottom. Enter:

```
https://oaktree-gpt-demo-production.up.railway.app/health
```

(This is just a placeholder — it's a valid URL on our server. For a real deployment you'd use an actual privacy policy page.)

---

## Step 6: Save and Test

1. Click **Save** (top right) → choose **Only me** for now
2. You'll be taken to the GPT chat interface
3. The first time you use an action, ChatGPT will show a confirmation popup asking to allow the API connection. Click **Allow** or **Always allow**.

---

## Step 7: Try These Demo Prompts

### Demo 1: Client Meeting Prep
```
Prepare me for tomorrow's meeting with Northshore Pension Fund.
```
The GPT should call multiple endpoints (client profile, positions, research, events) and synthesize a meeting brief.

### Demo 2: Onboarding Review
```
Review onboarding case ONB-2001 and tell me what's outstanding.
```
The GPT should pull the case, highlight missing documents and exceptions, check the screening status, and recommend next steps.

### Demo 3: Risk Memo
```
Generate this week's risk memo for the Strategic Income Composite.
```
The GPT should pull portfolio risk data, performance, sector exposure, risk flags, and format a professional memo.

### Demo 4: Write-Back (CRM Note)
```
Add a CRM note to Northshore Pension Fund summarizing our meeting prep findings.
```
The GPT should draft the note, show it to you, ask for confirmation, then write it to the API.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not connect to server" | Check that Railway is up: visit `https://oaktree-gpt-demo-production.up.railway.app/health` in your browser. Should return `{"status": "ok"}` |
| Actions not appearing | Make sure you pasted the full YAML schema without truncation. Check for a red error message below the schema box. |
| "Unauthorized" errors | Verify the API Key auth is set to `demo-key-2026` with header name `X-API-Key` |
| GPT asks to "allow" every time | Click "Always allow" on the first confirmation popup |
| GPT makes up data instead of calling API | Check that the Instructions include "Always query the API first. Never guess or fabricate data." |

---

## Showing the Web Dashboard During Demo

Before or after the ChatGPT demo, open the web dashboard to show the underlying data:

**https://oaktree-gpt-web-production.up.railway.app**

Talk track: "Here's the simulated enterprise data. We've got client profiles from what would be your CRM, portfolio holdings, analyst research, onboarding cases, compliance screening, and risk reports. The GPT you just saw is querying this exact data in real time through API Actions."
