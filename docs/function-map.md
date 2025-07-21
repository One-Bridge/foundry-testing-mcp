# Function Map – Foundry Testing MCP  
_(concise reference – updated 21 Jul 2025)_

This index lists the primary entry points exposed to an AI client plus the key internal helpers they rely on.  All functions are implemented in the current codebase unless noted.  Public‐facing functions follow the MCP tooling contract and return JSON-serialisable dictionaries.

---

## 1 Public MCP Tools (client-callable)

| Tool | Location | Purpose |
|------|----------|---------|
| `initialize_protocol_testing_agent` | `testing_tools.py` | Baseline scan, classify contracts/tests, suggest workflow, open session |
| `analyze_project_context` | same | Deep analysis with AI-failure prevention/detection and improvement plan |
| `execute_testing_workflow` | same | Run a multi-phase plan to create or enhance tests |
| `analyze_current_test_coverage` | same | Parse `forge coverage`; highlight gaps vs target |
| `validate_current_directory` | same | Confirm Foundry tool-chain & project structure |
| `debug_directory_detection` | same | Diagnose client/server cwd mismatch |
| `discover_foundry_projects` | same | Scan disks for Foundry projects (fallback) |
| `get_server_info` | `testing_server.py` | List tools, parameters, examples |
| `validate_foundry_config` | same | Validate and auto-suggest fixes for `foundry.toml` (optimizer, viaIR, remappings) |
| `get_mcp_resources_content` | same | Serve full template/pattern/doc payloads for offline AI use |

_All public tools take an optional `project_path` for explicit targeting._

---

## 2 Integration Adapter

| Function | Location | Purpose |
|----------|----------|---------|
| `run_tests` | `foundry_adapter.py` | Async wrapper around `forge test` (JSON mode) |
| `generate_coverage_report` | same | Runs `forge coverage`, parses LCOV / summary / JSON |
| `detect_project_structure` | same | Enumerate contracts/tests, read `foundry.toml` |
| `check_foundry_installation` | same | Return versions of `forge`, `cast`, `anvil` |

The adapter exposes *only* these helpers; the tool layer assembles them into higher-level features.

---

## 3 Analysis Modules

| Module | Key Public API | Responsibility |
|--------|----------------|----------------|
| `ProjectAnalyzer` | `analyze_project` | Regex-first classification, risk scores, maturity level |
| `AIFailureDetector` | `analyze_test_file`, `generate_failure_report` | Detect twelve AI test anti-patterns with AST-based false-positive filtering |
| `ASTAnalyzer` | `analyze_solidity_file` (optional) | Semantic enrichments when `solc` present |

These modules are imported by the tool layer; they are **not** exposed directly to the client.

---

## 4 Resource Endpoints

| MCP Resource URI | Served By | Content |
|------------------|-----------|---------|
| `testing://foundry-patterns` | `testing_resources.py` | Folder & naming conventions, best practices |
| `testing://security-patterns` | same | Reentrancy, flash-loan, oracle manipulation patterns |
| `testing://templates/{type}` | same | Solidity test templates (unit, integration, invariant, security, fork, helper) |
| `testing://templates` | same | Catalog of available templates |
| `testing://documentation` | same | In-memory copies of docs for offline AI access |

---

## 5 Prompt Helpers

Prompt functions wrap best-practice guidance into reusable prompts for the AI.  Located in `testing_prompts.py`.

`analyze_contract_for_testing` • `design_test_strategy` • `review_test_coverage` • `design_security_tests` • `optimize_test_performance`

---

## 6 Server Infrastructure

| Function | Purpose |
|----------|---------|
| `TestingMCPServer.__init__` | Instantiate FastMCP server, inject components |
| `_register_components` | Attach tools, resources, prompts |
| `run_server` | Start stdio or HTTP loop |

---

## 7 Typical Call Graph

```text
Client → initialize_protocol_testing_agent
         └─ ProjectAnalyzer.analyze_project
         └─ FoundryAdapter.detect_project_structure

Client → execute_testing_workflow
         └─ FoundryAdapter.run_tests / generate_coverage_report (per phase)
         └─ AIFailureDetector.analyze_test_file (QA gate)
```

Use this map to navigate the codebase or to extend functionality (e.g., add new MCP tools or adapters). 