"""
Enterprise GPT Demo — Web Dashboard
Flask frontend for viewing simulated enterprise data.
"""

import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "demo-key-2026")
HEADERS = {"X-API-Key": API_KEY}


def api_get(path):
    """Call the FastAPI backend and return JSON."""
    try:
        r = requests.get(f"{API_BASE}{path}", headers=HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# --- Dashboard ---

@app.route("/")
def index():
    clients = api_get("/clients")
    onboarding = api_get("/onboarding")
    portfolios = api_get("/risk")
    research = api_get("/research")
    return render_template(
        "index.html",
        clients=clients,
        onboarding=onboarding,
        portfolios=portfolios,
        research=research,
    )


# --- Clients ---

@app.route("/clients")
def clients_list():
    data = api_get("/clients")
    return render_template("clients.html", data=data)


@app.route("/client/<client_id>")
def client_detail(client_id):
    client = api_get(f"/client/{client_id}")
    positions = api_get(f"/client/{client_id}/positions")
    return render_template("client_detail.html", client=client, positions=positions)


# --- Research ---

@app.route("/research")
def research_list():
    data = api_get("/research")
    return render_template("research.html", data=data)


@app.route("/research/<slug>")
def research_detail(slug):
    data = api_get(f"/research/{slug}")
    events = api_get(f"/events/{slug}")
    return render_template("research_detail.html", data=data, events=events)


# --- Onboarding ---

@app.route("/onboarding")
def onboarding_list():
    data = api_get("/onboarding")
    return render_template("onboarding.html", data=data)


@app.route("/onboarding/<case_id>")
def onboarding_detail(case_id):
    data = api_get(f"/onboarding/{case_id}")
    return render_template("onboarding_detail.html", data=data)


# --- Screening ---

@app.route("/screening/<case_id>")
def screening_detail(case_id):
    data = api_get(f"/screening/{case_id}")
    return render_template("screening_detail.html", data=data)


# --- Risk / Portfolios ---

@app.route("/risk")
def risk_list():
    data = api_get("/risk")
    return render_template("risk.html", data=data)


@app.route("/risk/<portfolio_id>")
def risk_detail(portfolio_id):
    data = api_get(f"/risk/{portfolio_id}")
    return render_template("risk_detail.html", data=data)


# --- Health ---

@app.route("/health")
def health():
    api_health = api_get("/health")
    return render_template("health.html", api_health=api_health)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
