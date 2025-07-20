# MCP Tool Guidance - Foundry Testing MCP

## Overview

This document provides practical guidance for using the Foundry Testing MCP tools effectively. The system includes seven MCP tools that provide testing assistance for smart contract development using the Foundry toolchain.

## Available Tools and Their Purposes

### Primary Workflow Tools

**initialize_protocol_testing_agent** (Start Here)
- **Purpose**: Analyzes current project structure and recommends testing approaches
- **When to Use**: Beginning testing work on any Foundry project
- **Parameters**: analysis_mode (interactive/direct), project_path (optional)
- **Output**: Project analysis and workflow recommendations
- **Note**: Uses project analysis to understand current testing state

**analyze_project_context** (Deep Analysis)
- **Purpose**: Detailed project assessment with AI failure detection
- **When to Use**: Need comprehensive analysis of existing test quality
- **Parameters**: include_ai_failure_detection (bool), generate_improvement_plan (bool), project_path (optional)
- **Output**: Testing maturity analysis, AI failure report, improvement plan
- **Note**: Can detect common issues in AI-generated tests

**execute_testing_workflow** (Implementation)
- **Purpose**: Provides structured implementation guidance through phases
- **When to Use**: Ready to implement testing improvements systematically
- **Parameters**: workflow_type, objectives, scope, session_id, project_path
- **Output**: Phase-by-phase implementation plan with specific actions
- **Note**: Builds on results from analysis tools

### Supporting Tools

**analyze_current_test_coverage** (Coverage Assessment)
- **Purpose**: Analyzes test coverage using Foundry's coverage tools
- **When to Use**: Need current coverage metrics or progress monitoring
- **Parameters**: target_coverage (default 90), include_branches (bool)
- **Output**: Coverage percentages, gap analysis, recommendations
- **Note**: Integrates with `forge coverage` but may have subprocess issues in some environments

**validate_current_directory** (Setup Verification)
- **Purpose**: Validates project setup and Foundry configuration
- **When to Use**: Troubleshooting setup issues or environment problems
- **Parameters**: None
- **Output**: Project validation status, setup recommendations
- **Note**: Checks for foundry.toml, proper directory structure, and Foundry installation

**debug_directory_detection** (Advanced Troubleshooting)
- **Purpose**: Diagnoses directory detection and path issues
- **When to Use**: Tools report wrong directory or cannot find project files
- **Parameters**: None
- **Output**: Directory detection analysis, configuration guidance
- **Note**: Helps resolve MCP client/server directory mismatches

**discover_foundry_projects** (Project Discovery)
- **Purpose**: Finds available Foundry projects in directory structure
- **When to Use**: Working with multiple projects or when auto-detection fails
- **Parameters**: None
- **Output**: List of discovered projects with metadata
- **Note**: Helps locate projects when path detection isn't working

## Available Resources

The system provides several MCP resources for templates and documentation:

### Testing Templates
- **Resource**: `testing://templates/{template_type}`
- **Available Types**: unit, integration, invariant, security, fork, helper
- **Content**: Template code with placeholder values for customization
- **Usage**: Access specific template by type, replace placeholders with your values

### Template Catalog
- **Resource**: `testing://templates`
- **Content**: Overview of all available templates with descriptions and use cases
- **Usage**: Browse available templates to understand options

### Testing Patterns
- **Resource**: `testing://foundry-patterns`
- **Content**: Best practices, file organization, naming conventions
- **Usage**: Reference for structuring test projects and following conventions

### Security Patterns
- **Resource**: `testing://security-patterns`
- **Content**: Security testing approaches and vulnerability test cases
- **Usage**: Guidance for implementing security-focused testing

### Documentation
- **Resource**: `testing://documentation`
- **Content**: Testing methodologies and comprehensive guides
- **Usage**: Reference documentation for testing strategies

## Available Prompts

The system provides structured prompts for testing guidance:

- **analyze-contract-for-testing**: Contract analysis framework
- **design-test-strategy**: Testing strategy development
- **review-test-coverage**: Coverage review and improvement
- **design-security-tests**: Security testing approaches  
- **optimize-test-performance**: Performance optimization guidance

## Recommended Workflows

### Workflow 1: New Project Testing

**Scenario**: Starting testing on a new smart contract project

```
1. initialize_protocol_testing_agent()
   → Analyzes project structure (contracts but no tests)
   → Recommends foundational testing approach
   
2. execute_testing_workflow()
   → workflow_type: "create_foundational_suite" 
   → objectives: "Create comprehensive test suite"
   → scope: "comprehensive"
   
3. analyze_current_test_coverage()
   → Monitor progress during implementation
   → Validate coverage targets are being met
```

**Expected Timeline**: 1-2 weeks depending on project complexity

### Workflow 2: Enhance Existing Tests

**Scenario**: Improving existing test suite quality and coverage

```
1. initialize_protocol_testing_agent()
   → Analyzes existing tests and identifies current maturity level
   → Recommends enhancement approach based on current state
   
2. analyze_project_context()
   → include_ai_failure_detection: true
   → generate_improvement_plan: true
   → Provides detailed analysis of current test quality
   
3. execute_testing_workflow()
   → workflow_type: "expand_test_coverage" or based on analysis
   → objectives: Based on specific gaps identified
   → scope: "comprehensive"
   
4. analyze_current_test_coverage()
   → Validate improvements meet target goals
```

**Expected Timeline**: 3-5 days for analysis, 1-2 weeks for implementation

### Workflow 3: Quick Coverage Assessment

**Scenario**: Need immediate coverage information

```
1. analyze_current_test_coverage()
   → target_coverage: 90 (or appropriate target)
   → include_branches: true
   → Immediate coverage analysis with recommendations
```

**Expected Timeline**: Immediate results (if coverage tools work properly)

### Workflow 4: Troubleshooting Setup Issues

**Scenario**: Tools reporting errors or configuration problems

```
1. validate_current_directory()
   → Checks project structure and Foundry setup
   → Provides specific setup recommendations if issues found
   
2. debug_directory_detection() (if directory issues persist)
   → Analyzes directory detection and environment variables
   → Provides MCP client configuration guidance
   
3. Retry primary workflow after resolving issues
```

**Expected Timeline**: 15-30 minutes for common setup issues

## Common Use Cases and Solutions

### Use Case 1: "I need comprehensive testing for my DeFi protocol"

**Recommended Approach**:
```
1. initialize_protocol_testing_agent()
   → Analyzes protocol complexity and current state
   → Recommends appropriate testing approach

2. analyze_project_context() 
   → include_ai_failure_detection: true
   → Identifies any existing test quality issues

3. execute_testing_workflow()
   → workflow_type: "comprehensive"
   → objectives: "Create comprehensive test suite with security focus"
   → scope: "comprehensive"
   → Provides structured implementation plan

4. Use helper template for common utilities:
   → testing://templates/helper
   → Create test/utils/TestHelper.sol for reusable functions

5. analyze_current_test_coverage()
   → target_coverage: 90+
   → Monitor progress and validate comprehensive coverage
```

### Use Case 2: "My tests have good coverage but something seems wrong"

**Recommended Approach**:
```
1. analyze_project_context()
   → include_ai_failure_detection: true
   → May reveal quality issues like circular logic or mock problems

2. Review AI failure report for specific issues and fixes

3. execute_testing_workflow()
   → workflow_type: "enhance_quality" 
   → objectives: "Fix identified test quality issues"
   → Focus on improving test effectiveness rather than adding more tests
```

### Use Case 3: "Tools aren't working properly"

**Recommended Approach**:
```
1. validate_current_directory()
   → Check if you're in correct directory with proper Foundry project

2. If validation fails:
   → Follow specific setup recommendations
   → Ensure foundry.toml exists and forge commands work

3. If directory detection issues persist:
   → debug_directory_detection()
   → Follow MCP client configuration guidance
   → Set MCP_CLIENT_CWD environment variable if needed

4. Retry primary workflow after fixing configuration
```

## Known Issues and Limitations

### Current Limitations

**Directory Detection Issues**:
- May fail in some MCP client configurations
- Server and client may work in different directories
- **Solution**: Use `debug_directory_detection()` and configure MCP client properly

**Coverage Analysis Issues**:
- Subprocess execution problems in some environments
- May fail when `forge coverage` has issues
- **Solution**: Ensure `forge coverage` works manually first, check environment setup

**Project Context Detection**:
- Occasional null pointer exceptions during analysis
- May not detect all project patterns correctly
- **Solution**: Ensure proper project structure and try `validate_current_directory()`

**Tool Routing Issues**:
- Some MCP clients may have naming convention problems
- Tools might not be found in certain configurations
- **Solution**: Check MCP client configuration and server startup logs

### Functional Limitations

**AI Failure Detection**:
- Detects common patterns but isn't perfect
- May miss sophisticated test quality issues
- Works best with typical AI-generated test problems

**AST Analysis**:
- Uses Solidity compiler when available, falls back to regex patterns
- May not catch all complex code patterns
- Provides good analysis for typical contracts

**Coverage Integration**:
- Depends on Foundry's coverage tools working properly
- Some environments may have subprocess or parsing issues
- Best effort parsing of coverage output

## Best Practices

### Effective Tool Usage

**Start with Validation**:
- Always begin with `validate_current_directory()` if encountering issues
- Ensure basic Foundry commands work before using MCP tools
- Check that you're in the project root directory

**Use Systematic Approach**:
- Follow recommended workflows rather than jumping between tools
- Complete analysis before starting implementation
- Use session continuity features when available

**Monitor Progress**:
- Use `analyze_current_test_coverage()` regularly to track improvements
- Address quality issues identified by AI failure detection
- Validate that changes achieve intended goals

### Template Usage

**Helper Template Usage** (New Feature):
- Use `testing://templates/helper` to create `test/utils/TestHelper.sol`
- Inherit from TestHelper in your test contracts to access utility functions
- Customize placeholder values for your specific contract needs
- Includes utilities for account setup, token distribution, time manipulation, etc.

**Template Organization**:
- Save templates in appropriate directories (test/utils/ for helper)
- Replace all placeholder values with your specific implementations
- Follow the recommended file structure from `testing://foundry-patterns`

### Quality Assurance

**AI Failure Detection Usage**:
- Enable AI failure detection when analyzing existing tests
- Address identified issues before adding more tests
- Focus on meaningful assertions that can actually fail

**Coverage Validation**:
- Use realistic coverage targets (80% basic, 90% production)
- Focus on meaningful coverage rather than just hitting percentages
- Ensure tests actually validate expected behavior

## Integration with Development Workflow

### Individual Development

**During Development**:
- Use tools at key development milestones
- Run coverage analysis before major releases
- Address test quality issues as they're identified

**Project Organization**:
- Follow file structure recommendations from testing patterns
- Use consistent naming conventions for tests
- Organize tests by functionality and type

### Team Development

**Coordination**:
- Share analysis results and improvement plans
- Establish consistent testing standards
- Use helper templates for shared utility functions

**Quality Standards**:
- Set minimum coverage requirements based on project needs
- Address AI failure detection issues in code reviews
- Maintain testing documentation and rationale

## Error Recovery and Troubleshooting

### Common Error Scenarios

**"Project validation failed"**
- **Cause**: Not in Foundry project directory or missing foundry.toml
- **Solution**: Navigate to project root, run `forge init --force` if needed

**"Directory detection may be incorrect"**
- **Cause**: MCP client and server working in different directories
- **Solution**: Configure MCP client working directory, set MCP_CLIENT_CWD

**"Coverage analysis failed"**
- **Cause**: `forge coverage` not working or subprocess issues
- **Solution**: Test `forge coverage` manually, check project compilation

**"Tools not found"**
- **Cause**: MCP client configuration or server startup issues
- **Solution**: Check MCP client setup, verify server is running properly

### Recovery Strategies

**When Analysis Seems Wrong**:
1. Verify you're in the correct project directory
2. Check that basic Foundry commands work (`forge test`, `forge build`)
3. Ensure project follows standard Foundry structure
4. Use `validate_current_directory()` for specific guidance

**When Tools Report Unexpected Results**:
1. Check server logs for detailed error information
2. Verify MCP client configuration includes proper working directory
3. Try running equivalent Foundry commands manually
4. Use troubleshooting tools for specific guidance

This guidance provides realistic expectations and practical approaches for using the Foundry Testing MCP system effectively, acknowledging current limitations while maximizing the benefits of available functionality. 