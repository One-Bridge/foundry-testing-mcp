# MCP Tool Guidance - Foundry Testing MCP v2.0

## Overview

This document provides comprehensive guidance for using the Foundry Testing MCP v2.0 tools effectively. The system includes seven primary tools designed to provide context-aware testing assistance for smart contract development.

## Tool Overview and Relationships

### Primary Workflow Tools

**initialize_protocol_testing_agent** (Start Here)
- **Purpose**: Analyzes current project and recommends appropriate workflow
- **When to Use**: Beginning any testing work, first interaction with project
- **Output**: Project analysis and workflow recommendations

**analyze_project_context** (Deep Analysis)
- **Purpose**: Comprehensive project analysis with AI failure detection
- **When to Use**: Need detailed assessment of existing tests or quality issues
- **Output**: Testing maturity analysis, AI failure report, improvement plan

**execute_testing_workflow** (Implementation)
- **Purpose**: Structured implementation of testing improvements
- **When to Use**: Ready to implement comprehensive testing strategy
- **Output**: Phase-by-phase implementation plan with specific actions

### Supporting Tools

**analyze_current_test_coverage** (Quick Assessment)
- **Purpose**: Fast coverage analysis and gap identification
- **When to Use**: Need current coverage metrics or progress monitoring
- **Output**: Coverage percentages, gap analysis, specific recommendations

**validate_current_project** (Setup Verification)
- **Purpose**: Validates project setup and environment
- **When to Use**: Getting setup errors or troubleshooting project issues
- **Output**: Project validation status, setup recommendations

**debug_directory_detection** (Advanced Troubleshooting)
- **Purpose**: Diagnoses directory and path detection issues
- **When to Use**: Tools report wrong directory or can't find project files
- **Output**: Directory detection analysis, configuration guidance

**get_server_info** (Server Information)
- **Purpose**: Provides comprehensive information about server capabilities and usage guidance
- **When to Use**: First time using the MCP server or need to understand available tools
- **Output**: Complete tool catalog, workflow relationships, quick start instructions

## Recommended Workflows

### Workflow 1: New Project Testing

**Scenario**: Starting testing on a new smart contract project

```
1. initialize_protocol_testing_agent
   → Analyzes project structure
   → Recommends "create_foundational_suite" workflow
   
2. execute_testing_workflow
   → workflow_type: "create_foundational_suite"
   → objectives: "Create comprehensive test suite"
   → scope: "comprehensive"
   
3. analyze_current_test_coverage
   → Monitor progress during implementation
   → Validate coverage targets are met
```

**Expected Timeline**: 1-2 weeks for comprehensive implementation

### Workflow 2: Enhance Existing Tests

**Scenario**: Improving existing test suite quality and coverage

```
1. initialize_protocol_testing_agent
   → Analyzes existing tests and contracts
   → Recommends "expand_test_coverage" or "enhance_security_testing" workflow
   
2. analyze_project_context
   → include_ai_failure_detection: true
   → generate_improvement_plan: true
   → Provides detailed analysis and prioritized improvements
   
3. execute_testing_workflow
   → workflow_type: "expand_test_coverage" or "enhance_security_testing"
   → objectives: Based on analysis results
   → scope: "comprehensive"
   
4. analyze_current_test_coverage
   → Validate improvements achieved target goals
```

**Expected Timeline**: 3-5 days for analysis and planning, 1-2 weeks for implementation

### Workflow 3: Quick Coverage Check

**Scenario**: Need immediate coverage assessment

```
1. analyze_current_test_coverage
   → target_coverage: 90 (or appropriate target)
   → include_branches: true
   → Provides immediate coverage analysis
```

**Expected Timeline**: Immediate results

### Workflow 4: Troubleshooting Setup Issues

**Scenario**: Tools reporting errors or wrong directory

```
1. validate_current_project
   → Checks project structure and Foundry setup
   → If validation fails, follow setup recommendations
   
2. debug_directory_detection (if directory issues persist)
   → Analyzes directory detection logic
   → Provides specific configuration fixes
   
3. Retry primary workflow after fixing issues
```

**Expected Timeline**: 15-30 minutes to resolve common issues

## Tool Usage Patterns

### Pattern 1: Systematic Development

**Use Case**: Methodical approach to comprehensive testing

**Tools Sequence**:
1. `initialize_protocol_testing_agent` - Understand current state
2. `analyze_project_context` - Deep analysis if needed
3. `execute_testing_workflow` - Implement improvements
4. `analyze_current_test_coverage` - Validate results

**Benefits**:
- Comprehensive understanding of project needs
- Structured implementation approach
- Built-in quality validation

### Pattern 2: Iterative Improvement

**Use Case**: Continuous improvement of testing quality

**Tools Sequence**:
1. `analyze_current_test_coverage` - Assess current state
2. `analyze_project_context` - Identify specific issues
3. `execute_testing_workflow` - Address priority issues
4. Repeat cycle for continuous improvement

**Benefits**:
- Focus on highest-impact improvements
- Manageable incremental progress
- Regular validation of improvements

### Pattern 3: Quality Assurance Focus

**Use Case**: Emphasis on detecting and fixing test quality issues

**Tools Sequence**:
1. `analyze_project_context` with AI failure detection enabled
2. Review AI failure report and prioritize fixes
3. `execute_testing_workflow` focusing on quality improvements
4. `analyze_current_test_coverage` to validate fixes

**Benefits**:
- Identifies hidden quality issues
- Prevents false confidence from flawed tests
- Ensures test reliability

## Common Use Cases and Solutions

### Use Case 1: "I need to test my DeFi protocol before audit"

**Recommended Approach**:
```
1. initialize_protocol_testing_agent
   → Will analyze protocol complexity and recommend comprehensive approach

2. analyze_project_context
   → include_ai_failure_detection: true
   → Identifies security testing gaps and quality issues

3. execute_testing_workflow
   → workflow_type: "comprehensive"
   → objectives: "Achieve audit-ready testing with security focus"
   → scope: "comprehensive"
   → Will provide security-focused implementation plan

4. analyze_current_test_coverage
   → target_coverage: 95
   → Validates audit-ready coverage levels
```

### Use Case 2: "My existing tests seem comprehensive but coverage is low"

**Recommended Approach**:
```
1. analyze_project_context
   → include_ai_failure_detection: true
   → May reveal tests with circular logic or mock issues

2. Review AI failure report for specific quality issues

3. execute_testing_workflow
   → workflow_type: "expand_test_coverage" 
   → objectives: "Fix test quality issues and improve real coverage"
   → Focus on fixing identified problems rather than adding more tests
```

### Use Case 3: "I'm getting wrong directory errors"

**Recommended Approach**:
```
1. validate_current_project
   → Check if you're in correct directory and project is properly set up

2. If validation fails:
   → Follow setup recommendations (foundry.toml, proper directory structure)

3. If directory detection issues persist:
   → debug_directory_detection
   → Follow MCP client configuration guidance

4. Retry primary workflow after fixing configuration
```

### Use Case 4: "I want to check if my current tests are good enough"

**Recommended Approach**:
```
1. analyze_current_test_coverage
   → Provides immediate coverage assessment

2. If coverage looks good but want quality assessment:
   → analyze_project_context with AI failure detection
   → May reveal hidden quality issues despite good coverage

3. If issues found:
   → execute_testing_workflow to address specific problems
```

## Error Handling and Troubleshooting

### Common Error Scenarios

**"Project validation failed"**
- **Cause**: Not in proper Foundry project directory or missing foundry.toml
- **Solution**: Navigate to project root, run `forge init --force` if needed
- **Tool**: Use `validate_current_project` for specific guidance

**"Directory detection may be incorrect"**
- **Cause**: MCP client and server working in different directories
- **Solution**: Configure MCP client to set working directory properly
- **Tool**: Use `debug_directory_detection` for configuration guidance

**"No tests found for coverage analysis"**
- **Cause**: No test files exist or tests can't run with `forge test`
- **Solution**: Create basic tests first, verify tests run manually
- **Tool**: Use `initialize_protocol_testing_agent` to start test creation

**"Foundry not found"**
- **Cause**: Foundry not installed or not in PATH
- **Solution**: Install Foundry and ensure commands are accessible
- **Tool**: Use `validate_current_project` to verify installation

### Recovery Strategies

**When Tools Report Unexpected Results**:
1. Verify you're in the correct project directory
2. Check that foundry.toml exists and is properly configured
3. Ensure Foundry commands work manually (`forge test`, `forge build`)
4. Review MCP client configuration for directory settings

**When Analysis Seems Inaccurate**:
1. Check that all contract files are in expected locations (src/ directory)
2. Verify test files follow proper naming conventions (.t.sol extension)
3. Ensure project structure follows Foundry conventions
4. Consider if project has unusual structure that needs explanation

## Best Practices

### Effective Tool Usage

**Start with Context**:
- Always begin with `initialize_protocol_testing_agent` for new work
- Understand current project state before making changes
- Use analysis results to inform implementation decisions

**Focus on Quality**:
- Enable AI failure detection for existing projects
- Address quality issues before adding more tests
- Validate improvements with coverage analysis

**Systematic Approach**:
- Follow recommended workflows rather than jumping between tools
- Complete phases before moving to next steps
- Document decisions and rationale for future reference

### Project Organization

**Before Using Tools**:
- Ensure proper Foundry project structure
- Verify all contracts are in src/ directory
- Confirm existing tests follow naming conventions
- Check that basic Foundry commands work

**During Implementation**:
- Follow generated implementation plans systematically
- Test changes incrementally
- Monitor coverage and quality metrics regularly
- Document new test scenarios and rationale

**After Implementation**:
- Validate final results meet target criteria
- Document testing strategy and maintenance procedures
- Set up regular coverage monitoring
- Plan for continuous improvement

### Integration with Development Workflow

**Individual Development**:
- Use tools at key development milestones
- Integrate coverage checking into regular workflow
- Address quality issues as they're identified
- Maintain testing documentation

**Team Development**:
- Establish consistent testing standards
- Share analysis results and improvement plans
- Coordinate testing efforts across team members
- Maintain shared testing resources and templates

**CI/CD Integration**:
- Automate coverage analysis in build pipelines
- Include quality validation in automated testing
- Generate reports for team visibility
- Enforce minimum quality standards before deployment

## Success Metrics

### Coverage Metrics

**Target Coverage Levels**:
- **Basic Projects**: 80%+ line coverage
- **Production Projects**: 90%+ line coverage, 85%+ branch coverage
- **Security-Critical Projects**: 95%+ line coverage with comprehensive security testing

### Quality Metrics

**AI Failure Detection**:
- Zero detected circular logic issues
- No mock inconsistencies identified
- Comprehensive edge case coverage
- All security scenarios validated

### Process Metrics

**Implementation Efficiency**:
- Reduced time to achieve target coverage
- Fewer iterations needed for quality validation
- Faster identification and resolution of issues
- Improved audit preparation time

**Team Productivity**:
- Consistent testing approaches across team
- Reduced debugging time for test issues
- Better coordination of testing efforts
- Improved knowledge sharing and documentation

This guidance provides a foundation for effective use of the Foundry Testing MCP v2.0. The tool's context-aware approach and quality assurance features make it particularly valuable for teams developing production smart contracts requiring comprehensive testing and security validation. 