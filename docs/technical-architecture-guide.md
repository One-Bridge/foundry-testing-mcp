# Foundry Testing MCP - Technical Architecture Guide

## Overview

The Foundry Testing MCP is a comprehensive smart contract testing assistant that provides intelligent project analysis, adaptive workflows, and deep integration with the Foundry toolchain. This system combines regex-first analysis with optional AST enhancement, AI failure detection, and context-aware mock generation to deliver production-ready testing solutions.

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
            │  │ • Mock Context  │  │ • Adaptive Workflows│  │
            │  │   Detection     │  │                     │  │
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
            │  │   Prompts       │  │ • Environment Mgmt │  │
            │  │ • 4 Templates   │  │                     │  │
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
            │  │ • get_server_info                      │    │
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

The Project Analysis Engine provides intelligent project understanding through multiple analysis layers.

#### ProjectAnalyzer Component

**Purpose**: Comprehensive project state analysis with regex-first approach and optional AST enhancement

**Architecture**: Regex-first analysis with optional AST semantic enhancement when `solc` is available

**Key Capabilities**:
- **Regex-First Contract Analysis**: Reliable, deterministic contract classification using scoring-based patterns
- **Enhanced Mock Context Detection**: Extracts detailed requirements for generating compatible mocks
- **Testing Phase Detection**: 5-tier maturity classification (none/basic/intermediate/advanced/production)
- **Security Level Assessment**: Security testing maturity evaluation
- **Contract Type Classification**: DeFi, NFT, governance, bridge, utility classification with scoring
- **Optional AST Enhancement**: Semantic analysis when Solidity compiler is available

**Core Data Structures**:
```python
@dataclass
class ContractAnalysis:
    path: str
    contract_name: str
    contract_type: str  # "defi", "nft", "governance", "bridge", "utility"
    functions: List[str]
    state_variables: List[str]
    security_patterns: List[str]
    risk_score: float
    dependencies: List[str]
    mock_requirements: Dict[str, Any]  # Enhanced mock context

@dataclass
class ProjectState:
    project_path: str
    project_type: str
    testing_phase: TestingPhase
    security_level: SecurityLevel
    test_files: List[TestFileAnalysis]
    contracts: List[ContractAnalysis]
    coverage_data: Dict[str, Any]
    foundry_config: Dict[str, Any]
    identified_gaps: List[str]
    next_recommendations: List[str]
```

**Enhanced Mock Context Detection** (NEW):
```python
# Mock requirements extraction for better test generation
mock_requirements = {
    "erc_interface_type": {
        "type": "erc20|erc721|custom",
        "exact_signatures_needed": bool,
        "required_functions": List[str]
    },
    "access_control_variant": {
        "variant": "standard|upgradeable|none",
        "avoid_functions": List[str],  # e.g., ["getRoleMemberCount"]
        "safe_functions": List[str]
    },
    "upgradeable_pattern": {
        "pattern": "uups|transparent|none",
        "avoid_direct_upgrade": bool,  # Prevents direct upgradeTo() calls
        "safe_upgrade_testing": bool
    },
    "circular_dependency_risks": {
        "risk_level": "low|medium|high",
        "avoid_helper_duplication": bool
    }
}
```

**Core Methods**:
```python
class ProjectAnalyzer:
    async def analyze_project(project_path: str) -> ProjectState
    def _comprehensive_regex_analysis(file_path: Path) -> ContractAnalysis
    def _extract_mock_requirements(content, contract_name, functions, deps) -> Dict[str, Any]
    def _detect_erc_interface_type(content: str, functions: List[str]) -> Dict[str, Any]
    def _detect_access_control_variant(content: str, deps: List[str]) -> Dict[str, Any]
    def _detect_upgradeable_pattern(content: str, deps: List[str]) -> Dict[str, Any]
    def _determine_contract_type_comprehensive(content: str) -> str
    def _calculate_comprehensive_risk_score(content, functions, patterns, type) -> float
```

**Testing Phase Classification**:
- **Production**: 50+ tests, 85%+ coverage, security tests, advanced patterns
- **Advanced**: 20+ tests, 75%+ coverage, security tests, mocks
- **Intermediate**: 10+ tests, 60%+ coverage, basic patterns
- **Basic**: 3+ tests, 30%+ coverage
- **None**: Minimal or no tests

**Implementation Status**: ✅ Fully implemented with regex-first architecture and enhanced mock detection

#### AIFailureDetector Component

**Purpose**: Quality assurance for test code with semantic understanding

**Architecture**: AST-enhanced pattern detection with regex fallback

**Detected Failure Patterns** (8 types):
1. **Circular Logic**: Tests validating implementation against itself
2. **Mock Cheating**: Mocks that always return expected values
3. **Insufficient Edge Cases**: Missing boundary condition testing
4. **Missing Security Scenarios**: Lack of access control or attack testing
5. **Always-Passing Tests**: Tests that provide no validation
6. **Inadequate Randomization**: Predictable or overly constrained fuzz inputs
7. **Missing Negative Tests**: No error condition testing
8. **Implementation Dependency**: Tests coupled to specific implementation details

**Core Methods**:
```python
class AIFailureDetector:
    async def analyze_test_file(file_path: str, content: str) -> List[FailureDetection]
    async def generate_failure_report(failures: List[FailureDetection]) -> Dict[str, Any]
    async def _detect_ast_based_failures(semantic_analysis, file_path) -> List[FailureDetection]
    def _detect_pattern_failures(failure_type, config, file_path, content) -> List[FailureDetection]
```

**Implementation Status**: ✅ Working with AST enhancement and regex fallback

#### AST Analysis System

**Purpose**: Optional semantic code analysis using Abstract Syntax Trees

**Architecture**: Solidity AST via `solc --ast-json` with comprehensive fallback

**Capabilities**:
- **Solidity Contract Analysis**: Via solc AST generation when available
- **Semantic Relationship Mapping**: Function calls, state dependencies
- **Security Pattern Detection**: Access control, reentrancy guards, oracle dependencies
- **Control Flow Analysis**: Function interaction mapping
- **Fallback Mechanisms**: Graceful degradation to regex analysis when AST fails

**Core Components**:
```python
class ASTAnalyzer:
    async def analyze_solidity_file(file_path: str) -> SemanticAnalysis
    def _parse_solidity_ast(ast_json: Dict, file_path: str) -> List[ASTNode]
    def _detect_security_patterns(nodes: List[ASTNode]) -> List[SecurityPattern]
    async def _fallback_text_analysis(file_path: str) -> SemanticAnalysis
```

**Implementation Status**: ✅ Working with comprehensive fallback to regex analysis

### 2. Foundry Integration Layer

#### FoundryAdapter Component

**Purpose**: Deep integration with Foundry toolchain

**Real Tool Integration**:
- **Coverage Analysis**: Multi-format parsing (lcov, summary, json)
- **Test Execution**: Coordinated `forge test` with coverage generation
- **Project Structure Detection**: foundry.toml parsing and validation
- **Gas Analysis**: Gas usage reporting and optimization insights
- **Environment Management**: Working directory resolution and validation

**Core Methods**:
```python
class FoundryAdapter:
    async def generate_coverage_report(project_path: str, format: str) -> Dict[str, Any]
    async def run_tests(project_path: str, test_pattern: str, coverage: bool) -> Dict[str, Any]
    async def detect_project_structure(project_path: str) -> Dict[str, Any]
    def _parse_summary_coverage(summary_output: str) -> Dict[str, Any]
    def _generate_contextual_coverage_analysis(coverage_pct: float, files: List) -> str
```

**Enhanced Coverage Analysis**:
- **Contextual Feedback**: Recognition of good coverage achievements
- **Gap Identification**: Specific uncovered areas with recommendations
- **Professional Standards**: Different thresholds for development vs production

**Implementation Status**: ✅ Working with known subprocess limitations in some environments

### 3. Template and Resource System

#### TestingResources Component

**Purpose**: Comprehensive knowledge base for testing patterns and templates

**Available Resources** (5 MCP resources):
1. `testing://foundry-patterns` - Best practices and file organization
2. `testing://security-patterns` - Security testing methodologies
3. `testing://templates/{template_type}` - Individual template access
4. `testing://templates` - Template catalog overview
5. `testing://documentation` - Testing methodologies and guides

**Template System** (4 production templates):
- **test_contract_template.sol**: Basic unit test template with comprehensive patterns
- **integration_test_template.sol**: Multi-contract interaction testing
- **invariant_test_template.sol**: Property-based testing with handler patterns
- **test_helper_template.sol**: Common utility functions and test helpers

**Template Features**:
- **Dynamic Substitution**: `{{CONTRACT_NAME}}`, `{{FUNCTION_NAME}}`, etc.
- **Best Practice Patterns**: Industry-standard testing approaches
- **Mock Integration**: Context-aware mock generation guidance
- **Security Focus**: Built-in security testing patterns

**Implementation Status**: ✅ Fully implemented with 4 production templates

#### TestingPrompts Component

**Purpose**: Structured guidance prompts for AI-driven testing workflows

**Available Prompts** (5 structured prompts):
1. `analyze-contract-for-testing` - Contract analysis framework
2. `design-test-strategy` - Comprehensive testing strategy development
3. `review-test-coverage` - Coverage review and improvement guidance
4. `design-security-tests` - Security-focused testing approaches
5. `optimize-test-performance` - Performance optimization strategies

**Implementation Status**: ✅ Working with tool-oriented guidance

### 4. MCP Tool Suite

#### Core Tools Implementation (8 tools)

**🚀 initialize_protocol_testing_agent**
- **Purpose**: Entry point for intelligent project analysis
- **Implementation**: ✅ AST-enhanced with contextual recommendations
- **Capabilities**: Project maturity assessment, workflow recommendations, session management
- **Enhanced Features**: Mock requirements detection, contract type classification

**🔍 analyze_project_context**
- **Purpose**: Deep analysis with AI failure detection
- **Implementation**: ✅ Comprehensive analysis with improvement planning
- **Capabilities**: Testing phase assessment, security level evaluation, AI failure detection
- **Enhanced Features**: Contract-specific risk scoring, mock generation context

**⚡ execute_testing_workflow**
- **Purpose**: Structured multi-phase workflow execution
- **Implementation**: ✅ Context-aware adaptive workflows
- **Capabilities**: Phase-based planning, session continuity, progress tracking
- **Workflow Types**: create_new_suite, comprehensive, evaluate_existing, security_focused

**📊 analyze_current_test_coverage**
- **Purpose**: Real Foundry coverage analysis with contextual feedback
- **Implementation**: ✅ Working with enhanced parsing and contextual analysis
- **Capabilities**: Multi-format coverage parsing, gap identification, professional recommendations
- **Enhanced Features**: Context-aware feedback, achievement recognition

**✅ validate_current_directory**
- **Purpose**: Project validation and environment setup
- **Implementation**: ✅ Enhanced validation with setup guidance
- **Capabilities**: Foundry installation check, project structure validation, diagnostic guidance

**🐛 debug_directory_detection**
- **Purpose**: Advanced troubleshooting for environment issues
- **Implementation**: ✅ Comprehensive environment analysis
- **Capabilities**: MCP client/server directory debugging, path resolution, configuration guidance

**🔍 discover_foundry_projects**
- **Purpose**: Automatic project discovery and selection
- **Implementation**: ✅ Intelligent project scanning with metadata
- **Capabilities**: Multi-project environment support, project metadata collection

**ℹ️ get_server_info**
- **Purpose**: Enhanced server capabilities overview
- **Implementation**: ✅ Comprehensive tool guidance and status
- **Capabilities**: Tool catalog, workflow recommendations, troubleshooting guidance

#### Session Management System

**TestingSession Architecture**:
```python
class TestingSession:
    session_id: str
    project_path: str
    current_phase: int
    completed_phases: List[int]
    workflow_type: str
    workflow_state: Dict[str, Any]
    generated_tests: List[str]
    analysis_results: Dict[str, Any]
```

**Features**:
- **Persistent State**: Workflow continuity across tool interactions
- **Progress Tracking**: Phase completion and advancement
- **Context Continuity**: Maintained analysis results and recommendations

**Implementation Status**: ✅ Full session persistence and management

### 5. Data Flow Architecture

#### Enhanced Analysis Flow

```
Project Files → ProjectAnalyzer (Regex-First) → Contract Classification
     ↓                ↓                              ↓
Test Files → Mock Requirements Detection → Enhanced Context
     ↓                ↓                              ↓
Coverage Data → Gap Identification → Contextual Recommendations
     ↓                ↓                              ↓
Optional AST → Semantic Enhancement → Refined Analysis
```

#### Mock Generation Flow (NEW)

```
Contract Analysis → Mock Requirements → Template Context → Working Mocks
       ↓                    ↓                  ↓               ↓
Interface Detection → Signature Mapping → Compatible Mocks → First-Pass Success
       ↓                    ↓                  ↓               ↓
Dependency Analysis → Risk Assessment → Safe Patterns → Reduced Debugging
```

#### Workflow Execution Flow

```
Project Analysis → Intelligent Workflow Selection → Adaptive Phase Planning
       ↓                    ↓                           ↓
Context Awareness → Maturity-Based Recommendations → Implementation Guidance
       ↓                    ↓                           ↓
Session Management → Progress Tracking → Continuous Improvement
```

## Implementation Status Summary

### Fully Implemented Components ✅

**Core Analysis Engine**:
- ✅ **ProjectAnalyzer**: Regex-first analysis with optional AST enhancement
- ✅ **Mock Context Detection**: 8 comprehensive mock requirement methods
- ✅ **Contract Classification**: 5-type scoring-based classification system
- ✅ **Testing Phase Detection**: 5-tier maturity assessment
- ✅ **AI Failure Detection**: 8 failure types with AST enhancement

**Tool Suite**:
- ✅ **All 8 MCP Tools**: Complete with parameter validation and error handling
- ✅ **Session Management**: Persistent state and workflow continuity
- ✅ **Context Awareness**: Project-specific recommendations and guidance

**Template System**:
- ✅ **4 Production Templates**: Unit, integration, invariant, helper templates
- ✅ **5 MCP Resources**: Comprehensive knowledge base access
- ✅ **5 Structured Prompts**: AI-guided workflow assistance

**Foundry Integration**:
- ✅ **Real Command Execution**: Coverage analysis, test execution, project validation
- ✅ **Multi-Format Parsing**: lcov, summary, json coverage parsing
- ✅ **Environment Management**: Directory detection and configuration

### Recent Enhancements (Latest Release) 🆕

**Enhanced Mock Context Detection**:
- ✅ **ERC Interface Detection**: Exact signature requirements for ERC20/721
- ✅ **AccessControl Variant Awareness**: Prevents `getRoleMemberCount()` errors
- ✅ **UUPS Pattern Safety**: Avoids direct `upgradeTo()` calls
- ✅ **Circular Dependency Prevention**: Helper function duplication detection
- ✅ **Interface Compatibility**: Strict compliance checking

**Improved Analysis**:
- ✅ **Regex-First Architecture**: Reliable, deterministic analysis without external dependencies
- ✅ **Scoring-Based Classification**: More accurate contract type detection
- ✅ **Comprehensive Risk Scoring**: Contract-type-aware risk assessment

### Known Issues and Limitations ⚠️

**Environment Dependencies**:
- **Directory Detection**: May require MCP client configuration in some environments
- **Subprocess Execution**: Coverage analysis can fail due to subprocess limitations
- **AST Analysis**: Falls back to regex when `solc` unavailable (graceful degradation)

**Analysis Scope**:
- **Pattern Recognition**: Regex-based with AST enhancement (not full semantic analysis)
- **Coverage Parsing**: Best-effort parsing with multiple fallback mechanisms
- **Large Projects**: Performance may degrade with 100+ contracts

**Integration Considerations**:
- **MCP Client Compatibility**: Some clients may require specific configuration
- **Foundry Version Compatibility**: Tested with modern Foundry versions
- **Working Directory**: Requires proper MCP client working directory setup

## Security and Safety Considerations

### Code Execution Safety

**Foundry Command Execution**:
- ✅ **Validated Commands**: Sanitized parameter construction
- ✅ **Restricted Scope**: Limited to standard Foundry operations
- ✅ **Working Directory Validation**: Contained execution environment
- ✅ **Error Boundary Management**: Comprehensive subprocess error handling

**File System Access**:
- ✅ **Read-Only Analysis**: No modification of project files
- ✅ **Project Scope Restriction**: Limited to project directory
- ✅ **Path Validation**: Prevention of directory traversal attacks
- ✅ **Temporary File Management**: Automatic cleanup of analysis artifacts

### Data Privacy and Security

**Project Information**:
- ✅ **Local Processing**: All analysis performed locally
- ✅ **No External Transmission**: Project data remains on user's system
- ✅ **Session Cleanup**: Automatic cleanup after workflow completion
- ✅ **User Control**: User retains complete control over data processing

## Performance Characteristics

### Analysis Performance

**Project Analysis**:
- **Typical Projects (10-50 contracts)**: 1-3 seconds
- **Large Projects (50-100 contracts)**: 3-8 seconds
- **Very Large Projects (100+ contracts)**: 8-15 seconds (may degrade)

**Coverage Analysis**:
- **Execution Time**: Depends on `forge coverage` performance
- **Parsing Performance**: Sub-second for typical projects
- **Memory Usage**: Proportional to project size (efficient)

**Mock Requirements Detection**:
- **Analysis Time**: 100-500ms per contract
- **Memory Overhead**: Minimal additional memory usage
- **Scalability**: Linear with number of contracts

### Memory and Resource Usage

**Server Memory**:
- **Base Memory**: ~50-100MB for server initialization
- **Analysis Memory**: +10-50MB during project analysis
- **Session Storage**: Minimal overhead (~1-5MB per active session)

**Disk Usage**:
- **Template Storage**: ~50KB for all templates
- **Log Files**: Configurable, typically <10MB
- **Temporary Files**: Automatically cleaned up

## Deployment and Configuration

### Installation and Setup

**System Requirements**:
- **Python**: 3.8+ with required packages from requirements.txt
- **Foundry**: Latest version recommended (optional for basic functionality)
- **Operating System**: Linux, macOS, Windows (with WSL recommended)

**Installation Process**:
```bash
# Clone repository
git clone <repository-url>
cd foundry-testing-mcp

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from components.testing_server import TestingMCPServer; print('✅ Installation successful')"
```

**Configuration Options**:
```python
# Environment Variables
LOG_LEVEL=INFO                    # Logging verbosity
MCP_CLIENT_CWD=/path/to/project  # Override working directory
FOUNDRY_PROFILE=default          # Foundry profile selection

# Server Configuration
transport_mode="stdio"           # stdio|http
host="localhost"                 # HTTP mode only
port=8000                       # HTTP mode only
```

### MCP Client Integration

**Cursor/Claude Integration**:
```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "python",
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
      "cwd": "/path/to/your/solidity/project"
    }
  }
}
```

**Development Mode**:
```bash
# Start with verbose logging
python run.py

# Start in production mode (silent)
python run_clean.py
```

## Future Development Roadmap

### Planned Enhancements

**Analysis Improvements**:
- **Enhanced AST Analysis**: More sophisticated semantic understanding
- **Security Vulnerability Detection**: Expanded security pattern recognition
- **Gas Optimization Analysis**: Automated gas optimization recommendations

**Tool Integration**:
- **Slither Integration**: Static analysis tool integration
- **Mythril Integration**: Security analysis enhancement
- **Hardhat Compatibility**: Cross-framework support

**User Experience**:
- **Web Interface**: Optional web-based dashboard
- **Visual Reports**: Enhanced coverage and analysis visualization
- **Integration Templates**: Framework-specific setup templates

### Technical Debt and Improvements

**Current Limitations to Address**:
- **Subprocess Reliability**: More robust subprocess execution
- **Error Handling**: Enhanced error recovery and user guidance
- **Performance Optimization**: Improved analysis performance for large projects
- **Configuration Management**: Simplified setup and configuration

This technical architecture reflects the current production state of the Foundry Testing MCP, providing a comprehensive view of implemented capabilities, known limitations, and practical deployment guidance. The system delivers production-ready testing assistance with intelligent project understanding and context-aware mock generation. 