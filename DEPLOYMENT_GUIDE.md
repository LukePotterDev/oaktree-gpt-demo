# Oaktree GPT 301 Demo — Deployment Guide

This guide walks you through deploying the Enterprise GPT Demo API from GitHub to Railway, then connecting it to a Custom GPT in ChatGPT.

**What you'll end up with:**
- A live API running at a public URL (Railway)
- A Custom GPT in ChatGPT that queries that API in real time
- Three working demos: Client Meeting Prep, Onboarding Review, Risk Memo

**Time required:** ~30 minutes

**Prerequisites:**
- A GitHub account (free)
- A Railway account (free tier works — [railway.app](https://railway.app))
- ChatGPT Plus or Team subscription (required for Custom GPTs with Actions)

---

## Part 1: Deploy the API to Railway

### Step 1: Fork the GitHub Repository

1. Go to **https://github.com/LukePotterDev/oaktree-gpt-demo**
2. Click the **Fork** button (top right)
3. Leave all defaults and click **Create fork**
4. You now have your own copy at `https://github.com/YOUR-USERNAME/oaktree-gpt-demo`

### Step 2: Create a Railway Account

1. Go to **https://railway.app**
2. Click **Login** (top right)
3. Sign in with your **GitHub account** (easiest — it links automatically)
4. If prompted, authorize Railway to access your GitHub

### Step 3: Create a New Project in Railway

1. On the Railway dashboard, click **+ New Project**
2. Select **Deploy from GitHub repo**
3. If this is your first time, Railway will ask to install its GitHub app — click **Configure GitHub** and grant access to your repositories (you can limit to just the `oaktree-gpt-demo` repo)
4. Select **oaktree-gpt-demo** from the list
5. Railway will detect the Dockerfile and start building automatically

### Step 4: Configure the Service

Once the build starts, you need to set up networking so the API is publicly accessible:

1. Click on the service card (it'll say "oaktree-gpt-demo" or similar)
2. Go to the **Settings** tab
3. Scroll down to **Networking** → **Public Networking**
4. Click **Generate Domain**
5. Railway will give you a URL like: `https://oaktree-gpt-demo-production.up.railway.app`
6. **Copy this URL** — you'll need it for the ChatGPT setup

> **Note:** The API runs on port 8000 inside the container. Railway handles the routing automatically via the Dockerfile's `EXPOSE 8000` and the uvicorn startup command. If the deployment fails, go to **Settings → Networking** and set the **Port** to `8000`.

### Step 5: Verify the API is Running

Open your browser and go to:

```
https://YOUR-RAILWAY-URL/health
```

You should see:
```json
{"status": "ok", "service": "Enterprise GPT 301 Demo", "version": "2.0.0"}
```

If you see this, the API is live. If not, check the **Deploy Logs** tab in Railway for error messages.

You can also check the interactive API docs at:
```
https://YOUR-RAILWAY-URL/docs
```

---

## Part 2: Deploy the Web Dashboard (Optional)

The web dashboard is a visual interface that shows all the underlying data. It's useful for demos ("here's the data the GPT is querying") but not required for the GPT to work.

### Step 1: Add a Second Service in Railway

1. In your Railway project, click **+ New** → **GitHub Repo**
2. Select the same **oaktree-gpt-demo** repo
3. Once added, click on the new service card

### Step 2: Configure the Web Service

1. Go to **Settings** tab
2. Under **Source** → **Root Directory**, set it to: `web`
   - This tells Railway to build from the `web/` subfolder (which has its own Dockerfile)
3. Under **Networking**, click **Generate Domain**
4. Copy this URL too (this is your dashboard URL)

### Step 3: Set Environment Variables

1. Go to the **Variables** tab
2. Add these two variables:

| Variable | Value |
|----------|-------|
| `API_BASE_URL` | `https://YOUR-API-RAILWAY-URL` (the URL from Part 1, Step 4) |
| `API_KEY` | `demo-key-2026` |

3. Railway will redeploy automatically after adding variables

### Step 4: Verify the Dashboard

Open the dashboard URL in your browser. You should see a page with links to Clients, Research, Onboarding, Risk, etc.

---

## Part 3: Set Up the Custom GPT in ChatGPT

### Step 1: Open the GPT Editor

1. Go to **https://chatgpt.com**
2. Click your profile icon (bottom-left) → **My GPTs**
3. Click **+ Create a GPT** (top right)
4. Click the **Configure** tab at the top

### Step 2: Set the Name and Description

| Field | Value |
|-------|-------|
| **Name** | `Financial Services Assistant` |
| **Description** | `Queries enterprise systems to prepare meeting briefs, review onboarding cases, and generate risk memos.` |

### Step 3: Paste the Instructions (System Prompt)

In the **Instructions** box, paste everything below exactly as-is:

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

### Step 4: Add the API Action

This is the most important step — it connects the GPT to the live API.

1. Scroll down to **Actions** and click **Create new action**

#### 4a: Set Authentication

1. Click **Authentication** (gear icon or link at the top of the Action editor)
2. Select **API Key**
3. Fill in:

| Field | Value |
|-------|-------|
| **API Key** | `demo-key-2026` |
| **Auth Type** | `Custom` |
| **Custom Header Name** | `X-API-Key` |

4. Click **Save**

#### 4b: Paste the OpenAPI Schema

In the **Schema** box, delete everything that's there and paste this entire block:

```yaml
openapi: 3.1.0
info:
  title: Enterprise GPT 301 Demo API
  version: 2.0.0
servers:
  - url: https://YOUR-RAILWAY-URL-HERE
paths:
  /clients:
    get:
      operationId: listClients
      summary: List all clients
      responses:
        "200":
          description: List of clients
  /client/{client_id}:
    get:
      operationId: getClient
      summary: Get client profile
      parameters:
        - name: client_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Client profile
  /client/{client_id}/positions:
    get:
      operationId: getClientPositions
      summary: Get client holdings/positions
      parameters:
        - name: client_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Client positions
  /research:
    get:
      operationId: listResearch
      summary: List all available research by issuer
      responses:
        "200":
          description: Research index
  /research/{issuer_slug}:
    get:
      operationId: getResearch
      summary: Get research notes for an issuer
      parameters:
        - name: issuer_slug
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Research notes
  /events/{issuer_slug}:
    get:
      operationId: getEvents
      summary: Get recent events for an issuer
      parameters:
        - name: issuer_slug
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Recent events
  /onboarding:
    get:
      operationId: listOnboarding
      summary: List onboarding cases
      parameters:
        - name: status
          in: query
          required: false
          schema:
            type: string
      responses:
        "200":
          description: List of onboarding cases
  /onboarding/{case_id}:
    get:
      operationId: getOnboarding
      summary: Get onboarding case details
      parameters:
        - name: case_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Onboarding case details
  /screening/{case_id}:
    get:
      operationId: getScreening
      summary: Get KYC/AML screening results
      parameters:
        - name: case_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Screening results
  /risk:
    get:
      operationId: listPortfolios
      summary: List portfolio composites
      responses:
        "200":
          description: List of portfolios
  /risk/{portfolio_id}:
    get:
      operationId: getRisk
      summary: Get portfolio risk summary
      parameters:
        - name: portfolio_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Portfolio risk summary
  /crm/note:
    post:
      operationId: createCRMNote
      summary: Create a CRM note
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
                content:
                  type: string
                author:
                  type: string
                confirmation:
                  type: string
      responses:
        "200":
          description: Note created
  /compliance/case:
    post:
      operationId: createComplianceCase
      summary: Open a compliance case
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
                case_type:
                  type: string
                description:
                  type: string
                severity:
                  type: string
                author:
                  type: string
                confirmation:
                  type: string
      responses:
        "200":
          description: Case opened
  /tasks/create:
    post:
      operationId: createTask
      summary: Create a task
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
                related_to:
                  type: string
                priority:
                  type: string
                description:
                  type: string
                confirmation:
                  type: string
      responses:
        "200":
          description: Task created
```

**IMPORTANT:** Replace `https://YOUR-RAILWAY-URL-HERE` on line 7 with your actual Railway URL from Part 1, Step 4 (e.g., `https://oaktree-gpt-demo-production.up.railway.app`).

#### 4c: Verify the Actions Loaded

After pasting, you should see **Available Actions** listed below the schema box:

- listClients
- getClient
- getClientPositions
- listResearch
- getResearch
- getEvents
- listOnboarding
- getOnboarding
- getScreening
- listPortfolios
- getRisk
- createCRMNote
- createComplianceCase
- createTask

If you see all 14 actions listed, you're good. If there are errors, check that the YAML was pasted completely and the URL is correct.

### Step 5: Set Privacy Policy URL

At the bottom of the Action editor, there's a **Privacy policy URL** field. Enter:

```
https://YOUR-RAILWAY-URL/health
```

(Replace with your actual Railway URL. This is a placeholder — for a production deployment you'd use a real privacy policy page.)

### Step 6: Save the GPT

1. Click **Save** (top right)
2. Choose **Only me** (or share with your team as needed)
3. You'll be taken to the GPT's chat interface

**First-time popup:** The first time the GPT tries to call the API, ChatGPT will show a confirmation dialog asking to allow the connection. Click **"Always allow"** so it doesn't ask every time.

---

## Part 4: Test the Three Demo Workflows

### Demo 1: Client Meeting Prep

Type this into the GPT:
```
Prepare me for tomorrow's meeting with Northshore Pension Fund.
```

**What should happen:** The GPT calls multiple endpoints (client profile, positions, research, events) and produces a meeting brief with talking points, likely questions, and follow-up actions.

### Demo 2: Onboarding Review

```
Review onboarding case ONB-2001 and tell me what's outstanding.
```

**What should happen:** The GPT pulls the case details, shows missing documents and exceptions, checks KYC/AML screening, and recommends next steps.

### Demo 3: Risk Memo

```
Generate this week's risk memo for the Strategic Income Composite.
```

**What should happen:** The GPT pulls portfolio risk data ($4.2B portfolio, YTD performance, risk flags, sector exposure) and formats a professional memo.

### Bonus: Write-Back Demo

```
Add a CRM note to Northshore Pension Fund summarizing our meeting prep findings.
```

**What should happen:** The GPT drafts the note, shows you a preview, asks for confirmation, then writes it to the API.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Railway build fails** | Check the Deploy Logs tab. Most common issue: make sure Railway is building from the root directory (not `web/`). The Dockerfile should be auto-detected. |
| **"Could not connect to server" in ChatGPT** | Visit `https://YOUR-RAILWAY-URL/health` in a browser. If it doesn't load, the API isn't running. Check Railway deployment status. |
| **Actions don't appear after pasting schema** | Make sure you pasted the complete YAML without truncation. Check for a red error below the schema box. Try re-pasting. |
| **"Unauthorized" errors** | Verify the API Key auth is set to `demo-key-2026` with header name `X-API-Key` (case-sensitive). |
| **GPT asks to "allow" on every message** | Click "Always allow" on the first confirmation popup. |
| **GPT makes up data instead of calling the API** | Check that the Instructions contain "Always query the API first. Never guess or fabricate data." |
| **Railway says "port not found"** | Go to Settings → Networking and manually set the port to `8000`. |
| **Web dashboard shows errors** | Make sure the `API_BASE_URL` environment variable points to the API service URL (not the web dashboard URL). |

---

## Quick Reference

| Item | Value |
|------|-------|
| **GitHub Repo** | `https://github.com/LukePotterDev/oaktree-gpt-demo` |
| **API Key** | `demo-key-2026` |
| **API Key Header** | `X-API-Key` |
| **Health Check** | `GET /health` (no auth required) |
| **API Docs** | `GET /docs` (interactive Swagger UI) |
| **Client IDs** | `CLI-001` (Northshore Pension), `CLI-002` (Cascade Family Office) |
| **Onboarding Cases** | `ONB-2001` (in progress), `ONB-2002` (complete) |
| **Screening Cases** | `SCR-3001` (cleared), `SCR-3002` (under review) |
| **Portfolio IDs** | `STRAT-INCOME`, `INFRA-COINVEST` |
| **Research Slugs** | `crestmark-distressed-debt-v`, `crestmark-strategic-income`, `crestmark-re-opportunity-iv` |
