# Function Map - Foundry Testing MCP v2.0

## Overview

This document provides a comprehensive map of all functions across the Foundry Testing MCP system components. Each function is described in non-technical terms to help readers understand the complete functional surface area and how logic flows through the application.

## Core MCP Tools (User-Facing Interface)

These are the primary tools that users interact with through their AI assistants.

### initialize_protocol_testing_agent()
**Purpose**: Entry point that analyzes the current smart contract project and recommends appropriate testing workflows.
**Operation**: Scans the project directory, identifies existing contracts and tests, evaluates project maturity, and provides specific next steps based on current state.
**Logic Flow**: This is always the first function called, which then directs users to other appropriate tools.

### analyze_project_context()
**Purpose**: Performs deep analysis of project testing quality and identifies improvement opportunities.
**Operation**: Examines existing test files for quality issues, calculates risk scores for contracts, detects AI-generated test failures, and creates prioritized improvement plans.
**Logic Flow**: Called after initial analysis when detailed assessment is needed, feeds results into workflow execution.

### execute_testing_workflow()
**Purpose**: Implements structured testing improvements through guided, multi-phase workflows.
**Operation**: Creates detailed implementation plans with specific phases, tracks progress through testing maturity levels, and provides step-by-step guidance for comprehensive test suite development.
**Logic Flow**: Executes the main implementation work, coordinating with analysis results to deliver targeted improvements.

### analyze_current_test_coverage()
**Purpose**: Provides immediate assessment of test coverage percentages and identifies specific gaps.
**Operation**: Runs Foundry coverage analysis, calculates line and branch coverage metrics, compares against target goals, and recommends specific areas for improvement.
**Logic Flow**: Used for quick health checks and progress monitoring throughout development.

### validate_current_project()
**Purpose**: Verifies that the project environment is properly configured for testing workflows.
**Operation**: Checks Foundry installation, validates project structure, confirms file organization, and provides setup recommendations when issues are found.
**Logic Flow**: Troubleshooting tool used when other functions report configuration problems.

### debug_directory_detection()
**Purpose**: Diagnoses and resolves issues where the MCP system cannot locate project files correctly.
**Operation**: Analyzes directory detection logic, examines environment variables, identifies client-server directory mismatches, and provides specific configuration fixes.
**Logic Flow**: Advanced troubleshooting tool used when directory-related errors persist after basic validation.

## Foundry Integration Layer

These functions provide direct integration with the Foundry smart contract development toolkit.

### check_foundry_installation()
**Purpose**: Verifies that Foundry tools are properly installed and accessible on the system.
**Operation**: Attempts to execute Foundry commands, retrieves version information, and reports installation status with troubleshooting guidance.
**Logic Flow**: Called during project validation to ensure toolchain availability.

### detect_project_structure()
**Purpose**: Analyzes the organization and contents of smart contract projects.
**Operation**: Scans directories for contracts, tests, and scripts, parses configuration files, identifies dependencies, and maps project architecture.
**Logic Flow**: Provides foundational project understanding used by analysis and workflow functions.

### run_tests()
**Purpose**: Executes smart contract tests using Foundry with optional coverage and gas reporting.
**Operation**: Constructs appropriate test commands, manages test execution, captures results and error output, and parses test outcomes for analysis.
**Logic Flow**: Core execution engine called by coverage analysis and workflow validation steps.

### generate_coverage_report()
**Purpose**: Creates detailed test coverage analysis showing which code paths are tested.
**Operation**: Runs Foundry coverage tools, processes coverage data into readable formats, calculates coverage percentages, and identifies untested code areas.
**Logic Flow**: Essential component of coverage analysis and gap identification processes.

### run_invariant_tests()
**Purpose**: Executes property-based tests that verify system invariants always hold true.
**Operation**: Runs specialized Foundry invariant testing, processes results to identify invariant violations, and provides analysis of system property adherence.
**Logic Flow**: Used in advanced testing workflows to verify critical system properties.

### analyze_gas_usage()
**Purpose**: Measures and reports gas consumption patterns across contract functions.
**Operation**: Executes tests with gas reporting enabled, parses gas usage data, identifies high-consumption functions, and provides optimization insights.
**Logic Flow**: Part of comprehensive testing analysis for performance optimization.

### initialize_project()
**Purpose**: Sets up new Foundry projects with proper structure and configuration.
**Operation**: Creates necessary directories, generates configuration files, establishes testing framework, and verifies project initialization success.
**Logic Flow**: Called for new project setup when project validation indicates missing structure.

### get_forge_config()
**Purpose**: Retrieves current Foundry configuration settings for the project.
**Operation**: Reads Foundry configuration files, parses settings and parameters, and provides configuration details for analysis and troubleshooting.
**Logic Flow**: Supporting function used by project analysis and validation processes.

## Project Analysis Engine

These functions provide intelligent analysis of project state and testing quality.

### analyze_project()
**Purpose**: Comprehensive analysis of project testing maturity and security posture.
**Operation**: Evaluates testing phase progression, assesses security testing coverage, calculates contract risk scores, and generates detailed project state assessment.
**Logic Flow**: Core analysis engine that feeds results into improvement planning and workflow selection.

### detect_testing_phase()
**Purpose**: Determines current level of testing sophistication within the project.
**Operation**: Analyzes existing test patterns, evaluates test comprehensiveness, assesses security test coverage, and classifies project into maturity levels.
**Logic Flow**: Classification system used to tailor recommendations and workflow selection.

### assess_security_level()
**Purpose**: Evaluates the current state of security-focused testing within the project.
**Operation**: Reviews security test patterns, checks for vulnerability coverage, assesses security test quality, and rates security testing maturity.
**Logic Flow**: Security-specific assessment that influences workflow priorities and recommendations.

### calculate_contract_risk()
**Purpose**: Assigns risk scores to individual contracts based on complexity and security patterns.
**Operation**: Analyzes contract code for complexity indicators, identifies security-sensitive patterns, evaluates external dependencies, and calculates numerical risk scores.
**Logic Flow**: Risk assessment used to prioritize testing efforts and identify high-priority contracts.

### identify_testing_gaps()
**Purpose**: Pinpoints specific areas where testing coverage or quality is insufficient.
**Operation**: Compares current testing against comprehensive standards, identifies missing test categories, highlights untested code paths, and prioritizes gaps by importance.
**Logic Flow**: Gap analysis that drives specific improvement recommendations and implementation priorities.

## AI Failure Detection System

These functions identify and prevent common issues with AI-generated test code.

### analyze_test_file()
**Purpose**: Examines individual test files for problematic patterns that indicate AI-generated failures.
**Operation**: Parses test code structure, identifies suspicious patterns, detects logical inconsistencies, and flags potential quality issues with severity ratings.
**Logic Flow**: Quality assurance component that validates test reliability before relying on coverage metrics.

### detect_circular_logic()
**Purpose**: Identifies tests that validate contracts against their own implementation rather than specifications.
**Operation**: Analyzes test logic patterns, identifies self-referential validation, detects implementation dependencies, and flags tests that cannot provide meaningful validation.
**Logic Flow**: Specific failure detection that prevents false confidence in test suites.

### detect_mock_cheating()
**Purpose**: Finds test mocks that always return expected values, making tests meaningless.
**Operation**: Examines mock implementations, identifies overly simplistic behaviors, detects mocks without failure scenarios, and flags unrealistic test conditions.
**Logic Flow**: Quality validation that ensures tests can actually fail when they should.

### detect_missing_edge_cases()
**Purpose**: Identifies areas where tests fail to cover boundary conditions and error scenarios.
**Operation**: Analyzes test input ranges, identifies missing boundary testing, checks for error condition coverage, and highlights gaps in edge case testing.
**Logic Flow**: Completeness validation that ensures comprehensive test coverage.

### generate_failure_report()
**Purpose**: Creates comprehensive reports of detected AI-generated test failures with remediation guidance.
**Operation**: Aggregates detected issues, prioritizes problems by severity, provides specific fix recommendations, and generates actionable improvement plans.
**Logic Flow**: Reporting system that translates technical analysis into practical improvement guidance.

## Resource Management System

These functions provide access to templates, documentation, and project-specific resources.

### get_foundry_testing_patterns()
**Purpose**: Provides comprehensive testing patterns and best practices for Foundry projects.
**Operation**: Delivers structured guidance on test organization, naming conventions, assertion patterns, and mocking strategies with practical examples.
**Logic Flow**: Reference system that supports implementation phases with proven patterns.

### get_test_template()
**Purpose**: Generates specific test templates for different testing scenarios and contract types.
**Operation**: Selects appropriate template based on testing needs, customizes template content for specific use cases, and provides usage instructions.
**Logic Flow**: Template delivery system that accelerates test creation with proven structures.

### get_current_project_analysis()
**Purpose**: Provides real-time analysis of the current project's structure and testing state.
**Operation**: Analyzes current directory contents, evaluates project organization, assesses testing coverage, and generates project-specific insights and recommendations.
**Logic Flow**: Dynamic analysis resource that adapts to current project state.

### get_current_coverage_report()
**Purpose**: Delivers current test coverage analysis with detailed metrics and recommendations.
**Operation**: Executes coverage analysis, processes coverage data, calculates comprehensive metrics, and provides specific improvement guidance.
**Logic Flow**: Coverage reporting system that supports ongoing monitoring and improvement.

### get_testing_documentation()
**Purpose**: Provides comprehensive testing guides and documentation for different scenarios.
**Operation**: Delivers structured documentation covering testing strategies, troubleshooting guides, best practices, and implementation patterns.
**Logic Flow**: Knowledge base system that supports users with comprehensive guidance.

### get_available_templates()
**Purpose**: Lists all available test templates with descriptions of their use cases and features.
**Operation**: Catalogs template options, describes template capabilities, explains use case scenarios, and provides selection guidance.
**Logic Flow**: Template discovery system that helps users select appropriate starting points.

## Guided Prompts System

These functions provide structured prompts for AI assistants to guide testing workflows.

### analyze_contract_for_testing()
**Purpose**: Generates comprehensive analysis prompts for evaluating contracts and planning test strategies.
**Operation**: Creates structured analysis frameworks, incorporates security considerations, provides systematic evaluation approaches, and guides thorough contract assessment.
**Logic Flow**: Analysis guidance system that ensures comprehensive contract evaluation.

### design_test_strategy()
**Purpose**: Provides prompts for creating comprehensive testing strategies tailored to specific projects.
**Operation**: Guides strategic planning processes, incorporates risk assessment, balances coverage with efficiency, and creates implementation roadmaps.
**Logic Flow**: Strategic planning system that ensures comprehensive and efficient testing approaches.

### review_test_coverage()
**Purpose**: Generates prompts for systematic review of current test coverage and identification of improvements.
**Operation**: Guides coverage analysis processes, identifies gap patterns, prioritizes improvements, and provides actionable enhancement recommendations.
**Logic Flow**: Coverage review system that supports ongoing testing quality improvement.

### design_security_tests()
**Purpose**: Provides specialized prompts for creating security-focused test scenarios based on threat models.
**Operation**: Incorporates professional security methodologies, addresses known vulnerability patterns, guides threat modeling, and ensures comprehensive security validation.
**Logic Flow**: Security guidance system that applies professional audit standards to testing.

### optimize_test_performance()
**Purpose**: Generates prompts for improving test suite performance and efficiency without sacrificing coverage.
**Operation**: Guides performance analysis, identifies optimization opportunities, balances speed with thoroughness, and provides implementation strategies.
**Logic Flow**: Optimization guidance system that maintains quality while improving efficiency.

## Server Infrastructure

These functions manage the overall MCP server operation and component coordination.

### register_components()
**Purpose**: Integrates all system components into the MCP server framework for coordinated operation.
**Operation**: Initializes component connections, establishes communication pathways, registers tools and resources, and ensures proper system integration.
**Logic Flow**: System initialization that enables coordinated operation of all components.

### run_server()
**Purpose**: Manages the main server execution loop and handles client connections.
**Operation**: Starts server processes, manages client communications, coordinates component interactions, and handles shutdown procedures.
**Logic Flow**: Server management system that enables MCP client connectivity and operation.

### cleanup()
**Purpose**: Manages resource cleanup and proper shutdown procedures for all system components.
**Operation**: Releases system resources, closes connections, saves state information, and ensures clean shutdown without data loss.
**Logic Flow**: Resource management system that maintains system stability and data integrity.

### get_server_info()
**Purpose**: Provides comprehensive information about server capabilities, tools, and usage guidance.
**Operation**: Catalogs available tools, explains workflow relationships, provides usage examples, and delivers orientation information for new users.
**Logic Flow**: Information system that helps users understand and effectively utilize the MCP capabilities.

## Logic Flow Summary

The system operates through coordinated interactions between these functional layers:

1. **Entry Point**: Users begin with `initialize_protocol_testing_agent()` which analyzes current state
2. **Analysis Phase**: Deep analysis via `analyze_project_context()` provides detailed assessment  
3. **Implementation Phase**: `execute_testing_workflow()` guides structured improvements
4. **Validation Phase**: `analyze_current_test_coverage()` monitors progress and validates results
5. **Support Systems**: Foundry integration, AI failure detection, and resource management support all phases
6. **Quality Assurance**: AI failure detection and security guidance ensure professional standards throughout

This functional architecture enables context-aware, quality-assured testing guidance that adapts to project needs while maintaining professional security standards. The system's modular design allows for targeted functionality while ensuring comprehensive coverage of testing requirements. 