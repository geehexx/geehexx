# Andrew Crozier

*Building agents that survive contact with production traffic, not just the demo.*

Engineering Manager and AI Lead. Fifteen years of distributed systems, now applied to agentic AI. I lead the technical development of an AI governance and procurement intelligence platform — multi-agent on PydanticAI and AWS Bedrock, with human-in-the-loop approval gates and a hybrid retrieval pipeline (pgvector + BM25 + trigram, fused via reciprocal rank). The interesting work is making the agents NOT fall over when traffic actually shows up.

## The Short Version

Currently **Lead AI Engineer** at a stealth UK startup. Previously **Engineering Manager** at Agoda B2B Platforms (100K+ RPM booking funnel, 2.4M+ properties), and an Engineering Manager at Toptal for six years building the talent-matching engine. Open to UK / EU / remote.

## What I Have Shipped Recently

A few of the harder problems of running agents in production, with the systems I built to solve them:

- **Adaptive retry token bucket** — prevents thundering-herd retries under sub-agent fan-out. Refill rate halves on throttle, doubles on success. Bounded; no infinite-loop risk under contention.
- **Body-content retry classifier** — distinguishes hard quotas (`MONTHLY_REQUEST_COUNT`) from transient throttling so retries do not burn the budget against a wall. Closes the failure mode where status-code-only classification is wrong both ways.
- **Per-chunk stalled-stream protection** — bounds upstream-hang waits to a known grace period. Surfaces a typed `StalledStreamError` so callers can route to a terminal SSE error event instead of a silent truncation.
- **SQLite-WAL coord mailbox** — multi-agent coordination layer with advisory scope leases, deterministic agent naming, A2A v1.0 endpoint at port 8771, and a property-based eval that grades how well a fresh agent picks up a session from its handoff document.
- **Memory-librarian PreToolUse hook** — secret scanner that blocks Write or Edit calls into a research-notes directory when the content carries credential-shaped strings. Closes a regression vector that produced live keys in plaintext four days after a redaction pass.

## Background

**Agoda B2B Platforms (2023–2024)** — Engineering Manager. Led 15+ engineers across multiple squads on the booking funnel. Scala and Kotlin on Kubernetes with RabbitMQ, Redis, and the Saga pattern. Drove the Scala-to-Kotlin migration across three squads with zero booking-funnel downtime. Onboarded 15+ enterprise white-label clients including Citibank, US Bank, American Airlines, WestJet, and KrisFlyer. Prevented retry-storm failures via Envoy retry budgets in a custom Istio service mesh.

**BaxEnergy (2025–2026)** — Engineering Manager (consulting). Engineering maturity assessment after Yokogawa's June 2024 acquisition. Modernisation roadmap delivered in 8 weeks across 2 squads, ~35% MTTR reduction in the first quarter. DORA metrics, on-call rotation, incident management protocols.

**Toptal (2017–2023, 6+ years)** — Engineering Manager and Senior Software Engineer. Distributed teams across booking platforms, affiliate marketing, classifieds, and media. Strong on hands-on diagnosis (Redis circuit breakers, retry storms, distributed transactions), modernisation roadmaps, and partner API design.

**Toptal (2016, freelance network)** — Two early engagements before joining Toptal's internal team full-time. A greenfield ecommerce build for an Australian equestrian-event booking startup (latest Python and Django backend, Angular 2 SPA, full-stack solo IC delivery). A US engineer-coaching platform that worked with software engineers on offer negotiation and career-leveling (Django, working closely with a non-technical founder). Generalist freelance skills: scoping ambiguous greenfield builds against fixed budget, scope negotiation, weekly status reporting that translates engineering risk into business language.

## Stack

Python, Kotlin, Scala, TypeScript. AWS (CDK, ECS, RDS, ElastiCache, Bedrock, WAF). PydanticAI, LangGraph, AG-UI. PostgreSQL with pgvector, ParadeDB, Redis. Kubernetes, Istio. RabbitMQ, Saga pattern. Optuna for parameter sweeping.

## How to Reach Me

- Email: andrewcrozier86 at gmail dot com
- LinkedIn: [linkedin.com/in/ancrozier](https://www.linkedin.com/in/ancrozier)
- Location: Greater Sydney Area (open to UK / EU / remote)
