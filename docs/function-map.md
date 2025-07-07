# Function Map - Foundry Testing MCP v2.0

## Overview

This document provides a comprehensive map of all functions across the Foundry Testing MCP system components. Each function is described in non-technical terms to help readers understand the complete functional surface area and how logic flows through the application.

## Core MCP Tools (User-Facing Interface)

These are the primary tools that users interact with through their AI assistants.

### initialize_protocol_testing_agent()
**Purpose**: Entry point that analyzes the current smart contract project and recommends appropriate testing workflows.
**Operation**: Scans the project directory, identifies existing contracts and tests, evaluates project maturity, and provides specific next steps based on current state.
**Logic Flow**: This is always the first function called, which then directs users to other appropriate tools.
**Current State**: ✅ Fully implemented with interactive and direct analysis modes

### analyze_project_context()
**Purpose**: Performs deep analysis of project testing quality and identifies improvement opportunities with AI failure detection.
**Operation**: Examines existing test files for quality issues, calculates risk scores for contracts, detects AI-generated test failures, and creates prioritized improvement plans.
**Logic Flow**: Called after initial analysis when detailed assessment is needed, feeds results into workflow execution.
**Current State**: ✅ Fully implemented with comprehensive AI failure detection system

### execute_testing_workflow()
**Purpose**: Implements structured testing improvements through guided, multi-phase workflows.
**Operation**: Creates detailed implementation plans with specific phases, tracks progress through testing maturity levels, and provides step-by-step guidance for comprehensive test suite development.
**Logic Flow**: Executes the main implementation work, coordinating with analysis results to deliver targeted improvements.
**Current State**: ✅ Fully implemented with 6+ workflow types (create_new_suite, evaluate_existing, comprehensive, security)

### analyze_current_test_coverage()
**Purpose**: Provides immediate assessment of test coverage percentages and identifies specific gaps.
**Operation**: Runs Foundry coverage analysis, calculates line and branch coverage metrics, compares against target goals, and recommends specific areas for improvement.
**Logic Flow**: Used for quick health checks and progress monitoring throughout development.
**Current State**: ✅ Fully implemented with real forge coverage parsing

### validate_current_project()
**Purpose**: Verifies that the project environment is properly configured for testing workflows.
**Operation**: Checks Foundry installation, validates project structure, confirms file organization, and provides setup recommendations when issues are found.
**Logic Flow**: Troubleshooting tool used when other functions report configuration problems.
**Current State**: ✅ Fully implemented with comprehensive validation checks

### debug_directory_detection()
**Purpose**: Diagnoses and resolves issues where the MCP system cannot locate project files correctly.
**Operation**: Analyzes directory detection logic, examines environment variables, identifies client-server directory mismatches, and provides specific configuration fixes.
**Logic Flow**: Advanced troubleshooting tool used when directory-related errors persist after basic validation.
**Current State**: ✅ Fully implemented with detailed debugging output

### get_server_info()
**Purpose**: Provides comprehensive information about server capabilities, tools, and usage guidance.
**Operation**: Catalogs available tools, explains workflow relationships, provides usage examples, and delivers orientation information for new users.
**Logic Flow**: Information system that helps users understand and effectively utilize the MCP capabilities.
**Current State**: ✅ Fully implemented with complete capability overview

## Foundry Integration Layer (FoundryAdapter)

These functions provide direct integration with the Foundry smart contract development toolkit.

### check_foundry_installation()
**Purpose**: Verifies that Foundry tools are properly installed and accessible on the system.
**Operation**: Attempts to execute Foundry commands, retrieves version information, and reports installation status with troubleshooting guidance.
**Logic Flow**: Called during project validation to ensure toolchain availability.
**Current State**: ✅ Implemented with version detection and error handling

### run_coverage()
**Purpose**: Executes comprehensive test coverage analysis using Foundry tools.
**Operation**: Runs `forge coverage` with appropriate flags, processes output in multiple formats (lcov, summary, json), and provides detailed coverage metrics.
**Logic Flow**: Core coverage analysis engine used by coverage tools.
**Current State**: ✅ Fully implemented with multi-format support

### run_tests()
**Purpose**: Executes smart contract tests using Foundry with optional coverage and gas reporting.
**Operation**: Constructs appropriate test commands, manages test execution, captures results and error output, and parses test outcomes for analysis.
**Logic Flow**: Core execution engine called by coverage analysis and workflow validation steps.
**Current State**: ✅ Implemented with comprehensive output parsing

### parse_project_structure()
**Purpose**: Analyzes the organization and contents of smart contract projects.
**Operation**: Scans directories for contracts, tests, and scripts, parses configuration files, identifies dependencies, and maps project architecture.
**Logic Flow**: Provides foundational project understanding used by analysis and workflow functions.
**Current State**: ✅ Implemented with detailed structure analysis

### validate_foundry_project()
**Purpose**: Comprehensive validation of Foundry project setup and configuration.
**Operation**: Checks for foundry.toml, validates directory structure, verifies dependencies, and ensures proper project organization.
**Logic Flow**: Project validation system used by multiple tools.
**Current State**: ✅ Fully implemented with detailed validation reporting

## Project Analysis Engine (ProjectAnalyzer)

These functions provide intelligent analysis of project state and testing quality.

### analyze_testing_phase()
**Purpose**: Determines current level of testing sophistication within the project.
**Operation**: Analyzes existing test patterns, counts test functions, evaluates test comprehensiveness, and classifies project into maturity levels (none/basic/intermediate/advanced/production).
**Logic Flow**: Classification system used to tailor recommendations and workflow selection.
**Current State**: ✅ Fully implemented with 5-tier maturity classification

### analyze_security_testing()
**Purpose**: Evaluates the current state of security-focused testing within the project.
**Operation**: Reviews security test patterns, checks for vulnerability coverage, assesses access control testing, and rates security testing maturity.
**Logic Flow**: Security-specific assessment that influences workflow priorities and recommendations.
**Current State**: ✅ Implemented with security pattern detection

### calculate_contract_risk_score()
**Purpose**: Assigns risk scores to individual contracts based on complexity and security patterns.
**Operation**: Analyzes contract code for complexity indicators, identifies security-sensitive patterns, evaluates external dependencies, and calculates numerical risk scores.
**Logic Flow**: Risk assessment used to prioritize testing efforts and identify high-priority contracts.
**Current State**: ✅ Implemented with comprehensive risk factors

### generate_improvement_plan()
**Purpose**: Creates actionable improvement plans based on project analysis results.
**Operation**: Synthesizes analysis results, prioritizes improvements by impact and effort, creates phased implementation plans, and provides specific recommendations.
**Logic Flow**: Planning system that translates analysis into actionable guidance.
**Current State**: ✅ Fully implemented with priority-based planning

### detect_existing_patterns()
**Purpose**: Identifies existing testing patterns and methodologies already in use.
**Operation**: Scans test files for established patterns, recognizes testing frameworks, identifies security testing approaches, and catalogs existing capabilities.
**Logic Flow**: Pattern recognition that informs adaptive workflow selection.
**Current State**: ✅ Implemented with pattern library

## AI Failure Detection System (AIFailureDetector)

These functions identify and prevent common issues with AI-generated test code.

### analyze_test_file()
**Purpose**: Examines individual test files for problematic patterns that indicate AI-generated failures.
**Operation**: Parses test code structure using AST analysis, identifies suspicious patterns, detects logical inconsistencies, and flags potential quality issues with severity ratings.
**Logic Flow**: Quality assurance component that validates test reliability before relying on coverage metrics.
**Current State**: ✅ Fully implemented with 8 failure types detection

### detect_circular_logic()
**Purpose**: Identifies tests that validate contracts against their own implementation rather than specifications.
**Operation**: Analyzes test logic patterns using regex matching, identifies self-referential validation, detects implementation dependencies, and flags tests that cannot provide meaningful validation.
**Logic Flow**: Specific failure detection that prevents false confidence in test suites.
**Current State**: ✅ Implemented with pattern matching and AST analysis

### detect_mock_cheating()
**Purpose**: Finds test mocks that always return expected values, making tests meaningless.
**Operation**: Examines mock implementations, identifies overly simplistic behaviors, detects mocks without failure scenarios, and flags unrealistic test conditions.
**Logic Flow**: Quality validation that ensures tests can actually fail when they should.
**Current State**: ✅ Implemented with mock pattern analysis

### detect_missing_edge_cases()
**Purpose**: Identifies areas where tests fail to cover boundary conditions and error scenarios.
**Operation**: Analyzes test input ranges, identifies missing boundary testing, checks for error condition coverage, and highlights gaps in edge case testing.
**Logic Flow**: Completeness validation that ensures comprehensive test coverage.
**Current State**: ✅ Implemented with edge case pattern detection

### detect_always_passing_tests()
**Purpose**: Finds tests with assertions that can never fail, providing false confidence.
**Operation**: Analyzes assertion patterns, identifies trivial assertions like assertTrue(true), detects self-comparing variables, and flags meaningless validations.
**Logic Flow**: Critical failure detection that prevents false security confidence.
**Current State**: ✅ Implemented with assertion pattern analysis

### generate_failure_report()
**Purpose**: Creates comprehensive reports of detected AI-generated test failures with remediation guidance.
**Operation**: Aggregates detected issues, prioritizes problems by severity, provides specific fix recommendations, and generates actionable improvement plans.
**Logic Flow**: Reporting system that translates technical analysis into practical improvement guidance.
**Current State**: ✅ Fully implemented with detailed reporting and recommendations

### suggest_improvements()
**Purpose**: Provides specific, actionable suggestions for fixing detected AI failures.
**Operation**: Maps failure types to improvement strategies, generates targeted recommendations, provides implementation examples, and prioritizes fixes by impact.
**Logic Flow**: Remediation system that turns problem detection into solution guidance.
**Current State**: ✅ Implemented with comprehensive suggestion engine

## Professional Testing Guidance (TestingPrompts)

These functions provide structured guidance based on professional security methodologies.

### get_professional_guidance()
**Purpose**: Provides expert-level testing guidance incorporating methodologies from leading security firms.
**Operation**: Delivers structured guidance based on Trail of Bits, OpenZeppelin, and ConsenSys methodologies, with specific focus on DeFi security patterns and economic attack scenarios.
**Logic Flow**: Professional knowledge base that elevates testing to audit-ready standards.
**Current State**: ✅ Implemented with comprehensive methodology integration

### generate_security_prompts()
**Purpose**: Creates specialized prompts for security-focused testing scenarios.
**Operation**: Generates prompts for specific attack vectors, incorporates threat modeling, guides vulnerability testing, and ensures comprehensive security validation.
**Logic Flow**: Security guidance system that applies professional audit standards to testing.
**Current State**: ✅ Implemented with security-specific prompt generation

### get_workflow_prompts()
**Purpose**: Provides contextual prompts for different workflow phases and objectives.
**Operation**: Generates phase-specific guidance, adapts prompts to project maturity, provides implementation direction, and ensures professional standards throughout.
**Logic Flow**: Workflow support system that maintains quality and professionalism.
**Current State**: ✅ Implemented with adaptive prompt generation

## Resource Management System (TestingResources)

These functions provide access to templates, documentation, and project-specific resources.

### get_test_template()
**Purpose**: Generates specific test templates for different testing scenarios and contract types.
**Operation**: Selects appropriate template based on testing needs, customizes template content for specific use cases, and provides usage instructions.
**Logic Flow**: Template delivery system that accelerates test creation with proven structures.
**Current State**: ✅ Implemented with unit, integration, and invariant templates

### get_comprehensive_testing_guide()
**Purpose**: Provides detailed testing guides tailored to current project state and objectives.
**Operation**: Generates context-aware documentation, incorporates project-specific recommendations, provides step-by-step guidance, and ensures comprehensive coverage.
**Logic Flow**: Documentation system that supports implementation with detailed guidance.
**Current State**: ✅ Implemented with dynamic guide generation

### get_security_testing_patterns()
**Purpose**: Delivers security-specific testing patterns and vulnerability scenarios.
**Operation**: Provides attack scenario templates, vulnerability testing patterns, economic attack simulations, and defensive testing strategies.
**Logic Flow**: Security resource system that ensures comprehensive vulnerability coverage.
**Current State**: ✅ Implemented with comprehensive security pattern library

### get_foundry_integration_guide()
**Purpose**: Provides guidance for optimal integration with Foundry tools and workflows.
**Operation**: Delivers Foundry-specific best practices, tool integration patterns, optimization strategies, and troubleshooting guidance.
**Logic Flow**: Tool integration support that maximizes Foundry capabilities.
**Current State**: ✅ Implemented with detailed Foundry integration guidance

## Server Infrastructure (TestingServer)

These functions manage the overall MCP server operation and component coordination.

### register_tools()
**Purpose**: Registers all MCP tools with the FastMCP server framework.
**Operation**: Initializes tool definitions, establishes parameter schemas, configures tool metadata, and enables MCP client integration.
**Logic Flow**: System initialization that enables MCP protocol communication.
**Current State**: ✅ Fully implemented with FastMCP integration

### register_resources()
**Purpose**: Makes documentation and templates available as MCP resources.
**Operation**: Registers resource endpoints, configures access patterns, enables dynamic content generation, and supports client resource requests.
**Logic Flow**: Resource system that provides comprehensive documentation access.
**Current State**: ✅ Implemented with dynamic resource generation

### run_server()
**Purpose**: Manages the main server execution loop and handles client connections.
**Operation**: Starts server processes, manages client communications, coordinates component interactions, and handles shutdown procedures.
**Logic Flow**: Server management system that enables MCP client connectivity and operation.
**Current State**: ✅ Fully implemented with robust error handling

### handle_stdio()
**Purpose**: Manages stdio-based communication with MCP clients.
**Operation**: Processes stdin/stdout communication, handles JSON-RPC protocol, manages request/response cycles, and ensures reliable communication.
**Logic Flow**: Communication layer that enables MCP protocol operation.
**Current State**: ✅ Implemented with FastMCP framework

## Logic Flow Summary

The system operates through coordinated interactions between these functional layers:

1. **Entry Point**: Users begin with `initialize_protocol_testing_agent()` which analyzes current state
2. **Deep Analysis Phase**: `analyze_project_context()` provides detailed assessment with AI failure detection
3. **Implementation Phase**: `execute_testing_workflow()` guides structured improvements with contextual workflows
4. **Validation Phase**: `analyze_current_test_coverage()` monitors progress using real Foundry output
5. **Quality Assurance**: AI failure detection prevents false confidence from flawed tests
6. **Professional Standards**: Integrated security methodologies ensure audit-ready results
7. **Support Systems**: Foundry integration, resource management, and troubleshooting support all phases

## Current Implementation Status

### Fully Implemented Components ✅
- **All 7 Core MCP Tools**: Complete with parameter validation and error handling
- **AI Failure Detection**: 8 failure types with comprehensive analysis
- **Project Analysis**: Multi-tier maturity assessment with risk scoring
- **Foundry Integration**: Real tool integration with output parsing
- **Professional Guidance**: Security methodology integration
- **Resource System**: Templates and dynamic documentation
- **Server Infrastructure**: FastMCP-based with robust communication

### Key Capabilities Verified ✅
- **Context Awareness**: Adapts to current project state rather than generic advice
- **Real Tool Integration**: Parses actual `forge coverage` and `forge test` output
- **AI Quality Assurance**: Detects and prevents common AI-generated test failures
- **Professional Standards**: Integrates methodologies from leading security firms
- **Adaptive Workflows**: 6+ workflow types that build on existing work
- **Comprehensive Troubleshooting**: Directory detection and project validation

This functional architecture enables context-aware, quality-assured testing guidance that adapts to project needs while maintaining professional security standards. The system's modular design allows for targeted functionality while ensuring comprehensive coverage of testing requirements. 