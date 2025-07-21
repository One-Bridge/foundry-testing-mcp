# User Stories & Implementation Outline – Foundry Testing MCP

_Last revised: 2025-07-20_

This guide shows two practical workflows for teams using the MCP server:

1. **Green-field** – add a full test suite to a project with no tests.  
2. **Brown-field** – lift an existing suite to production-ready quality.

Both paths rely on the same three tools:

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `initialize_protocol_testing_agent` | Scan project, classify contracts, pick a workflow |
| 2 | `execute_testing_workflow` | Generate phase plan; create or enhance tests |
| 3 | `analyze_current_test_coverage` | Measure progress toward coverage target |

All analysis is regex-first and requires only the local Foundry tool-chain and access to an MCP-capable LLM coding agent.

---

## Scenario A – From Zero to Tested

```text
my-protocol/
├─ src/          # Solidity contracts
├─ foundry.toml  # Foundry config
└─ test/         # empty
```

1. **Analyse**
   ```python
   initialize_protocol_testing_agent()
   ```
   • Contracts are classified (DeFi, governance, etc.).  
   • Risk scores and security patterns are surfaced.  
   • MCP recommends the `create_foundational_suite` workflow.

2. **Generate plan**
   ```python
   execute_testing_workflow(
       workflow_type="create_foundational_suite",
       objectives="90%+ coverage with security focus"
   )
   ```
   The server returns four phases (infrastructure, core unit tests, integration/security, advanced patterns) with TODO lists.
   Injects common AI failure patterns for code generation into model context window. 

3. **Use templates** – Pull unit, integration, invariant and helper templates from the resource API and fill in placeholders.

4. **Check coverage**
   ```python
   analyze_current_test_coverage(target_coverage=90)
   ```
   Iterate until target reached; gaps are reported per file.

---

## Scenario B – Improving an Existing Suite

```text
mature-protocol/
├─ src/                  # contracts
├─ test/                 # basic tests exist
└─ foundry.toml
```

1. **Baseline scan**
   ```python
   initialize_protocol_testing_agent()
   ```
   Summarizes repo maturity; risk hotspots identified.

2. **Deep dive**
   ```python
   analyze_project_context(include_ai_failure_detection=True)
   ```
   Flags mock cheating and missing negative tests; supplies an improvement plan.

3. **Focused workflow**
   ```python
   execute_testing_workflow(
       workflow_type="expand_test_coverage",
       objectives="Raise to 90% coverage and fix AI-failure issues"
   )
   ```
   A three-phase plan (quality remediation → coverage expansion → advanced security) is delivered with specific TODOs.

4. **Refactor mocks & tests** – Apply helper template, replace trivial mocks with configurable ones, add negative and edge-case tests.

5. **Validate**
   ```python
   analyze_current_test_coverage(target_coverage=90)
   ```
   and
   ```python
   analyze_project_context(include_ai_failure_detection=True)
   ```
   Ensure both coverage and quality gates pass.

---

## Quick Reference

| Command | When to Run | What You Get |
|---------|-------------|--------------|
| `validate_current_directory()` | Setup troubleshooting | Confirms Foundry project & tool-chain present |
| `debug_directory_detection()` | Path issues | Guidance on fixing client/server `cwd` mismatch |
| `get_server_info()` | On-boarding | List of tools, parameters, examples |

For architectural detail see `technical-architecture-guide.md`; for business context see `executive-summary.md`.  All templates live under `testing://templates/*`. 