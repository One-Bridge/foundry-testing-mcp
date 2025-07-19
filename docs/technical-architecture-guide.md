# Foundry Testing MCP - Technical Architecture Guide

## Overview

The Foundry Testing MCP provides smart contract testing assistance through project analysis, adaptive workflows, and integration with Foundry tools. This document provides technical documentation for the architecture components, their current implementation status, and known limitations.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Cursor/Claude)               │
│                   Standard MCP Interface                    │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────────────────────────────────────┐
            │             FastMCP Server                      │
            │                                                 │
            │  ┌─────────────────┐  ┌─────────────────────┐  │
            │  │ Project Analysis│  │   Workflow          │  │
            │  │    Engine       │  │   Management        │  │
            │  │                 │  │                     │  │
            │  │ • ProjectAnalyzer│  │ • TestingTools     │  │
            │  │ • AI Failure    │  │ • Session Tracking │  │
            │  │   Detector      │  │ • Phase Planning   │  │
            │  │ • AST Analyzer  │  │ • Context Awareness│  │
            │  └─────────────────┘  └─────────────────────┘  │
            │                                                 │
            │  ┌─────────────────┐  ┌─────────────────────┐  │
            │  │ Template and    │  │  Foundry            │  │
            │  │ Resource        │  │  Integration        │  │
            │  │ System          │  │                     │  │
            │  │                 │  │ • Command Execution│  │
            │  │ • Testing       │  │ • Coverage Parsing │  │
            │  │   Resources     │  │ • Error Handling   │  │
            │  │ • Testing       │  │ • Output Analysis  │  │
            │  │   Prompts       │  │                     │  │
            │  └─────────────────┘  └─────────────────────┘  │
            │                                                 │
            │  ┌─────────────────────────────────────────┐    │
            │  │            MCP Tool Suite               │    │
            │  │                                         │    │
            │  │ • initialize_protocol_testing_agent    │    │
            │  │ • analyze_project_context              │    │
            │  │ • execute_testing_workflow             │    │
            │  │ • analyze_current_test_coverage        │    │
            │  │ • validate_current_directory           │    │
            │  │ • debug_directory_detection            │    │
            │  │ • discover_foundry_projects            │    │
            │  └─────────────────────────────────────────┘    │
            └─────────────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────────────────┐
        │                Foundry Toolchain                    │
        │        forge test • forge coverage • forge build    │
        │              cast • forge script                    │
        └─────────────────────────────────────────────────────┘
```

## Core System Components

### 1. Project Analysis Engine

The Project Analysis Engine provides project state understanding and testing maturity assessment.

#### ProjectAnalyzer Component

**Purpose**: Project state analysis and testing maturity classification

**Key Capabilities**:
- **Testing Phase Detection**: Categorizes projects into none/basic/intermediate/advanced/production phases based on test count, coverage, and patterns
- **Security Level Assessment**: Evaluates security testing maturity using basic pattern detection
- **Contract Analysis**: Basic analysis of contract structure and complexity
- **Gap Identification**: Identifies missing testing areas with recommendations

**Core Methods**:
```python
class ProjectAnalyzer:
    async def analyze_project(project_path: str) -> ProjectState
    def _determine_testing_phase(test_files, coverage_data) -> TestingPhase
    def _determine_security_level(test_files, contracts) -> SecurityLevel
    def _identify_gaps(contracts, test_files, coverage_data) -> List[str]
    def _generate_recommendations(testing_phase, security_level, gaps, contracts) -> List[str]
```

**Testing Phase Classification**:
- **Production**: 50+ tests, 85%+ coverage, security tests, advanced patterns
- **Advanced**: 20+ tests, 75%+ coverage, some security tests, mocks
- **Intermediate**: 10+ tests, 60%+ coverage, basic patterns
- **Basic**: 3+ tests, 30%+ coverage
- **None**: Minimal or no tests

**Implementation Status**: ✅ Working with basic pattern recognition

#### AIFailureDetector Component

**Purpose**: Quality assurance for test code to identify common issues

**Detected Patterns** (8 types):
- **Circular Logic**: Tests that validate implementation against itself
- **Mock Cheating**: Mocks that always return expected values
- **Insufficient Edge Cases**: Missing boundary condition testing
- **Missing Security Scenarios**: Lack of access control or attack testing
- **Always-Passing Tests**: Tests that provide no validation
- **Implementation Dependency**: Tests coupled to specific implementation details

**Core Methods**:
```python
class AIFailureDetector:
    async def analyze_test_file(file_path: str, content: str) -> List[TestFailure]
    async def generate_failure_report(failures: List[TestFailure]) -> Dict[str, Any]
    def detect_circular_logic(content: str) -> List[TestFailure]
    def detect_mock_cheating(content: str) -> List[TestFailure]
```

**Implementation Status**: ✅ Working with regex and basic AST pattern detection

#### AST Analysis

**Purpose**: Semantic code analysis for Solidity contracts

**Capabilities**:
- Basic contract structure analysis
- Function and modifier detection
- Import and inheritance parsing
- Fallback to regex patterns when AST parsing fails

**Implementation Status**: ✅ Working with fallback mechanisms

### 2. Foundry Integration

The Foundry integration provides real tool coordination and output parsing.

#### FoundryAdapter Component

**Real Tool Integration**:
- **Coverage Analysis**: Parses `forge coverage` output in multiple formats (lcov, summary, json)
- **Test Execution**: Coordinates `forge test` commands with coverage generation
- **Output Parsing**: Extracts coverage percentages and file-by-file analysis
- **Error Handling**: Manages subprocess execution issues and provides fallbacks

**Core Methods**:
```python
class FoundryAdapter:
    async def generate_coverage_report(project_path: str, format: str = "lcov")
    def _parse_summary_coverage(summary_output: str) -> Dict[str, Any]
    def _extract_percentage(text: str) -> float
    def _extract_basic_coverage_info(stderr_output: str) -> Dict[str, Any]
```

**Known Issues**:
- Subprocess execution problems in some environments
- Coverage parsing may fail with complex project structures
- Directory detection issues with some MCP client configurations

**Implementation Status**: ✅ Working with known limitations

### 3. Template and Resource System

#### TestingResources Component

**Purpose**: Provides templates, documentation, and best-practice patterns

**Available Resources** (5 total):
1. `testing://foundry-patterns` - Best practices and file organization
2. `testing://security-patterns` - Security testing approaches
3. `testing://templates/{template_type}` - Specific template access
4. `testing://templates` - Template catalog overview
5. `testing://documentation` - Testing methodologies

**Template Types** (6 total):
- **unit**: Basic unit test template
- **integration**: Multi-contract interaction testing
- **invariant**: Property-based testing with handler pattern
- **security**: Access control and attack scenario testing
- **fork**: Mainnet forking test template
- **helper**: Common utility functions (newly added)

**Template Features**:
- Dynamic placeholder substitution (`{{CONTRACT_NAME}}`, `{{FUNCTION_NAME}}`, etc.)
- Usage instructions for each template type
- Best-practice patterns and conventions

**Implementation Status**: ✅ Fully implemented with helper template recently added

#### TestingPrompts Component

**Purpose**: Provides structured guidance prompts for testing scenarios

**Available Prompts** (5 total):
1. `analyze-contract-for-testing` - Contract analysis framework
2. `design-test-strategy` - Testing strategy development
3. `review-test-coverage` - Coverage review and improvement
4. `design-security-tests` - Security testing approaches
5. `optimize-test-performance` - Performance optimization guidance

**Implementation Status**: ✅ Working with basic prompt templates

### 4. MCP Tool Suite

#### Core Tools Implementation

**🚀 initialize_protocol_testing_agent**
- **Purpose**: Entry point for project analysis and workflow recommendations
- **Implementation**: ✅ Working with project state detection
- **Capabilities**: Project structure analysis, maturity assessment, workflow recommendations
- **Session Management**: Creates persistent sessions for workflow continuity

**🔍 analyze_project_context**
- **Purpose**: Deep analysis with AI failure detection and improvement planning
- **Implementation**: ✅ Working with comprehensive analysis capabilities
- **Capabilities**: Testing phase assessment, AI failure detection, contract risk analysis
- **Output**: Detailed reports with prioritized recommendations

**⚡ execute_testing_workflow**
- **Purpose**: Structured workflow execution with adaptive phases
- **Implementation**: ✅ Working with context-aware phase generation
- **Capabilities**: Multi-phase planning, session continuity, progress tracking
- **Workflow Types**: create_foundational_suite, expand_test_coverage, comprehensive, security, etc.

**📊 analyze_current_test_coverage**
- **Purpose**: Coverage analysis using real Foundry output
- **Implementation**: ✅ Working with known subprocess issues
- **Capabilities**: Real coverage parsing, gap identification, contextual recommendations
- **Limitations**: May fail in some environments due to subprocess execution

**✅ validate_current_directory**
- **Purpose**: Project validation and environment troubleshooting
- **Implementation**: ✅ Working with basic validation
- **Capabilities**: Foundry installation check, project structure validation
- **Output**: Setup recommendations and issue resolution guidance

**🐛 debug_directory_detection**
- **Purpose**: Advanced troubleshooting for directory and path issues
- **Implementation**: ✅ Working with environment analysis
- **Capabilities**: Environment variable analysis, path resolution debugging
- **Use Case**: Resolves MCP client/server directory mismatches

**🔍 discover_foundry_projects**
- **Purpose**: Find available Foundry projects in directory structure
- **Implementation**: ✅ Working with project discovery
- **Capabilities**: Automatic project detection, metadata collection
- **Use Case**: Multiple project environments and auto-detection failures

#### Session Management

**TestingSession Class**:
```python
class TestingSession:
    session_id: str
    project_path: str
    current_phase: int
    workflow_type: str
    workflow_state: Dict[str, Any]
    generated_tests: List[str]
    analysis_results: Dict[str, Any]
```

**Features**:
- Persistent session state across tool interactions
- Workflow progress tracking
- Context continuity for multi-step processes

**Implementation Status**: ✅ Basic implementation working

### 5. Data Flow Architecture

#### Analysis Flow

```
Project Files → ProjectAnalyzer → Testing Phase Detection
     ↓                ↓                    ↓
Test Files → Contract Analysis → Security Level Assessment
     ↓                ↓                    ↓
Coverage Data → Gap Identification → Recommendations
```

#### Workflow Execution Flow

```
Project Analysis → Workflow Selection → Phase Planning → Implementation Guidance
       ↓                    ↓                 ↓                    ↓
Current State → Appropriate Workflow → Structured Phases → Specific Actions
```

#### Quality Assurance Flow

```
Test Files → AI Failure Detection → Issue Report → Remediation Guidance
     ↓              ↓                    ↓               ↓
Content Analysis → Pattern Matching → Severity Assessment → Action Items
```

## Implementation Status Summary

### Fully Implemented Components ✅

- **All 7 MCP Tools**: Complete with parameter validation and error handling
- **Project Analysis**: Testing maturity assessment with 5-tier classification
- **AI Failure Detection**: 8 failure types with pattern recognition
- **Template System**: 6 template types including new helper template
- **Resource System**: 5 MCP resources with dynamic content
- **Prompt System**: 5 structured prompts for guidance
- **Foundry Integration**: Real command execution with output parsing
- **Session Management**: Basic session persistence and state tracking

### Known Issues and Limitations ⚠️

**Environment Issues**:
- **Directory Detection**: May fail in some MCP client configurations
- **Subprocess Execution**: Coverage analysis can fail due to subprocess issues
- **Path Resolution**: Client/server directory mismatches in some setups

**Analysis Limitations**:
- **AST Analysis**: Falls back to regex patterns when Solidity parsing fails
- **Coverage Parsing**: Best-effort parsing with fallback mechanisms
- **Pattern Detection**: Basic pattern recognition, not comprehensive semantic analysis

**Integration Issues**:
- **MCP Client Compatibility**: Some naming convention issues with certain clients
- **Tool Routing**: Occasional tool discovery problems
- **Error Handling**: Some edge cases not fully covered

### Performance Characteristics

**Analysis Performance**:
- Project analysis: ~1-3 seconds for typical projects
- Coverage analysis: Depends on `forge coverage` execution time
- AI failure detection: ~1-2 seconds per test file

**Memory Usage**:
- Session storage: Minimal overhead for typical workflows
- AST parsing: Memory usage depends on contract complexity
- Template loading: Templates loaded on-demand

**Scalability**:
- Handles projects with 50+ contracts effectively
- Performance degrades with very large projects (100+ contracts)
- Session management scales to typical development workflows

## Security Considerations

### Code Execution Safety

**Foundry Command Execution**:
- Validated command construction with parameter sanitization
- Execution limited to standard Foundry commands
- Working directory validation and containment
- Error boundary management for subprocess failures

**File System Access**:
- Read-only analysis operations on project files
- Restricted to project directory scope
- Validated path inputs to prevent directory traversal
- Temporary file cleanup after analysis

### Data Privacy

**Project Information**:
- All analysis performed locally without external transmission
- No sensitive project data stored permanently
- Session data cleanup after workflow completion
- User control over data processing and analysis

## Deployment and Configuration

### Installation Requirements

**Python Dependencies**:
- Python 3.8+ with required packages from requirements.txt
- FastMCP framework for MCP server implementation
- Foundry toolchain integration dependencies

**Foundry Integration**:
- Foundry installation required for full functionality
- `forge`, `cast`, and other Foundry tools must be accessible
- Proper Foundry project structure (foundry.toml, src/, test/)

### Configuration Options

**Environment Variables**:
- `LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `MCP_CLIENT_CWD`: Override working directory for MCP client integration
- `FOUNDRY_PROFILE`: Specify Foundry profile for tool execution

**MCP Client Integration**:
- Server startup with `run_clean.py` for production (silent operation)
- Development mode with `run.py` for debugging (verbose logging)
- HTTP mode support for development and testing

### Known Deployment Issues

**Common Problems**:
- Directory detection failures requiring MCP client configuration
- Subprocess execution issues in containerized environments
- Path resolution problems with relative vs absolute paths

**Troubleshooting**:
- Use `debug_directory_detection()` tool for path issues
- Check Foundry installation with `validate_current_directory()`
- Review MCP client configuration for proper working directory setup
- Monitor server logs for detailed error information

## Future Development Considerations

### Improvement Areas

**Enhanced Analysis**:
- More sophisticated AST analysis with better Solidity parsing
- Improved pattern recognition for security vulnerabilities
- Better handling of complex project structures

**Tool Integration**:
- More robust subprocess execution and error handling
- Better compatibility with various MCP client configurations
- Enhanced coverage analysis with more detailed reporting

**User Experience**:
- More contextual recommendations based on project type
- Better error messages and troubleshooting guidance
- Improved session management and workflow continuity

### Technical Debt

**Current Limitations**:
- Subprocess execution reliability needs improvement
- Directory detection logic could be more robust
- Error handling could be more comprehensive
- AST analysis fallback mechanisms need refinement

This technical architecture provides a realistic view of the current implementation status, acknowledging both capabilities and limitations while providing practical guidance for deployment and usage. 