<div align="center">

# Andrew Crozier

### Lead AI Engineer / Engineering Manager

**Production agents · Hybrid retrieval · MCP systems · Distributed platforms**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-andrewcrozier-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ancrozier/)
[![GitHub](https://img.shields.io/badge/GitHub-geehexx-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/geehexx)
[![AI Systems](https://img.shields.io/badge/Focus-production_AI_systems-7C3AED?style=for-the-badge)](#now)
[![Open to](https://img.shields.io/badge/Open_to-AU_%2F_EU_%2F_Asia_remote-16A34A?style=for-the-badge)](#reach-me)

</div>

---

```text
I build the parts of AI systems that keep working after the demo:
retrieval quality, tool boundaries, stream safety, retry behavior, evaluation loops,
human approval gates, observability, infrastructure, and the teams/processes around them.
```

I work where **LLMs meet backend engineering**: agent orchestration, RAG, search, evals, governance, distributed systems, and reliability under real production constraints.

Demo agents are easy. Agents that survive throttling, retries, stream stalls, partial handoffs, quota walls, governance boundaries, and real users are the interesting problem.

---

## Now

Building an **AI governance and procurement intelligence platform**.

| System area | What I am building |
|---|---|
| **Agentic architecture** | Multi-agent workflows with 20+ specialist sub-agents, PydanticAI, AWS Bedrock, human-in-the-loop approval gates, and quality validation loops |
| **Conversation layer** | LangGraph + AG-UI conversational flows with procurement-specific guardrails and SSE streaming |
| **Retrieval** | Hybrid search over pgvector cosine similarity, BM25, and trigram matching, fused with Reciprocal Rank Fusion |
| **Discovery** | Entropy / mutual-information guided interactive discovery over an ontology, with graceful degradation for vague queries |
| **Infrastructure** | AWS CDK Python across ECS Fargate, RDS PostgreSQL, ElastiCache Redis, Cognito, WAF, and cdk-nag controls |
| **Production hardening** | Typed failure paths, retry classification, stream-stall handling, eval loops, and approval boundaries for high-risk tool use |

---

## Public Work

A selected set of public repos that reflect the kind of systems I like building: agent interfaces, MCP servers, LLM gateways, retrieval/analysis tools, and reliability hardening.

| Repo / work | What it demonstrates |
|---|---|
| [`mcp-web`](https://github.com/geehexx/mcp-web) | MCP server for intelligent web and local-file summarization: extraction, smart chunking, streaming summaries, local/cloud LLM support, caching, security controls, metrics, and tests |
| [`hitl-mcp-cli`](https://github.com/geehexx/hitl-mcp-cli) | Human-in-the-loop MCP server and terminal UI for agent approvals, choices, confirmations, notifications, interaction logging, and async-first workflows |
| [`phraseturner`](https://github.com/geehexx/phraseturner) | Text-analysis MCP server with configurable personas, readability/naturalness/tone scoring, AI-detection signals, semantic persona search, and graceful degradation |
| [`llm-bedrock-converse`](https://github.com/geehexx/llm-bedrock-converse) | `llm` plugin for AWS Bedrock Converse: Claude models, streaming, tool calling, MCP integration, multimodal inputs, embeddings, and automatic retry behavior |
| [`msteams-mcp`](https://github.com/geehexx/msteams-mcp) | MCP server for Microsoft Teams interaction: message search, replies, thread access, authentication flow, and assistant-facing collaboration workflows |
| [`kiro-proxy`](https://github.com/geehexx/kiro-proxy) fork work | Gateway reliability work around streaming, model-name preservation, retry behavior, quota classification, RE2/complexity classification, local gates, and failure-mode cleanup |

Recent reliability PRs I care about:

- [`feat(retry): wire body-content classifier into http_client`](https://github.com/geehexx/kiro-proxy/pull/17) — separates hard quota failures from transient throttling so retries do not burn budget against an unrecoverable wall.
- [`feat(openai): RE2 + complexity classifier`](https://github.com/geehexx/kiro-proxy/pull/18) — adds safer regex handling and complexity classification to an OpenAI-compatible route.
- [`feat(routes): preserve client model name in response`](https://github.com/geehexx/kiro-proxy/pull/16) — fixes a subtle client/gateway contract bug where normalized upstream model names leaked back into downstream behavior.

---

## Production Failure Modes I Like Closing

A lot of applied AI engineering is not prompt cleverness. It is removing ambiguity from the failure paths.

- **Adaptive retry token buckets** — prevent thundering-herd retries under sub-agent fan-out; bounded refill/backoff behavior under contention.
- **Body-content retry classification** — distinguishes hard quota markers from transient throttling and capacity signals.
- **Per-chunk stalled-stream protection** — bounds upstream-hang waits and emits typed terminal errors instead of silent truncation.
- **Agent handoff durability** — coordination mailboxes, advisory leases, deterministic agent naming, and handoff evaluation for fresh-agent recovery.
- **Tool-use safety hooks** — block write/edit paths when credential-shaped strings or unsafe outputs enter protected directories.
- **Eval-before-autonomy loops** — measure behavior before adding more agency, tools, or orchestration complexity.

---

## Career Snapshot

| Context | Signal |
|---|---|
| **Stealth startup** | Lead AI Engineer for a production agentic AI / procurement intelligence platform |
| **Agoda / Rocket Travel by Agoda** | Engineering Manager for B2B booking platforms; led 15+ engineers; supported 100K+ RPM peak load across 2.4M+ properties; onboarded enterprise partners including Citibank, US Bank, American Airlines, WestJet, KrisFlyer, and JTB |
| **Toptal** | Engineering Manager / Senior Software Engineer / Product Manager across talent matching, vetting, ETL, enterprise delivery, and remote engineering systems; scaled team from 5 to 15+ engineers |
| **BaxEnergy / Yokogawa** | Engineering maturity assessment and modernization roadmap across two squads; DORA metrics, incident protocols, on-call design, and MTTR reduction |
| **Dubizzle / OLX Group** | Built jobs.dubizzle.com from scratch, rebuilt the core ad-placement workflow, and helped move a Django monolith toward service-oriented architecture |

<details>
<summary><strong>Earlier systems work</strong></summary>

- **Coins.ph** — Python/Django payments-platform modernization, KYC identity verification, WebRTC video capture, facial recognition/liveness workflows, and growth integrations during pre-Series A.
- **Insydo** — CTO/co-founder; semantic recommendation systems using word2vec/Gensim, TF-IDF, collaborative filtering, Aerospike, and custom Python infrastructure.
- **ITP** — CMS/platform work for 40+ Middle East media sites; multi-tier caching with CouchDB, Memcached, and Redis; page-load reduction from 10s+ to under 250ms.
- **Freelance / early Toptal network** — greenfield Django/Angular builds, founder-facing technical translation, fixed-budget delivery, scope negotiation, and product-risk diagnosis.

</details>

---

## Toolbox

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Kotlin-7F52FF?style=flat&logo=kotlin&logoColor=white" alt="Kotlin" />
  <img src="https://img.shields.io/badge/Scala-DC322F?style=flat&logo=scala&logoColor=white" alt="Scala" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazonwebservices&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/OpenTelemetry-000000?style=flat&logo=opentelemetry&logoColor=white" alt="OpenTelemetry" />
</p>

**AI / agents / retrieval**  
PydanticAI · LangGraph · AG-UI · AWS Bedrock · LangChain · Hugging Face Transformers · sentence-transformers · ONNX Runtime · FastEmbed · pgvector · ParadeDB · Qdrant · Pinecone · Reciprocal Rank Fusion · Optuna · LangSmith · OpenTelemetry · MCP · Agentic RAG · LLMOps

**Backend / distributed systems**  
Python · Kotlin · Scala · TypeScript · Ruby · Java · PostgreSQL · Redis · RabbitMQ · Kafka · BigQuery · Elasticsearch · REST · GraphQL · gRPC · Saga pattern · Sidekiq · Docker

**Infrastructure**  
AWS CDK · ECS Fargate · RDS · ElastiCache · Cognito · WAF · Kubernetes · Istio · Terraform · OpenTofu · CI/CD · cdk-nag

**Leadership / operating systems**  
Engineering strategy · RFCs / ADRs · hiring · mentorship · performance management · incident management · on-call design · DORA metrics · OKRs · remote-first engineering · technical due diligence · platform modernization

---

## Engineering Biases

- Typed errors over mysterious fallthroughs.
- Guardrails around irreversible tool actions.
- Evals before more autonomy.
- Observability before optimism.
- Explicit retry budgets; no infinite faith in exponential backoff.
- Hybrid retrieval when lexical precision and semantic recall both matter.
- Infrastructure that rolls back cleanly.
- Teams that write decisions down before they become folklore.

---

## Useful Conversations

I am usually useful for:

- building production AI / agent platforms;
- taking RAG systems from prototype to measurable quality;
- hardening distributed systems under real load;
- designing human-in-the-loop governance for AI workflows;
- leading backend/platform teams through modernization;
- diagnosing reliability failures across infra, code, process, and team boundaries.

---

## Reach Me

- **LinkedIn:** [linkedin.com/in/ancrozier](https://www.linkedin.com/in/ancrozier/)
- **GitHub:** [github.com/geehexx](https://github.com/geehexx)
- **Location:** Australia-based, currently traveling Asia
- **Open to:** AU / EU / Asia remote opportunities; relocation or on-site possible for the right role
