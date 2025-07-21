# Smart Contract Testing MCP Server

## Executive Overview

This repository hosts a Model-Context-Protocol (MCP) server that helps engineering teams automate and improve the testing of Solidity smart contracts built with the [Foundry](https://book.getfoundry.sh/) tool-chain.  
The server exposes a small set of MCP tools that can be called from an AI client (e.g. Cursor, Claude-Desktop) to:

1. Inspect a project’s structure, configuration, and current test quality.
2. Detect common weaknesses in AI-generated tests such as circular logic or missing edge cases.
3. Generate structured testing workflows—unit, integration, invariant, fuzz, and security tests.
4. Drive Foundry commands (`forge test`, `forge coverage`, gas reporting) and parse the results.
5. Provide domain-specific guidance, reusable templates, and up-to-date best practices.

The codebase is written in Python and relies on standard tooling only; no cloud services are required.

---

## Quick Setup

### 1 Clone the repository
```bash
git clone https://github.com/your-org/foundry-testing-mcp.git
cd foundry-testing-mcp
```

### 2 Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
```

### 3 Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4 Install the Foundry tool-chain (if not already present)
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 5 Run the MCP server

• **For AI-client integration** (silent stdio mode):
```bash
python run_clean.py
```

• **For local debugging** (verbose logging, optional HTTP mode):
```bash
python run.py                       # MCP_TRANSPORT_MODE=stdio (default)
# or
MCP_TRANSPORT_MODE=http python run.py
```

Point your MCP-compatible client at the process you just started.  The server communicates over stdio unless `MCP_TRANSPORT_MODE` is set to `http`.

---

## Core Components

| Path | Responsibility |
|------|----------------|
| `components/testing_server.py`   | Starts the FastMCP server and registers all tools & resources |
| `components/testing_tools.py`    | Defines high-level MCP tools: initialise, analyse, execute workflows, etc. |
| `components/foundry_adapter.py`  | Thin wrapper around Foundry CLI commands and result parsing |
| `components/ai_failure_detector.py` | AST-aware detection of eight failure types in generated tests |
| `components/project_analyzer.py` | End-to-end project inspection: contracts, tests, coverage, risk |
| `components/testing_resources.py`| In-memory library of templates, patterns, and documentation |
| `templates/`                     | Ready-to-use Solidity test templates |
| `docs/`                          | Additional architecture notes and guidance |

---

## Primary MCP Tools

The server registers seven tools; the first three cover most day-to-day needs.

1. **`initialize_protocol_testing_agent`** – Inspect the current project and suggest appropriate workflows.
2. **`analyze_project_context`** – Deep dive with AI failure detection and risk scoring.
3. **`execute_testing_workflow`** – Run a multi-phase test-generation workflow (create or enhance suites).
4. `analyze_current_test_coverage` – Parse `forge coverage` output, highlight gaps.
5. `validate_current_directory` – Confirm the working directory is a valid Foundry project.
6. `debug_directory_detection` – Troubleshoot path-resolution problems between client and server.
7. `get_server_info` – Summarise server capabilities and configuration.

Detailed parameter lists are available via the `get_server_info` tool or by reading the doc-strings in `components/testing_tools.py`.

---

## Minimal Usage Example (from an AI client)
```python
# 1. Ensure your shell is in the root of a Foundry project
# 2. In the client, call the initialise tool:
initialize_protocol_testing_agent()

# 3. Let the AI review the output and pick a workflow, e.g.:
execute_testing_workflow(
    workflow_type="create_new_suite",
    objectives="achieve 90%+ coverage with security focus"
)
```

---

## Directory Layout (abridged)
```
foundry-testing-mcp/
├── components/        # Server code (Python)
├── templates/         # Solidity test templates
├── docs/              # Supplementary documentation
├── run_clean.py       # Stdio server entry-point
├── run.py             # Development entry-point
└── requirements.txt   # Python dependencies
```

© MIT-licensed.  No warranty is provided; use at your own risk.
