"""
Smart Contract Testing MCP Server - Testing Resources (Refactored)

This module provides the knowledge base for the MCP, including structured patterns
and best-practice templates for test generation. All dynamic analysis logic has been
moved to the tools module.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class TestingResources:
    """
    Manages access to test templates, documentation, and structured testing patterns.
    This is now a pure knowledge base without dynamic analysis capabilities.
    """
    
    def __init__(self):
        """Initialize testing resources."""
        self.server_root = Path(__file__).parent.parent.resolve()
        self.templates_dir = self.server_root / "templates"
        self.docs_dir = self.server_root / "docs"
        logger.info(f"Testing resources initialized - Server root: {self.server_root}")
    
    def register_resources(self, mcp) -> None:
        """Register all testing resources with the MCP server."""
        
        # Foundry testing patterns resource with actionable patterns
        @mcp.resource("testing://foundry-patterns")
        async def get_foundry_testing_patterns() -> Dict[str, Any]:
            """Access comprehensive, structured Foundry testing patterns."""
            return {
                "name": "Foundry Testing Patterns",
                "description": "Actionable patterns and best practices for Foundry testing with concrete code snippets.",
                "version": "2.0.0",
                "content": {
                    "test_organization": {
                        "description": "Recommended test file organization grouped by functionality and test type.",
                        "file_structure_pattern": """
test/
├── {{CONTRACT_NAME}}.t.sol                    # Core unit and integration tests
├── {{CONTRACT_NAME}}.invariant.t.sol          # Invariant/property-based tests
├── {{CONTRACT_NAME}}.security.t.sol           # Security-focused tests
├── {{CONTRACT_NAME}}.fork.t.sol               # Mainnet fork tests
├── handlers/
│   └── {{CONTRACT_NAME}}Handler.sol           # Handler for invariant testing
├── mocks/
│   ├── Mock{{DEPENDENCY_NAME}}.sol
│   └── MockERC20.sol
└── utils/
    ├── TestHelper.sol
    └── TestConstants.sol
                        """,
                        "naming_conventions": {
                            "test_files": "{{CONTRACT_NAME}}.{{TYPE}}.t.sol where TYPE is optional (security, invariant, fork)",
                            "test_functions": "test_{{FUNCTION_NAME}}_{{WHEN_CONDITION}}_{{SHOULD_RESULT}} - Example: test_transfer_whenAmountExceedsBalance_shouldRevert",
                            "test_contracts": "{{CONTRACT_NAME}}Test - Example: TokenTest, VaultTest",
                            "handler_contracts": "{{CONTRACT_NAME}}Handler - For invariant testing"
                        }
                    },
                    "testing_patterns": {
                        "setup_patterns": [
                            {
                                "name": "Standard Setup Pattern",
                                "description": "Using setUp() to initialize contracts and test accounts consistently",
                                "code_snippet": """
function setUp() public {
    {{OWNER_ACCOUNT}} = makeAddr("owner");
    {{USER_ACCOUNT}} = makeAddr("user");
    {{ATTACKER_ACCOUNT}} = makeAddr("attacker");
    
    vm.prank({{OWNER_ACCOUNT}});
    {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}();
    
    // Setup initial state
    vm.deal({{USER_ACCOUNT}}, 100 ether);
    vm.deal({{ATTACKER_ACCOUNT}}, 10 ether);
}
                                """
                            },
                            {
                                "name": "Mock Setup Pattern",
                                "description": "Setting up mock contracts for external dependencies",
                                "code_snippet": """
function setUp() public {
    mockToken = new MockERC20("Mock Token", "MTK", 18);
    mockOracle = new MockPriceOracle();
    
    vm.prank({{OWNER_ACCOUNT}});
    {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}(
        address(mockToken),
        address(mockOracle)
    );
}
                                """
                            }
                        ],
                        "assertion_patterns": [
                            {
                                "name": "State Verification",
                                "description": "Asserting contract state changes with descriptive messages",
                                "code_snippet": """
assertEq({{CONTRACT_INSTANCE}}.owner(), {{EXPECTED_OWNER}}, "Owner should be set correctly");
assertEq({{CONTRACT_INSTANCE}}.balanceOf({{USER_ACCOUNT}}), {{EXPECTED_BALANCE}}, "User balance mismatch");
                                """
                            },
                            {
                                "name": "Event Emission Testing",
                                "description": "Verifying events are emitted with correct parameters",
                                "code_snippet": """
vm.expectEmit(true, true, true, true);
emit {{EVENT_NAME}}({{PARAM1}}, {{PARAM2}}, {{PARAM3}});

vm.prank({{CALLER_ACCOUNT}});
{{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}({{FUNCTION_PARAMS}});
                                """
                            },
                            {
                                "name": "Error Condition Testing",
                                "description": "Testing revert conditions with specific error messages",
                                "code_snippet": """
vm.expectRevert({{CONTRACT_NAME}}.{{ERROR_NAME}}.selector);
vm.prank({{UNAUTHORIZED_ACCOUNT}});
{{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();

// For string error messages
vm.expectRevert("{{ERROR_MESSAGE}}");
{{CONTRACT_INSTANCE}}.{{FUNCTION_THAT_REVERTS}}();
                                """
                            }
                        ],
                        "advanced_patterns": [
                            {
                                "name": "Time Manipulation",
                                "description": "Testing time-dependent functionality",
                                "code_snippet": """
// Fast forward time
vm.warp(block.timestamp + {{TIME_DELTA}});

// Test time-based conditions
assertTrue({{CONTRACT_INSTANCE}}.isExpired(), "Contract should be expired");
                                """
                            },
                            {
                                "name": "Fork Testing Pattern",
                                "description": "Testing against mainnet state",
                                "code_snippet": """
function setUp() public {
    vm.createFork(vm.envString("MAINNET_RPC_URL"));
    {{REAL_CONTRACT}} = {{INTERFACE}}({{MAINNET_ADDRESS}});
}

function test_{{FUNCTION_NAME}}_onMainnetFork() public {
    // Test with real mainnet state
    uint256 realBalance = {{REAL_CONTRACT}}.balanceOf({{WHALE_ADDRESS}});
    assertGt(realBalance, 0, "Whale should have balance");
}
                                """
                            }
                        ]
                    },
                    "best_practices": {
                        "test_isolation": "Each test should be completely independent - use setUp() for common initialization",
                        "descriptive_naming": "Test names should read like documentation: test_function_whenCondition_shouldResult",
                        "comprehensive_coverage": "Test success paths, error conditions, edge cases, and security scenarios",
                        "gas_awareness": "Include gas consumption tests for critical functions",
                        "security_first": "Every privileged function needs access control tests, every external call needs reentrancy tests"
                    }
                }
            }
        
        # Security patterns resource with machine-readable test cases
        @mcp.resource("testing://security-patterns")
        async def get_security_testing_patterns() -> Dict[str, Any]:
            """Get structured security patterns with comprehensive test case examples."""
            return {
                "name": "Foundry Security Test Patterns",
                "description": "A comprehensive library of security vulnerabilities and how to test for them effectively.",
                "version": "2.0.0",
                "categories": {
                    "access_control": {
                        "description": "Testing authorization and permission mechanisms",
                        "patterns": [
                            {
                                "vulnerability": "Unauthorized Function Access",
                                "description": "Ensures functions with access modifiers cannot be called by unauthorized accounts",
                                "severity": "High",
                                "test_case_snippet": """
function test_{{FUNCTION_NAME}}_whenCalledByUnauthorized_shouldRevert() public {
    address unauthorized = makeAddr("unauthorized");
    
    vm.prank(unauthorized);
    vm.expectRevert({{CONTRACT_NAME}}.Unauthorized.selector);
    {{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();
}

function test_{{FUNCTION_NAME}}_whenCalledByOwner_shouldSucceed() public {
    vm.prank({{OWNER_ACCOUNT}});
    {{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();
    // Add success assertions
}
                                """
                            },
                            {
                                "vulnerability": "Role-Based Access Control",
                                "description": "Testing role-based permissions with proper role management",
                                "severity": "High",
                                "test_case_snippet": """
function test_roleManagement_whenGrantingRole_shouldWork() public {
    bytes32 role = {{CONTRACT_INSTANCE}}.{{ROLE_NAME}}();
    
    vm.prank({{ADMIN_ACCOUNT}});
    {{CONTRACT_INSTANCE}}.grantRole(role, {{USER_ACCOUNT}});
    
    assertTrue({{CONTRACT_INSTANCE}}.hasRole(role, {{USER_ACCOUNT}}));
}

function test_protectedFunction_whenUserLacksRole_shouldRevert() public {
    vm.prank({{USER_ACCOUNT}});
    vm.expectRevert({{ACCESS_CONTROL_ERROR}});
    {{CONTRACT_INSTANCE}}.{{ROLE_PROTECTED_FUNCTION}}();
}
                                """
                            }
                        ]
                    },
                    "reentrancy": {
                        "description": "Testing protection against reentrancy attacks",
                        "patterns": [
                            {
                                "vulnerability": "Single-Function Reentrancy",
                                "description": "Tests protection against reentrancy attacks on withdrawal functions",
                                "severity": "Critical",
                                "test_case_snippet": """
contract MaliciousReentrant {
    {{CONTRACT_NAME}} public target;
    bool public attacked = false;
    
    constructor(address _target) {
        target = {{CONTRACT_NAME}}(_target);
    }
    
    function attack() external payable {
        target.withdraw();
    }
    
    receive() external payable {
        if (!attacked) {
            attacked = true;
            target.withdraw(); // Attempt reentrancy
        }
    }
}

function test_withdraw_whenReentrant_shouldRevert() public {
    MaliciousReentrant attacker = new MaliciousReentrant(address({{CONTRACT_INSTANCE}}));
    
    // Setup: fund attacker's deposit
    vm.deal(address(attacker), 1 ether);
    vm.prank(address(attacker));
    {{CONTRACT_INSTANCE}}.deposit{value: 1 ether}();
    
    // Attack should fail
    vm.expectRevert("ReentrancyGuard: reentrant call");
    attacker.attack();
}
                                """
                            }
                        ]
                    },
                    "economic_exploits": {
                        "description": "Testing economic attack vectors and incentive misalignment",
                        "patterns": [
                            {
                                "vulnerability": "Flash Loan Attack",
                                "description": "Testing protection against flash loan manipulation",
                                "severity": "Critical",
                                "test_case_snippet": """
contract FlashLoanAttacker {
    {{CONTRACT_NAME}} public target;
    IERC20 public token;
    
    constructor(address _target, address _token) {
        target = {{CONTRACT_NAME}}(_target);
        token = IERC20(_token);
    }
    
    function attack(uint256 amount) external {
        // Simulate flash loan
        vm.assume(token.transfer(address(this), amount));
        
        // Perform manipulation
        target.{{VULNERABLE_FUNCTION}}();
        
        // Repay flash loan
        token.transfer(msg.sender, amount);
    }
}

function test_{{FUNCTION_NAME}}_whenFlashLoanAttack_shouldBeMitigated() public {
    FlashLoanAttacker attacker = new FlashLoanAttacker(
        address({{CONTRACT_INSTANCE}}),
        address({{TOKEN_ADDRESS}})
    );
    
    uint256 flashLoanAmount = 1000000e18;
    
    // Attack should either revert or be ineffective
    vm.expectRevert(); // or check that attack has no effect
    attacker.attack(flashLoanAmount);
}
                                """
                            }
                        ]
                    },
                    "oracle_manipulation": {
                        "description": "Testing oracle price manipulation resistance",
                        "patterns": [
                            {
                                "vulnerability": "Price Oracle Manipulation",
                                "description": "Testing resistance to oracle price manipulation attacks",
                                "severity": "High",
                                "test_case_snippet": """
function test_priceDependent_whenOracleManipulated_shouldResist() public {
    // Record initial state
    uint256 initialValue = {{CONTRACT_INSTANCE}}.getTotalValue();
    
    // Manipulate oracle price dramatically
    mockOracle.setPrice({{MANIPULATED_PRICE}});
    
    // Function should either revert or use safeguards
    vm.expectRevert("Price manipulation detected");
    {{CONTRACT_INSTANCE}}.{{PRICE_DEPENDENT_FUNCTION}}();
    
    // Or verify safeguards limit impact
    uint256 newValue = {{CONTRACT_INSTANCE}}.getTotalValue();
    uint256 maxAllowedChange = initialValue * {{MAX_CHANGE_PCT}} / 100;
    assertLt(
        newValue > initialValue ? newValue - initialValue : initialValue - newValue,
        maxAllowedChange,
        "Price change should be limited by safeguards"
    );
}
                                """
                            }
                        ]
                    }
                }
            }
        
        # Enhanced test templates with placeholders
        @mcp.resource("testing://templates/{template_type}")
        async def get_test_template(template_type: str) -> Dict[str, Any]:
            """Get test templates with dynamic placeholders for code generation."""
            template_content, placeholders = await self._load_template(template_type)
            
            return {
                "name": f"{template_type.title()} Test Template",
                "description": f"Best-practice template for {template_type} testing scenarios",
                "template_type": template_type,
                "content": template_content,
                "placeholders": placeholders,
                "usage_instructions": self._get_template_usage_instructions(template_type)
            }
        
        # Available templates resource
        @mcp.resource("testing://templates")
        async def get_available_templates() -> Dict[str, Any]:
            """Get list of available test templates with descriptions."""
            return {
                "name": "Available Test Templates",
                "description": "Comprehensive test templates for different testing scenarios",
                "templates": {
                    "unit": {
                        "name": "Unit Test Template",
                        "description": "Template for testing individual contract functions with comprehensive coverage",
                        "use_cases": [
                            "Function-level testing with edge cases",
                            "State variable validation",
                            "Access control verification",
                            "Error condition testing with specific error types"
                        ],
                        "placeholders": ["{{CONTRACT_NAME}}", "{{OWNER_ACCOUNT}}", "{{USER_ACCOUNT}}"]
                    },
                    "integration": {
                        "name": "Integration Test Template", 
                        "description": "Template for testing complex workflows and contract interactions",
                        "use_cases": [
                            "Multi-contract workflow testing",
                            "User journey simulation",
                            "Cross-contract interaction validation",
                            "End-to-end scenario testing"
                        ],
                        "placeholders": ["{{CONTRACT_A_NAME}}", "{{CONTRACT_B_NAME}}", "{{WORKFLOW_NAME}}"]
                    },
                    "invariant": {
                        "name": "Invariant Test Template (Handler Pattern)",
                        "description": "Best-practice template for property-based/stateful fuzz testing using Handler pattern",
                        "use_cases": [
                            "System invariant verification",
                            "Property preservation under random state changes",
                            "Protocol correctness validation",
                            "Complex stateful fuzzing scenarios"
                        ],
                        "placeholders": ["{{CONTRACT_NAME}}", "{{INVARIANT_DESCRIPTION}}", "{{HANDLER_FUNCTIONS}}"]
                    },
                    "security": {
                        "name": "Security Test Template",
                        "description": "Template for comprehensive security testing with attack scenarios",
                        "use_cases": [
                            "Access control penetration testing",
                            "Reentrancy attack simulation",
                            "Economic exploit testing",
                            "Oracle manipulation resistance"
                        ],
                        "placeholders": ["{{CONTRACT_NAME}}", "{{ATTACK_SCENARIOS}}", "{{SECURITY_ASSERTIONS}}"]
                    },
                    "fork": {
                        "name": "Fork Test Template",
                        "description": "Template for testing against real mainnet state",
                        "use_cases": [
                            "Integration with existing protocols",
                            "Real-world state validation",
                            "Mainnet behavior verification",
                            "Migration testing"
                        ],
                        "placeholders": ["{{FORK_BLOCK}}", "{{MAINNET_ADDRESSES}}", "{{REAL_CONTRACT_INTERFACES}}"]
                    },
                    "helper": {
                        "name": "Test Helper Utilities Template",
                        "description": "Template for centralized helper functions to reduce code duplication",
                        "use_cases": [
                            "Account setup and funding utilities",
                            "Common state manipulation helpers",
                            "Reusable assertion patterns",
                            "Test data generation functions",
                            "Gas measurement and performance testing",
                            "Logging and debugging utilities"
                        ],
                        "placeholders": ["{{CONTRACT_NAME}}", "{{CONTRACT_INSTANCE}}", "{{TEST_DATA_TYPE}}", "{{STATE_ASSERTIONS}}"]
                    }
                }
            }
        
        # Testing methodology documentation
        @mcp.resource("testing://documentation")
        async def get_testing_documentation() -> Dict[str, Any]:
            """Get comprehensive testing documentation and methodologies."""
            return {
                "name": "Smart Contract Testing Documentation",
                "description": "Comprehensive testing guides and professional methodologies",
                "version": "2.0.0",
                "sections": {
                    "foundry_methodology": {
                        "title": "Foundry Testing Methodology",
                        "content": {
                            "test_types": {
                                "unit": "Test individual functions in isolation with comprehensive edge cases",
                                "integration": "Test complex workflows and multi-contract interactions", 
                                "invariant": "Test system properties that should always hold using stateful fuzzing",
                                "fork": "Test against real mainnet state for realistic validation",
                                "security": "Test specific attack vectors and defensive mechanisms"
                            },
                            "test_structure": {
                                "setup": "Use setUp() for consistent test initialization",
                                "naming": "Use descriptive names: test_function_whenCondition_shouldResult",
                                "isolation": "Each test should be completely independent",
                                "assertions": "Use descriptive assertion messages for debugging"
                            }
                        }
                    },
                    "security_methodology": {
                        "title": "Security Testing Best Practices",
                        "content": {
                            "attack_vectors": [
                                "Access Control: Test unauthorized access to privileged functions",
                                "Reentrancy: Simulate reentrancy attacks on external calls",
                                "Economic: Test flash loan attacks and price manipulation",
                                "Oracle: Test oracle manipulation and data freshness",
                                "Governance: Test voting manipulation and proposal attacks"
                            ],
                            "defensive_testing": [
                                "Verify all access controls function correctly",
                                "Test circuit breakers and emergency stops",
                                "Validate input sanitization and bounds checking",
                                "Test rate limiting and cooldown mechanisms"
                            ]
                        }
                    },
                    "coverage_strategy": {
                        "title": "Test Coverage Strategy",
                        "content": {
                            "targets": {
                                "minimum": "80% line coverage with basic error testing",
                                "production": "90% line coverage with 85% branch coverage",
                                "audit_ready": "95% line coverage with comprehensive security testing"
                            },
                            "priorities": [
                                "Critical functions first (admin, money movement)",
                                "Error conditions and edge cases",
                                "Security-sensitive code paths",
                                "Integration points and external calls"
                            ]
                        }
                    }
                }
            }
        
        logger.info("Testing resources registered successfully")
    
    # Template loading and generation methods
    async def _load_template(self, template_type: str) -> Tuple[str, List[str]]:
        """Load template content with dynamic placeholders."""
        templates = {
            "unit": (self._get_unit_test_template(), [
                "{{CONTRACT_NAME}}", "{{OWNER_ACCOUNT}}", "{{USER_ACCOUNT}}", 
                "{{FUNCTION_NAME}}", "{{EXPECTED_VALUE}}", "{{ERROR_TYPE}}"
            ]),
            "integration": (self._get_integration_test_template(), [
                "{{CONTRACT_A_NAME}}", "{{CONTRACT_B_NAME}}", "{{WORKFLOW_NAME}}",
                "{{INTERACTION_FUNCTION}}", "{{EXPECTED_STATE}}"
            ]),
            "invariant": (self._get_invariant_test_template(), [
                "{{CONTRACT_NAME}}", "{{HANDLER_NAME}}", "{{INVARIANT_DESCRIPTION}}",
                "{{INVARIANT_CONDITION}}", "{{HANDLER_FUNCTIONS}}"
            ]),
            "security": (self._get_security_test_template(), [
                "{{CONTRACT_NAME}}", "{{ATTACK_CONTRACT}}", "{{VULNERABILITY_TYPE}}",
                "{{PROTECTION_MECHANISM}}", "{{EXPECTED_DEFENSE}}"
            ]),
            "fork": (self._get_fork_test_template(), [
                "{{FORK_URL}}", "{{FORK_BLOCK}}", "{{MAINNET_CONTRACT}}", 
                "{{REAL_ADDRESS}}", "{{WHALE_ADDRESS}}"
            ]),
            "helper": (self._get_helper_test_template(), [
                "{{CONTRACT_NAME}}", "{{CONTRACT_INSTANCE}}", "{{TEST_DATA_TYPE}}",
                "{{SCENARIO_1_SETUP}}", "{{SCENARIO_2_SETUP}}", "{{SCENARIO_3_SETUP}}",
                "{{STATE_ASSERTIONS}}", "{{DEPOSIT_WORKFLOW_STEPS}}", "{{WITHDRAWAL_WORKFLOW_STEPS}}",
                "{{ADDITIONAL_DATA_FIELDS}}", "{{STATE_LOGGING_CODE}}"
            ])
        }
        
        return templates.get(template_type, (self._get_default_test_template(), ["{{CONTRACT_NAME}}"]))
    
    def _get_unit_test_template(self) -> str:
        """Best-practice unit test template with comprehensive patterns."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import "../src/{{CONTRACT_NAME}}.sol";

contract {{CONTRACT_NAME}}Test is Test {
    {{CONTRACT_NAME}} public {{CONTRACT_INSTANCE}};

    // Test accounts using makeAddr for better debugging
    address public {{OWNER_ACCOUNT}} = makeAddr("owner");
    address public {{USER_ACCOUNT}} = makeAddr("user");
    address public {{OTHER_USER}} = makeAddr("otherUser");

    // Events for testing (copy from contract)
    event {{EVENT_NAME}}(address indexed user, uint256 amount);

    function setUp() public {
        vm.prank({{OWNER_ACCOUNT}});
        {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}();
        
        // Setup initial balances if needed
        vm.deal({{USER_ACCOUNT}}, 10 ether);
        vm.deal({{OTHER_USER}}, 10 ether);
    }

    // ====== BASIC FUNCTIONALITY TESTS ======

    function test_initialState() public {
        assertEq({{CONTRACT_INSTANCE}}.owner(), {{OWNER_ACCOUNT}}, "Owner should be set correctly");
        // Add other initial state assertions
    }

    function test_{{FUNCTION_NAME}}_whenValidInput_shouldSucceed() public {
        // Arrange
        uint256 {{INPUT_VALUE}} = 100;
        
        // Act
        vm.prank({{USER_ACCOUNT}});
        {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}({{INPUT_VALUE}});
        
        // Assert
        assertEq({{CONTRACT_INSTANCE}}.{{STATE_VARIABLE}}(), {{EXPECTED_VALUE}}, "State should be updated correctly");
    }

    // ====== ERROR CONDITION TESTS ======

    function test_{{FUNCTION_NAME}}_whenUnauthorized_shouldRevert() public {
        vm.prank({{USER_ACCOUNT}});
        vm.expectRevert({{CONTRACT_NAME}}.Unauthorized.selector);
        {{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();
    }

    function test_{{FUNCTION_NAME}}_whenInvalidInput_shouldRevert() public {
        vm.prank({{USER_ACCOUNT}});
        vm.expectRevert("{{ERROR_MESSAGE}}");
        {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(0); // Invalid input
    }

    // ====== EVENT EMISSION TESTS ======

    function test_{{FUNCTION_NAME}}_whenCalled_shouldEmitEvent() public {
        uint256 amount = 100;
        
        vm.expectEmit(true, true, true, true);
        emit {{EVENT_NAME}}({{USER_ACCOUNT}}, amount);
        
        vm.prank({{USER_ACCOUNT}});
        {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(amount);
    }

    // ====== EDGE CASE TESTS ======

    function test_{{FUNCTION_NAME}}_whenMaxValue_shouldWork() public {
        uint256 maxValue = type(uint256).max;
        
        vm.prank({{USER_ACCOUNT}});
        // Should either work or revert gracefully
        try {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(maxValue) {
            // If it succeeds, verify state is correct
            assertTrue({{CONTRACT_INSTANCE}}.{{STATE_VARIABLE}}() >= 0);
        } catch {
            // If it reverts, that's also acceptable for edge cases
        }
    }

    // ====== FUZZ TESTS ======

    function testFuzz_{{FUNCTION_NAME}}(uint256 {{FUZZ_INPUT}}) public {
        {{FUZZ_INPUT}} = bound({{FUZZ_INPUT}}, 1, 1000000e18);
        
        vm.prank({{USER_ACCOUNT}});
        {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}({{FUZZ_INPUT}});
        
        // Verify invariants hold
        assertTrue({{CONTRACT_INSTANCE}}.{{INVARIANT_CHECK}}(), "Invariant should hold");
    }
}"""

    def _get_invariant_test_template(self) -> str:
        """Best-practice invariant test template using Handler pattern."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {StdInvariant, Test} from "forge-std/StdInvariant.sol";
import {{{HANDLER_NAME}}} from "./handlers/{{HANDLER_NAME}}.sol";
import {{{CONTRACT_NAME}}} from "../../src/{{CONTRACT_NAME}}.sol";

/**
 * @title {{CONTRACT_NAME}} Invariant Tests
 * @notice Tests system-level properties that should always hold
 * @dev Uses Handler pattern for effective stateful fuzzing
 */
contract {{CONTRACT_NAME}}InvariantTest is StdInvariant, Test {
    {{CONTRACT_NAME}} public {{CONTRACT_INSTANCE}};
    {{HANDLER_NAME}} public handler;

    function setUp() public {
        // Deploy contract
        {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}();
        
        // Deploy handler with reference to contract
        handler = new {{HANDLER_NAME}}({{CONTRACT_INSTANCE}});
        
        // Configure invariant testing
        targetContract(address(handler));
        
        // Optional: Exclude specific functions from fuzzing
        // bytes4[] memory selectors = new bytes4[](1);
        // selectors[0] = {{HANDLER_NAME}}.functionToExclude.selector;
        // targetSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
    }

    // ====== CORE INVARIANTS ======

    function invariant_{{INVARIANT_NAME}}() public view {
        // {{INVARIANT_DESCRIPTION}}
        assertTrue(
            {{CONTRACT_INSTANCE}}.{{INVARIANT_CONDITION}}(),
            "{{INVARIANT_DESCRIPTION}} should always hold"
        );
    }

    function invariant_balanceConsistency() public view {
        // Example: Total supply should equal sum of all balances
        uint256 totalSupply = {{CONTRACT_INSTANCE}}.totalSupply();
        uint256 handlerBalance = {{CONTRACT_INSTANCE}}.balanceOf(address(handler));
        
        // Add more balance checks as needed
        assertGe(totalSupply, handlerBalance, "Total supply should be >= handler balance");
    }

    function invariant_stateTransitions() public view {
        // Example: Contract should never be in invalid state
        assertTrue(
            {{CONTRACT_INSTANCE}}.isValidState(),
            "Contract should always be in valid state"
        );
    }

    // ====== CALL SUMMARY ======

    function invariant_callSummary() public view {
        // Log statistics about fuzzing runs
        console.log("--- Invariant Test Summary ---");
        console.log("Total calls made:", handler.totalCalls());
        console.log("Successful calls:", handler.successfulCalls());
        console.log("Failed calls:", handler.failedCalls());
        console.log("Current contract state:", {{CONTRACT_INSTANCE}}.{{STATE_VARIABLE}}());
    }
}

// ====== HANDLER CONTRACT TEMPLATE ======
// Create this file at: test/handlers/{{HANDLER_NAME}}.sol

/*
contract {{HANDLER_NAME}} is Test {
    {{CONTRACT_NAME}} public immutable {{CONTRACT_INSTANCE}};
    
    uint256 public totalCalls;
    uint256 public successfulCalls;
    uint256 public failedCalls;

    modifier countCall(bool success) {
        totalCalls++;
        if (success) successfulCalls++;
        else failedCalls++;
        _;
    }

    constructor({{CONTRACT_NAME}} _{{CONTRACT_INSTANCE}}) {
        {{CONTRACT_INSTANCE}} = _{{CONTRACT_INSTANCE}};
    }

    function {{HANDLER_FUNCTION}}(uint256 amount) public countCall(true) {
        amount = bound(amount, 1, 1000000e18);
        
        try {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(amount) {
            // Function succeeded
        } catch {
            // Function failed - this might be expected
            failedCalls++;
            successfulCalls--; // Adjust count
        }
    }

    // Add more handler functions for different contract interactions
}
*/"""

    def _get_security_test_template(self) -> str:
        """Comprehensive security test template with common attack patterns."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import "../src/{{CONTRACT_NAME}}.sol";

/**
 * @title {{CONTRACT_NAME}} Security Tests
 * @notice Comprehensive security testing with common attack patterns
 * @dev Tests for access control, reentrancy, economic exploits, and more
 */
contract {{CONTRACT_NAME}}SecurityTest is Test {
    {{CONTRACT_NAME}} public {{CONTRACT_INSTANCE}};

    // Test accounts
    address public owner = makeAddr("owner");
    address public user = makeAddr("user");
    address public attacker = makeAddr("attacker");
    address public admin = makeAddr("admin");

    function setUp() public {
        vm.prank(owner);
        {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}();
        
        // Setup balances for testing
        vm.deal(user, 10 ether);
        vm.deal(attacker, 5 ether);
    }

    // ====== ACCESS CONTROL TESTS ======

    function test_{{PROTECTED_FUNCTION}}_whenCalledByOwner_shouldSucceed() public {
        vm.prank(owner);
        {{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();
        
        // Verify expected state change
        assertTrue({{CONTRACT_INSTANCE}}.{{EXPECTED_STATE}}(), "Function should succeed for owner");
    }

    function test_{{PROTECTED_FUNCTION}}_whenCalledByAttacker_shouldRevert() public {
        vm.prank(attacker);
        vm.expectRevert({{CONTRACT_NAME}}.Unauthorized.selector);
        {{CONTRACT_INSTANCE}}.{{PROTECTED_FUNCTION}}();
    }

    function test_roleBasedAccess_whenUserLacksRole_shouldRevert() public {
        bytes32 requiredRole = {{CONTRACT_INSTANCE}}.{{REQUIRED_ROLE}}();
        
        vm.prank(user);
        vm.expectRevert(); // Should revert with AccessControl error
        {{CONTRACT_INSTANCE}}.{{ROLE_PROTECTED_FUNCTION}}();
    }

    // ====== REENTRANCY TESTS ======

    function test_{{FUNCTION_NAME}}_whenReentrant_shouldRevert() public {
        ReentrancyAttacker attackerContract = new ReentrancyAttacker({{CONTRACT_INSTANCE}});
        
        // Fund the attacker contract
        vm.deal(address(attackerContract), 1 ether);
        
        vm.expectRevert("ReentrancyGuard: reentrant call");
        attackerContract.attack();
    }

    // ====== ECONOMIC EXPLOIT TESTS ======

    function test_flashLoanAttack_shouldBeMitigated() public {
        FlashLoanAttacker flashAttacker = new FlashLoanAttacker({{CONTRACT_INSTANCE}});
        
        // Simulate flash loan attack
        vm.expectRevert("{{EXPECTED_PROTECTION_ERROR}}");
        flashAttacker.executeFlashLoanAttack(1000000e18);
    }

    function test_priceManipulation_shouldBeResistant() public {
        // Setup price manipulation scenario
        uint256 normalPrice = {{CONTRACT_INSTANCE}}.getCurrentPrice();
        
        // Attempt to manipulate price
        vm.prank(attacker);
        {{CONTRACT_INSTANCE}}.{{PRICE_AFFECTING_FUNCTION}}(type(uint256).max);
        
        uint256 manipulatedPrice = {{CONTRACT_INSTANCE}}.getCurrentPrice();
        
        // Price change should be limited by safeguards
        uint256 maxAllowedChange = normalPrice * 10 / 100; // 10% max change
        assertLt(
            manipulatedPrice > normalPrice ? manipulatedPrice - normalPrice : normalPrice - manipulatedPrice,
            maxAllowedChange,
            "Price manipulation should be limited"
        );
    }

    // ====== FRONT-RUNNING TESTS ======

    function test_frontRunningProtection() public {
        // Setup legitimate transaction
        uint256 userValue = 100e18;
        
        // Attacker tries to front-run
        vm.prank(attacker);
        {{CONTRACT_INSTANCE}}.{{VULNERABLE_FUNCTION}}(userValue + 1);
        
        // User's transaction should still work or be protected
        vm.prank(user);
        {{CONTRACT_INSTANCE}}.{{VULNERABLE_FUNCTION}}(userValue);
        
        // Verify protection mechanisms worked
        assertTrue({{CONTRACT_INSTANCE}}.{{PROTECTION_CHECK}}(), "Front-running protection should work");
    }

    // ====== INPUT VALIDATION TESTS ======

    function test_{{FUNCTION_NAME}}_whenZeroInput_shouldHandle() public {
        vm.prank(user);
        
        // Should either revert gracefully or handle zero correctly
        try {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(0) {
            // If it succeeds, verify state is still valid
            assertTrue({{CONTRACT_INSTANCE}}.{{INVARIANT_CHECK}}(), "Zero input should maintain invariants");
        } catch Error(string memory reason) {
            // Graceful revert is acceptable
            assertEq(reason, "{{EXPECTED_ZERO_ERROR}}", "Should revert with expected error");
        }
    }

    function test_{{FUNCTION_NAME}}_whenMaxInput_shouldHandle() public {
        vm.prank(user);
        
        uint256 maxInput = type(uint256).max;
        
        try {{CONTRACT_INSTANCE}}.{{FUNCTION_NAME}}(maxInput) {
            // Verify no overflow or unexpected behavior
            assertTrue({{CONTRACT_INSTANCE}}.{{INVARIANT_CHECK}}(), "Max input should maintain invariants");
        } catch {
            // Overflow protection is acceptable
        }
    }

    // ====== TIME MANIPULATION TESTS ======

    function test_timeBasedFunction_whenTimeManipulated_shouldResist() public {
        // Record initial state
        uint256 initialValue = {{CONTRACT_INSTANCE}}.{{TIME_DEPENDENT_VALUE}}();
        
        // Fast forward time significantly
        vm.warp(block.timestamp + 365 days);
        
        // Function should handle time jumps gracefully
        vm.prank(user);
        {{CONTRACT_INSTANCE}}.{{TIME_DEPENDENT_FUNCTION}}();
        
        // Verify reasonable behavior
        uint256 newValue = {{CONTRACT_INSTANCE}}.{{TIME_DEPENDENT_VALUE}}();
        assertGt(newValue, initialValue, "Value should increase with time");
        assertLt(newValue, initialValue * 2, "Value increase should be reasonable");
    }
}

// ====== ATTACK CONTRACT IMPLEMENTATIONS ======

contract ReentrancyAttacker {
    {{CONTRACT_NAME}} public target;
    bool public attacked = false;

    constructor({{CONTRACT_NAME}} _target) {
        target = _target;
    }

    function attack() external payable {
        target.{{VULNERABLE_FUNCTION}}{value: msg.value}();
    }

    receive() external payable {
        if (!attacked && address(target).balance > 0) {
            attacked = true;
            target.{{VULNERABLE_FUNCTION}}();
        }
    }
}

contract FlashLoanAttacker {
    {{CONTRACT_NAME}} public target;

    constructor({{CONTRACT_NAME}} _target) {
        target = _target;
    }

    function executeFlashLoanAttack(uint256 amount) external {
        // Simulate receiving flash loan
        // Perform manipulation
        target.{{MANIPULATION_FUNCTION}}(amount);
        
        // Simulate repaying flash loan
        // Attack should be mitigated by this point
    }
}"""

    def _get_fork_test_template(self) -> str:
        """Fork testing template for mainnet integration tests."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import "../src/{{CONTRACT_NAME}}.sol";

/**
 * @title {{CONTRACT_NAME}} Fork Tests
 * @notice Tests contract behavior against real mainnet state
 * @dev Requires MAINNET_RPC_URL environment variable
 */
contract {{CONTRACT_NAME}}ForkTest is Test {
    {{CONTRACT_NAME}} public {{CONTRACT_INSTANCE}};
    
    // Mainnet addresses (update with actual addresses)
    address constant {{MAINNET_TOKEN}} = {{TOKEN_ADDRESS}};
    address constant {{WHALE_ADDRESS}} = {{WHALE_ACCOUNT}};
    address constant {{PROTOCOL_ADDRESS}} = {{REAL_PROTOCOL_ADDRESS}};
    
    // Test accounts
    address public user = makeAddr("user");
    
    function setUp() public {
        // Create fork at specific block for consistent testing
        vm.createFork(vm.envString("MAINNET_RPC_URL"), {{FORK_BLOCK}});
        
        // Deploy our contract
        {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}({{MAINNET_DEPENDENCIES}});
        
        // Setup test conditions
        vm.deal(user, 10 ether);
    }

    function test_integration_withRealProtocol() public {
        // Get real state from mainnet
        uint256 realBalance = IERC20({{MAINNET_TOKEN}}).balanceOf({{WHALE_ADDRESS}});
        assertGt(realBalance, 0, "Whale should have token balance");
        
        // Test interaction with real protocol
        vm.prank({{WHALE_ADDRESS}});
        IERC20({{MAINNET_TOKEN}}).transfer(address({{CONTRACT_INSTANCE}}), 1000e18);
        
        // Verify our contract works with real tokens
        uint256 contractBalance = IERC20({{MAINNET_TOKEN}}).balanceOf(address({{CONTRACT_INSTANCE}}));
        assertEq(contractBalance, 1000e18, "Contract should receive real tokens");
    }

    function test_realWorldScenario_{{SCENARIO_NAME}}() public {
        // Simulate real-world usage scenario
        uint256 amount = 100e18;
        
        // Impersonate whale account
        vm.startPrank({{WHALE_ADDRESS}});
        
        // Perform real interaction
        IERC20({{MAINNET_TOKEN}}).approve(address({{CONTRACT_INSTANCE}}), amount);
        {{CONTRACT_INSTANCE}}.{{REAL_WORLD_FUNCTION}}(amount);
        
        vm.stopPrank();
        
        // Verify expected behavior with real state
        assertTrue({{CONTRACT_INSTANCE}}.{{SUCCESS_CONDITION}}(), "Real-world scenario should work");
    }

    function test_gasUsage_onMainnetFork() public {
        uint256 gasBefore = gasleft();
        
        vm.prank(user);
        {{CONTRACT_INSTANCE}}.{{GAS_EXPENSIVE_FUNCTION}}();
        
        uint256 gasUsed = gasBefore - gasleft();
        console.log("Gas used:", gasUsed);
        
        // Verify gas usage is reasonable
        assertLt(gasUsed, {{MAX_GAS_LIMIT}}, "Gas usage should be within limits");
    }
}"""

    def _get_helper_test_template(self) -> str:
        """Helper test template with common utility functions."""
        # Read the helper template from the templates directory
        try:
            from pathlib import Path
            template_path = Path(__file__).parent.parent / "templates" / "test_helper_template.sol"
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # Fallback template if file reading fails
            return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {IERC20} from "forge-std/interfaces/IERC20.sol";

/**
 * @title TestHelper
 * @dev Centralized helper functions for smart contract testing
 */
contract TestHelper is Test {
    
    function setupStandardAccounts() internal returns (
        address owner,
        address admin, 
        address user1,
        address user2,
        address attacker
    ) {
        owner = makeAddr("owner");
        admin = makeAddr("admin");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        attacker = makeAddr("attacker");
        
        vm.deal(owner, 100 ether);
        vm.deal(admin, 50 ether);
        vm.deal(user1, 10 ether);
        vm.deal(user2, 10 ether);
        vm.deal(attacker, 5 ether);
    }
    
    function giveTokens(IERC20 token, address user, uint256 amount) internal {
        deal(address(token), user, amount);
    }
    
    function timeWarpAndMine(uint256 timeInSeconds, uint256 blocks) internal {
        vm.warp(block.timestamp + timeInSeconds);
        vm.roll(block.number + blocks);
    }
}"""

    def _get_default_test_template(self) -> str:
        """Default fallback template."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import "../src/{{CONTRACT_NAME}}.sol";

contract {{CONTRACT_NAME}}Test is Test {
    {{CONTRACT_NAME}} public {{CONTRACT_INSTANCE}};
    
    address public owner = makeAddr("owner");
    
    function setUp() public {
        vm.prank(owner);
        {{CONTRACT_INSTANCE}} = new {{CONTRACT_NAME}}();
    }
    
    function test_example() public {
        assertTrue(true, "Example test should pass");
    }
}"""

    def _get_template_usage_instructions(self, template_type: str) -> List[str]:
        """Get usage instructions for each template type."""
        instructions = {
            "unit": [
                "Replace {{CONTRACT_NAME}} with your actual contract name",
                "Update {{OWNER_ACCOUNT}}, {{USER_ACCOUNT}} with meaningful names",
                "Customize {{FUNCTION_NAME}} and related placeholders for your specific functions",
                "Add contract-specific events and error types",
                "Implement comprehensive edge cases for your contract logic"
            ],
            "integration": [
                "Define {{CONTRACT_A_NAME}} and {{CONTRACT_B_NAME}} for your interacting contracts",
                "Specify {{WORKFLOW_NAME}} to describe the user journey being tested",
                "Implement the multi-step interaction logic",
                "Verify end-to-end state changes across contracts"
            ],
            "invariant": [
                "Create the Handler contract in test/handlers/{{HANDLER_NAME}}.sol",
                "Define system invariants that should always hold",
                "Implement handler functions that call your contract with fuzzing",
                "Use bound() to constrain fuzz inputs to valid ranges"
            ],
            "security": [
                "Identify specific attack vectors relevant to your contract",
                "Implement attack contracts that simulate real exploits",
                "Test both that attacks fail AND that legitimate usage works",
                "Include economic and oracle manipulation scenarios if applicable"
            ],
            "fork": [
                "Set MAINNET_RPC_URL environment variable",
                "Update mainnet addresses with real protocol addresses",
                "Choose appropriate fork block number for consistent testing",
                "Test realistic scenarios with actual mainnet state"
            ],
            "helper": [
                "Save as test/utils/TestHelper.sol for easy import across test files",
                "Replace {{CONTRACT_NAME}} and {{CONTRACT_INSTANCE}} with your contract details",
                "Customize {{TEST_DATA_TYPE}} struct to match your test data needs",
                "Implement specific workflow steps in {{DEPOSIT_WORKFLOW_STEPS}} and {{WITHDRAWAL_WORKFLOW_STEPS}}",
                "Add contract-specific state assertions in {{STATE_ASSERTIONS}}",
                "Import in your test files: import '../utils/TestHelper.sol'",
                "Inherit from TestHelper: contract MyTest is TestHelper"
            ]
        }
        
        common_instructions = [
            "Copy template to your test directory",
            "Replace all {{PLACEHOLDER}} values with your specific values",
            "Run tests with: forge test",
            "Use --gas-report flag for gas analysis",
            "Add more test cases specific to your contract's functionality"
        ]
        
        return common_instructions + instructions.get(template_type, []) 