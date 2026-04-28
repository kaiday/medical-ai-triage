# Medical AI Triage

AI-powered hospital patient triage system — OpenAI Hackathon Sydney 2026

## Overview

A web application that automates the initial hospital check-in process by collecting patient symptoms and using AI to classify urgency, enabling nurses to prioritise care faster and more accurately.

The AI suggests a triage priority; a nurse always reviews and confirms. The human is always in the loop.

## Urgency Levels

| Level | Label | Target Response |
|---|---|---|
| 🔴 CRITICAL | Immediate | See immediately |
| 🟠 HIGH | Urgent | Within 15 minutes |
| 🟡 MEDIUM | Semi-urgent | Within 30–60 minutes |
| 🟢 LOW | Non-urgent | Within 2 hours |

## Architecture

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Tailwind + shadcn/ui |
| Real-time | Supabase Realtime |
| Backend | FastAPI (Python 3.12) |
| Database | Supabase (Postgres) |
| AI | OpenAI API (server-side proxy) |
| Auth | Supabase Auth — anon patient sessions + JWT nurse login |
| Deployment | Railway (pilot) → Docker Compose (on-premise) |

## Project Structure

```
medical-ai-triage/
├── frontend/        # React + TypeScript patient intake & nurse dashboard
├── backend/         # FastAPI — triage API, AI classification proxy
└── docs/            # Architecture and requirements documentation
```

## License

MIT
