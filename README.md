# Smart Contract Testing MCP Server 🔒⚡

> **Interactive AI-Powered Smart Contract Testing Workflows**

Revolutionary AI-powered testing framework for Solidity smart contracts using the Foundry toolchain. Transform your testing workflow from manual, ad-hoc processes into systematic, AI-guided experiences that achieve 95%+ coverage with comprehensive security testing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Foundry](https://img.shields.io/badge/Foundry-Compatible-orange.svg)](https://book.getfoundry.sh/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://gofastmcp.com/)

## 🌟 Key Features

### 🤖 **Interactive AI-Guided Workflows**
- **Initialize Protocol Testing Agent** - Choose from guided workflow paths
- **Multi-Phase Testing Execution** - Structured 4-phase testing approach  
- **Real-time Recommendations** - AI-powered testing strategy suggestions
- **Session Management** - Save, load, and continue testing sessions

### 🔧 **Deep Foundry Integration**
- **Comprehensive CLI Integration** - `forge test`, `forge coverage`, gas analysis
- **Advanced Coverage Analysis** - LCOV reporting with gap identification
- **Invariant & Fuzz Testing** - Property-based testing support
- **Performance Optimization** - Gas usage analysis and optimization

### 📝 **Professional Test Generation**
- **Unit Test Templates** - Comprehensive function-level testing
- **Integration Test Suites** - Multi-contract interaction testing
- **Invariant Test Generation** - System-wide property verification
- **Security Test Patterns** - Access control and vulnerability testing

### 📊 **Intelligent Analysis & Reporting**
- **Coverage Gap Analysis** - Identify untested code paths
- **Security Assessment** - Vulnerability detection and testing
- **Performance Metrics** - Gas optimization recommendations
- **Documentation Generation** - Automated testing documentation

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Foundry Toolkit** - Install from [getfoundry.sh](https://getfoundry.sh/)
- **Node.js** (for some integrations)
- **MCP Client** - Cursor, Claude Desktop, or other MCP-compatible AI client

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/smart-contract-testing-mcp.git
cd smart-contract-testing-mcp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

### Quick Demo

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the MCP server (from project directory)
python run.py

# Alternative: Run the server module directly
python -m components.testing_server

# For HTTP mode (instead of stdio)
export MCP_TRANSPORT_MODE=http
python run.py
```

## 🏗️ Architecture

```
smart-contract-testing-mcp/
├── components/                    # Core MCP components
│   ├── testing_server.py         # Main FastMCP server
│   ├── foundry_adapter.py        # Foundry CLI integration
│   ├── testing_tools.py          # Interactive workflow tools  
│   ├── testing_resources.py      # MCP resources (docs, templates)
│   └── testing_prompts.py        # AI guidance prompts
├── templates/                     # Solidity test templates
│   ├── test_contract_template.sol # Unit test template
│   ├── invariant_test_template.sol # Invariant test template
│   └── integration_test_template.sol # Integration test template
├── docs/                          # Documentation
└── requirements.txt               # Python dependencies
```

## 🎯 Core Workflows

### 1. Initialize Protocol Testing Agent

**Perfect for: New projects or developers starting fresh**

```python
# MCP Tool Call
initialize_protocol_testing_agent(
    project_path="./my-defi-protocol",
    analysis_mode="interactive"
)
```

**Returns:**
- Project structure analysis
- Workflow recommendations  
- Available testing paths:
  - **Create New Test Suite** - For new projects
  - **Evaluate & Enhance Existing** - For projects with existing tests

### 2. Execute Testing Workflow

**4-Phase Structured Approach:**

#### Phase 1: Contract Analysis & Discovery
- Scan and analyze all contracts
- Map dependencies and inheritance
- Identify critical functions and attack vectors
- Generate security assessment

#### Phase 2: Test Architecture Design  
- Design comprehensive test structure
- Define coverage strategy and targets
- Plan test categories and organization
- Create implementation roadmap

#### Phase 3: Test Implementation
- Generate professional test templates
- Implement unit, integration, and security tests
- Create invariant and fuzz test suites
- Setup test utilities and helpers

#### Phase 4: Coverage Analysis & Optimization
- Run comprehensive coverage analysis
- Identify and address gaps
- Optimize test performance
- Generate documentation and CI/CD integration

## 🛠️ MCP Components

### Tools
- `initialize_protocol_testing_agent` - Main workflow entry point
- `execute_testing_workflow` - Structured testing execution
- `analyze_test_coverage` - Coverage analysis with recommendations
- `generate_comprehensive_tests` - Automated test generation
- `manage_testing_session` - Session state management

### Resources  
- `testing/foundry-patterns` - Best practices and patterns
- `testing/templates/{test_type}` - Professional test templates
- `testing/coverage-report/{project}` - Coverage analysis reports
- `testing/best-practices` - Comprehensive testing guidelines

### Prompts
- `analyze-contract-for-testing` - Contract analysis guidance
- `design-test-strategy` - Testing strategy development  
- `review-test-coverage` - Coverage improvement recommendations
- `design-security-tests` - Security testing approaches
- `optimize-test-performance` - Performance optimization guidance

## 📋 Generated Test Examples

### Unit Test Template
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    
    function setUp() public {
        myContract = new MyContract();
    }
    
    function testInitialState() public {
        assertEq(myContract.owner(), address(this));
    }
    
    function testAccessControl() public {
        vm.expectRevert("Unauthorized");
        vm.prank(address(0x1));
        myContract.adminFunction();
    }
}
```

### Invariant Test Template
```solidity
contract InvariantTest is Test {
    MyContract public myContract;
    
    function setUp() public {
        myContract = new MyContract();
        targetContract(address(myContract));
    }
    
    function invariant_totalSupplyEqualsBalances() public {
        assertEq(myContract.totalSupply(), _sumAllBalances());
    }
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Server Configuration  
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8002
MCP_TRANSPORT_MODE=stdio  # or 'http'

# Foundry Configuration
FOUNDRY_PROFILE=default
COVERAGE_TARGET=90
MAX_FUZZ_RUNS=10000
INVARIANT_RUNS=256

# Testing Configuration
ENABLE_GAS_OPTIMIZATION=true
```

### Integration with Cursor/Claude

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "smart-contract-testing": {
      "command": "python",
      "args": ["-m", "components.testing_server"],
      "env": {
        "MCP_TRANSPORT_MODE": "stdio"
      }
    }
  }
}
```

## 🎨 Usage Examples

### Basic Testing Workflow

```python
# 1. Initialize the testing agent
result = await initialize_protocol_testing_agent(
    project_path="./my-protocol"
)

# 2. Execute comprehensive testing workflow  
workflow = await execute_testing_workflow(
    workflow_type="create_new_suite",
    project_path="./my-protocol", 
    objectives="Achieve 95% coverage with security focus",
    scope="comprehensive"
)

# 3. Analyze coverage
coverage = await analyze_test_coverage(
    project_path="./my-protocol",
    target_coverage=95
)
```

### Advanced Coverage Analysis

```python
# Get detailed coverage analysis with recommendations
analysis = await analyze_test_coverage(
    project_path="./defi-protocol",
    target_coverage=90,
    include_branches=True,
    detailed_report=True
)

# Result includes:
# - Current coverage metrics
# - Gap identification  
# - Specific recommendations
# - Implementation priority
```

## 🧪 Testing the MCP Server

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=components tests/

# Run integration tests
pytest tests/integration/

# Test specific components
pytest tests/test_foundry_adapter.py -v
```

## 📈 Performance & Metrics

### Coverage Targets
- **Unit Tests**: 100% line coverage
- **Integration Tests**: 95% branch coverage  
- **Security Tests**: All critical functions
- **Gas Optimization**: <50,000 gas for standard operations

### Performance Benchmarks
- **Test Generation**: <30 seconds for typical contract
- **Coverage Analysis**: <60 seconds for medium project
- **Workflow Execution**: 2-4 hours for complete suite

## 🛡️ Security & Best Practices

### Security Testing Features
- **Access Control Verification** - Test all permission boundaries
- **Reentrancy Protection** - Comprehensive reentrancy testing
- **Integer Overflow/Underflow** - Boundary condition testing
- **Economic Attack Simulation** - MEV and flash loan attack testing

### Best Practices Integration
- **Professional Templates** - Industry-standard test patterns
- **Security-First Approach** - Security testing prioritized
- **Comprehensive Coverage** - Multi-dimensional coverage analysis
- **Performance Optimization** - Gas-efficient test patterns

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
black . && isort . && flake8 .

# Run type checking
mypy components/
```

## 📚 Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[User Guide](docs/guide.md)** - Step-by-step usage guide  
- **[Best Practices](docs/best-practices.md)** - Testing best practices
- **[Examples](docs/examples.md)** - Real-world examples

## 🔗 Related Projects

- **[FastMCP](https://gofastmcp.com/)** - The FastMCP framework powering this server
- **[Foundry](https://book.getfoundry.sh/)** - The Foundry toolkit for smart contract development
- **[MCP Specification](https://modelcontextprotocol.io/)** - The Model Context Protocol specification

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastMCP Team** - For the excellent MCP framework
- **Foundry Team** - For the powerful smart contract testing toolkit  
- **Smart Contract Security Community** - For testing patterns and best practices

---

**Ready to revolutionize your smart contract testing?** 

Get started with the Smart Contract Testing MCP Server and experience AI-powered, systematic testing workflows that ensure your protocols are secure, reliable, and thoroughly tested.

[Get Started](#-quick-start) | [Documentation](docs/) | [Examples](docs/examples.md) | [Community](https://github.com/your-org/smart-contract-testing-mcp/discussions) 

## 🖥️ Usage

### For MCP Clients (Cursor, Claude Desktop)

**Use `run_clean.py` for MCP client integration:**

```bash
# This is the clean version for MCP protocol communication
python run_clean.py
```

**Update your MCP client configuration:**

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/path/to/foundry-testing-mcp/venv/bin/python",
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
      "env": {
        "MCP_TRANSPORT_MODE": "stdio"
      }
    }
  }
}
```

### For Development and Debugging

**Use `run.py` for development with full logging:**

```bash
# Development version with detailed output and logging
python run.py

# Run in HTTP mode for debugging
MCP_TRANSPORT_MODE=http python run.py

# Run with debug logging
LOG_LEVEL=DEBUG python run.py
```

### Key Differences:

| Feature | `run_clean.py` | `run.py` |
|---------|----------------|----------|
| **Purpose** | MCP client integration | Development & debugging |
| **Output** | Silent (MCP protocol only) | Verbose logging & banner |
| **Logging** | Disabled | Full logging to console |
| **Use Case** | Cursor, Claude Desktop | Local development |
| **Startup** | Instant | Shows startup progress |

## 🛠️ Available Tools

Once connected through your MCP client:

### Core Workflow Tools

1. **`initialize_protocol_testing_agent()`**
   - Initialize testing session in your project directory
   - Analyzes project structure and recommends workflows

2. **`execute_testing_workflow()`**
   - Execute 4-phase structured testing workflow
   - Supports "create_new_suite" and "evaluate_existing" modes

3. **`analyze_current_test_coverage()`**
   - Generate comprehensive coverage reports
   - Identifies gaps and provides actionable recommendations

4. **`validate_current_project()`**
   - Validates Foundry project structure
   - Provides setup guidance and troubleshooting

### AI Analysis Tools

5. **`get_server_info()`**
   - Server status and usage instructions
   - Troubleshooting guidance

## 📚 Resources Available

- **`testing/foundry-patterns`**: Best practices and testing patterns
- **`testing/templates/unit`**: Unit test templates
- **`testing/templates/integration`**: Integration test templates
- **`testing/templates/invariant`**: Invariant test templates
- **`testing/templates/fuzz`**: Fuzz test templates
- **`testing/templates/security`**: Security test templates

## 🎯 Quick Start Example

1. **Navigate to your Foundry project:**
```bash
cd /path/to/your-solidity-project
```

2. **Initialize testing (via MCP client):**
```
initialize_protocol_testing_agent()
```

3. **Execute comprehensive testing workflow:**
```
execute_testing_workflow(
  workflow_type="create_new_suite",
  objectives="Create comprehensive test suite with 95% coverage and security focus"
)
```

4. **Analyze coverage:**
```
analyze_current_test_coverage(target_coverage=95)
```

## 🔍 Troubleshooting

### MCP Client Issues

**Red dot in Cursor/Claude Desktop:**
- Ensure you're using `run_clean.py` (not `run.py`)
- Verify virtual environment path in MCP configuration
- Check that no other server instances are running

**Server not recognized:**
- Verify Python path points to your virtual environment
- Test configuration: `/path/to/venv/bin/python run_clean.py`
- Check MCP server logs for errors

### Common Solutions

**"Foundry not found" error:**
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Verify installation
forge --version
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x run_clean.py run.py

# Check virtual environment activation
source venv/bin/activate
```

**Module import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## 🏗️ Development Setup

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=components

# Run specific test file
python -m pytest tests/test_foundry_adapter.py -v
```

### Code Quality

```bash
# Format code
black components/ tests/

# Lint code
flake8 components/ tests/

# Type checking
mypy components/
```

## 🔗 Integration Examples

### Cursor Integration

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/Users/yourname/foundry-testing-mcp/venv/bin/python",
      "args": ["/Users/yourname/foundry-testing-mcp/run_clean.py"],
      "env": {
        "MCP_TRANSPORT_MODE": "stdio"
      }
    }
  }
}
```

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "python",
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
      "cwd": "/path/to/foundry-testing-mcp",
      "env": {
        "MCP_TRANSPORT_MODE": "stdio"
      }
    }
  }
}
```

## 📖 Documentation

- **[Executive Summary](docs/executive-summary.md)**: Business case and strategic value
- **[Technical Architecture](docs/technical-architecture-guide.md)**: Detailed technical specifications
- **[User Implementation Walkthrough](docs/user-implementation-walkthrough.md)**: Step-by-step usage guide

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Foundry](https://github.com/foundry-rs/foundry) for the excellent testing framework
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP server implementation
- The broader smart contract security community for testing best practices

---

**Transform your smart contract testing today!** 🚀

*For support, please open an issue or contact the maintainers.* 