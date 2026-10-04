# Lear 3.0 Architectural Transformation Plan: Agent-Driven Orchestration, Oh-My-Pi Memory, Prebuilt MCPs & Sentry Network

**Document:** `plan.md`  
**Status:** Architectural Specification & Transformation Roadmap  
**Target Milestone:** Lear v3.0 ("The Autonomous AI DevOps Agent Swarm")  
**Authors / Reviewers:** Anant, Aryan, Aradhya, Agrim, Avi, Parv  
**Anchored In:** [`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md), [`CHANGELOG.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/CHANGELOG.md), [`ROADMAP.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/ROADMAP.md), [`agent_guidelines.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/agent_guidelines.md)

---

## 1. Executive Summary & Paradigm Shift

Lear v2.x successfully established the foundation of a local-first DevOps assistant: a 14-provider connector ecosystem, 29 discrete actions, a 5-tier permission engine, local append-only audit logging, an active Tauri desktop client with pure SVG telemetry widgets, and bidirectional email/Slack incident routing.

However, as revealed by real-world production incident tests and the architectural audit in [`ROADMAP.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/ROADMAP.md):
1. **The Monolith Bottleneck:** Backend logic is concentrated in a 3,896-line `server.py` and a 146-KB monolithic prompt in `diagnosis_agent.py`.
2. **Bespoke Connector Burden:** Hand-coding and maintaining individual API clients (`aws.py`, `kubernetes.py`, `github.py`, etc.) for every service creates massive surface area, brittle auth maintenance, and redundant schema mapping.
3. **Flawed Routing Philosophy (Model Routing vs. Agent Routing):** Currently, systems treat AI as a model switcher (e.g. routing between Gemini, DeepSeek, Claude, or Kimi based on cost/latency). This fails complex DevOps operations. **We must not route models; we must route agents.** An incident is not a single prompt-response text completion; it is a collaborative investigation across Kubernetes, cloud infrastructure, CI/CD pipelines, APM metrics, and security policies.
4. **Ad-Hoc Memory:** The current memory (`.prash/memory.json` in `local_memory.py`) is a basic append-only list with naive string hashing. It lacks multi-tiered working memory, causal graph tracking, semantic vector retrieval, and persistent topological knowledge.
5. **Brittle Custom Guardrails:** Safety enforcement currently relies on hardcoded regex checks in `_apply_deterministic_guardrails` instead of pre-trained, verifiable guardrail engines.
6. **Reactive Polling vs. Autonomous Sentries:** The existing watcher loop is a synchronous polling thread that lacks intelligent anomaly suppression, multi-signal correlation, and autonomous incident dispatching.

### The Transformation Blueprint
Lear v3.0 transitions Lear from a bespoke, script-driven tool into a **standardized, orchestrator-driven multi-agent platform**:
- **Oh-My-Pi Tripartite Memory Subsystem:** Working/Short-Term, Episodic/Experiential, and Long-Term/Topological knowledge bases.
- **Standard Agent Harness:** Moving away from bespoke while-loops and custom state machines to a battle-tested agent workflow runtime with native checkpointing, time-travel, and human-in-the-loop (HITL) pause/resume.
- **Prebuilt CLI & Model Context Protocol (MCP):** Replacing custom connector code with standardized MCP servers and prebuilt CLI execution harnesses.
- **Pre-Trained Guardrails:** Adopting enterprise pre-trained safety frameworks (NeMo Guardrails, Llama Guard) for input, dialogue, action, and output verification.
- **Autonomous Sentries (Sentinels):** Distributed, lightweight observation sentries that filter 95%+ of telemetry noise and awaken specialized agents only on verified anomalies.
- **Agent Routing (Meta-Orchestrator Swarm):** A supervisory meta-orchestrator that coordinates a swarm of specialized domain agents (Kubernetes Agent, Cloud Infra Agent, CI/CD Agent, Observability Agent, Security Agent, Remediation Agent).

```
═══════════════════════════════════════════════════════════════════════════════════════════
                              LEAR 3.0 PARADIGM SHIFT
═══════════════════════════════════════════════════════════════════════════════════════════

   [ OLD: Bespoke & Model-Centric ]                 [ NEW: Orchestrated & Agent-Centric ]
  ┌────────────────────────────────┐              ┌────────────────────────────────────────┐
  │ User / Slack / Webhook / Watch │              │ Continuous Autonomous Sentry Network   │
  └───────────────┬────────────────┘              └───────────────────┬────────────────────┘
                  │                                                   ▼
                  ▼                               ┌────────────────────────────────────────┐
  ┌────────────────────────────────┐              │   Supervisor Agent (Meta-Orchestrator) │
  │ Model Router: Picks LLM Model  │              └───────┬───────────┬────────────┬───────┘
  │ (DeepSeek vs Gemini vs Claude) │                      │           │            │
  └───────────────┬────────────────┘          ┌───────────▼─┐   ┌─────▼─────┐   ┌──▼───────────┐
                  ▼                           │ K8s Agent   │   │ Cloud Agt │   │ Sec/APM Agt  │
  ┌────────────────────────────────┐          └──────┬──────┘   └─────┬─────┘   └──┬───────────┘
  │ Monolithic Diagnosis Script    │                 │                │            │
  │ (146KB prompt, regex rails)    │                 ▼                ▼            ▼
  └───────────────┬────────────────┘         ════════════════════════════════════════════════
                  ▼                           OH-MY-PI MEMORY (Working | Episodic | Semantic)
  ┌────────────────────────────────┐         ════════════════════════════════════════════════
  │ 14 Hand-Coded Bespoke Connects │                 │                │            │
  │ (aws.py, kubernetes.py, etc.)  │                 ▼                ▼            ▼
  └────────────────────────────────┘          ┌────────────────────────────────────────────┐
                                              │   Pre-Trained Guardrails (Input/Action/Out)│
                                              └─────────────────────┬──────────────────────┘
                                                                    ▼
                                              ┌────────────────────────────────────────────┐
                                              │   Prebuilt MCP Ecosystem & Standard CLIs   │
                                              │   (K8s MCP, AWS MCP, GitHub MCP, kubectl)  │
                                              └────────────────────────────────────────────┘
```

---

## 2. Deep Dive: The Six Core Pillars

### Pillar 1: Oh-My-Pi Tripartite Memory Subsystem

The current implementation in `prash/brain/local_memory.py` only maintains a flat `.prash/memory.json` containing string-matched signatures and a list of previous dictionaries. 

Lear 3.0 implements the **Oh-My-Pi** tripartite cognitive memory architecture, providing distinct storage tiers, retrieval semantics, and retention lifecycles:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        OH-MY-PI MEMORY ARCHITECTURE                                    │
├─────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ Tier 1: SHORT-TERM      │ Tier 2: EPISODIC             │ Tier 3: LONG-TERM             │
│ (Working Memory Buffer) │ (Incident Experience Engine) │ (Semantic & Topology Graph)   │
├─────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • In-flight incident    │ • Trajectory storage:        │ • Infrastructure graph:       │
│   telemetry window      │   [Trigger → Root Cause →    │   Topology, dependencies,     │
│ • Tool call scratchpad  │    Plan → Verification]      │   service mesh, namespaces    │
│ • Active cluster / env  │ • Error signature vector     │ • Team policies & playbooks   │
│   session context       │   embeddings + exact hash    │ • SLO thresholds & budgets    │
│ • Compacted tokens via  │ • "I've seen this before"    │ • Blast radius definitions    │
│   recursive summarizer  │   instant replay engine      │ • Multi-account boundaries    │
│ • Ephemeral (TTL: Run)  │ • Counter-episodic failure   │ • Persistent (Local RocksDB / │
│                         │   trajectories (anti-goals)  │   SQLite-vec / LanceDB)       │
└─────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

#### 1.1 Short-Term (Working) Memory
- **Purpose:** Maintains real-time scratchpad state for active multi-agent dialogues and tool execution loops.
- **Implementation:** Sliding context window with token-budget enforcement. When conversation or tool outputs exceed 75% of context window, an asynchronous **Recursive Memory Compressor** synthesizes intermediate milestones into structured state snapshots without losing critical variable definitions (e.g. pod names, namespace, exit codes, IP addresses).
- **Session Boundary:** Scoped to active incident ID or chat session ID (`session_id` in `ChatWorkspace.tsx`).

#### 1.2 Episodic Memory ("I've Seen This Before" Replay Engine)
- **Purpose:** Enables zero-shot and few-shot resolution of recurring operational incidents. As established in [`tasks/.demo/05_EPISODIC_MEMORY.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/tasks/.demo/05_EPISODIC_MEMORY.md), when an incident is encountered that matches a previously verified fix, Lear should not burn 45 seconds re-diagnosing from first principles; it should replay the verified runbook in under 3 seconds.
- **Storage Schema:**
  ```json
  {
    "episode_id": "ep_20261002_oom_checkout",
    "timestamp": "2026-10-02T23:14:00Z",
    "environment": "production",
    "service": "checkout-api",
    "error_signature_hash": "sha256:e3b0c442...",
    "vector_embedding": [0.0124, -0.0451, "..."],
    "trigger_telemetry": {
      "exit_code": 137,
      "reason": "OOMKilled",
      "metric_snapshot": {"memory_utilization": 0.99, "restart_count": 5}
    },
    "investigation_graph": [
      {"agent": "k8s_specialist", "action": "mcp_k8s_get_pod_events", "result": "Back-off restarting failed container"},
      {"agent": "observability", "action": "mcp_datadog_query_memory", "result": "Gradual leak over 6 hours"}
    ],
    "winning_action": {
      "action_name": "kubernetes_patch_resources",
      "target": "deployment/checkout-api",
      "parameters": {"memory_limit": "2Gi", "memory_request": "1Gi"}
    },
    "verification_result": {
      "verified": true,
      "post_state": "Running",
      "healthy_duration_seconds": 300
    },
    "confidence_score": 0.96,
    "user_feedback": "APPROVED_AND_VERIFIED"
  }
  ```
- **Dual-Index Retrieval:**
  1. *Deterministic Exact Hash:* Matches error signature strings (e.g. `OOMKilled:checkout-api:container-checkout`).
  2. *Semantic Vector Similarity:* Local fast vector index (using local ONNX MiniLM embeddings + local LanceDB/SQLite-vec) to surface similar incidents across different namespaces or services with cosine similarity $\ge 0.88$.
- **Counter-Episodic Storage:** Records failed remediation attempts. If `restart-pod` failed for a specific `CrashLoopBackOff` episode, the episodic store marks `restart-pod` as an *anti-pattern* for that error signature, preventing the agent swarm from repeating fruitless actions.

#### 1.3 Long-Term (Declarative & Topological) Memory
- **Purpose:** Retains enduring enterprise knowledge, infrastructure topology, team policies, and operational runbooks.
- **Graph Topology:** Stores relationship graphs:
  - `(Service: checkout-api) -[DEPENDS_ON]-> (Database: postgres-primary)`
  - `(Service: checkout-api) -[MONITORED_BY]-> (Datadog: checkout-dashboard)`
  - `(Service: checkout-api) -[DEPLOYED_VIA]-> (ArgoCD: checkout-app)`
  - `(Cluster: us-east-prod) -[BLAST_RADIUS_TIER]-> (Tier: 1_CRITICAL)`
- **Local Persistence Guarantee:** Preserves the foundational law from [`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) §4: *Credentials and enterprise infrastructure topologies never leave the user's local filesystem.* Stored locally in `.prash/memory/` using encrypted SQLite-vec / LanceDB.

---

### Pillar 2: The Agent Harness & Orchestration Runtime

Currently, Lear executes actions and diagnoses through ad-hoc functions (`prash fix` in `fix.py`, `_chat_stream_reasoning` in `server.py`, and `dispatch_action` in `dispatch.py`). 

Lear 3.0 replaces bespoke while-loops with a **Standardized Agent Workflow Harness** (e.g. StateGraph-based execution engine):

```
                     ┌────────────────────────────────────────┐
                     │          Incident Ingestion            │
                     │ (Sentry Alert / CLI / Chat / Webhook)  │
                     └───────────────────┬────────────────────┘
                                         ▼
                     ┌────────────────────────────────────────┐
                     │         Input Guardrail Check          │
                     │  (Prompt Injection / Secret Scrubbing) │
                     └───────────────────┬────────────────────┘
                                         ▼
                     ┌────────────────────────────────────────┐
                     │    Supervisor / Meta-Orchestrator      │◄───────────┐
                     │  (State Planning, Agent Delegation)    │            │
                     └─────┬─────────────┬──────────────┬─────┘            │
                           │             │              │                  │
               ┌───────────▼─┐     ┌─────▼─────┐  ┌─────▼──────────┐       │
               │ K8s Agent   │     │ Cloud Agt │  │ Observability  │       │
               └─────┬───────┘     └─────┬─────┘  └─────┬──────────┘       │
                     │                   │              │                  │
                     └─────────────┬─────┴──────────────┘                  │
                                   ▼                                       │
                     ┌────────────────────────────────────────┐            │
                     │    Episodic Memory Replay / Match?     │            │
                     └─────────────┬──────────────────────────┘            │
                        No Match   │         Match Found                   │
                           ┌───────┴──────────────┐                        │
                           ▼                      ▼                        │
                     ┌───────────┐        ┌───────────────┐                │
                     │ Multi-Step│        │ Fast-Track    │                │
                     │ Reasoning │        │ Replay Plan   │                │
                     └─────┬─────┘        └───────┬───────┘                │
                           └──────────┬───────────┘                        │
                                      ▼                                    │
                     ┌────────────────────────────────────────┐            │
                     │ Action Guardrail & Permission Engine   │            │
                     │   (SAFE vs APPROVAL vs NEVER)          │            │
                     └────────────────┬───────────────────────┘            │
                                      ▼                                    │
                     [ Permission Mode == ASK / APPROVAL? ]                │
                                ├── YES ──> [ HITL State Pause ]           │
                                │                 │ (User confirms in UI)  │
                                │                 ▼                        │
                                └─── NO ──> [ Execute via MCP Tools ]      │
                                                  │                        │
                                                  ▼                        │
                                     ┌────────────────────────┐            │
                                     │ Post-Fix Verification  │            │
                                     │  (Does pod stay up?)   │            │
                                     └────────────┬───────────┘            │
                                                  │                        │
                                        Verified? ├── NO ──(Loop back)─────┘
                                                  │
                                                  └── YES ──> [ Write Audit & Save Episode ]
```

#### Key Capabilities of the Harness:
1. **Checkpointing & State Recovery:** Every state transition (Investigating → Diagnosed → Awaiting Approval → Executing → Verifying) is checkpointed to local SQLite. If the backend process restarts or crashes mid-incident, it resumes exactly where it stopped.
2. **First-Class Human-in-the-Loop (HITL) Interrupts:** 
   - When an agent decides to execute a mutation requiring approval (e.g. `rollback_deployment`, `terraform_apply`, `scale_replicas`), the harness halts the agent execution loop and emits a structured `ActionRequestEvent` over WebSocket / SSE.
   - The desktop app (`ChatWorkspace.tsx` and `Dashboard.tsx`) renders the interactive confirmation card with exact command parameters and blast radius.
   - Upon user approval (`POST /api/incidents/{id}/approve` or chat button), the harness unpauses the execution thread and passes the approval token.
3. **Time-Travel & Rollback of Agent State:** Allows developers to inspect past agent reasoning steps, rewind state, or branch into alternative investigation hypotheses during post-incident reviews.
4. **Standardized Streaming Protocol:** Replaces custom string buffering with structured event streaming (`AgentThoughtEvent`, `AgentToolCallEvent`, `AgentToolResultEvent`, `AgentVerificationEvent`, `AgentFinalAnswerEvent`).

---

### Pillar 3: Prebuilt CLIs & Model Context Protocol (MCP) Ecosystem

Currently, Lear has 14 bespoke connectors in `prash/connectors/` (`aws.py`, `kubernetes.py`, `azure.py`, `gcp.py`, `datadog.py`, `github.py`, etc.). Maintaining 14 custom REST/SDK wrappers is high-friction, error-prone, and unsustainable.

Lear 3.0 adopts the open **Model Context Protocol (MCP)** and prebuilt CLI execution harnesses:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LEAR 3.0 MCP GATEWAY ARCHITECTURE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                          Agent Swarm (Tool Call Consumers)                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                   ▼                                                    │
│               Lear Unified MCP Client Manager & Tool Registry                          │
│     (Dynamic Tool Discovery, Schema Introspection, Permission Enforcement)             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│              Prebuilt Local MCP Servers (Stdio / SSE Transport)                        │
│                                                                                        │
│   ┌────────────────────┐  ┌─────────────────────┐  ┌────────────────────────────────┐  │
│   │ Kubernetes MCP     │  │ GitHub / GitLab MCP │  │ Cloud MCPs (AWS / GCP / Azure) │  │
│   │ (Pods, Deployments,│  │ (Issues, PRs, CI,   │  │ (EC2, CloudWatch, IAM, S3,    │  │
│   │  Logs, Events, K8s)│  │  Workflows, Commits)│  │  VPC, Cost, CloudTrail)        │  │
│   └─────────┬──────────┘  └──────────┬──────────┘  └───────────────┬────────────────┘  │
│             │                        │                             │                   │
│   ┌─────────▼──────────┐  ┌──────────▼──────────┐  ┌───────────────▼────────────────┐  │
│   │ Observability MCP  │  │ Security & IAC MCP  │  │ Prebuilt Sandboxed CLI Harness │  │
│   │ (Datadog, Grafana, │  │ (Snyk, Gitleaks,    │  │ (kubectl, gh, aws, az, gcloud, │  │
│   │  Prometheus, Sentry│  │  Terraform, Helm)   │  │  terraform - with sanitized IO)│  │
│   └────────────────────┘  └─────────────────────┘  └────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Advantages of the Prebuilt MCP Architecture:
1. **Zero Custom API Maintenance:** Prebuilt, community-maintained MCP servers implement standard JSON-RPC interfaces over stdio or SSE.
2. **Dynamic Tool Schema Discovery:** When Lear boots, the MCP Gateway connects to configured MCP servers, queries `tools/list`, and dynamically exposes validated JSON schemas to the Agent Swarm.
3. **Native Credential Isolation:** MCP servers run as isolated child processes reading local configuration or environment variables, preserving credential secrecy.
4. **Prebuilt CLI Harness:** For operations where an MCP server is unavailable or where native CLI speed is optimal, Lear uses a hardened, non-interactive CLI harness wrapping official binaries (`kubectl`, `aws-cli`, `az`, `gh`, `terraform`). The harness:
   - Sets non-interactive flags (`--batch`, `-y`, `PAGER=cat`).
   - Enforces execution timeouts (15s default).
   - Sanitizes and validates stdout/stderr.
   - Restricts shell execution paths to eliminate command injection vulnerabilities.

---

### Pillar 4: Pre-Trained Enterprise Guardrails Subsystem

Rather than relying on fragile manual string matching (e.g. `_apply_deterministic_guardrails` in `diagnosis_agent.py`), Lear 3.0 integrates **Pre-Trained Enterprise Guardrails** (leveraging frameworks like NeMo Guardrails, Guardrails AI, and Llama Guard):

```
                                  [ User Input / Alert Trigger ]
                                                │
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │              INPUT GUARDRAILS                 │
                        │ • Jailbreak & Prompt Injection Defense        │
                        │ • PII, Secret & Token Scrubber                │
                        │ • Scope Classifier (DevOps / Infra relevance) │
                        └───────────────────────┬───────────────────────┘
                                                │ (Pass)
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │             DIALOGUE & POLICY RAILS           │
                        │ • Lear Operating Charter Enforcement          │
                        │ • "Never Delete Production DB" Colang Rules   │
                        │ • Blast Radius Containment Policy             │
                        └───────────────────────┬───────────────────────┘
                                                │ (Plan Formulated)
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │             ACTION & TOOL RAILS               │
                        │ • Permission Tier Classifier (SAFE vs APPROV) │
                        │ • Circuit Breaker Threshold Verification      │
                        │ • Target Exact Match Validation               │
                        │ • Dry-run Parameter Fuzzing & Schema Check    │
                        └───────────────────────┬───────────────────────┘
                                                │ (Executed)
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │             OUTPUT GUARDRAILS                 │
                        │ • Telemetry Hallucination Verifier            │
                        │ • Residual Secret Leakage Redaction           │
                        │ • Factual Honesty & Verification Assessment   │
                        └───────────────────────────────────────────────┘
```

#### Guardrail Verification Layers:
1. **Input Rails:**
   - Detects adversarial manipulation or indirect prompt injection from parsed error logs (e.g. malicious log payloads designed to hijack the agent).
   - Redacts credentials, tokens, AWS Secret Keys, and private SSH keys *before* any text enters reasoning prompts.
2. **Policy & Operational Rails:**
   - Formal safety rules written in declarative policy specifications (Colang / Pydantic rules).
   - *Example Rule:* Any mutation command containing `rm -rf`, `DROP DATABASE`, `mkfs`, `delete namespace default`, or altering IAM root permissions is blocked unconditionally with an unbypassable safety exception.
3. **Action & Execution Rails:**
   - Enforces Lear's 5 permission modes (`read-only`, `ask every time`, `auto-safe`, `environment-scoped`, `bypass`).
   - Validates that every tool call parameter targets the explicit verified resource (e.g. target must match `pod/checkout-api-7b89f`, never a generic wildcard `pod/*`).
4. **Output Rails:**
   - Validates that explanations and metric numbers cite real data gathered in tool calls. If an agent claims "Memory dropped to 42%", the output rail verifies that the Observability tool output actually contained `42%`.

---

### Pillar 5: Autonomous Sentries (Sentinels) Network

In Lear v2, `watcher.py` was a simple, single-threaded while-loop that polled endpoints and pushed raw notifications. 

Lear 3.0 introduces the **Autonomous Sentry (Sentinel) Network**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS SENTRY (SENTINEL) NETWORK                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   ┌─────────────────────────┐  ┌─────────────────────────┐  ┌───────────────────────┐  │
│   │    K8s Cluster Sentry   │  │    Cloud Infra Sentry    │  │   APM / Telemetry     │  │
│   │ • CrashLoopBackOff      │  │ • CloudWatch Metric Alarm│  │   Sentry              │  │
│   │ • OOMKilled events      │  │ • EC2 / VM State Degrade │  │ • Error rate spikes   │  │
│   │ • Pending / Failed Pods │  │ • IAM drift & anomalies  │  │ • Latency breaches    │  │
│   │ • Evicted nodes         │  │ • Disk read/write spikes │  │ • PagerDuty incidents │  │
│   └────────────┬────────────┘  └────────────┬────────────┘  └───────────┬───────────┘  │
│                │                            │                           │              │
│                └──────────────────────┬─────┴───────────────────────────┘              │
│                                       ▼                                                │
│                 ┌───────────────────────────────────────────┐                          │
│                 │   Sentry Telemetry Aggregator & Denoiser  │                          │
│                 │   (Sliding Window Correlation & Debounce) │                          │
│                 └─────────────────────┬─────────────────────┘                          │
│                                       ▼                                                │
│                 [ Anomaly Crosses Multi-Signal Threshold? ]                            │
│                        ├── NO  ──> [ Suppress Noise & Update Live Telemetry Cache ]    │
│                        └── YES ──> [ Formulate Incident Genesis Envelope ]             │
│                                          │                                             │
│                                          ▼                                             │
│                 ┌───────────────────────────────────────────┐                          │
│                 │   Incident Dispatcher & Swarm Activator   │                          │
│                 │ • Pings UI WebSocket & Incident Center    │                          │
│                 │ • Awakens Supervisor Agent with Envelope  │                          │
│                 └───────────────────────────────────────────┘                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Sentry Characteristics:
- **Autonomous & Asynchronous:** Each Sentry runs as a lightweight, non-blocking background worker dedicated to a specific infrastructure scope.
- **95%+ Noise Suppression:** Telemetry jitter (e.g. temporary CPU spike during a cron run, a 1-second network disconnect, or a single 502 error) is buffered and debounced over a 45-second sliding window before raising an alarm.
- **Multi-Signal Correlation:** Joins disparate signals (e.g., K8s pod restarted + Datadog memory spike + GitHub deployment pushed 2 minutes ago) into a unified incident context.
- **Incident Genesis Envelope:** When an incident triggers, the Sentry packages all relevant metrics, logs, recent commits, and affected resource IDs into an immutable envelope and dispatches it directly into the Agent Orchestrator.

---

### Pillar 6: Agent-Based Routing vs. Model Routing

> **"Let's not route models, let's route agents. Make this properly AI based."**

In legacy systems, "routing" means picking whether to call Claude 3.5 Sonnet, Gemini 1.5 Pro, or DeepSeek V3 based on prompt length or token costs. That is model routing.

Lear 3.0 implements **Agent Routing**: the user's intent or the Sentry's incident envelope is routed to **specialized autonomous agents**, each possessing specialized system prompts, domain knowledge, dedicated MCP tools, and sub-memory slices.

```
                                  [ Incident Genesis / User Query ]
                                                  │
                                                  ▼
                        ┌───────────────────────────────────────────────────┐
                        │       SUPERVISOR AGENT (Meta-Orchestrator)        │
                        │ • Analyzes incident domain and complexity         │
                        │ • Consults Oh-My-Pi Long-Term Memory (Topology)   │
                        │ • Builds Multi-Agent Execution Plan (DAG)         │
                        └───────┬───────────────┬───────────────┬───────────┘
                                │               │               │
            ┌───────────────────▼─┐       ┌─────▼─────┐   ┌─────▼───────────────────┐
            │                     │       │           │   │                         │
            ▼                     ▼       ▼           ▼   ▼                         ▼
┌────────────────────────┐ ┌────────────┐ ┌─────────────┐ ┌───────────────┐ ┌───────────────┐
│ Kubernetes Specialist  │ │ Cloud Infra│ │ CI/CD &     │ │ Observability │ │ Security &    │
│ Agent                  │ │ Agent      │ │ GitOps Agent│ │ & APM Agent   │ │ Compliance Agt│
├────────────────────────┤ ├────────────┤ ├─────────────┤ ├───────────────┤ ├───────────────┤
│ • Pods, Services,      │ │ • AWS/GCP/ │ │ • GitHub CI │ │ • Datadog     │ │ • Snyk CVEs   │
│   Deployments, Ingress │   Azure VMs  │ • GitLab CI   │ • Prometheus    │ • Gitleaks scan │
│ • OOMKills, Probes     │ │ • CloudWatch│ • PR Creation │ • Grafana logs  │ • IAM least priv│
│ • K8s MCP Tools        │ │ • VPC/IAM  │ • Git Bisect  │ • Trace analysis│ • Audit bounds  │
└───────────┬────────────┘ └─────┬──────┘ └──────┬──────┘ └───────┬───────┘ └───────┬───────┘
            │                    │               │                │                 │
            └────────────────────┴───────┬───────┴────────────────┴─────────────────┘
                                         ▼
                        ┌───────────────────────────────────────────────────┐
                        │      REMEDIATION & VERIFICATION AGENT (Operator)  │
                        │ • Synthesizes domain agent findings               │
                        │ • Checks Oh-My-Pi Episodic Memory for prior wins  │
                        │ • Generates verified fix plan                     │
                        │ • Enforces Permission Engine (SAFE vs APPROVAL)   │
                        │ • Executes via Action MCPs                        │
                        │ • Re-probes infrastructure to verify recovery     │
                        └───────────────────────────────────────────────────┘
```

#### Specialized Agent Capabilities:

| Agent Name | Primary Mission | Tools & MCP Capabilities | Collaboration Seam |
|---|---|---|---|
| **Supervisor (Meta-Orchestrator)** | Incident decomposition, task planning, sub-agent delegation, and final synthesis. | Agent delegation dispatcher, state graph manager, topology query. | Routes tasks, manages state transitions, ensures completion. |
| **Kubernetes Specialist** | Diagnosis and remediation of K8s cluster and pod failures. | K8s MCP: `get_pod_status`, `fetch_pod_logs`, `describe_pod_events`, `patch_deployment_resources`, `restart_pod`. | Requests APM traces from Observability Agent; sends fix plan to Operator. |
| **Cloud Infra Specialist** | Cloud computing, network, security group, and VM instance diagnosis. | Cloud MCP: `describe_instances`, `get_cloudwatch_metrics`, `restart_instance`, `query_cloudtrail`. | Correlates VM health with K8s node status; feeds cloud context to Supervisor. |
| **CI/CD & GitOps Specialist** | Build failures, deployment mismatches, config drift, secret injection. | GitHub/GitLab MCP: `fetch_workflow_run`, `view_commit_diff`, `create_fix_pr`, `sync_git_repo`. | Correlates deployment timestamps with incident trigger times. |
| **Observability & APM Specialist**| Metric anomaly detection, distributed trace inspection, log aggregation. | Observability MCP: `query_datadog_timeseries`, `fetch_grafana_logs`, `query_sentry_issue`. | Confirms whether metric recovered post-remediation. |
| **Security & Compliance Agent** | Secret leaks, container vulnerability scans, unverified mutations. | Security MCP: `run_gitleaks`, `scan_snyk_vulnerabilities`, `verify_iam_bounds`. | Validates that proposed remediation does not violate security policy. |
| **Remediation & Operator Agent** | Safe execution, approval gate orchestration, and post-fix verification. | Lear Action Engine: `dispatch_action`, `verify_action_success`, `execute_rollback`. | Directly interacts with Human-in-the-Loop approval cards in Desktop UI. |

---

## 3. Preserving Lear Core Principles & Desktop Alignment

Lear 3.0 builds directly upon the proven foundations documented in [`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) and [`CHANGELOG.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/CHANGELOG.md):

1. **"Credentials Never Leave the User's Machine" ([`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) §4):**
   - The MCP servers, agent orchestrator, guardrails, and Oh-My-Pi memory run locally.
   - LLM prompts are filtered through local Input Guardrails that scrub credentials and secrets before any prompt is transmitted.
2. **Permission Engine Integrity ([`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) §5):**
   - The five permission modes (`read-only`, `ask every time`, `auto-safe`, `environment-scoped`, `bypass`) are enforced by the Remediation Agent and the Action Guardrail.
   - Destructive actions (`DROP DATABASE`, data wipe) remain permanently classified as `NEVER` and cannot be bypassed.
3. **Local Append-Only Audit Trail ([`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) §6):**
   - Every agent interaction, tool invocation, guardrail block, user approval, and verification result is appended to `.prash/audit.jsonl` and surfaced via `/api/activity`.
4. **Desktop UI Integration ([`CHANGELOG.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/CHANGELOG.md)):**
   - The Tauri + React frontend (`ChatWorkspace.tsx`, `Dashboard.tsx`, `Notifications.tsx`, `ServiceWidget.tsx`, `Integrations.tsx`) communicates with the Agent Orchestrator through clean, typed API endpoints:
     - `POST /api/chat/stream`: Emits SSE streaming agent reasoning tokens and structured sub-agent activity pills.
     - `POST /api/chat/execute`: Routes interactive approvals from UI cards directly to the Remediation Agent.
     - `GET /api/incidents`: Fetches live incident state, agent investigation summaries, and episodic replay badges ("Replayed from Episode #14").
     - `/ws/events`: Streams real-time sentry alarms, live metric pulses, and agent state transitions to desktop widgets without polling.

---

## 4. Detailed Engineering Roadmap: Goals, Tasks & Subtasks

```
═══════════════════════════════════════════════════════════════════════════════════════════
                         LEAR 3.0 TRANSFORMATION ROADMAP (5 PHASES)
═══════════════════════════════════════════════════════════════════════════════════════════

 [PHASE 1: Foundation & MCP Gateway] ────> [PHASE 2: Oh-My-Pi Memory Subsystem]
                   │                                         │
                   ▼                                         ▼
 [PHASE 3: Guardrails & Sentries]    ────> [PHASE 4: Multi-Agent Orchestrator Swarm]
                   │                                         │
                   └───────────────────┬─────────────────────┘
                                       ▼
                       [PHASE 5: Desktop UX & E2E Validation]
```

---

### Phase 1: Architecture Modularization & MCP Gateway Integration
**Goal:** Decompose the monolith backend, eliminate bespoke connector maintenance, and establish the Model Context Protocol (MCP) tool execution gateway.

#### Task 1.1: Backend Decomposition & AppState Modularization
- [ ] **Subtask 1.1.1:** Split `server.py` into clean modular routers under `prash/api/routes/`:
  - `routes/connectors.py` (Registry, connection state, masked credentials)
  - `routes/chat.py` (SSE streaming, session management, multi-agent transcript)
  - `routes/incidents.py` (Incident lifecycle, approvals, resolution state)
  - `routes/watcher.py` (Sentry controls, health status, cadence)
  - `routes/dashboard.py` (Aggregated health, mission control metrics)
  - `routes/settings.py` (Model settings, safety modes, retention)
  - `routes/activity.py` (Audit log pagination, filter queries)
- [ ] **Subtask 1.1.2:** Extract all mutable global dictionaries (`_activity_log`, `_notifications`, `_watch_handles`, `_ws_clients`) into a thread-safe `AppState` class injected via FastAPI dependency injection (`request.app.state`).
- [ ] **Subtask 1.1.3:** Reduce `server.py` to an application factory under 200 lines. Verify all existing unit tests in `tests/test_desktop_api.py` remain 100% green.

#### Task 1.2: Unified MCP Client Gateway Implementation
- [ ] **Subtask 1.2.1:** Implement `prash/mcp/client_manager.py`:
  - Async client lifecycle management supporting standard MCP Stdio and SSE transports.
  - Automatic process supervisor for local MCP servers with health checks and crash restart.
- [ ] **Subtask 1.2.2:** Configure prebuilt MCP server integrations:
  - `@modelcontextprotocol/server-kubernetes` (Cluster read/write, logs, events, specs)
  - `@modelcontextprotocol/server-github` (Repo context, PRs, workflows, commit history)
  - Cloud MCP adapters (AWS, GCP, Azure CLI stdio bridges)
  - Prebuilt Observability MCP adapters (Datadog, Sentry, Prometheus)
- [ ] **Subtask 1.2.3:** Build `prash/mcp/tool_registry.py`:
  - Queries `tools/list` on all connected MCP servers at startup.
  - Generates unified, cached tool manifests with Pydantic JSON schemas.
  - Implements dynamic tool filtering based on active agent role (e.g. K8s Agent only receives K8s MCP tools).
- [ ] **Subtask 1.2.4:** Write integration tests in `tests/test_mcp_gateway.py` verifying tool discovery, invocation, schema validation, and timeout handling.

#### Task 1.3: Sandboxed CLI Harness
- [ ] **Subtask 1.3.1:** Implement `prash/mcp/cli_harness.py`:
  - Hardened execution harness for native command-line tools (`kubectl`, `gh`, `aws`, `az`, `terraform`).
  - Strict parameter sanitization and token allowlisting to prevent shell injection.
  - Configurable timeouts, non-interactive environment forcing, and clean stdout/stderr streaming.
- [ ] **Subtask 1.3.2:** Add test suite in `tests/test_cli_harness.py` covering timeout enforcement, exit-code capture, and injection rejection.

---

### Phase 2: Oh-My-Pi Cognitive Memory Subsystem
**Goal:** Implement the full tripartite cognitive memory architecture (Short-Term, Episodic, Long-Term) with local encrypted storage and instant runbook replay.

#### Task 2.1: Short-Term (Working) Memory Buffer
- [ ] **Subtask 2.1.1:** Implement `prash/memory/working_memory.py`:
  - In-memory thread-safe state store bound to active incident/chat sessions.
  - Tracks scratchpad notes, active resource pointers, intermediate tool results, and execution hypotheses.
- [ ] **Subtask 2.1.2:** Implement `prash/memory/context_compressor.py`:
  - Monitors token consumption against model context limits.
  - When context reaches 75% threshold, triggers recursive summarization of prior tool steps while preserving exact technical identifiers (names, IPs, error codes).
- [ ] **Subtask 2.1.3:** Unit tests in `tests/test_working_memory.py` validating state isolation across concurrent sessions and compression fidelity.

#### Task 2.2: Episodic Memory & Replay Engine
- [ ] **Subtask 2.2.1:** Implement `prash/memory/episodic_store.py`:
  - Replaces `prash/brain/local_memory.py` with an enterprise episodic storage engine.
  - Captures full trajectory envelopes: [Trigger State → Diagnosis Hypothesis → Action Plan → Verification Result → Resolution].
  - Persists locally in `.prash/memory/episodes.db` using SQLite with JSON extensions.
- [ ] **Subtask 2.2.2:** Implement fast dual-indexing:
  - Exact error signature indexing via SHA-256 hash lookup.
  - Semantic vector indexing using a local embedding model (ONNX Runtime with `all-MiniLM-L6-v2`) and local vector search (`sqlite-vec` or `lancedb`).
- [ ] **Subtask 2.2.3:** Implement `prash/memory/replay_engine.py`:
  - Given an incoming incident signature, queries episodic store.
  - If exact match or semantic similarity $\ge 0.88$ with verified confidence $> 0.90$, generates a "Fast-Track Replay Recommendation" citing previous episode ID.
  - Stores anti-trajectories: if an action failed, flags it as an anti-pattern to prevent redundant failed retries.
- [ ] **Subtask 2.2.4:** Unit tests in `tests/test_episodic_memory.py` proving:
  - JSON round-trip and vector retrieval accuracy.
  - First incident diagnosis runs full loop; identical second incident matches episode and recommends instant replay.
  - Anti-pattern suppression after failed verification.

#### Task 2.3: Long-Term (Semantic & Topology) Memory Graph
- [ ] **Subtask 2.3.1:** Implement `prash/memory/topology_graph.py`:
  - Stores infrastructure service dependency graph (services, databases, ingress, clusters, cloud accounts).
  - Populates relationships dynamically from project configurations in `prash.yaml` and discovered MCP resources.
- [ ] **Subtask 2.3.2:** Implement `prash/memory/policy_store.py`:
  - Stores organizational runbooks, SLO thresholds, blast-radius boundaries, and developer preferences.
  - Formats relevant policies as contextual prompts injected into the Supervisor Agent.
- [ ] **Subtask 2.3.3:** Integration tests in `tests/test_topology_memory.py` validating dependency traversal and policy retrieval.

---

### Phase 3: Pre-Trained Guardrails & Autonomous Sentry Network
**Goal:** Deploy verifiable enterprise guardrails for input/policy/action/output safety, and replace the legacy watcher with autonomous, noise-filtering Sentries.

#### Task 3.1: Pre-Trained Enterprise Guardrails Subsystem
- [ ] **Subtask 3.1.1:** Implement `prash/guardrails/input_rails.py`:
  - Integrates pre-trained classifiers for prompt injection and jailbreak detection on incoming logs, emails, Slack messages, and user prompts.
  - Local regex and NER token scrubber redacting secrets, private keys, passwords, and tokens before LLM ingestion.
- [ ] **Subtask 3.1.2:** Implement `prash/guardrails/policy_rails.py`:
  - Declarative policy rules (Colang / Pydantic rules engine) enforcing operational bounds.
  - Replaces hardcoded string matches in `_apply_deterministic_guardrails`.
  - Unconditionally blocks destructive commands (`rm -rf`, `DROP TABLE`, `delete namespace`).
- [ ] **Subtask 3.1.3:** Implement `prash/guardrails/action_rails.py`:
  - Wraps `prash/permissions.py` and `prash/circuit_breaker.py`.
  - Verifies tool parameters match exact targets (no wildcards).
  - Intercepts mutating actions, checks active permission mode (`read-only`, `ask every time`, `auto-safe`, `environment-scoped`, `bypass`), and gates execution.
- [ ] **Subtask 3.1.4:** Implement `prash/guardrails/output_rails.py`:
  - Verifies agent explanations against real tool outputs (hallucination defense).
  - Ensures no masked credentials or raw internal secrets leak into output text.
- [ ] **Subtask 3.1.5:** Unit test suite in `tests/test_guardrails.py` covering prompt injection blocking, secret redaction, policy enforcement, and hallucination catching.

#### Task 3.2: Autonomous Sentry (Sentinel) Network
- [ ] **Subtask 3.2.1:** Implement `prash/sentries/base.py`:
  - Abstract base class for non-blocking, autonomous sentries with configurable polling intervals, sliding window buffers, and health probes.
- [ ] **Subtask 3.2.2:** Implement specialized sentries:
  - `KubernetesSentry`: Monitors Pod restarts, `CrashLoopBackOff`, `OOMKilled`, node readiness, and namespace events.
  - `CloudInfraSentry`: Monitors CloudWatch alarms, EC2 instance health checks, Azure/GCP VM states, and disk/network spikes.
  - `ObservabilitySentry`: Monitors Datadog/Prometheus metric thresholds, APM error rate spikes, and PagerDuty alerts.
  - `GitOpsSentry`: Monitors GitHub/GitLab workflow run failures, commit drift, and Terraform state discrepancies.
- [ ] **Subtask 3.2.3:** Implement `prash/sentries/denoiser.py`:
  - 45-second sliding window telemetry debouncer.
  - Correlates multi-source signals (e.g. K8s pod restart + Datadog error spike + git push).
  - Suppresses transient blips, preventing alert fatigue and wasteful agent invocations.
- [ ] **Subtask 3.2.4:** Implement `prash/sentries/dispatcher.py`:
  - When an anomaly crosses verified threshold, compiles an immutable `IncidentEnvelope` and awakens the Agent Orchestrator.
  - Broadcasts live status updates over `/ws/events` to Tauri desktop widgets.
- [ ] **Subtask 3.2.5:** Unit tests in `tests/test_sentries.py` demonstrating noise suppression on transient spikes and rapid alert dispatching on real correlated failures.

---

### Phase 4: Agent Routing & Multi-Agent Orchestrator Swarm
**Goal:** Replace model routing with an intelligent Meta-Orchestrator that routes to specialized autonomous agents within a standardized workflow harness.

#### Task 4.1: Workflow Harness Core & StateGraph Engine
- [ ] **Subtask 4.1.1:** Implement `prash/orchestrator/state.py`:
  - Standardized TypedDict / Pydantic state model for incident workflows:
    ```python
    class OrchestratorState(BaseModel):
        incident_id: str
        envelope: IncidentEnvelope
        working_memory: WorkingMemory
        active_plan: List[str]
        current_agent: str
        agent_findings: Dict[str, Any]
        proposed_actions: List[Dict[str, Any]]
        execution_status: str
        verification_result: Optional[Dict[str, Any]]
        audit_records: List[Dict[str, Any]]
    ```
- [ ] **Subtask 4.1.2:** Implement `prash/orchestrator/harness.py`:
  - StateGraph workflow manager with node execution, conditional edge routing, and SQLite checkpointing.
  - Native Human-in-the-Loop (HITL) interrupt when an action requires approval, allowing seamless pause and resume upon user input.
- [ ] **Subtask 4.1.3:** Implement event streaming bridge:
  - Transforms internal agent transitions into typed SSE/WebSocket events (`thought`, `delegation`, `tool_call`, `approval_needed`, `verified`).

#### Task 4.2: Specialized Domain Agents
- [ ] **Subtask 4.2.1:** Implement `SupervisorAgent` (`prash/agents/supervisor.py`):
  - Formulates the master investigation plan based on incident envelope and Oh-My-Pi topology memory.
  - Routes sub-tasks to specialized domain agents, aggregates findings, and synthesizes root-cause analyses.
- [ ] **Subtask 4.2.2:** Implement `KubernetesAgent` (`prash/agents/kubernetes.py`):
  - Expert on pod events, crash loops, container termination reasons, resource limits, and service manifests.
  - Consumes Kubernetes MCP tools.
- [ ] **Subtask 4.2.3:** Implement `CloudInfraAgent` (`prash/agents/cloud.py`):
  - Specializes in AWS/GCP/Azure compute instances, IAM roles, security groups, CloudWatch alarms, and VPC configurations.
  - Consumes Cloud MCP tools.
- [ ] **Subtask 4.2.4:** Implement `ObservabilityAgent` (`prash/agents/observability.py`):
  - Specializes in metric timeseries, APM traces, Grafana/Datadog logs, and error rate correlation.
  - Consumes Observability MCP tools.
- [ ] **Subtask 4.2.5:** Implement `GitOpsAgent` (`prash/agents/gitops.py`):
  - Specializes in CI build logs, git diffs, PR generation, and secret configuration.
  - Consumes GitHub/GitLab MCP tools.
- [ ] **Subtask 4.2.6:** Implement `SecurityAgent` (`prash/agents/security.py`):
  - Audits proposed fixes against security baselines, scans for secret leaks, and verifies least-privilege compliance.
- [ ] **Subtask 4.2.7:** Implement `RemediationAgent` (`prash/agents/remediation.py`):
  - Formulates safe remediation plans, checks Oh-My-Pi episodic memory, routes approvals through Permission Engine, executes actions, and runs post-fix verification probes.

#### Task 4.3: Agent Routing & Multi-Agent Collaboration
- [ ] **Subtask 4.3.1:** Implement Agent-to-Agent (A2A) consultation protocol:
  - Enables Kubernetes Agent to query Observability Agent for APM trace correlation without user intervention.
- [ ] **Subtask 4.3.2:** Implement agent delegation fallbacks and timeout guards:
  - If a specialist agent does not produce findings within 30 seconds, Supervisor steps in with graceful degradation.
- [ ] **Subtask 4.3.3:** Unit and integration tests in `tests/test_agent_orchestrator.py` verifying multi-agent delegation, checkpoint resume, and HITL pause/unpause.

---

### Phase 5: Desktop UX Overhaul, E2E Verification & Cutover
**Goal:** Align the Tauri desktop interface (`ChatWorkspace.tsx`, `Dashboard.tsx`, `Notifications.tsx`) with the new multi-agent orchestrator, prove end-to-end functionality, and execute seamless cutover.

#### Task 5.1: Desktop UI Enhancement (`ChatWorkspace.tsx` & `Dashboard.tsx`)
- [ ] **Subtask 5.1.1:** Update `ChatWorkspace.tsx` to display multi-agent thought streams:
  - Render agent delegation pills (`[Supervisor -> Kubernetes Specialist]`, `[Observability Specialist Consulting Datadog]`).
  - Interactive Action Approval cards with clear blast-radius badges, parameter diffs, and one-click "Approve" / "Deny" buttons.
  - Episodic Memory Replay badge ("⚡ Replayed from verified episode `ep_20261002_oom` with 96% confidence").
- [ ] **Subtask 5.1.2:** Update `Dashboard.tsx` with live Sentry status:
  - Animated radar pulse indicator showing active Sentries (K8s, Cloud, APM, GitOps).
  - Incident resolution timeline linked to episodic memory records.
- [ ] **Subtask 5.1.3:** Update `Integrations.tsx` to display MCP Server connectivity:
  - Shows connected MCP servers, dynamically discovered tool counts, and transport health (stdio/SSE).

#### Task 5.2: End-to-End Verification & Benchmark Suite
- [ ] **Subtask 5.2.1:** Execute the canonical definition of done from [`PRASH_V2.md`](file:///c:/Users/anant/Downloads/Lear-Backend/Lear-Backend/PRASH_V2.md) §0b:
  - Inject real `CrashLoopBackOff` failure into test Kubernetes cluster.
  - Verify Sentry detects failure and awakens Supervisor Agent.
  - Verify Supervisor routes to Kubernetes Specialist Agent.
  - Verify agent checks Oh-My-Pi episodic memory (first run: diagnoses from scratch, executes verified fix, saves episode).
  - Verify post-fix verification probe confirms pod recovery and records to audit log.
  - Inject identical failure again; verify agent matches episode and suggests replay in under 3 seconds.
- [ ] **Subtask 5.2.2:** Benchmark multi-agent orchestrator latency and token usage against legacy monolith.
- [ ] **Subtask 5.2.3:** Run full regression suite across all 41 test files, ensuring zero regressions.

#### Task 5.3: Documentation & Production Cutover
- [ ] **Subtask 5.3.1:** Update `README.md`, `ROADMAP.md`, and `CHANGELOG.md` with Lear 3.0 architecture documentation.
- [ ] **Subtask 5.3.2:** Provide contributor runbook for adding new MCP servers and specialized domain agents.
- [ ] **Subtask 5.3.3:** Final team review and milestone sign-off.

---

## 5. Architectural Comparison Matrix

| Capability | Lear 2.x (Current) | Lear 3.0 (Target) | Impact / Benefit |
|---|---|---|---|
| **Architecture Paradigm** | Monolithic script (`server.py`, `diagnosis_agent.py`) | Orchestrator Workflow Harness + Agent Swarm | High modularity, testability, crash resilience |
| **Routing Mechanism** | Model Routing (picking LLM model) | **Agent Routing** (routing specialized AI agents) | True AI-native reasoning, deep domain specialization |
| **Tool Execution** | 14 custom hand-coded connectors (`aws.py`, etc.) | **Prebuilt MCP Servers** + Sandboxed CLI Harness | Zero connector maintenance burden, open ecosystem |
| **Safety & Verification** | Hardcoded regex checks (`_apply_deterministic_guardrails`) | **Pre-Trained Enterprise Guardrails** (NeMo / Llama Guard) | Robust injection defense, verifiable policy enforcement |
| **Memory System** | Flat append-only `.prash/memory.json` | **Oh-My-Pi Tripartite Memory** (Working, Episodic, Semantic) | Instant runbook replay, causal learning, topology aware |
| **Monitoring / Watcher** | Synchronous polling while-loop | **Autonomous Sentry Network** with 95% denoiser | Autonomous proactive defense, zero alert fatigue |
| **State & Approvals** | Bespoke in-memory dicts | StateGraph with SQLite checkpoints & native HITL | Resumable across server restarts, strict safety gates |
| **Desktop UI Stream** | Raw string chunking over SSE | Typed Agent Thought & Delegation Events | Rich multi-agent visibility, interactive approval cards |

---

## 6. Risk Analysis & Blast-Radius Containment

| Risk | Severity | Mitigation Strategy |
|---|---|---|
| **MCP Server Crash / Timeout** | Medium | MCP Client Manager wraps all calls with 15s timeout, exponential backoff, circuit breakers, and fallback to native CLI harness. |
| **Agent Hallucination in Remediation** | High | Pre-trained Output Guardrail cross-references proposed actions against verified tool outputs and strict schema validators. |
| **Accidental Production Mutation** | Critical | Permission Engine permanently classifies destructive operations as `NEVER`. Production mutations strictly require explicit human approval via interactive UI cards regardless of bypass mode. |
| **Episodic Memory Poisoning** | High | Only fixes that pass post-remediation verification probes (pod remains healthy for $\ge 60$ seconds) are committed to the episodic store. Failed fixes are stored as anti-patterns. |
| **Local Vector Index Performance Overhead** | Low | Local ONNX Runtime with quantized `all-MiniLM-L6-v2` generates embeddings in under 12ms. Vector queries over SQLite-vec complete in under 5ms. |

---

## 7. Immediate Next Steps (Sprint Kickoff)

1. **Review and Team Alignment:** Review `plan.md` across team members (Anant, Aryan, Aradhya, Agrim, Avi, Parv).
2. **Phase 1 Kickoff (Day 1-3):**
   - Aryan & Parv: Split `server.py` into modular route files under `prash/api/routes/` and extract `AppState`.
   - Anant: Scaffold `prash/mcp/client_manager.py` and integrate the first prebuilt Kubernetes MCP server.
   - Agrim: Benchmark local embedding generation with ONNX for the Oh-My-Pi Episodic Memory index.
   - Avi: Update `ChatWorkspace.tsx` mock types to support multi-agent thought streams and approval cards.
