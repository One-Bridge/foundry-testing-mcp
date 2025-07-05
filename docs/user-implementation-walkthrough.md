# Foundry Testing MCP v2.0 - User Implementation Walkthrough

## Quick Start Guide

This walkthrough demonstrates how to use the Foundry Testing MCP v2.0 to create comprehensive, professional-grade tests for smart contracts. The enhanced system provides context-aware guidance that understands your current project state and adapts workflows to your testing maturity level, integrating professional security methodologies and real Foundry tool analysis.

## Prerequisites

### Environment Setup

```bash
# 1. Install Foundry (if not already installed)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# 2. Verify Foundry installation
forge --version
# Expected output: forge 0.x.x (hash, timestamp)

# 3. Navigate to your smart contract project
cd /path/to/your/smart-contract-project

# 4. Initialize Foundry project (if needed)
forge init --force

# 5. Verify project structure
ls -la
# Should see: foundry.toml, src/, test/, script/
```

### MCP Server Setup

The Foundry Testing MCP v2.0 is designed to work with MCP clients like Cursor with Claude. Ensure your MCP client is configured to connect to the testing server.

## Core Workflow: Context-Aware Testing

### Step 1: Initialize with Context Analysis

**Always start here** - The MCP will analyze your current project state and provide tailored guidance.

**Tool**: `initialize_protocol_testing_agent`

```
USER: I want to improve the testing for my DeFi protocol. We have some basic tests but need better coverage and security testing.

ASSISTANT: I'll analyze your current project and recommend the best testing approach. Let me start by understanding your current state.

[Calls: initialize_protocol_testing_agent with analysis_mode="interactive"]
```

**Enhanced Response**: The system now provides:
- **Current State Summary**: Testing phase, test count, coverage estimate, identified patterns
- **Contextual Workflow Options**: Six specialized workflows based on your project maturity
- **Effort Estimates**: Realistic timelines (1-4 weeks) based on current state
- **Next Steps**: Clear guidance tailored to your specific situation

### Step 2: Choose Context-Appropriate Workflow

Based on your project analysis, you'll receive workflow options like:

#### For New Projects (No Tests)
```json
{
  "create_foundational_suite": {
    "title": "Create Foundational Test Suite",
    "phases": 3,
    "effort": "1-2 weeks",
    "focus": "Establishing testing infrastructure from scratch"
  }
}
```

#### For Basic Tests (< 10 tests)
```json
{
  "expand_test_coverage": {
    "title": "Expand Test Coverage & Quality", 
    "phases": 3,
    "effort": "1 week",
    "focus": "Building on existing tests to achieve comprehensive coverage"
  }
}
```

#### For Solid Foundations (Good Coverage)
```json
{
  "enhance_security_testing": {
    "title": "Advanced Security & Integration Testing",
    "phases": 4, 
    "effort": "1-2 weeks",
    "focus": "Adding sophisticated security testing and integration scenarios"
  }
}
```

#### For DeFi Protocols
```json
{
  "defi_security_testing": {
    "title": "DeFi Protocol Security Testing",
    "phases": 4,
    "effort": "2-3 weeks", 
    "focus": "Economic attacks and DeFi-specific vulnerabilities"
  }
}
```

### Step 3: Execute Contextual Workflow

**Tool**: `execute_testing_workflow`

```
USER: Let's go with the "enhance_security_testing" workflow since we have good basic coverage but need security focus.

ASSISTANT: Perfect choice! I can see you have solid test foundations. Let me create a security-focused workflow that builds on your existing 45 tests and 78% coverage.

[Calls: execute_testing_workflow with workflow_type="enhance_security_testing", objectives="Add comprehensive security testing for DeFi protocol", scope="comprehensive"]
```

**Enhanced Workflow Planning**: The system now analyzes your current context and provides:

**Current Context Integration**:
```json
{
  "current_context": {
    "testing_phase": "intermediate", 
    "security_level": "basic",
    "test_count": 45,
    "coverage_pct": 78.5,
    "has_security_tests": true,
    "contract_types": ["defi", "governance"]
  }
}
```

**Adaptive Phases**: Instead of generic phases, you get contextual phases that build on your work:

**Phase 1: Security Assessment & Gap Analysis**
- Audit existing security tests for completeness
- Identify missing attack vector coverage
- Assess contract risk patterns and vulnerabilities  
- Map security requirements to contract types

**Phase 2: Vulnerability Testing Implementation**
- Add access control and privilege escalation tests
- Implement reentrancy attack simulations
- Create oracle manipulation test scenarios
- Add flash loan attack resistance testing

**Phase 3: Advanced Security Testing**
- Implement property-based security testing
- Add invariant tests for critical security properties
- Create fuzz tests for input validation
- Add economic attack scenario testing

## Advanced Features

### Real Coverage Analysis

**Tool**: `analyze_current_test_coverage`

The MCP now parses actual `forge coverage` output instead of providing generic analysis:

```bash
# The MCP runs this internally:
forge test --coverage
forge coverage --report summary

# Then provides contextual analysis:
```

**Before (Generic)**: "Very poor coverage. Comprehensive testing strategy required."
**After (Context-Aware)**: "Very good coverage (92%)! Add edge cases, security tests, and integration scenarios to reach production standards."

**Enhanced Coverage Insights**:
- **File-by-file breakdown** from actual Foundry output
- **Contextual recommendations** based on testing phase
- **Gap identification** with specific uncovered areas
- **Priority-based improvement suggestions**

### AI Quality Assurance

**Tool**: `analyze_project_context` (with AI failure detection)

The system now detects common AI-generated test failures:

```
USER: Can you check if our AI-generated tests have any quality issues?

ASSISTANT: I'll analyze your tests for common AI failure patterns that could provide false confidence.

[Calls: analyze_project_context with include_ai_failure_detection=true]
```

**AI Failure Detection Results**:
```json
{
  "ai_failure_analysis": {
    "status": "moderate_issues",
    "failures_detected": [
      {
        "type": "circular_logic",
        "file": "test/TokenTest.t.sol", 
        "line": 45,
        "description": "Test validates contract against its own implementation",
        "severity": "high",
        "remediation": "Test against expected behavior, not implementation"
      },
      {
        "type": "mock_cheating",
        "file": "test/OracleTest.t.sol",
        "line": 67,
        "description": "Mock always returns expected value without validation",
        "severity": "medium", 
        "remediation": "Add realistic mock behavior and edge cases"
      }
    ]
  }
}
```

### Professional Security Integration

The MCP now integrates methodologies from leading security audit firms:

**Trail of Bits Framework**:
- Access control maturity assessment (Level 1-4)
- Architectural risk evaluation
- Invariant-driven development

**OpenZeppelin Standards**:
- Security pattern validation
- Comprehensive checklists
- Quality measures compliance

**ConsenSys Practices**: 
- Vulnerability pattern analysis
- Threat modeling approaches
- Economic attack scenarios

### DeFi-Specific Security Testing

For DeFi protocols, the system provides specialized security testing:

**Economic Attack Scenarios**:
```solidity
// Flash loan attack simulation
function testFlashLoanAttack() public {
    // Setup: Deploy vulnerable contract
    // Execute: Simulate flash loan attack
    // Verify: Attack is prevented/mitigated
}

// Oracle manipulation testing  
function testOracleManipulation() public {
    // Setup: Mock oracle with manipulated price
    // Execute: Attempt price manipulation exploit
    // Verify: System responds appropriately
}

// MEV protection validation
function testMEVProtection() public {
    // Setup: Simulate MEV extraction attempt
    // Execute: Front-running/sandwich attack
    // Verify: Protection mechanisms work
}
```

## Workflow Examples

### Example 1: New DeFi Project

**Starting Point**: Empty project with contracts but no tests

```
1. initialize_protocol_testing_agent()
   → Detects: No tests, DeFi contracts, high risk
   → Recommends: "create_foundational_suite" workflow

2. execute_testing_workflow("create_foundational_suite", "Create comprehensive test suite for AMM protocol")
   → Phase 1: Contract analysis and risk assessment
   → Phase 2: Test architecture design
   → Phase 3: Core test implementation

3. analyze_current_test_coverage()
   → Progress tracking and gap identification
```

### Example 2: Existing Project Enhancement

**Starting Point**: Project with 25 tests, 65% coverage, basic security

```
1. initialize_protocol_testing_agent()
   → Detects: Intermediate phase, needs security focus
   → Recommends: "enhance_security_testing" workflow

2. analyze_project_context(include_ai_failure_detection=true)
   → Identifies: AI test quality issues, security gaps
   → Provides: Prioritized improvement plan

3. execute_testing_workflow("enhance_security_testing", "Add comprehensive security testing")
   → Builds on existing 25 tests
   → Focuses on security gaps and attack vectors
   → Progressive enhancement rather than restart
```

### Example 3: Production Preparation

**Starting Point**: Mature project preparing for audit

```
1. initialize_protocol_testing_agent()
   → Detects: Advanced phase, audit preparation needed
   → Recommends: "comprehensive_audit_prep" workflow

2. execute_testing_workflow("comprehensive_audit_prep", "Prepare for security audit")
   → Phase 1: Comprehensive coverage review (95%+ target)
   → Phase 2: Security testing validation
   → Phase 3: Documentation and evidence preparation
   → Phase 4: Formal verification preparation
   → Phase 5: Audit documentation packages
```

## Troubleshooting and Validation

### Project Validation

**Tool**: `validate_current_project`

If you encounter issues, start with project validation:

```
USER: The MCP tools aren't finding my contracts properly.

ASSISTANT: Let me validate your project setup and diagnose any issues.

[Calls: validate_current_project()]
```

**Enhanced Validation**:
- **Foundry Installation Check**: Versions and accessibility
- **Project Structure Analysis**: foundry.toml, src/, test/ validation  
- **Environment Diagnostics**: Path resolution and permissions
- **Setup Recommendations**: Specific fixes for identified issues

### Directory Detection Debugging  

**Tool**: `debug_directory_detection`

For advanced troubleshooting when the MCP seems to be working in the wrong directory:

```
USER: The MCP thinks I'm in my home directory but I'm in my project folder.

ASSISTANT: Let me debug the directory detection and provide specific configuration fixes.

[Calls: debug_directory_detection()]
```

**Enhanced Debugging**:
- **Environment Variable Analysis**: MCP_CLIENT_CWD, MCP_PROJECT_PATH inspection
- **Path Resolution Debugging**: Shows resolved vs actual paths
- **Client Configuration Examples**: Specific MCP client setup guidance
- **Troubleshooting Instructions**: Step-by-step resolution guide

## Best Practices

### Context-Aware Development

1. **Always Start with Analysis**: Use `initialize_protocol_testing_agent` to understand current state
2. **Build Progressively**: Choose workflows that build on existing work
3. **Monitor Quality**: Use AI failure detection to catch test quality issues
4. **Use Real Data**: Leverage actual coverage analysis instead of estimates
5. **Apply Security Standards**: Follow integrated professional methodologies

### Professional Security Integration

1. **Risk-Based Testing**: Focus on high-risk contracts and functions first
2. **Attack Vector Coverage**: Include DeFi-specific economic attacks
3. **Property Validation**: Use invariant testing for critical system properties
4. **Audit Preparation**: Build toward professional audit standards from the start

### Tool Integration Best Practices

1. **Foundry Alignment**: Ensure recommendations align with actual `forge` capabilities
2. **Coverage Validation**: Use real coverage reports for decision making
3. **Progressive Enhancement**: Build on existing infrastructure rather than replacing
4. **Quality Assurance**: Regular AI failure detection to maintain test quality

## Success Metrics

### Context Awareness Success

- **Accurate State Detection**: MCP correctly identifies your testing phase
- **Relevant Recommendations**: Workflow suggestions match your actual needs
- **Progressive Guidance**: Builds on existing work rather than restarting
- **Appropriate Effort Estimates**: Realistic timelines based on current state

### Quality Assurance Success

- **Coverage Accuracy**: Analysis matches actual `forge coverage` output
- **AI Quality Detection**: Identifies and helps fix AI-generated test issues  
- **Security Integration**: Professional audit methodologies applied consistently
- **Tool Integration**: Seamless integration with existing Foundry workflows

### Professional Standards Achievement

- **Security Methodology Compliance**: Tests follow Trail of Bits/OpenZeppelin/ConsenSys standards
- **Audit Readiness**: Test suites meet professional audit preparation requirements
- **DeFi Security Coverage**: Economic attack scenarios and vulnerability testing
- **Production Standards**: High-quality, maintainable, and comprehensive test suites

The Foundry Testing MCP v2.0 transforms smart contract testing from generic AI guidance into professional-grade consulting that understands your project, builds on your work, and applies industry-leading security methodologies throughout your development process.