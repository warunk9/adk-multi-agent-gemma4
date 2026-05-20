# ADK Multi-Agent POC — Customer Support Triage with Gemma 4

A workshop POC demonstrating a multi-agent customer support system built with
[Google ADK (Python)](https://google.github.io/adk-docs/) and Gemma 4 via Google AI Studio.

## Architecture

```
User
 └── triage_agent  (router)
       ├── billing_agent   — payments, invoices, subscriptions, refunds
       ├── tech_agent      — bugs, errors, API issues, troubleshooting
       └── general_agent   — account access, policies, general queries
```

## Setup

**1. Install dependencies**
```bash
pip install -e .
```

**2. Configure your API key**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY from https://aistudio.google.com/apikey
```

**3. Run the agent**

Interactive web UI:
```bash
adk web
```

CLI mode:
```bash
adk run customer_support
```

## Try these sample prompts

| Scenario | Sample message |
|---|---|
| Billing | "I was charged twice this month, can you help?" |
| Technical | "I'm getting a 500 error when calling your API" |
| General | "How do I reset my password?" |

## Project structure

```
.
├── pyproject.toml
├── .env.example
└── customer_support/
    ├── __init__.py
    └── agent.py        ← all agent definitions live here
```
