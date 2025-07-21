# Foundry Testing MCP – Technical Architecture Guide

_Last updated: 2025-07-21_

The MCP server is a standalone Python service that allows an AI coding assistant to analyse, generate and run Solidity tests through the Foundry tool-chain.  This document explains the architecture, data flow and key design decisions.

---

## 1. High-Level View

```text
AI Client (Cursor / Claude) ──MCP protocol(stdio/http)──> MCP Server (Python)
                                         │
                                         ├─► Tool Layer (10 public tools)
                                         │   initialise • analyse • workflow …
                                         │
                                         ├─► Analysis Layer
                                         │   • ProjectAnalyzer (regex-first)
                                         │   • ASTAnalyzer   (optional)
                                         │   • AIFailureDetector
                                         │
                                         ├─► Integration Layer
                                         │   • FoundryAdapter (forge / cast / anvil)
                                         │
                                         └─► Resource Layer
                                             Templates • Patterns • Docs
```

* **Stateless transport** – The client controls the session; the server keeps minimal state (`TestingSession`) to track multi-phase workflows.
* **Local execution** – All analysis and test runs happen on the developer’s machine.  No Internet calls are made by default.

---

## 2. Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Regex-first analysis** | Works even when `solc` is missing (CI containers, air-gapped hosts). |
| **Optional AST enhancement** | Adds semantic insight when the Solidity compiler is available; otherwise skipped. |
| **Separation of concerns** | Analysis, workflow orchestration and tool execution live in separate packages. |
| **Graceful degradation** | Each layer provides a safe fallback rather than failing hard. |
| **Zero external services** | Simplifies security review and on-prem deployments. |

---

## 3. Core Components

### 3.1 Tool Layer (`components/testing_tools.py`)

Defines ten public MCP tools.  Each has:
* A clear JSON signature (validated automatically by FastMCP).
* Inline doc-strings that appear in `get_server_info`.
* Consistent error handling so that the AI client can reason about failures.

### 3.2 Analysis Layer

| Component | Key Tasks |
|-----------|-----------|
| `ProjectAnalyzer` | Scans contracts/tests, determines maturity level, classifies contract types, extracts mock requirements.  Pure regex with scoring heuristics. |
| `ASTAnalyzer` | If `solc` is on the PATH, generates a compact AST (`solc --ast-compact-json`) and enriches the regex results (control-flow, security patterns). |
| `AIFailureDetector` | Uses AST + regex to flag twelve common anti-patterns (circular logic, mock cheating, inadequate randomization, etc.).  Employs false-positive suppression for sophisticated suites.  Falls back to regex-only when AST fails. |

### 3.3 Integration Layer (`components/foundry_adapter.py`)

A thin wrapper around Foundry CLI commands.  Responsibilities:
* Build the command list (`forge test`, `forge coverage`, etc.).
* Spawn non-blocking subprocesses with async I/O.
* Parse output (JSON, LCOV, summary tables).
* Return structured dictionaries to the tool layer.

A single dependency on the user’s Foundry installation keeps the Python package lightweight.

### 3.4 Resource Layer

Static assets served through MCP resources:
* **Templates** (`templates/*.sol`) – unit, integration, invariant, helper.
* **Patterns / Docs** – plain-text guidance embedded in the wheel.

---

## 4. Data Flow

```text
  forge coverage ─┐       (subprocess)
                  ▼
 FoundryAdapter  ──►  Coverage JSON / LCOV  ──►  ProjectAnalyzer
                                            │
  test files ───────────────┐                │
                            ▼                ▼
                       AIFailureDetector  ——►  Failure report
                                            │
                                            ▼
                                  TestingTools – JSON response to client
```

*All interactions are asynchronous; slow shell commands do not block the event loop.*

---

## 5. Session Object

```python
@dataclass
class TestingSession:
    session_id: str
    project_path: str
    current_phase: int
    workflow_type: str
    analysis_results: Dict[str, Any]
```

The object is kept in memory only; no persistence layer is required.

---

## 6. Extension Points

| Need | Recommended Approach |
|------|----------------------|
| Additional static analysis (e.g., Slither) | Wrap in a new adapter similar to `FoundryAdapter`. |
| Visual reporting | Consume JSON outputs and render in a separate web UI. |
| Alternative test frameworks | Add another adapter; keep the tool contracts unchanged. |

---

## 7. Known Constraints

* **Directory detection** – The AI client must start the server with the project root as `cwd` _or_ set `MCP_CLIENT_CWD`.  Validation tools are provided.
* **Subprocess limits** – Some sandboxed CI environments block `forge`; coverage analysis will fail gracefully but return empty data.
* **Large projects** – Regex scanning is linear in file size; very large repos (>1000 files) may take ~10-15 s for initial analysis.

---

## 8. Security Considerations

*No network calls* and *no file writes* beyond temporary directories.  The greatest risk is privilege level of the Foundry compiler itself; standard best practices (run inside least-privileged container) apply.

---

## 9. Roadmap Snapshot

| Area | Short Term | Long Term |
|------|------------|-----------|
| Static analysis | Slither integration | Decompiler-based data-flow checks |
| Reporting       | HTML coverage dashboards | Integration with risk-score dashboards |
| Language support| Hardhat & Foundry parity | Multi-chain (Move, Cairo) |

---

For a compact business overview see `docs/executive-summary.md`.  Function reference lives in `docs/function-map.md`. 