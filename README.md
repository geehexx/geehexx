# Andrew Crozier

### Engineering Manager · Applied AI & Platform Systems

**Technical leadership · Production AI systems · Hybrid retrieval · Distributed platforms · Reliability engineering**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Andrew_Crozier-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/ancrozier)
[![GitHub](https://img.shields.io/badge/GitHub-geehexx-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/geehexx)
[![Focus](https://img.shields.io/badge/Focus-production_AI_systems-7C3AED?style=for-the-badge)](#now)
[![Open to](https://img.shields.io/badge/Open_to-AI_%2F_platform_%2F_backend_roles-16A34A?style=for-the-badge)](#reach-me)

---

```text
I build the parts of AI systems that still have to work after the demo: retrieval quality, tool boundaries, stream safety, retry behavior, evaluation loops, human approval gates, observability, infrastructure, and the engineering habits around them.
```

I work where LLMs meet backend engineering: agent orchestration, RAG, search, evals, governance, distributed systems, platform reliability, and the unglamorous failure paths that decide whether an AI product survives real users.

I am not trying to be a pure people manager. I have led teams, hired engineers, run delivery systems, written RFCs, and handled performance management, but my strongest work is still hands-on technical leadership: shaping systems, debugging hard edges, and helping teams make better engineering decisions.

---

## Now

Building production agentic workflows, hybrid retrieval, human-in-the-loop controls, and cloud infrastructure for enterprise decision support.

| System area | Current focus |
| --- | --- |
| **Agentic architecture** | Multi-step agent workflows, tool boundaries, approval gates, typed failure paths, and quality checks before autonomy expands |
| **Retrieval & discovery** | Hybrid lexical / semantic retrieval, ranking, query interpretation, and graceful degradation for vague or under-specified requests |
| **Conversation systems** | Stateful conversational flows, streaming behavior, guarded tool use, and product-facing interaction design |
| **Platform engineering** | AWS-based service architecture, infrastructure-as-code, data stores, security controls, and rollback-friendly deployment paths |
| **Reliability hardening** | Retry classification, stalled-stream handling, observability, resource isolation, and explicit operating constraints |

---

## Selected Public Work

I use GitHub less as a trophy case and more as a public engineering notebook: tools, experiments, reliability patches, and production-inspired patterns that expose how I think.

| Repo / work | What it demonstrates |
| --- | --- |
| [`geehexx`](https://github.com/geehexx/geehexx) | Canonical GitHub profile and CV source repo with typed YAML adapters, RenderCV/Pandoc generation, deterministic artifact QA, CI-uploaded review packages, and public/resume contact-boundary policy. |
| [`library-ops`](https://github.com/geehexx/library-ops) | Live Django/PostgreSQL library-operations demo with Work/Edition/Copy modeling, role boundaries, search, circulation state, Render deployment, and a governed multi-agent SDLC case study. |
| [`mcp-web`](https://github.com/geehexx/mcp-web) | MCP server for web and local-file summarization: extraction, chunking, streaming summaries, local/cloud LLM support, caching, security controls, metrics, and tests. |
| [`hitl-mcp-cli`](https://github.com/geehexx/hitl-mcp-cli) | Human-in-the-loop MCP server and terminal UI for approvals, choices, confirmations, notifications, interaction logging, and async-first workflows. |
| [`phraseturner`](https://github.com/geehexx/phraseturner) | Text-analysis MCP server with personas, readability/naturalness/tone scoring, semantic persona search, and graceful degradation. |
| [`PragmaLens`](https://github.com/geehexx/PragmaLens) | Evidence-oriented extraction prototype exploring structured outputs, explicit support spans, uncertainty, and validation-oriented prompt design. |
| [`llm-bedrock-converse`](https://github.com/geehexx/llm-bedrock-converse) | LLM plugin for AWS Bedrock Converse with streaming, tool calling, MCP integration, multimodal inputs, embeddings, and retry behavior. |
| [`msteams-mcp`](https://github.com/geehexx/msteams-mcp) | MCP server for Microsoft Teams interaction: message search, replies, thread access, authentication, and assistant-facing collaboration workflows. |
| [`kiro-proxy`](https://github.com/geehexx/kiro-proxy) fork work | Fork work around streaming, retry behavior, quota classification, model-name preservation, regex safety, and failure-mode cleanup. |

---

## Production Failure Modes I Like Closing

A lot of applied AI engineering is not prompt cleverness. It is removing ambiguity from failure paths.

- **Retry storms under fan-out** - bounded retry budgets, token buckets, and backoff behavior that does not amplify provider pain.
- **Hard quota vs transient throttling** - body-content classification so retries do not burn budget against unrecoverable walls.
- **Silent stream failures** - per-chunk stalled-stream protection and typed terminal errors instead of partial, misleading output.
- **Unsafe tool autonomy** - approval gates and write-path blocks around irreversible actions, credentials, and protected directories.
- **Weak retrieval confidence** - hybrid retrieval, rank fusion, query scoping, and evaluation before expanding agent autonomy.
- **Operational folklore** - ADRs, RFCs, runbooks, and decisions written down before they become archaeology.

---

## Career Snapshot

| Context | Signal |
| --- | --- |
| **Stealth Startup** | Lead AI Engineer for production agentic AI, retrieval, governance workflows, and platform infrastructure |
| **BaxEnergy (a Yokogawa Company)** | Engineering maturity assessment and modernization roadmap across delivery practices, incident response, DORA metrics, and cloud-native migration planning |
| **Agoda (Booking Holdings)** | Engineering Manager for B2B booking platforms; led multiple squads and supported high-scale booking flows across millions of properties and major enterprise partners |
| **Toptal** | Senior Software Engineer, Product Manager, and Engineering Manager across talent matching, vetting, ETL, enterprise delivery, and remote engineering systems |
| **Dubizzle (Naspers-backed)** | Built and scaled classifieds marketplace systems, rebuilt core ad-placement workflows, and helped move a Django monolith toward service-oriented architecture |

Earlier systems work:

- **Independent Freelance / Contract Engagements** - Built a greenfield ecommerce platform for an Australian equestrian-event booking startup using Python, Django, Angular 2, payment flows, admin tooling, and deployment ownership.
- **Coins.ph** - Led Django 1.8 LTS to 1.10 and Python 2.7 to 3.5.2 modernization across the payment-processing platform.
- **ITP Media Group** - Developed and maintained Django-based CMS platforms powering 40+ websites for the largest publishing house in the Middle East, serving 100+ media brands.

---

## Toolbox

**AI / agents / retrieval**
- Production agentic AI · RAG / Agentic RAG · hybrid search · vector databases · pgvector · Qdrant · Pinecone · BM25
- ParadeDB · Reciprocal Rank Fusion · PydanticAI · LangGraph · LangChain · AWS Bedrock · MCP / Model Context Protocol
- LLMOps · model evaluation · ONNX Runtime · sentence-transformers · FastEmbed · Optuna · LangSmith

**Backend / distributed systems**
- Python · Kotlin · Scala · Java · Ruby · Rails · Django · TypeScript · REST APIs · GraphQL · gRPC · PostgreSQL · Redis
- RabbitMQ · Kafka · BigQuery · Avro · Pandas · Elasticsearch · Sidekiq · event-driven architecture · Saga pattern
- high-availability systems · system design

**Infrastructure**
- AWS · AWS CDK · ECS Fargate · RDS PostgreSQL · ElastiCache Redis · Cognito · WAF · Kubernetes · Istio · Docker
- Terraform · OpenTofu · CI/CD · cdk-nag · observability · platform engineering · rollback-friendly deployment

**Technical leadership**
- technical roadmaps · architecture decisions · ADRs · RFCs · engineering maturity assessment · DORA metrics
- incident management · on-call design · hiring · headcount planning · mentorship · performance management
- stakeholder management · technical due diligence · remote-first delivery

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
- diagnosing reliability failures across infrastructure, code, process, and team boundaries;

---

## Reach Me

- **LinkedIn:** [linkedin.com/in/ancrozier](https://linkedin.com/in/ancrozier)
- **GitHub:** [github.com/geehexx](https://github.com/geehexx)
- **Location:** Thailand-based Australian citizen; remote Australia/APAC/EU/UK overlap
- **Open to:** Engineering Manager, applied AI, software engineering, backend/platform engineering, and hands-on technical leadership roles. Remote across Australia / APAC / EU / UK overlap preferred; other on-site arrangements possible for the right role.
