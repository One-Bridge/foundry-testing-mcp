"""
Smart Contract Testing MCP Server - Testing Resources

This module provides MCP resources for accessing documentation, templates, and reports.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class TestingResources:
    """
    Testing resources for the MCP server.
    
    This class provides access to test templates, documentation, and generated reports
    through the MCP resource system.
    """
    
    def __init__(self):
        """Initialize testing resources."""
        self.server_root = self._get_server_root()
        self.templates_dir = self.server_root / "templates"
        self.docs_dir = self.server_root / "docs"
        logger.info(f"Testing resources initialized - Server root: {self.server_root}")
    
    def _get_server_root(self) -> Path:
        """Get the root directory of the MCP server installation."""
        # Get the directory containing this file
        current_file = Path(__file__)
        # Go up to the project root (from components/ to root)
        server_root = current_file.parent.parent
        return server_root.resolve()
    
    def _get_current_project_path(self) -> Path:
        """Get the current project directory (where user is working)."""
        return Path.cwd()
    
    def register_resources(self, mcp) -> None:
        """
        Register all testing resources with the MCP server.
        
        Args:
            mcp: FastMCP server instance
        """
        # Foundry testing patterns resource
        @mcp.resource("testing/foundry-patterns")
        async def get_foundry_testing_patterns() -> Dict[str, Any]:
            """
            Access comprehensive Foundry testing patterns and best practices.
            
            Returns:
                Dictionary containing testing patterns, examples, and best practices
            """
            return {
                "name": "Foundry Testing Patterns",
                "description": "Comprehensive patterns and best practices for Foundry testing",
                "version": "1.0.0",
                "content": {
                    "test_organization": {
                        "file_structure": {
                            "description": "Recommended test file organization",
                            "pattern": """
test/
├── unit/           # Unit tests for individual functions
│   ├── Contract1.t.sol
│   └── Contract2.t.sol
├── integration/    # Integration tests for contract interactions
│   ├── Workflow1.t.sol
│   └── Workflow2.t.sol
├── invariant/      # Invariant/property-based tests
│   ├── Invariant1.t.sol
│   └── Invariant2.t.sol
├── fuzz/          # Fuzz testing
│   ├── Fuzz1.t.sol
│   └── Fuzz2.t.sol
├── mocks/         # Mock contracts for testing
│   ├── MockERC20.sol
│   └── MockOracle.sol
└── utils/         # Test utilities and helpers
    ├── TestUtils.sol
    └── TestConstants.sol
                            """
                        },
                        "naming_conventions": {
                            "test_files": "Use .t.sol suffix for test files",
                            "test_functions": "Use test prefix for test functions",
                            "test_contracts": "Use Test suffix for test contracts"
                        }
                    },
                    "testing_patterns": {
                        "setup_patterns": {
                            "description": "Common setup patterns for tests",
                            "examples": [
                                "State variable initialization",
                                "Mock contract deployment",
                                "User account setup",
                                "Initial funding and approvals"
                            ]
                        },
                        "assertion_patterns": {
                            "description": "Effective assertion strategies",
                            "examples": [
                                "State verification",
                                "Event emission checks",
                                "Balance and allowance verification",
                                "Error condition testing"
                            ]
                        },
                        "mocking_patterns": {
                            "description": "Mock contract and external dependency patterns",
                            "examples": [
                                "ERC20 token mocking",
                                "Oracle price feed mocking",
                                "External contract interaction mocking"
                            ]
                        }
                    },
                    "best_practices": {
                        "test_isolation": "Each test should be independent and repeatable",
                        "clear_naming": "Use descriptive test names that explain the scenario",
                        "comprehensive_coverage": "Cover success paths, error conditions, and edge cases",
                        "gas_optimization": "Test gas usage and optimization scenarios",
                        "security_focus": "Include security-specific test scenarios"
                    }
                }
            }
        
        # Test templates resource
        @mcp.resource("testing/templates/{template_type}")
        async def get_test_template(template_type: str) -> Dict[str, Any]:
            """
            Get test templates for different testing scenarios.
            
            Args:
                template_type: Type of template (unit, integration, invariant, fuzz, security)
                
            Returns:
                Dictionary containing the template content and usage instructions
            """
            template_content = await self._load_template(template_type)
            
            return {
                "name": f"{template_type.title()} Test Template",
                "description": f"Template for {template_type} testing scenarios",
                "template_type": template_type,
                "content": template_content,
                "usage": {
                    "description": f"How to use the {template_type} test template",
                    "instructions": await self._get_template_usage_instructions(template_type)
                }
            }
        
        # Current project analysis resource
        @mcp.resource("testing/project-analysis")
        async def get_current_project_analysis() -> Dict[str, Any]:
            """
            Get analysis of the current project directory.
            
            Returns:
                Dictionary containing project structure analysis
            """
            project_path = self._get_current_project_path()
            
            try:
                # Import here to avoid circular dependency
                from .foundry_adapter import FoundryAdapter
                
                adapter = FoundryAdapter()
                analysis = await adapter.detect_project_structure(str(project_path))
                
                return {
                    "name": "Current Project Analysis",
                    "description": "Analysis of the current project directory",
                    "project_path": str(project_path),
                    "analysis": analysis,
                    "recommendations": self._generate_project_recommendations(analysis)
                }
                
            except Exception as e:
                logger.error(f"Error analyzing current project: {e}")
                return {
                    "name": "Current Project Analysis",
                    "description": "Error analyzing current project",
                    "error": str(e),
                    "project_path": str(project_path)
                }
        
        # Test coverage resource
        @mcp.resource("testing/coverage-report")
        async def get_current_coverage_report() -> Dict[str, Any]:
            """
            Get current test coverage report for the project.
            
            Returns:
                Dictionary containing coverage report and analysis
            """
            project_path = self._get_current_project_path()
            
            try:
                # Import here to avoid circular dependency
                from .foundry_adapter import FoundryAdapter
                
                adapter = FoundryAdapter()
                coverage_result = await adapter.generate_coverage_report(str(project_path))
                
                return {
                    "name": "Current Coverage Report",
                    "description": "Test coverage analysis for the current project",
                    "project_path": str(project_path),
                    "coverage_data": coverage_result,
                    "analysis": self._analyze_coverage_data(coverage_result)
                }
                
            except Exception as e:
                logger.error(f"Error generating coverage report: {e}")
                return {
                    "name": "Current Coverage Report",
                    "description": "Error generating coverage report",
                    "error": str(e),
                    "project_path": str(project_path)
                }
        
        # Testing documentation resource
        @mcp.resource("testing/documentation")
        async def get_testing_documentation() -> Dict[str, Any]:
            """
            Get comprehensive testing documentation.
            
            Returns:
                Dictionary containing testing guides and documentation
            """
            return {
                "name": "Smart Contract Testing Documentation",
                "description": "Comprehensive testing guides and best practices",
                "sections": {
                    "getting_started": {
                        "title": "Getting Started with Smart Contract Testing",
                        "content": await self._get_getting_started_guide()
                    },
                    "foundry_guide": {
                        "title": "Foundry Testing Guide",
                        "content": await self._get_foundry_guide()
                    },
                    "security_testing": {
                        "title": "Security Testing Best Practices",
                        "content": await self._get_security_testing_guide()
                    },
                    "coverage_strategies": {
                        "title": "Test Coverage Strategies",
                        "content": await self._get_coverage_strategies_guide()
                    },
                    "troubleshooting": {
                        "title": "Common Issues and Solutions",
                        "content": await self._get_troubleshooting_guide()
                    }
                }
            }
        
        # Available templates list resource
        @mcp.resource("testing/templates")
        async def get_available_templates() -> Dict[str, Any]:
            """
            Get list of available test templates.
            
            Returns:
                Dictionary containing available templates and their descriptions
            """
            return {
                "name": "Available Test Templates",
                "description": "List of all available test templates",
                "templates": {
                    "unit": {
                        "name": "Unit Test Template",
                        "description": "Template for testing individual contract functions",
                        "use_cases": [
                            "Function-level testing",
                            "State variable testing",
                            "Access control testing",
                            "Error condition testing"
                        ]
                    },
                    "integration": {
                        "name": "Integration Test Template",
                        "description": "Template for testing contract interactions",
                        "use_cases": [
                            "Multi-contract workflows",
                            "User journey testing",
                            "Cross-contract interactions",
                            "End-to-end scenarios"
                        ]
                    },
                    "invariant": {
                        "name": "Invariant Test Template",
                        "description": "Template for property-based testing",
                        "use_cases": [
                            "System invariants",
                            "Property verification",
                            "State consistency testing",
                            "Business rule validation"
                        ]
                    },
                    "fuzz": {
                        "name": "Fuzz Test Template",
                        "description": "Template for fuzz testing with random inputs",
                        "use_cases": [
                            "Input validation testing",
                            "Edge case discovery",
                            "Robustness testing",
                            "Boundary condition testing"
                        ]
                    },
                    "security": {
                        "name": "Security Test Template",
                        "description": "Template for security-focused testing",
                        "use_cases": [
                            "Access control testing",
                            "Reentrancy testing",
                            "Economic attack testing",
                            "Vulnerability testing"
                        ]
                    }
                }
            }
        
        logger.info("Testing resources registered successfully")
    
    # Template loading methods
    async def _load_template(self, template_type: str) -> str:
        """Load template content from the templates directory."""
        template_map = {
            "unit": "test_contract_template.sol",
            "integration": "integration_test_template.sol",
            "invariant": "invariant_test_template.sol",
            "fuzz": "fuzz_test_template.sol",
            "security": "security_test_template.sol"
        }
        
        template_file = template_map.get(template_type)
        if not template_file:
            return self._get_default_test_template()
        
        template_path = self.templates_dir / template_file
        
        try:
            if template_path.exists():
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                # Return built-in template if file doesn't exist
                return self._get_builtin_template(template_type)
        except Exception as e:
            logger.warning(f"Error loading template {template_type}: {e}")
            return self._get_default_test_template()
    
    def _get_builtin_template(self, template_type: str) -> str:
        """Get built-in template content."""
        if template_type == "unit":
            return self._get_unit_test_template()
        elif template_type == "integration":
            return self._get_integration_test_template()
        elif template_type == "invariant":
            return self._get_invariant_test_template()
        elif template_type == "fuzz":
            return self._get_fuzz_test_template()
        elif template_type == "security":
            return self._get_security_test_template()
        else:
            return self._get_default_test_template()
    
    def _get_unit_test_template(self) -> str:
        """Get unit test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ContractName.sol";

contract ContractNameTest is Test {
    ContractName public contractName;
    
    // Test accounts
    address public owner = address(0x1);
    address public user1 = address(0x2);
    address public user2 = address(0x3);
    
    function setUp() public {
        vm.prank(owner);
        contractName = new ContractName();
    }
    
    function testInitialState() public {
        // Test initial contract state
        assertEq(contractName.owner(), owner);
        // Add more initial state assertions
    }
    
    function testBasicFunctionality() public {
        // Test basic contract functionality
        vm.prank(user1);
        contractName.someFunction();
        
        // Add assertions
        assertTrue(true);
    }
    
    function testAccessControl() public {
        // Test access control mechanisms
        vm.prank(user1);
        vm.expectRevert("Unauthorized");
        contractName.onlyOwnerFunction();
    }
    
    function testErrorConditions() public {
        // Test error conditions and edge cases
        vm.expectRevert("Invalid input");
        contractName.functionWithValidation(0);
    }
    
    function testEvents() public {
        // Test event emissions
        vm.expectEmit(true, true, true, true);
        emit SomeEvent(user1, 100);
        
        vm.prank(user1);
        contractName.functionThatEmitsEvent(100);
    }
}
        """
    
    def _get_integration_test_template(self) -> str:
        """Get integration test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/Contract1.sol";
import "../src/Contract2.sol";

contract IntegrationTest is Test {
    Contract1 public contract1;
    Contract2 public contract2;
    
    // Test accounts
    address public owner = address(0x1);
    address public user1 = address(0x2);
    address public user2 = address(0x3);
    
    function setUp() public {
        vm.prank(owner);
        contract1 = new Contract1();
        contract2 = new Contract2(address(contract1));
    }
    
    function testWorkflowIntegration() public {
        // Test complete workflow across contracts
        vm.prank(user1);
        contract1.step1();
        
        vm.prank(user1);
        contract2.step2();
        
        // Verify final state
        assertEq(contract1.getState(), 2);
        assertEq(contract2.getState(), 1);
    }
    
    function testCrossContractInteraction() public {
        // Test interactions between contracts
        vm.prank(user1);
        contract2.callContract1Function();
        
        // Verify the interaction worked
        assertTrue(contract1.wasCalledByContract2());
    }
}
        """
    
    def _get_invariant_test_template(self) -> str:
        """Get invariant test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ContractName.sol";

contract InvariantTest is Test {
    ContractName public contractName;
    
    function setUp() public {
        contractName = new ContractName();
        
        // Target contract for invariant testing
        targetContract(address(contractName));
    }
    
    function invariant_totalSupplyAlwaysPositive() public {
        // Example invariant: total supply should never be negative
        assertGe(contractName.totalSupply(), 0);
    }
    
    function invariant_balancesSumToTotalSupply() public {
        // Example invariant: sum of all balances equals total supply
        uint256 totalBalances = 0;
        address[] memory accounts = contractName.getAllAccounts();
        
        for (uint256 i = 0; i < accounts.length; i++) {
            totalBalances += contractName.balanceOf(accounts[i]);
        }
        
        assertEq(totalBalances, contractName.totalSupply());
    }
    
    function invariant_ownershipIsConsistent() public {
        // Example invariant: contract should always have a valid owner
        assertNotEq(contractName.owner(), address(0));
    }
}
        """
    
    def _get_fuzz_test_template(self) -> str:
        """Get fuzz test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ContractName.sol";

contract FuzzTest is Test {
    ContractName public contractName;
    
    function setUp() public {
        contractName = new ContractName();
    }
    
    function testFuzzDeposit(uint256 amount) public {
        amount = bound(amount, 1, 1000e18);
        
        vm.deal(address(this), amount);
        uint256 initialBalance = contractName.totalBalance();
        
        contractName.deposit{value: amount}();
        
        assertEq(contractName.totalBalance(), initialBalance + amount);
    }
    
    function testFuzzWithdraw(uint256 depositAmount, uint256 withdrawAmount) public {
        depositAmount = bound(depositAmount, 1, 1000e18);
        withdrawAmount = bound(withdrawAmount, 1, depositAmount);
        
        // Setup: deposit first
        vm.deal(address(this), depositAmount);
        contractName.deposit{value: depositAmount}();
        
        // Test: withdraw
        contractName.withdraw(withdrawAmount);
        
        assertEq(contractName.totalBalance(), depositAmount - withdrawAmount);
    }
}
        """
    
    def _get_security_test_template(self) -> str:
        """Get security test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ContractName.sol";

contract SecurityTest is Test {
    ContractName public contractName;
    
    function setUp() public {
        contractName = new ContractName();
    }
    
    function testAccessControl() public {
        vm.expectRevert("Ownable: caller is not the owner");
        contractName.onlyOwnerFunction();
    }
    
    function testReentrancyProtection() public {
        vm.expectRevert("ReentrancyGuard: reentrant call");
        // Test reentrancy attack
    }
    
    function testIntegerOverflow() public {
        // Test integer overflow scenarios
        uint256 maxValue = type(uint256).max;
        
        vm.expectRevert();
        contractName.functionWithArithmetic(maxValue, 1);
    }
    
    function testFrontRunningProtection() public {
        // Test front-running protection mechanisms
        // Implementation depends on specific contract logic
    }
}
        """
    
    def _get_default_test_template(self) -> str:
        """Get default test template."""
        return """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ContractName.sol";

contract ContractNameTest is Test {
    ContractName public contractName;
    
    function setUp() public {
        contractName = new ContractName();
    }
    
    function testExample() public {
        assertTrue(true);
    }
}
        """
    
    # Template usage instructions
    async def _get_template_usage_instructions(self, template_type: str) -> List[str]:
        """Get usage instructions for a template."""
        common_instructions = [
            "1. Copy the template to your test directory",
            "2. Replace 'ContractName' with your actual contract name",
            "3. Update import paths to match your project structure",
            "4. Customize test cases for your specific contract logic",
            "5. Run tests with 'forge test'"
        ]
        
        specific_instructions = {
            "unit": [
                "6. Focus on testing individual functions",
                "7. Test both success and failure scenarios",
                "8. Verify state changes and event emissions"
            ],
            "integration": [
                "6. Test complete workflows across multiple contracts",
                "7. Verify cross-contract interactions",
                "8. Test user journey scenarios"
            ],
            "invariant": [
                "6. Define system invariants that should always hold",
                "7. Use targetContract() to specify contracts to test",
                "8. Run with 'forge test --invariant'"
            ],
            "fuzz": [
                "6. Use bound() to limit fuzz input ranges",
                "7. Test with random inputs to find edge cases",
                "8. Configure fuzz runs in foundry.toml"
            ],
            "security": [
                "6. Test access control mechanisms",
                "7. Verify protection against common attacks",
                "8. Test with adversarial inputs"
            ]
        }
        
        return common_instructions + specific_instructions.get(template_type, [])
    
    # Analysis and documentation methods
    def _generate_project_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on project analysis."""
        recommendations = []
        
        if not analysis.get("is_foundry_project"):
            recommendations.append("Initialize as Foundry project with 'forge init --force'")
        
        if not analysis.get("contracts"):
            recommendations.append("Add smart contracts to the src/ directory")
        
        if not analysis.get("tests"):
            recommendations.append("Create test files in the test/ directory")
            recommendations.append("Use the MCP test templates to get started quickly")
        
        if len(analysis.get("contracts", [])) > len(analysis.get("tests", [])):
            recommendations.append("Add more test coverage - you have more contracts than test files")
        
        return recommendations
    
    def _analyze_coverage_data(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coverage data and provide insights."""
        analysis = {
            "status": "success" if coverage_data.get("success") else "error",
            "insights": [],
            "recommendations": []
        }
        
        if coverage_data.get("success") and coverage_data.get("summary"):
            summary = coverage_data["summary"]
            coverage_pct = summary.get("coverage_percentage", 0)
            
            if coverage_pct < 50:
                analysis["insights"].append("Low test coverage detected")
                analysis["recommendations"].append("Focus on adding basic test coverage")
            elif coverage_pct < 80:
                analysis["insights"].append("Moderate test coverage")
                analysis["recommendations"].append("Add tests for edge cases and error conditions")
            else:
                analysis["insights"].append("Good test coverage")
                analysis["recommendations"].append("Consider adding invariant and fuzz tests")
        
        return analysis
    
    # Documentation content methods
    async def _get_getting_started_guide(self) -> str:
        """Get getting started guide content."""
        return """
# Getting Started with Smart Contract Testing

## Overview
This guide helps you get started with comprehensive smart contract testing using Foundry.

## Prerequisites
- Foundry installed (`curl -L https://foundry.paradigm.xyz | bash`)
- Basic Solidity knowledge
- Understanding of testing concepts

## Quick Start
1. Navigate to your project directory
2. Initialize the testing agent: Use the `initialize_protocol_testing_agent` tool
3. Follow the guided workflow to create comprehensive tests
4. Run tests with `forge test`

## Testing Philosophy
- Test early and often
- Focus on critical paths and edge cases
- Include security testing from the start
- Maintain high test coverage
- Document test scenarios clearly
        """
    
    async def _get_foundry_guide(self) -> str:
        """Get Foundry guide content."""
        return """
# Foundry Testing Guide

## Key Commands
- `forge test`: Run all tests
- `forge test --coverage`: Run tests with coverage
- `forge test --gas-report`: Generate gas usage report
- `forge test --invariant`: Run invariant tests
- `forge test --fuzz`: Run fuzz tests

## Test Structure
- Use `setUp()` for test initialization
- Prefix test functions with `test`
- Use `vm.prank()` for access control testing
- Use `vm.expectRevert()` for error testing
- Use `vm.expectEmit()` for event testing

## Best Practices
- Keep tests isolated and independent
- Use descriptive test names
- Test both success and failure scenarios
- Include gas usage tests
- Organize tests by functionality
        """
    
    async def _get_security_testing_guide(self) -> str:
        """Get security testing guide content."""
        return """
# Security Testing Best Practices

## Common Vulnerabilities to Test
1. **Access Control**: Verify only authorized users can execute functions
2. **Reentrancy**: Test protection against reentrancy attacks
3. **Integer Overflow**: Test arithmetic operations
4. **Front-running**: Test MEV protection mechanisms
5. **Oracle Manipulation**: Test price feed dependencies

## Testing Strategies
- Use adversarial thinking
- Test with malicious inputs
- Verify invariants under attack
- Test economic incentives
- Include integration security tests

## Tools and Techniques
- Fuzz testing for edge cases
- Invariant testing for system properties
- Mock malicious contracts
- Simulate attack scenarios
        """
    
    async def _get_coverage_strategies_guide(self) -> str:
        """Get coverage strategies guide content."""
        return """
# Test Coverage Strategies

## Coverage Types
1. **Line Coverage**: Percentage of code lines executed
2. **Branch Coverage**: Percentage of decision branches taken
3. **Function Coverage**: Percentage of functions called
4. **Statement Coverage**: Percentage of statements executed

## Coverage Targets
- **Minimum**: 80% line coverage
- **Good**: 90% line coverage with 85% branch coverage
- **Excellent**: 95% line coverage with 90% branch coverage

## Strategies
- Start with critical functions
- Add edge case tests
- Include error condition tests
- Test all access control paths
- Verify all event emissions
        """
    
    async def _get_troubleshooting_guide(self) -> str:
        """Get troubleshooting guide content."""
        return """
# Troubleshooting Common Issues

## Common Problems and Solutions

### Tests Not Running
- Ensure test files have `.t.sol` extension
- Check that test functions start with `test`
- Verify imports are correct

### Coverage Issues
- Ensure forge-std is properly imported
- Check that contracts are in src/ directory
- Verify foundry.toml configuration

### Gas Estimation Errors
- Use `--gas-limit` flag for high-gas tests
- Check for infinite loops in contracts
- Verify external calls are properly mocked

### Access Control Tests Failing
- Use `vm.prank()` to simulate different callers
- Check that modifiers are properly implemented
- Verify test expectations match contract behavior

## Getting Help
- Check Foundry documentation
- Review test templates
- Use the MCP testing tools for guidance
        """ 