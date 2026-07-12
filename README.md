# 🌐 NexusPipe AI: Autonomous Multi-Agent Data Pipeline

NexusPipe AI is a high-performance, multi-tenant B2B SaaS platform engineered to automate the ingestion, validation, root-cause diagnosis, and documentation of unstructured system anomalies and server error logs. 

By orchestrating data streams sequentially across isolated, flagship Large Language Model (LLM) environments, NexusPipe AI transforms chaotic system data into production-ready, engineering-grade Markdown incident reports in under 10 seconds—slashing mean-time-to-resolution (MTTR) and eliminating manual operational review cycles.

---

## ⚡ Architectural Framework & Core Layers

NexusPipe AI operates across a modular four-tier technical layout to guarantee performance, data isolation, and total structural auditability:

```text
[1. Premium UI Layer] ➔ [2. Triage Layer: OpenAI] ➔ [3. Synthesis Layer: Anthropic] ➔ [4. Relational SQL Ledger]
```

1. **Ingestion & UI Layer**: A modern, dark-themed user interface styled with custom glassmorphism components. It provides an unauthenticated Sandbox Triage Hook for public testing alongside secure, authenticated dashboards for enterprise accounts.
2. **Triage Layer (Agent 1 - OpenAI)**: Evaluates incoming raw log payloads, strips away structural text noise, and extracts the core system exceptions, timestamps, and network vulnerabilities.
3. **Synthesis Layer (Agent 2 - Anthropic)**: Consumes Agent 1's structured summary and executes complex diagnostic mapping via the `claude-sonnet-4-6` engine to generate full, context-aware architectural incident mitigation reports.
4. **Relational Persistence Ledger (SQL Layer)**: Persists immutable tracking rows inside a structured ledger (`pipeline_metrics.db`), auditing system runtimes, pipeline status variables, and precise multi-model token expenses.

---

## 🔒 Enterprise Security & Isolation Topology

NexusPipe AI is explicitly architected to meet rigid corporate data protection standards:
* **Multi-Tenant Account Partitioning**: Managed via an integrated backend layer using the **Firebase Admin SDK**. User accounts are completely sandboxed; data queries and logging matrices are filtered strictly by authenticated email domains.
* **Zero-Leak Secret Management**: Production credentials, environment keys, and Firebase service account keys are stored locally via TOML configuration blocks and protected using strict branch exclusions (`.gitignore`), keeping your platform secure from online exposure.

---

## 🛠️ Local Environment Workspace Configuration

To pull down this repository and initialize the pipeline infrastructure locally on your workstation, execute the following steps:

### 1. Clone the Repository and Navigate In
```bash
git clone https://github.com
cd nexuspipe-ai
```

### 2. Isolate Dependencies via a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Local Secret Environment Variables
Create a hidden `.env` file in the root folder and input your private developer credentials:
```text
OPENAI_API_KEY="your-production-openai-key-here"
ANTHROPIC_API_KEY="your-production-anthropic-key-here"
```

### 4. Insert Your Firebase Initialization Token
Place your private Firebase configuration certificate inside the root project directory and ensure it is named exactly **`firebase_creds.json`**. 

### 5. Boot Up the Systems Dashboard
```bash
streamlit run dashboard.py
```
*The secure console will initialize and load seamlessly on your local environment at `http://localhost:8501`.*

---

## 📊 Commercial Licensing, Maintenance, & Retainers

NexusPipe AI is commercialized as an enterprise software utility under a hybrid infrastructure delivery contract:
* **Deployment & Core Architecture Setup Fee:** $2,500.00 (One-time platform environment configuration).
* **Managed AI Operations & Optimization Support Retainer:** $1,000.00 / month. 
  * Covers upstream API framework adaptation, continuous weekly prompt-drift auditing, priority SLA emergency debugging, and routine monthly multi-model token cost evaluations.

---

**Developed & Distributed by Josiah Castillo, Founder of NexusPipe AI.**  
*For corporate partnerships, contract custom integrations, or service level inquiries, reach out directly via the core authentication gateway.*
