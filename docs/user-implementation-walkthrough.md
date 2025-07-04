# Foundry Testing MCP - User Implementation Walkthrough

## Quick Start Guide

This walkthrough demonstrates how to use the Foundry Testing MCP to create comprehensive, world-class tests for a new Solidity smart contract protocol. We'll walk through the complete process from initial setup to advanced testing scenarios.

## Prerequisites

### Environment Setup

```bash
# 1. Ensure Foundry is installed
curl -L https://foundry.paradigm.xyz | bash
foundryup

# 2. Verify installation
forge --version
# Expected: forge 0.2.0 (or later)

# 3. Ensure MCP server is running locally
# (Typically started as a background process by your IDE/AI client)
```

### Example Protocol: TokenVault

For this walkthrough, we'll create comprehensive tests for a `TokenVault` protocol with the following contracts:

```solidity
// src/TokenVault.sol - Main vault contract
// src/VaultToken.sol - ERC20 vault shares
// src/interfaces/ITokenVault.sol - Interface definitions
// src/libraries/VaultMath.sol - Mathematical operations
```

## Step 1: Project Initialization

### Navigate to Your Protocol Directory

```bash
cd /path/to/your-protocol
```

**Verify project structure:**
```
your-protocol/
├── foundry.toml
├── src/
│   ├── TokenVault.sol
│   ├── VaultToken.sol
│   ├── interfaces/
│   └── libraries/
├── test/ (may be empty initially)
├── script/
└── lib/
```

### Initialize the Testing Agent

Use your MCP-enabled AI client (Cursor, Claude, etc.) and call:

```
initialize_protocol_testing_agent()
```

**Expected Response:**
```json
{
  "status": "initialized",
  "session_id": "uuid-session-123",
  "project_path": "/path/to/your-protocol",
  "project_info": {
    "is_foundry_project": true,
    "contracts": ["src/TokenVault.sol", "src/VaultToken.sol", ...],
    "tests": [],
    "analysis": {
      "is_new_project": true,
      "recommended_workflow": "create_new_suite"
    }
  },
  "available_workflows": {
    "create_new_suite": {
      "title": "Create New Test Suite from Scratch",
      "ideal_for": "New projects or complete testing overhauls",
      "estimated_phases": 4,
      "time_estimate": "2-4 hours"
    },
    "evaluate_existing": {
      "title": "Evaluate & Enhance Existing Tests"
    }
  },
  "recommendations": [
    "🚀 **Start Fresh**: Create a comprehensive test suite from scratch",
    "📋 **Plan First**: Begin with contract analysis and testing strategy",
    "🎯 **Set Goals**: Define coverage targets and testing objectives"
  ]
}
```

## Step 2: Execute Testing Workflow

### Launch Comprehensive Testing Workflow

```
execute_testing_workflow(
  workflow_type="create_new_suite",
  objectives="Create comprehensive test suite for TokenVault protocol with focus on security, gas optimization, and edge cases. Target 95% coverage with emphasis on deposit/withdrawal flows, access control, and economic attacks.",
  scope="comprehensive"
)
```

**Workflow Response:**
```json
{
  "status": "workflow_ready",
  "session_id": "uuid-session-123",
  "execution_phases": [
    {
      "phase": 1,
      "title": "Contract Analysis & Discovery",
      "actions": [
        "Scan project structure and identify all contracts",
        "Analyze contract dependencies and inheritance hierarchy",
        "Identify critical functions and state variables",
        "Map potential attack vectors and edge cases"
      ],
      "deliverables": [
        "Contract analysis report",
        "Dependency mapping",
        "Critical function inventory",
        "Security considerations document"
      ],
      "estimated_time": "30-45 minutes"
    }
  ],
  "current_phase_result": {
    "phase": 1,
    "status": "completed",
    "contracts_analyzed": [
      {
        "name": "TokenVault",
        "critical_functions": ["deposit", "withdraw", "emergencyPause"],
        "security_considerations": ["reentrancy", "access_control", "arithmetic"]
      }
    ]
  }
}
```

## Step 3: Interactive Contract Analysis

### Analyze Individual Contracts

Use the AI prompts for detailed contract analysis:

```
analyze-contract-for-testing src/TokenVault.sol
```

**AI Response Example:**
```markdown
## Contract Analysis: TokenVault.sol

### Contract Overview
- **Purpose**: Secure vault for ERC20 token deposits with yield distribution
- **Key Functions**: deposit(), withdraw(), claimRewards(), pause()/unpause()
- **Access Control**: Owner-based with emergency pause functionality

### Critical Testing Requirements

1. **Deposit Flow Testing**
   - Valid deposits with various token amounts
   - Zero amount deposit rejection
   - Insufficient allowance handling
   - Share calculation accuracy

2. **Withdrawal Flow Testing**
   - Valid withdrawals within balance limits
   - Withdrawal amount validation
   - Share burning mechanics
   - Emergency withdrawal scenarios

3. **Security Testing Priorities**
   - Reentrancy attack prevention
   - Access control bypass attempts
   - Integer overflow/underflow scenarios
   - Pause mechanism effectiveness

### Recommended Test Cases
```solidity
function testDepositValidAmount() public {
    // Test successful deposit with proper share minting
}

function testWithdrawExceedsBalance() public {
    // Test withdrawal attempt exceeding user balance
    vm.expectRevert("Insufficient balance");
}

function testReentrancyAttack() public {
    // Test reentrancy protection on withdraw function
}
```
```

## Step 4: Generate Test Templates

### Access Test Templates

```
Get resource: testing/templates/unit
```

**Response:** Complete unit test template with:
- Setup patterns for TokenVault testing
- Mock ERC20 token configuration
- User account management
- Common assertion patterns

### Create Initial Test Files

Based on the templates, create test files:

```solidity
// test/unit/TokenVault.t.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/TokenVault.sol";
import "../src/VaultToken.sol";
import "./mocks/MockERC20.sol";

contract TokenVaultTest is Test {
    TokenVault public vault;
    VaultToken public vaultToken;
    MockERC20 public underlying;
    
    address public owner = address(0x1);
    address public user1 = address(0x2);
    address public user2 = address(0x3);
    
    uint256 constant INITIAL_SUPPLY = 1000000e18;
    
    function setUp() public {
        vm.prank(owner);
        underlying = new MockERC20("Test Token", "TEST", INITIAL_SUPPLY);
        vaultToken = new VaultToken("Vault Shares", "vTEST");
        vault = new TokenVault(address(underlying), address(vaultToken));
        
        // Setup user balances
        underlying.transfer(user1, 10000e18);
        underlying.transfer(user2, 10000e18);
        
        // Setup approvals
        vm.prank(user1);
        underlying.approve(address(vault), type(uint256).max);
        vm.prank(user2);
        underlying.approve(address(vault), type(uint256).max);
    }
    
    function testDepositSuccess() public {
        uint256 depositAmount = 1000e18;
        
        vm.prank(user1);
        vault.deposit(depositAmount);
        
        assertEq(vault.balanceOf(user1), depositAmount);
        assertEq(underlying.balanceOf(address(vault)), depositAmount);
    }
    
    function testWithdrawSuccess() public {
        // Setup: user1 deposits first
        vm.prank(user1);
        vault.deposit(1000e18);
        
        uint256 withdrawAmount = 500e18;
        uint256 initialBalance = underlying.balanceOf(user1);
        
        vm.prank(user1);
        vault.withdraw(withdrawAmount);
        
        assertEq(vault.balanceOf(user1), 500e18);
        assertEq(underlying.balanceOf(user1), initialBalance + withdrawAmount);
    }
}
```

## Step 5: Advanced Testing Scenarios

### Generate Security Tests

```
design-security-tests contract_types="DeFi vault" threat_model="comprehensive"
```

**AI Guidance for Security Tests:**

```solidity
// test/security/TokenVaultSecurity.t.sol
contract TokenVaultSecurityTest is Test {
    // ... setup similar to unit tests ...
    
    function testReentrancyProtection() public {
        MaliciousReentrant attacker = new MaliciousReentrant(vault, underlying);
        
        // Fund attacker
        underlying.transfer(address(attacker), 1000e18);
        
        // Attempt reentrancy attack
        vm.expectRevert("ReentrancyGuard: reentrant call");
        attacker.attack();
    }
    
    function testAccessControlBypass() public {
        vm.prank(user1); // Non-owner
        vm.expectRevert("Ownable: caller is not the owner");
        vault.emergencyPause();
    }
    
    function testFlashLoanAttack() public {
        // Simulate flash loan attack scenario
        FlashLoanAttacker attacker = new FlashLoanAttacker();
        
        // Attack should fail due to vault protections
        vm.expectRevert("Attack prevented");
        attacker.executeFlashLoan(address(vault), 1000000e18);
    }
}
```

### Create Invariant Tests

```
Get resource: testing/templates/invariant
```

```solidity
// test/invariant/TokenVaultInvariant.t.sol
contract TokenVaultInvariantTest is Test {
    TokenVault public vault;
    MockERC20 public underlying;
    
    function setUp() public {
        // ... setup similar to unit tests ...
        targetContract(address(vault));
    }
    
    function invariant_totalSupplyEqualsDeposits() public {
        // Total vault token supply should equal total underlying deposits
        assertEq(
            vault.totalSupply(),
            underlying.balanceOf(address(vault))
        );
    }
    
    function invariant_userBalancesNeverExceedDeposits() public {
        // Sum of all user balances should never exceed vault total supply
        uint256 totalUserBalances = 0;
        address[] memory users = vault.getAllUsers();
        
        for (uint256 i = 0; i < users.length; i++) {
            totalUserBalances += vault.balanceOf(users[i]);
        }
        
        assertLe(totalUserBalances, vault.totalSupply());
    }
    
    function invariant_vaultNeverInsolvent() public {
        // Vault should always have enough underlying tokens to satisfy withdrawals
        assertGe(
            underlying.balanceOf(address(vault)),
            vault.totalSupply()
        );
    }
}
```

### Generate Fuzz Tests

```solidity
// test/fuzz/TokenVaultFuzz.t.sol
contract TokenVaultFuzzTest is Test {
    // ... setup ...
    
    function testFuzzDeposit(uint256 amount) public {
        amount = bound(amount, 1, 1000000e18);
        
        // Ensure user has enough tokens
        vm.assume(underlying.balanceOf(user1) >= amount);
        
        uint256 vaultBalanceBefore = underlying.balanceOf(address(vault));
        uint256 userSharesBefore = vault.balanceOf(user1);
        
        vm.prank(user1);
        vault.deposit(amount);
        
        assertEq(
            underlying.balanceOf(address(vault)),
            vaultBalanceBefore + amount
        );
        assertEq(
            vault.balanceOf(user1),
            userSharesBefore + amount
        );
    }
    
    function testFuzzWithdrawPartial(uint256 depositAmount, uint256 withdrawAmount) public {
        depositAmount = bound(depositAmount, 1000, 1000000e18);
        withdrawAmount = bound(withdrawAmount, 1, depositAmount);
        
        // Setup deposit
        vm.prank(user1);
        vault.deposit(depositAmount);
        
        // Test withdrawal
        vm.prank(user1);
        vault.withdraw(withdrawAmount);
        
        assertEq(vault.balanceOf(user1), depositAmount - withdrawAmount);
    }
}
```

## Step 6: Coverage Analysis and Optimization

### Run Coverage Analysis

```
analyze_current_test_coverage(target_coverage=95, include_branches=true)
```

**Coverage Report Example:**
```json
{
  "status": "success",
  "project_path": "/path/to/your-protocol",
  "coverage_summary": {
    "coverage_percentage": 87.5,
    "lines_covered": 175,
    "lines_total": 200,
    "functions_covered": 18,
    "functions_total": 20,
    "branches_covered": 85,
    "branches_total": 100
  },
  "gaps_identified": [
    "Emergency pause functionality not fully tested",
    "Edge case: withdrawal when vault is empty",
    "Admin function: updateFeeRate not covered"
  ],
  "recommendations": [
    "Add tests for emergency pause/unpause scenarios",
    "Test withdrawal attempts when vault balance is zero",
    "Create admin function tests for fee management"
  ]
}
```

### Address Coverage Gaps

Based on the analysis, add missing tests:

```solidity
// Additional tests to reach 95% coverage
function testEmergencyPause() public {
    vm.prank(owner);
    vault.pause();
    
    vm.prank(user1);
    vm.expectRevert("Pausable: paused");
    vault.deposit(1000e18);
}

function testWithdrawFromEmptyVault() public {
    vm.prank(user1);
    vm.expectRevert("Insufficient vault balance");
    vault.withdraw(1e18);
}

function testUpdateFeeRate() public {
    uint256 newFeeRate = 100; // 1%
    
    vm.prank(owner);
    vault.updateFeeRate(newFeeRate);
    
    assertEq(vault.feeRate(), newFeeRate);
}
```

## Step 7: Integration Testing

### Create Integration Test Suite

```
Get resource: testing/templates/integration
```

```solidity
// test/integration/VaultIntegration.t.sol
contract VaultIntegrationTest is Test {
    TokenVault public vault;
    VaultToken public vaultToken;
    MockERC20 public underlying;
    
    function testCompleteUserJourney() public {
        // 1. User deposits tokens
        vm.prank(user1);
        vault.deposit(1000e18);
        
        // 2. Vault accumulates yield (simulate)
        underlying.transfer(address(vault), 100e18); // 10% yield
        
        // 3. User partially withdraws
        vm.prank(user1);
        vault.withdraw(500e18);
        
        // 4. User claims rewards
        vm.prank(user1);
        uint256 rewards = vault.claimRewards();
        
        // Verify final state
        assertGt(rewards, 0);
        assertEq(vault.balanceOf(user1), 500e18);
    }
    
    function testMultiUserScenario() public {
        // Multiple users interact with vault
        vm.prank(user1);
        vault.deposit(1000e18);
        
        vm.prank(user2);
        vault.deposit(2000e18);
        
        // Simulate yield
        underlying.transfer(address(vault), 300e18); // 10% total yield
        
        // Users withdraw proportionally
        vm.prank(user1);
        vault.withdraw(500e18);
        
        vm.prank(user2);
        vault.withdraw(1000e18);
        
        // Verify proportional rewards
        uint256 user1Rewards = vault.pendingRewards(user1);
        uint256 user2Rewards = vault.pendingRewards(user2);
        
        assertApproxEqRel(user1Rewards * 2, user2Rewards, 1e16); // 1% tolerance
    }
}
```

## Step 8: Gas Optimization Testing

### Create Gas Tests

```solidity
// test/gas/TokenVaultGas.t.sol
contract TokenVaultGasTest is Test {
    // ... setup ...
    
    function testDepositGasUsage() public {
        uint256 gasBefore = gasleft();
        
        vm.prank(user1);
        vault.deposit(1000e18);
        
        uint256 gasUsed = gasBefore - gasleft();
        
        // Assert gas usage is within reasonable bounds
        assertLt(gasUsed, 100000); // Should use less than 100k gas
    }
    
    function testBatchDepositOptimization() public {
        // Compare single vs batch deposits
        uint256[] memory amounts = new uint256[](5);
        for (uint256 i = 0; i < 5; i++) {
            amounts[i] = 200e18;
        }
        
        uint256 gasBefore = gasleft();
        vm.prank(user1);
        vault.batchDeposit(amounts);
        uint256 batchGasUsed = gasBefore - gasleft();
        
        // Individual deposits gas usage
        uint256 individualGasUsed = 0;
        for (uint256 i = 0; i < 5; i++) {
            gasBefore = gasleft();
            vm.prank(user2);
            vault.deposit(200e18);
            individualGasUsed += (gasBefore - gasleft());
        }
        
        // Batch should be more efficient
        assertLt(batchGasUsed, individualGasUsed);
    }
}
```

## Step 9: Final Validation and Documentation

### Run Complete Test Suite

```bash
# Run all tests with coverage
forge test --coverage

# Run specific test categories
forge test --match-path "test/unit/*" -vvv
forge test --match-path "test/security/*" -vvv
forge test --match-path "test/integration/*" -vvv

# Run invariant tests
forge test --invariant -vvv

# Generate gas report
forge test --gas-report
```

### Validate Final Coverage

```
analyze_current_test_coverage(target_coverage=95)
```

**Expected Final Results:**
```json
{
  "status": "success",
  "coverage_summary": {
    "coverage_percentage": 96.2,
    "lines_covered": 192,
    "lines_total": 200,
    "analysis": "Excellent coverage! Consider adding edge case and integration tests."
  },
  "meets_target": true,
  "recommendations": [
    "✅ Excellent coverage achieved",
    "🛡️ Comprehensive security testing implemented",
    "⚡ Gas optimization tests included",
    "🔄 Integration scenarios covered"
  ]
}
```

## Step 10: Advanced Optimization

### Review and Optimize

```
optimize-test-performance performance_issues="general" optimization_goals="speed and coverage"
```

**AI Optimization Guidance:**

1. **Parallel Test Execution**
```bash
# Use parallel testing for faster execution
forge test --jobs 4
```

2. **Test Organization**
```solidity
// Group related tests in the same contract
contract TokenVaultDepositTests is Test { /* deposit tests */ }
contract TokenVaultWithdrawTests is Test { /* withdraw tests */ }
```

3. **Efficient Setup Patterns**
```solidity
// Use shared setup for similar test scenarios
abstract contract TokenVaultTestBase is Test {
    // Common setup code
}

contract TokenVaultUnitTest is TokenVaultTestBase {
    // Specific unit tests
}
```

## Expected Outcomes

### Test Suite Metrics
- **Coverage**: 95%+ line coverage, 90%+ branch coverage
- **Test Count**: 50+ comprehensive test cases
- **Security Tests**: 15+ security-focused scenarios
- **Performance Tests**: Gas usage validation for all functions
- **Integration Tests**: Complete user journey testing

### Quality Indicators
- **Zero Critical Vulnerabilities**: All common attack vectors tested
- **Comprehensive Edge Cases**: Boundary conditions and error scenarios covered
- **Gas Optimization**: Efficient execution patterns validated
- **Documentation**: Clear test descriptions and setup instructions

### Development Benefits
- **Faster Debugging**: Specific test failures pinpoint issues
- **Confident Deployment**: Comprehensive coverage reduces deployment risk
- **Maintainable Code**: Well-organized test suite supports future development
- **Security Assurance**: Proactive vulnerability testing and prevention

## Troubleshooting Common Issues

### Coverage Generation Fails
```bash
# Ensure tests pass first
forge test

# Try coverage with specific parameters
forge coverage --report lcov --report-file coverage.lcov
```

### Fuzz Tests Timeout
```solidity
// Adjust fuzz run configuration in foundry.toml
[fuzz]
runs = 1000  # Reduce if tests timeout
```

### Integration Test Failures
```solidity
// Use vm.roll() and vm.warp() for time-dependent tests
vm.warp(block.timestamp + 1 days);
vm.roll(block.number + 1000);
```

This walkthrough provides a complete framework for creating world-class smart contract tests using the Foundry Testing MCP. The AI-guided approach ensures comprehensive coverage while maintaining development efficiency and security best practices. 