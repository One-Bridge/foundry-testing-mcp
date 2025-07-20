# Foundry Testing MCP - User Implementation Walkthrough

## Quick Start Guide

This walkthrough demonstrates how to use the Foundry Testing MCP to assist with smart contract testing for Solidity projects. The system provides project analysis, testing workflow guidance, and integration with Foundry tools.

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

The Foundry Testing MCP is designed to work with MCP clients like Cursor with Claude. Configure your MCP client to connect to the testing server using the provided configuration.

## Core Workflow: Project Analysis and Testing Guidance

### Step 1: Initialize Project Analysis

Start with the main entry point tool to analyze your current project state.

**Tool**: `initialize_protocol_testing_agent`

**Parameters**:
- `analysis_mode`: "interactive" (guided) or "direct" (immediate analysis)
- `project_path`: Optional path (auto-detects if not provided)

**Example Usage**:
```
USER: I want to analyze my DeFi protocol for testing. We have some basic tests but need guidance on improving coverage and security testing.

AI Assistant: I'll analyze your current project state and recommend appropriate testing approaches.

[Tool Call: initialize_protocol_testing_agent(analysis_mode="interactive")]
```

**Expected Response**: The system provides:
- Project structure analysis
- Testing maturity classification (none/basic/intermediate/advanced/production)
- Security level assessment
- Available workflow recommendations
- Session ID for continued work

### Step 2: Detailed Project Assessment (Optional)

For more comprehensive analysis including AI failure detection.

**Tool**: `analyze_project_context`

**Parameters**:
- `include_ai_failure_detection`: true (recommended for AI-generated tests)
- `generate_improvement_plan`: true (recommended)
- `project_path`: Optional path

**Example Usage**:
```
USER: Can you analyze our existing tests for quality issues and provide a detailed improvement plan?

AI Assistant: I'll perform a comprehensive analysis including AI failure detection.

[Tool Call: analyze_project_context(include_ai_failure_detection=true, generate_improvement_plan=true)]
```

**Expected Response**:
- Testing phase and security level analysis
- AI failure detection report (if enabled)
- Contract risk scoring
- Prioritized improvement plan

### Step 3: Execute Testing Workflow

Implement structured testing improvements based on analysis results.

**Tool**: `execute_testing_workflow`

**Parameters**:
- `workflow_type`: Selected based on project state
- `objectives`: Specific testing goals
- `scope`: "unit", "integration", "comprehensive", "security"
- `session_id`: From initialization step
- `project_path`: Optional path

**Available Workflow Types**:
- `create_foundational_suite`: For new projects with minimal testing
- `enhance_coverage`: Build on existing tests to improve coverage
- `security_focus`: Add comprehensive security testing
- `integration_testing`: Multi-contract interaction testing

**Example Usage**:
```
USER: Let's execute the security_focus workflow to add comprehensive security testing to our existing test suite.

AI Assistant: I'll create a structured security testing workflow based on your project's current state.

[Tool Call: execute_testing_workflow(workflow_type="security_focus", objectives="Add comprehensive security testing for DeFi protocol", scope="security", session_id="<session_id>")]
```

## Analysis and Monitoring Tools

### Coverage Analysis

**Tool**: `analyze_current_test_coverage`

**Parameters**:
- `target_coverage`: Target percentage (default 90)
- `include_branches`: Include branch coverage analysis

**Usage**: Get current coverage metrics and gap identification

**Note**: This tool integrates with Foundry's `forge coverage` command. Some environments may experience subprocess execution issues.

### Project Validation

**Tool**: `validate_current_directory`

**Usage**: Verify project setup and Foundry configuration
**When to Use**: When encountering setup or configuration issues

### Troubleshooting

**Tool**: `debug_directory_detection`

**Usage**: Diagnose directory detection and path issues
**When to Use**: When tools report wrong directory or cannot find project files

### Project Discovery

**Tool**: `discover_foundry_projects`

**Usage**: Find available Foundry projects in directory structure
**When to Use**: When working with multiple projects or auto-detection fails

## Using MCP Resources

The system provides several resources accessible through MCP clients:

### Testing Patterns
- **Resource**: `testing://foundry-patterns`
- **Content**: Best practices, file organization, naming conventions with code examples

### Security Patterns
- **Resource**: `testing://security-patterns`
- **Content**: Vulnerability test cases and security testing approaches

### Test Templates
- **Resource**: `testing://templates/{template_type}`
- **Available Types**: unit, integration, invariant, security, fork
- **Content**: Template code with placeholders for customization

### Template Catalog
- **Resource**: `testing://templates`
- **Content**: Overview of all available templates with descriptions

### Documentation
- **Resource**: `testing://documentation`
- **Content**: Testing methodologies and comprehensive guides

## Using MCP Prompts

The system provides structured prompts for testing guidance:

### Contract Analysis
- **Prompt**: `analyze-contract-for-testing`
- **Parameters**: `contract_path`
- **Usage**: Get analysis framework for specific contracts

### Test Strategy Design
- **Prompt**: `design-test-strategy`
- **Parameters**: `contracts`, `risk_profile`, `coverage_target`
- **Usage**: Develop comprehensive testing strategies

### Coverage Review
- **Prompt**: `review-test-coverage`
- **Usage**: Systematic coverage review and improvement guidance

### Security Testing
- **Prompt**: `design-security-tests`
- **Parameters**: `contract_types`, `threat_model`
- **Usage**: Design security-focused testing approaches

### Performance Optimization
- **Prompt**: `optimize-test-performance`
- **Parameters**: `performance_issues`, `optimization_goals`
- **Usage**: Optimize test suite performance and efficiency

## Example Workflows

### New Project (No Tests)

1. **Initialize**: `initialize_protocol_testing_agent()`
   - System detects no tests, recommends foundational workflow
   
2. **Execute**: `execute_testing_workflow(workflow_type="create_foundational_suite")`
   - Provides step-by-step guidance for test suite creation
   
3. **Monitor**: `analyze_current_test_coverage()`
   - Track progress and identify gaps

### Existing Project Enhancement

1. **Initialize**: `initialize_protocol_testing_agent()`
   - System analyzes existing tests and identifies maturity level
   
2. **Deep Analysis**: `analyze_project_context(include_ai_failure_detection=true)`
   - Identifies test quality issues and improvement opportunities
   
3. **Execute**: `execute_testing_workflow(workflow_type="enhance_coverage")`
   - Builds on existing work with targeted improvements

### Security Testing Focus

1. **Initialize**: `initialize_protocol_testing_agent()`
   - System identifies security testing gaps
   
2. **Execute**: `execute_testing_workflow(workflow_type="security_focus")`
   - Comprehensive security testing implementation
   
3. **Validate**: Use security templates and patterns for implementation

## Troubleshooting Common Issues

### Directory Detection Problems

**Symptoms**: Tools report wrong directory or cannot find project files

**Solutions**:
1. Use `debug_directory_detection()` for detailed analysis
2. Check MCP client configuration for working directory settings
3. Verify environment variables (MCP_CLIENT_CWD)
4. Ensure proper project structure (foundry.toml, src/, test/)

### Coverage Analysis Issues

**Symptoms**: Coverage analysis fails or returns errors

**Solutions**:
1. Verify Foundry installation and project compilation
2. Check test execution with `forge test`
3. Try running `forge coverage` manually to identify issues
4. Review project validation with `validate_current_directory()`

### Tool Routing Issues

**Symptoms**: Tools not found or naming convention errors

**Solutions**:
1. Check MCP client configuration
2. Verify server startup and component registration
3. Use development runner (`run.py`) for detailed logging
4. Check server logs for tool registration status

## Template Usage Instructions

### Accessing Templates

1. Use `testing://templates` resource to see available templates
2. Request specific template with `testing://templates/{type}`
3. Replace placeholder values in template code
4. Follow provided usage instructions

### Template Types

- **Unit Tests**: Basic function-level testing with access control and error conditions
- **Integration Tests**: Multi-contract interaction testing
- **Invariant Tests**: Property-based testing using Handler pattern
- **Security Tests**: Attack scenario simulation and defense validation
- **Fork Tests**: Mainnet state integration testing

### Placeholder System

Templates use `{{PLACEHOLDER}}` syntax for dynamic values:
- `{{CONTRACT_NAME}}`: Replace with your contract name
- `{{OWNER_ACCOUNT}}`: Replace with owner address variable
- `{{USER_ACCOUNT}}`: Replace with user address variable
- Additional placeholders specific to each template type

## Best Practices

### Project Organization

1. Follow recommended file structure from `testing://foundry-patterns`
2. Use descriptive test names following the pattern: `test_function_whenCondition_shouldResult`
3. Organize tests by functionality and type (unit, integration, security)
4. Maintain separate files for different test categories

### Tool Usage

1. Always start with `initialize_protocol_testing_agent`
2. Use `validate_current_directory` when encountering setup issues
3. Monitor progress with `analyze_current_test_coverage`
4. Leverage templates and patterns for consistent implementation

### Quality Assurance

1. Enable AI failure detection for quality validation
2. Focus on meaningful assertions that can actually fail
3. Avoid circular logic in test validation
4. Use realistic mock implementations

## Limitations and Known Issues

### Current Limitations

- Directory detection may fail in some MCP client configurations
- Coverage analysis has subprocess execution issues in some environments
- Project context detection can encounter null pointer exceptions
- Some tool routing issues with MCP client naming conventions

### Development Status

The system is in active development with ongoing improvements to address real-world usage issues. Core functionality is implemented and working, with continued refinement based on user feedback.

### Getting Help

1. Use troubleshooting tools for common issues
2. Check server logs for detailed error information
3. Verify Foundry installation and project setup
4. Review MCP client configuration for proper integration

This walkthrough provides practical guidance for using the Foundry Testing MCP system effectively, with awareness of current capabilities and limitations.