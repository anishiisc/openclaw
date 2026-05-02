# 🦞 OpenClaw for Agentic AI — A Practitioner's Tutorial

> **Tutorial Note + Hands-On Python Code Artifacts for Understanding, Installing, and Building with OpenClaw**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![OpenClaw SDK](https://img.shields.io/badge/OpenClaw%20SDK-2.1.0-red.svg)](https://pypi.org/project/openclaw-sdk/)

---

## 📌 About

This repository contains the companion code and tutorial note for **"OpenClaw for Agentic AI: A Practitioner's Tutorial Note"** by **Dr. Anish Roychowdhury**.

OpenClaw — the open-source autonomous AI agent framework that crossed 250,000 GitHub stars in 60 days — represents a fundamental shift in how we build with AI. This tutorial covers the architecture, installation, security considerations, and provides four hands-on Python artifacts that run on your laptop or Google Colab.

---

## 📂 Repository Structure

```
openclaw/
│
├── OpenClaw_Tutorial_Note.tex       # LaTeX source — full tutorial note
├── OpenClaw_Tutorial_Note.pdf       # Compiled PDF (if available)
│
├── 01_openclaw_basic_agent.py       # Artifact 1: Your First OpenClaw Agent
├── 02_openclaw_skill_creator.py     # Artifact 2: Building a Custom Skill
├── 03_openclaw_multi_agent_pipeline.py  # Artifact 3: Multi-Agent Pipeline
├── 04_openclaw_agent_from_scratch.py    # Artifact 4: Agent Loop from Scratch
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
└── README.md                        # This file
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/anishiisc/openclaw.git
cd openclaw
```

### 2. Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Run Your First Artifact

```bash
# Simplest start — no OpenClaw gateway needed
python 04_openclaw_agent_from_scratch.py
```

---

## 📝 Code Artifacts

### Artifact 1: Your First OpenClaw Agent
**File:** `01_openclaw_basic_agent.py`

Connects to a local OpenClaw gateway via the Python SDK and executes a research task. Includes a standalone fallback using the Anthropic SDK directly (works in Colab without a gateway).

```bash
python 01_openclaw_basic_agent.py
```

**Prerequisites:** `pip install openclaw-sdk anthropic python-dotenv`

---

### Artifact 2: Building a Custom Skill
**File:** `02_openclaw_skill_creator.py`

Programmatically generates a complete "Stock Price Checker" skill with:
- `SKILL.md` — metadata and LLM instructions
- `tool.py` — tool implementation using `yfinance`
- `requirements.txt` and `README.md`

```bash
python 02_openclaw_skill_creator.py
```

**Prerequisites:** `pip install yfinance python-dotenv`

---

### Artifact 3: Multi-Agent Pipeline
**File:** `03_openclaw_multi_agent_pipeline.py`

Chains three specialised agents into a composable pipeline:

```
Research Topic → Researcher Agent → Summariser Agent → Reporter Agent → LinkedIn Post
```

Includes token tracking, cost estimation, and JSON report export.

```bash
python 03_openclaw_multi_agent_pipeline.py
```

**Prerequisites:** `pip install anthropic python-dotenv`

---

### Artifact 4: Agent Loop from Scratch ⭐
**File:** `04_openclaw_agent_from_scratch.py`

**The educational centrepiece.** Implements the core ReAct agent loop from first principles — the same pattern that powers OpenClaw internally. Includes 5 tools (calculator, file reader/writer, shell command, datetime) with safety sandboxing.

No OpenClaw SDK needed — just the Anthropic SDK.

```bash
python 04_openclaw_agent_from_scratch.py
```

**Prerequisites:** `pip install anthropic python-dotenv`

---

## 📦 Dependencies

```txt
anthropic>=0.39.0
openclaw-sdk>=2.1.0
python-dotenv>=1.0.0
yfinance>=0.2.36
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
# Required for all artifacts
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: only if connecting to a running OpenClaw gateway
OPENCLAW_GATEWAY_WS_URL=ws://127.0.0.1:18789/gateway
OPENCLAW_API_KEY=your-openclaw-api-key
```

---

## 📄 Tutorial Note (LaTeX)

The full tutorial note is provided as a LaTeX source file: `OpenClaw_Tutorial_Note.tex`

### Compile Locally

```bash
# Requires: texlive-full or equivalent
pdflatex OpenClaw_Tutorial_Note.tex
pdflatex OpenClaw_Tutorial_Note.tex  # Second pass for TOC
```

### Contents

| Section | Topic |
|---------|-------|
| 1 | Introduction: The Agent Inflection Point |
| 2 | Architecture: How OpenClaw Works |
| 3 | Installation Guide (3 methods + security hardening) |
| 4 | Code Artifacts: Hands-On Python Examples |
| 5 | Cost Awareness |
| 6 | Security: Eyes Wide Open |
| 7 | The Bigger Picture: Why OpenClaw Matters |
| 8 | Getting Started Checklist |
| 9 | References (14 sources, all 2025–2026) |

---

## ⚠️ Security Notice

OpenClaw is a powerful but **security-sensitive** tool. Before running any OpenClaw agent:

1. **Fix Canvas Host binding** to `loopback` in `~/.openclaw/openclaw.json`
2. **Never install unreviewed skills** from ClawHub
3. **Run in a sandboxed environment** (Docker, VM, or dedicated machine)
4. **Review the security section** (Section 6) of the tutorial note

See [Transparency Coalition's risk guide](https://www.transparencycoalition.ai/news/tcai-guide-the-risks-of-ai-agents-built-with-openclaw-and-other-frameworks) for comprehensive security analysis.

---

## 📚 Key References

1. [OpenClaw Official Docs](https://docs.openclaw.ai/start/getting-started)
2. [OpenClaw GitHub](https://github.com/openclaw/openclaw) — 347,000+ stars
3. [OpenClaw Python SDK (PyPI)](https://pypi.org/project/openclaw-sdk/)
4. [claw0: 0→1 Learn OpenClaw](https://github.com/shareAI-lab/claw0) — Teaching repository
5. [KDnuggets: OpenClaw Explained](https://www.kdnuggets.com/openclaw-explained-the-free-ai-agent-tool-going-viral-already-in-2026)
6. [Nvidia: OpenClaw Is To Agentic AI What GPT Was To Chatbots](https://www.nextplatform.com/ai/2026/03/17/nvidia-says-openclaw-is-to-agentic-ai-what-gpt-was-to-chattybots/)
7. [DigitalOcean: How to Run OpenClaw](https://www.digitalocean.com/community/tutorials/how-to-run-openclaw)

---

## 🔗 Google Colab Support

All artifacts support **dual-mode operation**:
- **SDK mode:** Connects to a running OpenClaw gateway (for local development)
- **Standalone mode:** Falls back to the Anthropic SDK directly (for Colab)

To run in Colab, simply set `ANTHROPIC_API_KEY` in the notebook environment and run any artifact. Artifacts 3 and 4 work fully standalone.

---

## 👤 Author

**Dr. Anish Roychowdhury**
Gen AI Architect · AI Educator · Practitioner

- 📧 anish.roychowdhury@gmail.com
- 📖 Published Poet — *Gin and Ginger* (Kolkata International Book Fair 2026)

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built with 🦞 and Claude*
