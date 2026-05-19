<div align="center">

# Andrew Crozier

### Applied AI & Software Engineering · Hands-on Technical Leadership

**Production agents · Hybrid retrieval · MCP systems · Distributed platforms · Reliability engineering**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Andrew_Crozier-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ancrozier/)
[![GitHub](https://img.shields.io/badge/GitHub-geehexx-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/geehexx)
[![Focus](https://img.shields.io/badge/Focus-production_AI_systems-7C3AED?style=for-the-badge)](#now)
[![Open to](https://img.shields.io/badge/Open_to-AI_%2F_platform_%2F_backend_roles-16A34A?style=for-the-badge)](#reach-me)

</div>

---

```text
I build the parts of AI systems that still have to work after the demo:
retrieval quality, tool boundaries, stream safety, retry behavior, evaluation loops,
human approval gates, observability, infrastructure, and the engineering habits around them.
```

I work where **LLMs meet backend engineering**: agent orchestration, RAG, search, evals, governance, distributed systems, platform reliability, and the unglamorous failure paths that decide whether an AI product survives real users.

I am not trying to be a pure people manager. I have led teams, hired engineers, run delivery systems, written RFCs, and handled performance management — but my strongest work is still **hands-on technical leadership**: shaping systems, debugging hard edges, and helping teams make better engineering decisions.

---

## Now

Building production agentic workflows, hybrid retrieval, human-in-the-loop controls,
and cloud infrastructure for enterprise decision support.

| System area | What I am focused on |
|---|---|
| **Agentic architecture** | Multi-step agent workflows, tool boundaries, approval gates, typed failure paths, and quality checks before autonomy expands |
| **Retrieval & discovery** | Hybrid lexical / semantic retrieval, ranking, query interpretation, and graceful degradation for vague or under-specified requests |
| **Conversation systems** | Stateful conversational flows, streaming behavior, guarded tool use, and product-facing interaction design |
| **Platform engineering** | AWS-based service architecture, infrastructure-as-code, data stores, security controls, and rollback-friendly deployment paths |
| **Reliability hardening** | Retry classification, stalled-stream handling, observability, resource isolation, and explicit operating constraints |

---

## Selected Public Work

I use GitHub less as a trophy case and more as a public engineering notebook: tools, experiments, reliability patches, and production-inspired patterns that expose how I think.

| Repo / work | What it demonstrates |
|---|---|
| [`mcp-web`](https://github.com/geehexx/mcp-web) | MCP server for web and local-file summarization: extraction, chunking, streaming summaries, local/cloud LLM support, caching, security controls, metrics, and tests |
| [`hitl-mcp-cli`](https://github.com/geehexx/hitl-mcp-cli) | Human-in-the-loop MCP server and terminal UI for approvals, choices, confirmations, notifications, interaction logging, and async-first workflows |
| [`phraseturner`](https://github.com/geehexx/phraseturner) | Text-analysis MCP server with personas, readability/naturalness/tone scoring, semantic persona search, and graceful degradation |
| [`llm-bedrock-converse`](https://github.com/geehexx/llm-bedrock-converse) | `llm` plugin for AWS Bedrock Converse: streaming, tool calling, MCP integration, multimodal inputs, embeddings, and retry behavior |
| [`msteams-mcp`](https://github.com/geehexx/msteams-mcp) | MCP server for Microsoft Teams interaction: message search, replies, thread access, authentication, and assistant-facing collaboration workflows |
| [`kiro-proxy`](https://github.com/geehexx/kiro-proxy) fork work | Gateway reliability work around streaming, retry behavior, quota classification, model-name preservation, regex safety, and failure-mode cleanup |

<details>
<summary><strong>More background</strong></summary>

---

## Production Failure Modes I Like Closing

A lot of applied AI engineering is not prompt cleverness. It is removing ambiguity from failure paths.

- **Retry storms under fan-out** — bounded retry budgets, token buckets, and backoff behavior that does not amplify provider pain.
- **Hard quota vs transient throttling** — body-content classification so retries do not burn budget against unrecoverable walls.
- **Silent stream failures** — per-chunk stalled-stream protection and typed terminal errors instead of partial, misleading output.
- **Unsafe tool autonomy** — approval gates and write-path blocks around irreversible actions, credentials, and protected directories.
- **Weak retrieval confidence** — hybrid retrieval, rank fusion, query scoping, and evaluation before expanding agent autonomy.
- **Operational folklore** — ADRs, RFCs, runbooks, and decisions written down before they become archaeology.

---

## Career Snapshot

| Context | Signal |
|---|---|
| **Stealth applied-AI platform** | Lead AI Engineer for production agentic AI, retrieval, governance workflows, and platform infrastructure |
| **Agoda / Rocket Travel by Agoda** | Engineering Manager for B2B booking platforms; led 15+ engineers; supported high-scale booking flows across 2.4M+ properties and major enterprise partners |
| **Toptal** | Senior Software Engineer, Product Manager, and Engineering Manager across talent matching, vetting, ETL, enterprise delivery, and remote engineering systems |
| **BaxEnergy / Yokogawa** | Engineering maturity assessment and modernization roadmap across delivery practices, incident response, DORA metrics, and cloud-native migration planning |
| **Dubizzle / OLX Group** | Built and scaled classifieds marketplace systems, rebuilt core ad-placement workflows, and helped move a Django monolith toward service-oriented architecture |

<details>
<summary><strong>Earlier systems work</strong></summary>

- **Coins.ph** — Python / Django payments-platform modernization, KYC identity verification, video capture, liveness workflows, and growth integrations.
- **Insydo** — CTO / co-founder; semantic recommendation systems using word2vec, TF-IDF, collaborative filtering, Aerospike, and custom Python infrastructure.
- **ITP Media Group** — CMS and platform work for 40+ Middle East media sites; multi-tier caching with CouchDB, Memcached, and Redis; page-load reduction from 10s+ to under 250ms.
- **Freelance / early Toptal network** — greenfield Django / Angular builds, founder-facing technical translation, fixed-budget delivery, scope negotiation, and product-risk diagnosis.

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
PydanticAI · LangGraph · AWS Bedrock · LangChain · Hugging Face Transformers · sentence-transformers · ONNX Runtime · FastEmbed · pgvector · Qdrant · Pinecone · BM25 · Reciprocal Rank Fusion · Optuna · LangSmith · OpenTelemetry · MCP · Agentic RAG · LLMOps

**Backend / distributed systems**
Python · Kotlin · Scala · TypeScript · Ruby · Java · Django · Rails · PostgreSQL · Redis · RabbitMQ · Kafka · BigQuery · Elasticsearch · REST · GraphQL · gRPC · Saga pattern · Sidekiq · Docker

**Infrastructure**
AWS CDK · ECS Fargate · RDS · ElastiCache · Cognito · WAF · Kubernetes · Istio · Terraform · OpenTofu · CI/CD · cdk-nag

**Technical leadership**
Architecture decisions · RFCs / ADRs · hiring · mentorship · performance management · incident management · on-call design · DORA metrics · OKRs · remote-first engineering · technical due diligence · platform modernization

---

## Engineering Biases

- Typed errors over mysterious fallthroughs.
- Guardrails around irreversible tool actions.
- Evals before more autonomy.
- Observability before optimism.
- Explicit retry budgets; no infinite faith in exponential backoff.
- Hybrid retrieval when lexical precision and semantic recall both matter.
- Infrastructure that rolls back cleanly.
- Teams that write decisions down before decisions become folklore.

---

## The Longer Thread

I got here the long way: programming young, learning by building, breaking things, and repeatedly deciding I needed to understand the layer underneath the abstraction.

That meant mIRC scripting, C++, BSD/network programming, GTK+, ncurses, Linux without a GUI for longer than was sensible, Django before it was boring, marketplace systems, fintech workflows, booking platforms, talent-matching systems, and now production AI systems.

The through-line is not a framework. It is systems curiosity plus enough production scar tissue to know where prototypes usually fail.

---

## Useful Conversations

I am usually useful for:

- building production AI / agent platforms;
- taking RAG systems from prototype to measurable quality;
- hardening distributed systems under real load;
- designing human-in-the-loop governance for AI workflows;
- building MCP and developer workflow tools;
- leading backend / platform teams without drifting away from the code;
- diagnosing reliability failures across infrastructure, code, process, and team boundaries.

</details>

---

## Reach Me

- **LinkedIn:** [linkedin.com/in/ancrozier](https://www.linkedin.com/in/ancrozier/)
- **GitHub:** [github.com/geehexx](https://github.com/geehexx)
- **Location:** Australia-based, currently traveling Asia
- **Open to:** AI engineering, software engineering, backend/platform engineering, and hands-on technical leadership roles. Remote across AU / EU / Asia preferred; relocation or on-site possible for the right role.
