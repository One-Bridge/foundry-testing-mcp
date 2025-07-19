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
- **Context-Aware Analysis** - Understands your current project state and testing maturity
- **AI Failure Detection** - Identifies 8 types of problematic AI-generated test patterns
- **Adaptive Workflows** - Six specialized workflows that build on existing work

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
- **AI Failure Detection** - Detects 8 critical failure types: circular logic, mock cheating, always-passing tests, missing edge cases, security gaps, inadequate randomization, missing negative tests, implementation dependency
- **Professional Security Integration** - Trail of Bits, OpenZeppelin, ConsenSys methodologies with DeFi-specific attack scenarios
- **Real Coverage Analysis** - Parses actual `forge coverage` output in multiple formats (lcov, summary, json) for accurate gap identification
- **Context-Aware Recommendations** - 5-tier project maturity assessment that builds on your existing work instead of restarting

## 🚀 Quick Start

> **Important**: Use `run_clean.py` for MCP client integration (Cursor, Claude Desktop). Use `run.py` only for development and debugging.

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

# Start the MCP server for client integration (Cursor, Claude Desktop)
python run_clean.py

# Alternative: Development mode with verbose logging
python run.py

# For HTTP mode debugging (development only)
export MCP_TRANSPORT_MODE=http
python run.py
```

## 🏗️ Architecture

```
foundry-testing-mcp/
├── components/                      # Core MCP components
│   ├── testing_server.py           # Main FastMCP server and MCP protocol handling
│   ├── foundry_adapter.py          # Foundry CLI integration and tool coordination
│   ├── testing_tools.py            # Interactive workflow tools and MCP tool definitions
│   ├── project_analyzer.py         # Project state analysis and testing maturity assessment
│   ├── ai_failure_detector.py      # AI-generated test quality assurance (8 failure types)
│   ├── testing_resources.py        # MCP resources (docs, templates, patterns)
│   ├── testing_prompts.py          # Professional testing guidance and prompts
│   └── __init__.py                 # Component initialization and exports
├── templates/                       # Solidity test templates
│   ├── test_contract_template.sol   # Unit test template
│   ├── invariant_test_template.sol  # Invariant test template
│   └── integration_test_template.sol # Integration test template
├── docs/                            # Comprehensive documentation
│   ├── executive-summary.md         # Business overview and value proposition
│   ├── function-map.md              # Complete technical function reference
│   └── technical-architecture-guide.md # Implementation details
├── run_clean.py                     # MCP client server runner (production)
├── run.py                           # Development server runner (debugging)
└── requirements.txt                 # Python dependencies
```

### Component Architecture

**Core System Components:**
- **`testing_server.py`**: FastMCP server that coordinates all MCP protocol communication
- **`testing_tools.py`**: Defines all 7 MCP tools available to AI clients with parameter validation
- **`project_analyzer.py`**: Analyzes project state, testing maturity (5 levels), and calculates contract risk scores
- **`ai_failure_detector.py`**: Detects 8 types of AI-generated test failures to prevent false confidence
- **`foundry_adapter.py`**: Real Foundry tool integration parsing `forge coverage`, `forge test` output
- **`testing_resources.py`**: Dynamic MCP resources providing templates and professional guidance
- **`testing_prompts.py`**: Professional testing methodologies from leading security audit firms

**Integration Flow:**
1. **MCP Client** connects via `testing_server.py`
2. **User calls tools** defined in `testing_tools.py`
3. **Project analysis** via `project_analyzer.py` determines current state
4. **AI failure detection** via `ai_failure_detector.py` ensures test quality
5. **Foundry integration** via `foundry_adapter.py` provides real tool coordination
6. **Professional guidance** via `testing_prompts.py` and `testing_resources.py`

## 🎯 Core Workflows

### 1. Initialize Protocol Testing Agent

**Perfect for: New projects or developers starting fresh**

```python
# MCP Tool Call (via your MCP client)
initialize_protocol_testing_agent(
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

**Six Adaptive Workflow Types:**

**For New Projects:**
- **`create_foundational_suite`** - Build testing infrastructure from scratch
- **`create_new_suite`** - Comprehensive new test suite creation

**For Existing Projects:**
- **`evaluate_existing`** - Enhance and build on current tests
- **`comprehensive`** - Full-scope testing improvement
- **`security`** - Security-focused testing enhancement
- **`defi_security_testing`** - DeFi-specific vulnerability testing

**Each workflow includes:**
- Context-aware phase planning based on current project state
- Professional security methodology integration  
- AI failure detection and quality assurance
- Real Foundry tool coordination for accurate analysis

## 🛠️ MCP Components

### Tools
- `initialize_protocol_testing_agent` - Main workflow entry point with project analysis
- `analyze_project_context` - Deep analysis with AI failure detection
- `execute_testing_workflow` - Structured testing execution with adaptive workflows
- `analyze_current_test_coverage` - Real coverage analysis with gap identification
- `validate_current_project` - Project validation and troubleshooting
- `debug_directory_detection` - Advanced directory troubleshooting
- `get_server_info` - Server capabilities and usage guidance

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

**🎯 Simple and Effective** - The MCP works with your current directory - no complex detection, just works where you are!

#### Option 1: Dynamic Configuration (Recommended)
Use this project-agnostic configuration that works with any Foundry project:

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

**How it works:**
- 🔍 **Auto-detects** your current project directory from environment variables
- 🔄 **Works with any project** - no need to change configuration when switching projects
- 💡 **Smart fallbacks** - provides clear guidance if detection fails

#### Option 2: Static Configuration (For specific projects)
If you want to lock the MCP to a specific project:

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/path/to/foundry-testing-mcp/venv/bin/python",
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
      "cwd": "/path/to/your-project",
      "env": {
        "MCP_TRANSPORT_MODE": "stdio",
        "MCP_CLIENT_CWD": "/path/to/your-project"
      }
    }
  }
}
```

#### Configuration Notes:
- Replace `/path/to/foundry-testing-mcp` with the actual path to your MCP server installation
- For **Option 2**, replace `/path/to/your-project` with your specific project path
- Use **Option 1** for maximum flexibility across multiple projects

**🎛️ Override Project Path**: All MCP tools now accept an optional `project_path` parameter:
```
initialize_protocol_testing_agent(project_path="/path/to/specific/project")
```

## 🎨 Usage Examples

### Context-Aware Analysis

**What makes this different from generic AI tools:**

```python
# Generic AI: "Start by writing unit tests for your contract functions..."
# This MCP: Analyzes your actual project first

result = await initialize_protocol_testing_agent()
# Returns context-aware recommendations:
# "Excellent foundation! 95 tests with 90% coverage detected. 
#  You're at Production level. Next: Add property-based testing 
#  and economic attack scenarios."
```

### AI Failure Detection in Action

```python
# Automatically detects problematic AI-generated tests
analysis = await analyze_project_context(
    include_ai_failure_detection=True
)

# Detects issues like:
# - Circular logic: assertEq(contract.balance(), contract.balance())
# - Mock cheating: Mocks that always return expected values  
# - Always-passing tests: assertTrue(true)
# - Missing security scenarios
```

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
coverage = await analyze_current_test_coverage(
    target_coverage=95,
    include_branches=True
)
```

### Advanced Coverage Analysis

```python
# Get detailed coverage analysis with recommendations
analysis = await analyze_current_test_coverage(
    target_coverage=90,
    include_branches=True
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
- **Test Generation**: Efficient automated generation for any contract size
- **Coverage Analysis**: Fast analysis for projects of any complexity
- **Workflow Execution**: Complete comprehensive test suite generation

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
      "cwd": "/path/to/your-project",
      "env": {
        "MCP_TRANSPORT_MODE": "stdio",
        "MCP_CLIENT_CWD": "/path/to/your-project"
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
   - Analyzes current project state and testing maturity 
   - Recommends appropriate workflows based on existing work
   - Entry point that understands your project context

2. **`analyze_project_context()`**
   - Deep analysis with AI failure detection (8 failure types)
   - Calculates contract risk scores and security assessment
   - Generates prioritized improvement plans

3. **`execute_testing_workflow()`**
   - Six adaptive workflow types that build on existing tests
   - Supports "create_new_suite", "evaluate_existing", "comprehensive", "security"
   - Context-aware phase planning with specific deliverables

4. **`analyze_current_test_coverage()`**
   - Parses real `forge coverage` output for accurate analysis
   - Identifies specific gaps with actionable recommendations
   - Compares against target coverage goals

### Project Validation Tools

5. **`validate_current_project()`**
   - Validates Foundry project structure and installation
   - Comprehensive environment checks and setup guidance

6. **`debug_directory_detection()`**
   - Advanced troubleshooting for MCP directory detection issues
   - Provides specific fixes for path resolution problems

7. **`get_server_info()`**
   - Complete server capabilities and tool overview
   - Usage guidance and quick start instructions

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

### Directory Detection Issues

**"Project path is /Users/username instead of my project directory":**

This is a common issue where the MCP server detects the wrong project directory. The server might show:
- `"project_path": "/Users/username"` (home directory)
- `"project_path": "/Users/username/foundry-testing-mcp"` (server directory)
- But your actual project is at `/Users/username/path/to/your-project`

**Root Cause:**
The MCP server is using its own working directory instead of your project directory.

**⚠️ Enhanced Detection:**
The server now automatically detects when it's running from its own directory and provides specific warnings:
```
⚠️  MCP server is using its own directory: /path/to/foundry-testing-mcp
This usually means the MCP client didn't set the correct working directory.
```

**Solutions:**

1. **REQUIRED: Set working directory in MCP client configuration:**
```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/run_clean.py"],
      "cwd": "/path/to/your-project",  // ← REQUIRED
      "env": {
        "MCP_CLIENT_CWD": "/path/to/your-project",  // ← REQUIRED
        "MCP_PROJECT_PATH": "/path/to/your-project"
      }
    }
  }
}
```

2. **Use the debugging tool for detailed guidance:**
```
debug_directory_detection()
```
This will show you exactly what directory the server is detecting and provide specific troubleshooting advice.

3. **Validate your setup:**
```
validate_current_project()
```
This tool will verify if the server can find your Foundry project correctly.

4. **Check server warnings:**
The server now provides clear warnings when directory detection fails and specific steps to fix the issue.

**Directory Detection Priority:**
1. Explicitly provided project path
2. `MCP_CLIENT_CWD` environment variable  
3. `MCP_PROJECT_PATH` environment variable
4. Server's current working directory (with enhanced warnings)

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

## 🤖 **Simple and Effective**

The MCP works with the **current directory** - simple and reliable:

### **How It Works**
- 📁 **Current Directory**: Works with whatever Foundry project you're currently in
- ✅ **Clear Validation**: Tells you immediately if current directory is valid
- 🎯 **No Magic**: No complex auto-detection - just works where you are

### **For AI Agents: Getting Started**
```
# Validate current directory first
validate_current_directory()

# Then use tools in current project
initialize_protocol_testing_agent()
execute_testing_workflow(workflow_type="create_new_suite", objectives="comprehensive testing")
```

### **Usage Pattern**
1. **Navigate to your Foundry project** (`cd /path/to/your/project`)
2. **Validate the setup** (`validate_current_directory()`)
3. **Start testing** (`initialize_protocol_testing_agent()`)

### **Clear Error Handling**
When things go wrong, you get:
- 🔧 **Clear error messages** about what's missing
- 📋 **Specific next steps** to fix the issue
- ✅ **Simple validation** to confirm setup 