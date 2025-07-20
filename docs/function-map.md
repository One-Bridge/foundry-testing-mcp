# Function Map - Foundry Testing MCP

## Overview

This document provides a comprehensive map of all functions across the Foundry Testing MCP system components. Each function is described with its actual implementation status and capabilities based on the current codebase.

## Core MCP Tools (User-Facing Interface)

These are the primary tools that users interact with through their MCP clients.

### initialize_protocol_testing_agent()
**Purpose**: Entry point that analyzes the current smart contract project and recommends appropriate testing workflows.
**Operation**: Scans the project directory, identifies existing contracts and tests, evaluates project maturity, and provides specific next steps based on current state.
**Parameters**: analysis_mode (interactive/direct), project_path (optional)
**Logic Flow**: This is always the first function called, which then directs users to other appropriate tools.
**Current State**: ✅ Implemented with AST-enhanced analysis and contextual workflow generation

### analyze_project_context()
**Purpose**: Performs deep analysis of project testing quality and identifies improvement opportunities with AI failure detection.
**Operation**: Examines existing test files for quality issues, calculates risk scores for contracts, detects AI-generated test failures, and creates prioritized improvement plans.
**Parameters**: include_ai_failure_detection (bool), generate_improvement_plan (bool), project_path (optional)
**Logic Flow**: Called after initial analysis when detailed assessment is needed, feeds results into workflow execution.
**Current State**: ✅ Implemented with comprehensive AI failure detection system

### execute_testing_workflow()
**Purpose**: Implements structured testing improvements through guided, multi-phase workflows.
**Operation**: Creates detailed implementation plans with specific phases, tracks progress through testing maturity levels, and provides step-by-step guidance for comprehensive test suite development.
**Parameters**: workflow_type, objectives, scope, session_id, project_path
**Logic Flow**: Executes the main implementation work, coordinating with analysis results to deliver targeted improvements.
**Current State**: ✅ Implemented with adaptive workflow generation based on project state

### analyze_current_test_coverage()
**Purpose**: Provides immediate assessment of test coverage percentages and identifies specific gaps.
**Operation**: Runs Foundry coverage analysis, calculates line and branch coverage metrics, compares against target goals, and recommends specific areas for improvement.
**Parameters**: target_coverage (default 90), include_branches (bool)
**Logic Flow**: Used for quick health checks and progress monitoring throughout development.
**Current State**: ✅ Implemented with real forge coverage parsing (note: subprocess execution issues in some environments)

### validate_current_directory()
**Purpose**: Verifies that the project environment is properly configured for testing workflows.
**Operation**: Checks Foundry installation, validates project structure, confirms file organization, and provides setup recommendations when issues are found.
**Parameters**: None
**Logic Flow**: Troubleshooting tool used when other functions report configuration problems.
**Current State**: ✅ Implemented with comprehensive validation checks

### debug_directory_detection()
**Purpose**: Diagnoses and resolves issues where the MCP system cannot locate project files correctly.
**Operation**: Analyzes directory detection logic, examines environment variables, identifies client-server directory mismatches, and provides specific configuration fixes.
**Parameters**: None
**Logic Flow**: Advanced troubleshooting tool used when directory-related errors persist after basic validation.
**Current State**: ✅ Implemented with detailed debugging output and MCP client configuration guidance

### discover_foundry_projects()
**Purpose**: Finds Foundry projects in the directory structure for project selection.
**Operation**: Scans common directories for Foundry projects, returns list with metadata, helps AI agents choose correct project path.
**Parameters**: None
**Logic Flow**: Project discovery tool for automatic project detection.
**Current State**: ✅ Implemented with automatic discovery capabilities

### get_server_info() (integrated in TestingMCPServer)
**Purpose**: Provides comprehensive information about server capabilities, tools, and usage guidance.
**Operation**: Catalogs available tools, explains workflow relationships, provides usage examples, and delivers orientation information for new users.
**Parameters**: None
**Logic Flow**: Information system that helps users understand and effectively utilize the MCP capabilities.
**Current State**: ✅ Implemented as part of server infrastructure

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
**Current State**: ✅ Implemented with multi-format support (note: some subprocess execution issues)

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
**Current State**: ✅ Implemented with detailed validation reporting

## Project Analysis Engine (ProjectAnalyzer)

These functions provide intelligent analysis of project state and testing quality.

### analyze_project()
**Purpose**: Main entry point for comprehensive project analysis.
**Operation**: Coordinates all analysis components to produce complete ProjectState with testing phase, security level, contracts, and tests analysis using regex-first approach.
**Logic Flow**: Central analysis function used by MCP tools, now using reliable regex-based contract detection.
**Current State**: ✅ Implemented with regex-first analysis and optional AST enhancement

### _analyze_contract_file()
**Purpose**: Analyzes individual contract files using regex-first approach with optional AST enhancement.
**Operation**: Uses comprehensive regex patterns for contract classification, function extraction, and security pattern detection. Optionally enhances results with AST analysis when Solidity compiler is available.
**Logic Flow**: Primary regex-based analysis with optional AST enhancement for additional insights.
**Current State**: ✅ Implemented with regex-first approach and optional AST enhancement

### _analyze_test_file()
**Purpose**: Analyzes individual test files using AST-based semantic analysis.
**Operation**: Identifies test patterns, security tests, mock usage, fuzz testing, and calculates complexity scores using semantic analysis.
**Logic Flow**: Test-level analysis with pattern recognition.
**Current State**: ✅ Implemented with AST analysis and pattern detection

### _determine_testing_phase()
**Purpose**: Determines current level of testing sophistication within the project.
**Operation**: Analyzes existing test patterns, counts test functions, evaluates test comprehensiveness, and classifies project into maturity levels (none/basic/intermediate/advanced/production).
**Logic Flow**: Classification system used to tailor recommendations and workflow selection.
**Current State**: ✅ Implemented with 5-tier maturity classification

### _determine_security_level()
**Purpose**: Evaluates the current state of security-focused testing within the project.
**Operation**: Reviews security test patterns, checks for vulnerability coverage, assesses access control testing, and rates security testing maturity.
**Logic Flow**: Security-specific assessment that influences workflow priorities and recommendations.
**Current State**: ✅ Implemented with security pattern detection

### _comprehensive_regex_analysis()
**Purpose**: Primary contract analysis method using comprehensive regex pattern matching.
**Operation**: Extracts contract names, functions, state variables, and dependencies using enhanced regex patterns. Determines contract types through scoring-based classification and calculates risk scores with contract-type awareness.
**Logic Flow**: Core analysis engine providing reliable results without external dependencies.
**Current State**: ✅ Implemented with enhanced pattern detection and scoring-based classification

### _calculate_comprehensive_risk_score()
**Purpose**: Assigns risk scores to contracts using contract-type-aware assessment.
**Operation**: Calculates base complexity score, applies contract type risk multipliers (DeFi=0.4, governance=0.3, etc.), analyzes security patterns with proper risk weights, and considers financial operation indicators.
**Logic Flow**: Enhanced risk assessment providing realistic scores for different contract types.
**Current State**: ✅ Implemented with contract-type awareness and enhanced security pattern analysis

### _calculate_risk_score()
**Purpose**: Legacy risk scoring method redirecting to comprehensive version.
**Operation**: Provides backward compatibility by calling comprehensive risk calculation with default utility contract type.
**Logic Flow**: Compatibility wrapper for existing code.
**Current State**: ✅ Implemented as wrapper for enhanced risk calculation

### _generate_recommendations()
**Purpose**: Creates actionable improvement plans based on project analysis results.
**Operation**: Synthesizes analysis results, prioritizes improvements by impact and effort, creates phased implementation plans, and provides specific recommendations.
**Logic Flow**: Planning system that translates analysis into actionable guidance.
**Current State**: ✅ Implemented with contextual recommendations based on project state

## AI Failure Detection System (AIFailureDetector)

These functions identify and prevent common issues with AI-generated test code.

### analyze_test_file()
**Purpose**: Examines individual test files for problematic patterns that indicate AI-generated failures.
**Operation**: Parses test code structure using AST analysis, identifies suspicious patterns, detects logical inconsistencies, and flags potential quality issues with severity ratings.
**Logic Flow**: Quality assurance component that validates test reliability before relying on coverage metrics.
**Current State**: ✅ Implemented with 8 failure types detection using AST and regex patterns

### _detect_ast_based_failures()
**Purpose**: Uses AST semantic analysis to detect AI failures more accurately than regex patterns.
**Operation**: Analyzes test function structure, identifies semantic issues, and provides context-aware failure detection.
**Logic Flow**: Advanced failure detection using semantic understanding.
**Current State**: ✅ Implemented with AST integration and enhanced accuracy

### generate_failure_report()
**Purpose**: Creates comprehensive reports of detected AI-generated test failures with remediation guidance.
**Operation**: Aggregates detected issues, prioritizes problems by severity, provides specific fix recommendations, and generates actionable improvement plans.
**Logic Flow**: Reporting system that translates technical analysis into practical improvement guidance.
**Current State**: ✅ Implemented with detailed reporting and remediation suggestions

### suggest_improvements()
**Purpose**: Provides specific, actionable suggestions for fixing detected AI failures.
**Operation**: Maps failure types to improvement strategies, generates targeted recommendations, provides implementation examples, and prioritizes fixes by impact.
**Logic Flow**: Remediation system that turns problem detection into solution guidance.
**Current State**: ✅ Implemented with comprehensive suggestion engine

## AST Analysis Engine (ASTAnalyzer)

These functions provide optional semantic code analysis enhancement using Abstract Syntax Trees.

### analyze_solidity_file()
**Purpose**: Provides optional semantic analysis enhancement when Solidity compiler is available.
**Operation**: Uses solc compiler to generate AST, parses semantic structure, identifies additional security patterns, and provides enhanced complexity metrics.
**Logic Flow**: Optional enhancement that adds insights to regex-based analysis when solc is installed.
**Current State**: ✅ Implemented as optional enhancement (requires solc installation)

### analyze_test_file()
**Purpose**: Performs semantic analysis of Solidity test files.
**Operation**: Analyzes test structure, identifies test patterns, and provides semantic understanding of test organization.
**Logic Flow**: Test-specific semantic analysis.
**Current State**: ✅ Implemented with test pattern recognition

### _extract_contract_nodes()
**Purpose**: Extracts contract-level semantic information from AST.
**Operation**: Identifies contracts, functions, state variables, events, and their relationships within the AST structure.
**Logic Flow**: AST parsing for contract structure.
**Current State**: ✅ Implemented with comprehensive node extraction

### _detect_security_patterns()
**Purpose**: Identifies security patterns in contract code using semantic analysis.
**Operation**: Recognizes access control patterns, reentrancy guards, oracle dependencies, and other security-relevant patterns through AST analysis.
**Logic Flow**: Security pattern detection using semantic understanding.
**Current State**: ✅ Implemented with pattern library

## Resource Management System (TestingResources)

These functions provide access to templates, documentation, and project-specific resources.

### get_foundry_testing_patterns()
**Purpose**: Provides structured testing patterns and best practices with code snippets.
**Operation**: Returns comprehensive testing patterns, file organization, naming conventions, and implementation examples.
**Resource**: `testing://foundry-patterns`
**Current State**: ✅ Implemented with actionable patterns and code examples

### get_security_testing_patterns()
**Purpose**: Delivers security-specific testing patterns and vulnerability scenarios.
**Operation**: Provides vulnerability test cases, attack scenarios, and security testing approaches with implementation examples.
**Resource**: `testing://security-patterns`
**Current State**: ✅ Implemented with comprehensive security pattern library

### get_test_template()
**Purpose**: Generates specific test templates for different testing scenarios and contract types.
**Operation**: Selects appropriate template based on testing needs, provides template content with placeholders, and includes usage instructions.
**Resource**: `testing://templates/{template_type}`
**Current State**: ✅ Implemented with unit, integration, invariant, security, and fork templates

### get_available_templates()
**Purpose**: Lists all available test templates with descriptions and use cases.
**Operation**: Provides template catalog with descriptions, use cases, and placeholder information.
**Resource**: `testing://templates`
**Current State**: ✅ Implemented with complete template catalog

### get_testing_documentation()
**Purpose**: Provides comprehensive testing methodologies and documentation.
**Operation**: Delivers testing guides, methodologies, coverage strategies, and best practices.
**Resource**: `testing://documentation`
**Current State**: ✅ Implemented with comprehensive documentation

## Prompt System (TestingPrompts)

These functions provide structured guidance based on professional testing methodologies.

### analyze_contract_for_testing
**Purpose**: Provides expert-level guidance for analyzing contracts for testing requirements.
**Operation**: Generates prompts with master system prompt integration, references MCP resources, and provides specific analysis framework.
**Current State**: ✅ Implemented with professional methodology integration

### design_test_strategy
**Purpose**: Creates structured prompts for comprehensive testing strategy development.
**Operation**: Guides test strategy design with risk-based approaches, resource references, and implementation planning.
**Current State**: ✅ Implemented with comprehensive strategy guidance

### review_test_coverage
**Purpose**: Provides prompts for systematic test coverage review and improvement.
**Operation**: Guides coverage analysis workflow, tool usage, and improvement planning.
**Current State**: ✅ Implemented with tool-oriented coverage guidance

### design_security_tests
**Purpose**: Creates prompts for security-focused testing approaches.
**Operation**: Guides security testing design with vulnerability focus, attack scenarios, and defense validation.
**Current State**: ✅ Implemented with security-specific guidance

### optimize_test_performance
**Purpose**: Provides prompts for test suite optimization and efficiency improvement.
**Operation**: Guides performance optimization with quality maintenance and workflow integration.
**Current State**: ✅ Implemented with optimization strategies

## Server Infrastructure (TestingServer)

These functions manage the overall MCP server operation and component coordination.

### __init__()
**Purpose**: Initializes the main MCP server with all components and dependency injection.
**Operation**: Sets up FastMCP server, initializes all components with proper dependencies, handles configuration, and manages component registration.
**Logic Flow**: Server initialization with enhanced error handling.
**Current State**: ✅ Implemented with comprehensive initialization and error handling

### _register_components()
**Purpose**: Registers all MCP tools, resources, and prompts with the FastMCP server framework.
**Operation**: Coordinates component registration, handles tool definitions, configures resource endpoints, and enables MCP protocol communication.
**Logic Flow**: System initialization that enables MCP protocol communication.
**Current State**: ✅ Implemented with enhanced logging and error handling

### run_server()
**Purpose**: Manages the main server execution loop and handles client connections.
**Operation**: Starts server processes, manages client communications, coordinates component interactions, and handles shutdown procedures.
**Logic Flow**: Server management system that enables MCP client connectivity and operation.
**Current State**: ✅ Implemented with stdio and http transport modes

## Logic Flow Summary

The system operates through coordinated interactions between these functional layers:

1. **Entry Point**: Users begin with `initialize_protocol_testing_agent()` which analyzes current state
2. **Deep Analysis Phase**: `analyze_project_context()` provides detailed assessment with AI failure detection
3. **Implementation Phase**: `execute_testing_workflow()` guides structured improvements with contextual workflows
4. **Validation Phase**: `analyze_current_test_coverage()` monitors progress using real Foundry output
5. **Quality Assurance**: AI failure detection prevents false confidence from flawed tests
6. **Resource Access**: Templates and documentation support implementation
7. **Support Systems**: Foundry integration, resource management, and troubleshooting support all phases

## Current Implementation Status

### Fully Implemented Components ✅
- **Core MCP Tools**: 7 tools with parameter validation and error handling
- **Regex-First Analysis**: Reliable contract classification and risk scoring without external dependencies
- **AI Failure Detection**: 8 failure pattern types with both AST and regex detection methods
- **Template System**: 6 template types with dynamic placeholder substitution
- **Foundry Integration**: CLI tool execution with coverage output parsing (environment-dependent)
- **Resource System**: 5 MCP resources providing patterns, templates, and documentation
- **Server Infrastructure**: FastMCP-based protocol communication with stdio/http modes

### Optional/Conditional Components 🔶
- **AST Enhancement**: Provides additional insights when Solidity compiler (solc) is installed
- **Coverage Analysis**: Functions in most environments but may fail in restricted execution contexts
- **Project Discovery**: Works with manual path specification when auto-detection fails

### Current Limitations ⚠️
- **Directory Resolution**: MCP client-server directory misalignment requires environment variable configuration in some setups
- **Subprocess Execution**: Coverage analysis dependent on execution environment permissions
- **MCP Client Compatibility**: Some clients require specific configuration for proper tool discovery

### Architecture Benefits ✅
- **Reliability**: Regex-first approach provides consistent results across environments
- **No External Dependencies**: Core functionality works without Solidity compiler installation
- **Graceful Degradation**: AST enhancement available when possible, regex fallback ensures basic functionality
- **Real Tool Integration**: Actual Foundry command execution and output parsing when environment permits

This functional architecture provides smart contract testing assistance through the MCP protocol, with documented limitations and ongoing development to address real-world usage issues. The modular design allows for targeted improvements while maintaining core functionality. 