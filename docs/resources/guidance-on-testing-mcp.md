# Guidance on Building a Smart Contract Testing MCP Server

## Overview

This document provides comprehensive guidance for building an MCP (Model Context Protocol) server focused on smart contract testing workflows using the Foundry toolchain. The server will create an interactive, agentic testing experience that helps developers design, review, and implement excellent testing coverage for Solidity-based protocols.

## Architecture & Design Patterns

### Core Architecture (Based on Deribit MCP Patterns)

```
testing-mcp/
├── components/
│   ├── __init__.py
│   ├── testing_server.py          # Main FastMCP server
│   ├── testing_resources.py       # Documentation & test file resources
│   ├── testing_tools.py           # Interactive workflow tools
│   ├── testing_prompts.py         # Guided analysis prompts
│   └── foundry_adapter.py         # Foundry CLI integration
├── docs/
│   ├── foundry-testing-patterns.md
│   ├── solidity-test-best-practices.md
│   └── testing-coverage-strategies.md
├── templates/
│   ├── test_contract_template.sol
│   ├── invariant_test_template.sol
│   └── integration_test_template.sol
└── requirements.txt
```

### Key Components

1. **FastMCP Server** - Main entry point with modular registration
2. **Foundry Adapter** - CLI integration for running tests and analysis
3. **Testing Resources** - Documentation and template access
4. **Interactive Tools** - Workflow management and test generation
5. **Guided Prompts** - Structured testing guidance

## Core Workflow Implementation

### 1. Initialize Protocol Testing Agent

The primary entry point should be a workflow tool that offers two main paths:

```python
@mcp.tool(
    annotations={
        "title": "Initialize Protocol Testing Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def initialize_protocol_testing_agent(
    project_path: str = "",
    analysis_mode: str = "interactive"
) -> Dict[str, Any]:
    """
    Initialize the interactive protocol testing agent with workflow selection.
    
    Args:
        project_path: Path to the Solidity project (optional for guided discovery)
        analysis_mode: "interactive" for guided flow, "direct" for immediate analysis
        
    Returns:
        Dictionary containing workflow options and next steps
    """
    
    # Detect project structure
    project_info = await _analyze_project_structure(project_path)
    
    workflow_options = {
        "status": "initialized",
        "project_info": project_info,
        "available_workflows": {
            "create_new_suite": {
                "title": "Create New Test Suite from Scratch",
                "description": "Design and implement a comprehensive test suite for your contracts",
                "features": [
                    "Contract analysis and test planning",
                    "Test template generation",
                    "Coverage strategy development",
                    "Best practices implementation"
                ],
                "ideal_for": "New projects or complete testing overhauls"
            },
            "evaluate_existing": {
                "title": "Evaluate & Enhance Existing Tests",
                "description": "Analyze current testing infrastructure and suggest improvements",
                "features": [
                    "Test coverage analysis",
                    "Gap identification",
                    "Refactoring suggestions",
                    "Performance optimization"
                ],
                "ideal_for": "Projects with existing tests that need enhancement"
            }
        },
        "next_steps": {
            "interactive": "Choose a workflow path to begin guided testing development",
            "direct": "Call execute_testing_workflow with your specific requirements"
        }
    }
    
    return workflow_options
```

### 2. Multi-Phase Testing Workflows

Following the Deribit MCP pattern, implement structured workflows with clear phases:

```python
@mcp.tool(
    annotations={
        "title": "Execute Testing Workflow",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def execute_testing_workflow(
    workflow_type: str,
    project_path: str,
    objectives: str,
    scope: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Execute a complete testing workflow with structured phases.
    
    Args:
        workflow_type: "create_new_suite" or "evaluate_existing"
        project_path: Path to the Solidity project
        objectives: Specific testing goals and requirements
        scope: Testing scope ("unit", "integration", "comprehensive")
        
    Returns:
        Dictionary containing workflow execution plan
    """
    
    workflow_plan = {
        "status": "workflow_ready",
        "workflow_type": workflow_type,
        "project_path": project_path,
        "objectives": objectives,
        "scope": scope,
        "execution_phases": []
    }
    
    if workflow_type == "create_new_suite":
        workflow_plan["execution_phases"] = [
            {
                "phase": 1,
                "title": "Contract Analysis & Discovery",
                "actions": [
                    "Scan project structure and identify contracts",
                    "Analyze contract dependencies and inheritance",
                    "Identify critical functions and state variables",
                    "Map attack vectors and edge cases"
                ],
                "deliverables": ["Contract analysis report", "Testing strategy document"]
            },
            {
                "phase": 2,
                "title": "Test Architecture Design",
                "actions": [
                    "Design test suite structure",
                    "Create test categories (unit, integration, invariant)",
                    "Define coverage targets and metrics",
                    "Plan mock and fixture strategies"
                ],
                "deliverables": ["Test architecture plan", "Coverage strategy"]
            },
            {
                "phase": 3,
                "title": "Test Implementation",
                "actions": [
                    "Generate test templates and boilerplate",
                    "Implement unit tests for core functions",
                    "Create integration test scenarios",
                    "Build invariant and fuzz tests"
                ],
                "deliverables": ["Complete test suite", "Test utilities"]
            },
            {
                "phase": 4,
                "title": "Coverage Analysis & Optimization",
                "actions": [
                    "Run comprehensive coverage analysis",
                    "Identify gaps and missing test cases",
                    "Optimize test performance",
                    "Document testing procedures"
                ],
                "deliverables": ["Coverage report", "Testing documentation"]
            }
        ]
    
    elif workflow_type == "evaluate_existing":
        workflow_plan["execution_phases"] = [
            {
                "phase": 1,
                "title": "Current Test Analysis",
                "actions": [
                    "Analyze existing test files and structure",
                    "Run coverage analysis on current tests",
                    "Identify testing patterns and anti-patterns",
                    "Assess test quality and maintainability"
                ],
                "deliverables": ["Test audit report", "Coverage baseline"]
            },
            {
                "phase": 2,
                "title": "Gap Analysis & Planning",
                "actions": [
                    "Identify uncovered code paths",
                    "Find missing edge cases and scenarios",
                    "Plan test refactoring strategies",
                    "Prioritize improvements by risk/impact"
                ],
                "deliverables": ["Gap analysis report", "Improvement roadmap"]
            },
            {
                "phase": 3,
                "title": "Enhancement Implementation",
                "actions": [
                    "Implement missing test cases",
                    "Refactor existing tests for better coverage",
                    "Add invariant and property-based tests",
                    "Improve test organization and utilities"
                ],
                "deliverables": ["Enhanced test suite", "Refactored tests"]
            },
            {
                "phase": 4,
                "title": "Validation & Documentation",
                "actions": [
                    "Validate improvement in coverage metrics",
                    "Performance test the enhanced suite",
                    "Update testing documentation",
                    "Create maintenance guidelines"
                ],
                "deliverables": ["Validation report", "Updated documentation"]
            }
        ]
    
    return workflow_plan
```

### 3. Foundry Integration Adapter

Create a specialized adapter for Foundry CLI operations:

```python
class FoundryAdapter:
    """
    Adapter for integrating with Foundry toolchain for smart contract testing.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.forge_config = self._load_forge_config()
    
    async def run_tests(self, test_pattern: str = "", coverage: bool = True) -> Dict[str, Any]:
        """Run Foundry tests with optional coverage analysis"""
        
    async def generate_coverage_report(self, format: str = "lcov") -> Dict[str, Any]:
        """Generate detailed coverage report"""
        
    async def run_invariant_tests(self, contract_name: str) -> Dict[str, Any]:
        """Run invariant/property-based tests"""
        
    async def analyze_gas_usage(self, function_name: str = "") -> Dict[str, Any]:
        """Analyze gas usage patterns"""
        
    async def get_test_structure(self) -> Dict[str, Any]:
        """Analyze current test file structure"""
```

### 4. Testing Resources

Implement comprehensive resources for testing documentation and templates:

```python
def _register_testing_resources() -> None:
    """Register testing-related resources"""
    
    @mcp.resource("testing/foundry-patterns")
    async def get_foundry_testing_patterns() -> Dict[str, Any]:
        """Access Foundry testing patterns and best practices"""
        
    @mcp.resource("testing/contract-analysis/{contract_name}")
    async def get_contract_analysis(contract_name: str) -> Dict[str, Any]:
        """Get detailed analysis of a specific contract for testing"""
        
    @mcp.resource("testing/coverage-report/{project_path}")
    async def get_coverage_report(project_path: str) -> Dict[str, Any]:
        """Get current test coverage report"""
        
    @mcp.resource("testing/templates/{test_type}")
    async def get_test_template(test_type: str) -> Dict[str, Any]:
        """Get test templates (unit, integration, invariant, fuzz)"""
```

### 5. Interactive Testing Prompts

Create guided prompts for different testing scenarios:

```python
def _register_testing_prompts() -> None:
    """Register interactive testing guidance prompts"""
    
    @mcp.prompt("analyze-contract-for-testing")
    async def analyze_contract_for_testing(contract_path: str) -> List[Dict[str, Any]]:
        """Analyze a contract and provide testing recommendations"""
        
    @mcp.prompt("design-test-strategy")
    async def design_test_strategy(
        contracts: str,
        risk_profile: str = "medium",
        coverage_target: int = 90
    ) -> List[Dict[str, Any]]:
        """Design comprehensive testing strategy"""
        
    @mcp.prompt("review-test-coverage")
    async def review_test_coverage(project_path: str) -> List[Dict[str, Any]]:
        """Review current test coverage and suggest improvements"""
```

## Technical Implementation Details

### 1. Project Structure Detection

```python
async def _analyze_project_structure(project_path: str) -> Dict[str, Any]:
    """Analyze Solidity project structure and identify testing opportunities"""
    
    structure_info = {
        "contracts": [],
        "existing_tests": [],
        "dependencies": [],
        "foundry_config": {},
        "testing_gaps": []
    }
    
    # Scan for contract files
    # Analyze existing test files
    # Check Foundry configuration
    # Identify testing patterns
    
    return structure_info
```

### 2. Test Generation Engine

```python
class TestGenerationEngine:
    """Engine for generating comprehensive test suites"""
    
    def __init__(self, foundry_adapter: FoundryAdapter):
        self.foundry = foundry_adapter
        self.templates = self._load_test_templates()
    
    async def generate_unit_tests(self, contract_info: Dict[str, Any]) -> List[str]:
        """Generate unit tests for contract functions"""
        
    async def generate_integration_tests(self, contracts: List[str]) -> List[str]:
        """Generate integration tests for contract interactions"""
        
    async def generate_invariant_tests(self, contract_info: Dict[str, Any]) -> List[str]:
        """Generate invariant/property-based tests"""
        
    async def generate_fuzz_tests(self, functions: List[str]) -> List[str]:
        """Generate fuzz tests for function robustness"""
```

### 3. Coverage Analysis Tools

```python
@mcp.tool(
    annotations={
        "title": "Analyze Test Coverage",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def analyze_test_coverage(
    project_path: str,
    target_coverage: int = 90,
    include_branches: bool = True
) -> Dict[str, Any]:
    """Comprehensive test coverage analysis with actionable insights"""
    
    # Run forge coverage
    # Parse LCOV report
    # Identify gaps
    # Provide recommendations
    
    return coverage_analysis
```

## Configuration & Environment

### Environment Variables

```python
class TestingConfig:
    """Configuration for testing MCP server"""
    
    # Server Configuration
    MCP_SERVER_PORT = int(os.getenv('MCP_SERVER_PORT', '8002'))
    MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', '127.0.0.1')
    MCP_TRANSPORT_MODE = os.getenv('MCP_TRANSPORT_MODE', 'stdio').lower()
    
    # Foundry Configuration
    FOUNDRY_PROFILE = os.getenv('FOUNDRY_PROFILE', 'default')
    COVERAGE_TARGET = int(os.getenv('COVERAGE_TARGET', '90'))
    
    # Testing Configuration
    MAX_FUZZ_RUNS = int(os.getenv('MAX_FUZZ_RUNS', '10000'))
    INVARIANT_RUNS = int(os.getenv('INVARIANT_RUNS', '256'))
```

### Dependencies

```python
# requirements.txt
fastmcp>=0.1.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
aiofiles>=23.0.0
pydantic>=2.0.0
rich>=13.0.0  # For pretty console output
```

## Best Practices Implementation

### 1. Error Handling

```python
class TestingError(Exception):
    """Base exception for testing MCP operations"""
    pass

class FoundryError(TestingError):
    """Foundry-specific errors"""
    pass

class CoverageError(TestingError):
    """Coverage analysis errors"""
    pass

# Implement consistent error handling across all tools
```

### 2. Logging & Monitoring

```python
import logging
from rich.logging import RichHandler

# Configure rich logging for better developer experience
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
```

### 3. Session Management

```python
class TestingSession:
    """Manage testing workflow sessions"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.current_phase = 0
        self.workflow_state = {}
        self.generated_tests = []
    
    async def save_state(self) -> None:
        """Save session state for resume capability"""
        
    async def load_state(self) -> None:
        """Load saved session state"""
```

## Integration Points

### 1. Foundry Integration

- Use `forge test` for running tests
- Use `forge coverage` for coverage analysis
- Use `forge create` for deployment testing
- Use `forge verify` for contract verification

### 2. IDE Integration

- Generate VS Code tasks for common operations
- Provide language server integration points
- Support for test debugging workflows

### 3. CI/CD Integration

- Generate GitHub Actions workflows
- Provide coverage reporting integration
- Support for automated testing pipelines

## Usage Patterns

### 1. New Project Initialization

```python
# User starts with: "Initialize Protocol Testing Agent"
# System responds with workflow options
# User selects "create_new_suite"
# System executes multi-phase workflow
```

### 2. Existing Project Enhancement

```python
# User starts with: "Initialize Protocol Testing Agent"
# System detects existing tests
# User selects "evaluate_existing"
# System analyzes and suggests improvements
```

### 3. Specific Testing Tasks

```python
# User can directly call specific tools:
# - analyze_test_coverage
# - generate_unit_tests
# - run_invariant_tests
# - optimize_test_performance
```

## Testing the MCP Server

### Unit Tests

```python
# test_testing_mcp.py
import pytest
from testing_mcp import TestingMCP

@pytest.mark.asyncio
async def test_initialize_protocol_testing_agent():
    """Test the main initialization workflow"""
    
@pytest.mark.asyncio
async def test_foundry_integration():
    """Test Foundry CLI integration"""
    
@pytest.mark.asyncio
async def test_coverage_analysis():
    """Test coverage analysis functionality"""
```

### Integration Tests

```python
# test_workflows.py
@pytest.mark.asyncio
async def test_complete_testing_workflow():
    """Test end-to-end testing workflow"""
    
@pytest.mark.asyncio
async def test_test_generation():
    """Test automated test generation"""
```

## Deployment & Distribution

### 1. Local Development

```bash
# Clone and setup
git clone <repo>
cd smart-contract-testing-mcp
pip install -r requirements.txt

# Run in development mode
python -m components.testing_server
```

### 2. Production Deployment

```bash
# Install as package
pip install smart-contract-testing-mcp

# Run as HTTP server
export MCP_TRANSPORT_MODE=http
python -m smart_contract_testing_mcp
```

### 3. Integration with Cursor/Claude

```json
{
  "mcpServers": {
    "smart-contract-testing": {
      "command": "python",
      "args": ["-m", "smart_contract_testing_mcp"],
      "env": {
        "MCP_TRANSPORT_MODE": "stdio"
      }
    }
  }
}
```

## Future Enhancements

### 1. Advanced Features

- AI-powered test case generation
- Automated security vulnerability testing
- Performance benchmarking integration
- Multi-chain testing support

### 2. Integration Expansions

- Hardhat compatibility layer
- Truffle migration support
- Remix IDE integration
- Slither security analysis integration

### 3. Workflow Enhancements

- Visual test coverage reporting
- Interactive test debugging
- Automated test maintenance
- Team collaboration features

## Conclusion

This MCP server will provide a comprehensive, interactive testing experience for smart contract developers. By following the established patterns from the Deribit MCP server and focusing on Foundry integration, we can create a powerful tool that significantly improves testing practices in the Solidity ecosystem.

The key success factors are:
1. **Interactive Workflows** - Guided, step-by-step testing development
2. **Foundry Integration** - Deep integration with the Foundry toolchain
3. **Comprehensive Coverage** - Support for all testing types and scenarios
4. **Professional Quality** - Production-ready code generation and best practices
5. **Extensible Architecture** - Easy to extend and customize for specific needs

This server will transform how developers approach smart contract testing, making it more systematic, comprehensive, and accessible to teams of all experience levels. 