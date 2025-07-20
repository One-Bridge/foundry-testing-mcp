# User Story and Outline - Building Robust Testing Suites with Foundry Testing MCP

## Overview

This document provides a practical guide for using the Foundry Testing MCP to build comprehensive testing suites for Solidity protocols. The system uses regex-first analysis to provide reliable contract classification and testing guidance without external dependencies, with optional AST enhancement when available.

This guide covers two scenarios: starting from scratch with contracts that have no tests, and improving existing projects for production deployment.

## Prerequisites

### Required Setup
- **Foundry installed**: `forge --version` should work in your terminal
- **Valid Foundry project**: foundry.toml exists in your project root  
- **MCP client configured**: Cursor, Claude Desktop, or compatible MCP client
- **Project structure**: Contracts in `src/` directory following Foundry conventions

### Optional Components (Environment-Dependent)
- **Solidity compiler (solc)**: Enables enhanced AST analysis (regex fallback available)
- **Subprocess execution permissions**: Required for coverage analysis integration
- **Proper directory configuration**: Auto-detection works in most setups, manual configuration available

### Supported Project Types
The system provides specialized analysis and guidance for:
- **DeFi Protocols**: Portfolio management, trading, lending, staking mechanisms
- **Governance Systems**: Voting mechanisms, proposal systems, timelock controls
- **Token Contracts**: ERC20, ERC721, ERC1155 implementations
- **Bridge Contracts**: Cross-chain functionality and asset bridging
- **Utility Contracts**: General-purpose smart contract logic

## Scenario 1: Starting from Scratch (No Existing Tests)

### Initial State
You have Solidity contracts in your `src/` directory but no testing infrastructure. Your project structure looks like:

```
my-protocol/
├── foundry.toml
├── src/
│   ├── MyToken.sol
│   ├── MyVault.sol
│   └── MyGovernance.sol
└── test/     # Empty or doesn't exist
```

### Step 1: Project Analysis and Planning

**Action**: Start with the initialization tool to understand your current state.

**MCP Tool Call**:
```
initialize_protocol_testing_agent(
    analysis_mode="interactive"
)
```

**What This Does**:
- Uses regex-based analysis to scan contracts in your `src/` directory
- Classifies contract types using scoring-based detection (DeFi, governance, token, etc.)
- Calculates contract-type-aware risk scores for prioritization
- Detects security patterns like access control, reentrancy protection
- Recommends testing approach based on contract analysis

**Expected Output**:
- Project analysis showing "None" testing phase (no existing tests found)
- Contract classification results (e.g., "Portfolio.sol: DeFi contract, risk score 0.7")
- Contract-specific testing guidance based on detected patterns
- Session ID for workflow continuity
- Workflow recommendation adapted to your contract types

**What You Learn**:
- Reliable contract classification without requiring solc installation
- Risk-based prioritization (DeFi contracts get higher priority than utility contracts)
- Security patterns present in your contracts
- Specific testing strategies recommended for your contract types

### Step 2: Create Testing Infrastructure

**Action**: Execute the foundational testing workflow.

**MCP Tool Call**:
```
execute_testing_workflow(
    workflow_type="create_foundational_suite",
    objectives="Create comprehensive test suite for production deployment",
    scope="comprehensive",
    session_id="<from_step_1>"
)
```

**What This Does**:
- Creates a structured 3-4 phase implementation plan
- Provides specific guidance for your contract types
- Generates file structure recommendations
- Offers template suggestions based on your contracts

**Phase-by-Phase Implementation**:

**Phase 1: Basic Test Infrastructure **
- Create `test/` directory structure
- Set up base test contracts
- Implement basic unit tests for core functions
- Establish testing patterns and conventions

**Phase 2: Core Functionality Testing **
- Comprehensive unit tests for all public functions
- Happy path testing for main contract workflows
- Basic edge case testing (zero values, boundary conditions)
- Mock implementations for external dependencies

**Phase 3: Integration and Security Testing **
- Multi-contract interaction tests
- Access control testing (admin functions, role-based permissions)
- Security scenario testing (reentrancy, overflow/underflow protection)
- Gas optimization validation

**Phase 4: Advanced Testing and Quality Assurance **
- Invariant testing for system properties
- Fuzz testing for edge case discovery
- Integration with external protocols (if applicable)
- Performance and gas cost optimization

### Step 3: Implement Helper Utilities

**Action**: Create shared testing utilities to reduce code duplication.

**MCP Resource Access**:
```
Access: testing://templates/helper
```

**Implementation**:
1. Create `test/utils/TestHelper.sol` using the helper template
2. Customize placeholders for your specific contracts
3. Include common functions like:
   - Account setup and funding
   - Token distribution for testing
   - Time manipulation for time-dependent tests
   - Common assertion patterns

**Benefits**:
- Consistent testing patterns across all test files
- Reduced code duplication
- Easier maintenance and updates
- Standardized test data generation

### Step 4: Template-Based Test Creation

**Action**: Use the 6 available templates to create structured tests for each contract type.

**Available Templates**:

**Unit Tests** (`testing://templates/unit`):
- Comprehensive function-level testing with edge cases
- State variable validation and access control verification
- Error condition testing with specific error types
```solidity
// Example structure from template
contract MyTokenTest is Test {
    function test_transfer_whenValidAmount_shouldTransferTokens() public {
        // Structured test with arrange/act/assert pattern
    }
    
    function test_transfer_whenInsufficientBalance_shouldRevert() public {
        // Error condition testing
    }
}
```

**Integration Tests** (`testing://templates/integration`):
- Multi-contract workflow testing and cross-contract interactions
- End-to-end scenario validation
```solidity
// Example for complex workflows
contract VaultIntegrationTest is Test {
    function test_depositWithdrawWorkflow() public {
        // Complete user journey testing
    }
}
```

**Security Tests** (`testing://templates/security`):
- Access control and privilege escalation testing
- Attack scenario simulation and defense validation
```solidity
// Security-focused testing patterns
contract SecurityTest is Test {
    function test_accessControl_preventUnauthorizedAccess() public {
        // Security validation
    }
}
```

**Invariant Tests** (`testing://templates/invariant`):
- Property-based testing using Handler pattern
- System-wide invariant verification
```solidity
// Stateful fuzzing for system properties
contract InvariantTest is StdInvariant, Test {
    function invariant_systemProperty() public view {
        // Properties that should always hold
    }
}
```

**Fork Tests** (`testing://templates/fork`):
- Real network integration testing
- Mainnet state interaction validation

**Helper Utilities** (`testing://templates/helper`):
- Shared testing utilities and common patterns
- Account setup and standardized test data generation

### Step 5: Monitor Progress and Quality

**Action**: Check coverage and identify gaps (environment-dependent).

**MCP Tool Call**:
```
analyze_current_test_coverage(
    target_coverage=90,
    include_branches=true
)
```

**What This Provides** (when environment permits):
- Current coverage percentages from actual `forge coverage` output
- Specific uncovered code sections and gap analysis
- Recommendations for reaching target coverage
- Contextual coverage assessment based on project type

**Alternative Approach** (if coverage analysis fails):
- Manually run `forge coverage --report summary` in terminal
- Use `forge test -vvv` to identify uncovered functions
- Focus on systematic test creation using templates
- Validate test completeness through manual review

**Iteration Process**:
1. Attempt automated coverage analysis 
2. If unavailable, use manual forge commands
3. Identify critical gaps in high-risk contracts first
4. Add tests using appropriate templates
5. Focus on security-critical functions and DeFi-specific patterns

### Step 6: Quality Assurance

**Action**: Ensure test quality and effectiveness.

**MCP Tool Call**:
```
analyze_project_context(
    include_ai_failure_detection=true,
    generate_improvement_plan=true
)
```

**What This Provides**:
- **For projects with tests**: Detection of 8 AI failure patterns including circular logic, mock cheating, insufficient edge cases
- **For projects without tests**: Prevention guidance and strategies to avoid common AI failures during test creation
- Contract-specific testing guidance based on regex analysis results
- Security testing priorities based on detected contract types and risk scores
- Prioritized improvement roadmap with specific implementation steps

**AI Failure Patterns Detected**:
- Circular logic in test validation
- Mock objects that always return expected values  
- Tests with insufficient edge case coverage
- Missing security scenarios and attack vectors
- Always-passing tests with no real validation
- Inadequate fuzz test randomization
- Missing negative test cases for error conditions
- Implementation-dependent validation

## Scenario 2: Improving Existing Tests (Mature Projects)

### Initial State
You have an existing project with some tests but need improvement for production deployment:

```
mature-protocol/
├── foundry.toml
├── src/
│   ├── ComplexProtocol.sol
│   ├── TokenManager.sol
│   └── GovernanceModule.sol
└── test/
    ├── BasicProtocolTest.sol     # 15 tests, basic functionality
    ├── TokenTest.sol             # 8 tests, happy path only
    └── mocks/
        └── MockExchange.sol      # Simple mocks
```

### Step 1: Current State Assessment

**Action**: Analyze existing testing infrastructure and identify improvement opportunities.

**MCP Tool Call**:
```
initialize_protocol_testing_agent(
    analysis_mode="interactive"
)
```

**What This Reveals**:
- Current testing phase classification using 5-tier assessment
- Contract classification results using regex-based analysis  
- Risk scores for existing contracts based on type and complexity
- Security patterns detected in current codebase
- Testing workflow recommendations adapted to current state

**Followed by**:
```
analyze_project_context(
    include_ai_failure_detection=true,
    generate_improvement_plan=true
)
```

**Deep Analysis Results**:
- **Contract Analysis**: "ComplexProtocol.sol: DeFi contract, risk score 0.8" (high priority)
- **Testing Maturity**: "Intermediate" - 23 tests, basic functionality covered
- **AI Failure Detection**: Identifies specific issues in existing tests like:
  - Mock objects that always return success without failure scenarios
  - Tests validating implementation against itself (circular logic)
  - Missing negative test cases for error conditions
  - Insufficient edge case coverage for financial calculations
- **Security Assessment**: Missing security scenarios for DeFi-specific risks
- **Contract-Specific Guidance**: DeFi testing strategies, security priorities
- **Improvement Plan**: Prioritized roadmap with phases and specific actions

### Step 2: Address Quality Issues First

**Action**: Fix existing test problems before adding new tests.

**Common Issues Found**:

**Mock Cheating Example**:
```solidity
// Problematic mock (always returns true)
contract MockExchange {
    function swap(uint256 amount) external pure returns (bool) {
        return true;  // Never fails!
    }
}
```

**Improved Version**:
```solidity
// Realistic mock with failure scenarios
contract MockExchange {
    mapping(uint256 => bool) public shouldFail;
    
    function swap(uint256 amount) external view returns (bool) {
        if (shouldFail[amount]) revert("Insufficient liquidity");
        return amount > 0;
    }
    
    function setShouldFail(uint256 amount, bool fail) external {
        shouldFail[amount] = fail;
    }
}
```

**Circular Logic Example**:
```solidity
// Problematic test (validates implementation against itself)
function test_balance_calculation() public {
    uint256 balance = protocol.calculateBalance(user);
    assertEq(balance, protocol.calculateBalance(user));  // Circular!
}
```

**Improved Version**:
```solidity
// Test validates expected behavior
function test_balance_calculation() public {
    protocol.deposit(user, 100);
    protocol.addReward(user, 10);
    
    uint256 balance = protocol.calculateBalance(user);
    assertEq(balance, 110);  // Validates expected result
}
```

### Step 3: Systematic Coverage Expansion

**Action**: Execute targeted workflow to enhance existing tests.

**MCP Tool Call**:
```
execute_testing_workflow(
    workflow_type="expand_test_coverage",
    objectives="Achieve 90%+ coverage with security focus for audit preparation",
    scope="comprehensive"
)
```

**Targeted Improvements**:

**Phase 1: Coverage Gap Analysis (Days 1-2)**
- Identify uncovered functions and branches
- Prioritize critical paths and security-sensitive code
- Plan test additions based on risk assessment

**Phase 2: Security Testing Enhancement (Days 3-5)**
- Add access control tests for admin functions
- Implement attack scenario testing
- Add reentrancy and overflow protection tests
- Test emergency pause and recovery mechanisms

**Phase 3: Edge Case and Integration Testing (Days 6-8)**
- Boundary value testing (max/min values, zero amounts)
- Multi-contract interaction scenarios
- Failure mode testing (what happens when external calls fail)
- State transition testing

**Phase 4: Advanced Testing Patterns (Days 9-12)**
- Invariant testing for system properties
- Fuzz testing for edge case discovery
- Fork testing against real protocols (if applicable)
- Gas optimization validation

### Step 4: Add Helper Utilities to Existing Tests

**Action**: Refactor existing tests to use shared utilities.

**Implementation Strategy**:
1. Create `test/utils/TestHelper.sol` using the helper template
2. Gradually refactor existing tests to inherit from TestHelper
3. Extract common patterns into reusable functions
4. Maintain backward compatibility during transition

**Before Refactoring**:
```solidity
contract TokenTest is Test {
    function setUp() public {
        vm.deal(address(0x1), 10 ether);
        vm.deal(address(0x2), 10 ether);
        token = new Token();
        // Repeated setup code...
    }
}
```

**After Refactoring**:
```solidity
contract TokenTest is Test, TestHelper {
    function setUp() public {
        setupAccounts();     // From TestHelper
        token = new Token();
        setupTokenBalances(token, 1000);  // From TestHelper
    }
}
```

### Step 5: Security Testing Focus

**Action**: Add comprehensive security testing for production readiness.

**Security Test Categories**:

**Access Control Testing**:
```solidity
function test_adminFunctions_revertForNonAdmin() public {
    vm.prank(user);
    vm.expectRevert("Unauthorized");
    protocol.emergencyPause();
}
```

**Reentrancy Protection**:
```solidity
function test_withdraw_protectedFromReentrancy() public {
    ReentrantAttacker attacker = new ReentrantAttacker(protocol);
    vm.expectRevert("ReentrancyGuard: reentrant call");
    attacker.attack();
}
```

**Economic Attack Scenarios**:
```solidity
function test_flashLoanAttack_mitigated() public {
    // Simulate flash loan attack scenario
    // Verify protocol defenses work correctly
}
```

### Step 6: Validation and Quality Assurance

**Action**: Validate improvements achieve production readiness.

**Final Validation Checklist**:

**Coverage Validation**:
```
analyze_current_test_coverage(target_coverage=90)
```
- Achieve 90%+ line coverage
- 85%+ branch coverage
- 95%+ function coverage

**Quality Validation**:
```
analyze_project_context(include_ai_failure_detection=true)
```
- Zero AI failure patterns detected
- All critical security scenarios covered
- Realistic mock implementations

**Expected Timeline**: 2-3 weeks for comprehensive improvements

## Common Patterns and Best Practices

### Test Organization

**Recommended Directory Structure**:
```
test/
├── unit/
│   ├── TokenTest.sol
│   ├── VaultTest.sol
│   └── GovernanceTest.sol
├── integration/
│   ├── TokenVaultIntegrationTest.sol
│   └── FullWorkflowTest.sol
├── security/
│   ├── AccessControlTest.sol
│   ├── ReentrancyTest.sol
│   └── AttackScenarioTest.sol
├── invariant/
│   ├── TokenInvariantTest.sol
│   └── VaultInvariantTest.sol
├── utils/
│   ├── TestHelper.sol
│   └── Mocks.sol
└── fork/
    └── MainnetIntegrationTest.sol
```

### Naming Conventions

**Test Function Naming**:
```solidity
function test_functionName_whenCondition_shouldResult() public {
    // Implementation
}

// Examples:
function test_transfer_whenInsufficientBalance_shouldRevert() public
function test_deposit_whenValidAmount_shouldUpdateBalance() public
function test_withdraw_whenPaused_shouldRevert() public
```

### Template Usage Patterns

**For Each Contract, Create**:
1. **Unit Test File**: Test individual functions in isolation
2. **Integration Test File**: Test interactions with other contracts
3. **Security Test File**: Test access control and attack scenarios
4. **Invariant Test File**: Test system-wide properties (for core contracts)

**Template Customization Process**:
1. Access appropriate template from `testing://templates/{type}`
2. Replace all `{{PLACEHOLDER}}` values with your specific details
3. Add contract-specific test scenarios
4. Follow usage instructions provided with each template

## Troubleshooting Common Issues

### Coverage Analysis Problems

**Symptom**: `analyze_current_test_coverage` fails or returns subprocess errors

**Root Cause**: Coverage analysis requires Foundry CLI integration and subprocess execution permissions

**Solutions**:
1. **Manual Verification**: Run `forge coverage --report summary` directly in terminal
2. **Project Validation**: Use `validate_current_directory()` to check Foundry setup
3. **Environment Check**: Ensure subprocess execution is permitted in your environment
4. **Alternative Approach**: Use manual forge commands and focus on systematic template-based test creation
5. **Fallback Strategy**: Prioritize high-risk contracts identified through regex analysis

### Directory Detection Issues

**Symptom**: Tools report wrong directory (e.g., home directory instead of project directory)

**Root Cause**: MCP client-server directory misalignment

**Solutions**:
1. **Diagnostic Tool**: Run `debug_directory_detection()` for detailed analysis
2. **Manual Path**: Specify project path explicitly in tool calls: `project_path="/path/to/project"`
3. **Environment Variables**: Set `MCP_CLIENT_CWD` to your project directory
4. **Client Configuration**: Configure MCP client working directory
5. **Project Discovery**: Use `discover_foundry_projects()` to find available projects

### AST Enhancement Unavailable

**Symptom**: Enhanced analysis not working, basic results only

**Root Cause**: Solidity compiler (solc) not installed or accessible

**Impact**: **Not Critical** - Core regex analysis provides reliable contract classification

**Solutions**:
1. **Continue with Regex**: Core functionality works without AST enhancement
2. **Install solc**: `curl -L https://github.com/ethereum/solidity/releases/download/v0.8.21/solc-static-linux -o solc && chmod +x solc && sudo mv solc /usr/local/bin/`
3. **Accept Limitations**: Regex analysis provides sufficient contract classification for most use cases

### MCP Client Integration Issues

**Symptom**: Tools not discovered or not responding in MCP client

**Root Cause**: MCP client configuration or tool routing issues

**Solutions**:
1. **Server Status**: Verify MCP server is running and accessible
2. **Client Restart**: Restart both MCP client and server
3. **Configuration Check**: Review MCP client configuration for server connection
4. **Manual Verification**: Test tools work via direct server access
5. **Alternative Access**: Use http mode for development and debugging

### Project Analysis Returns Generic Results

**Symptom**: All contracts classified as "utility" with low risk scores

**Root Cause**: Contracts may use non-standard patterns or very minimal code

**Solutions**:
1. **Pattern Review**: Check if your contracts use standard DeFi/governance/token patterns
2. **Manual Classification**: Proceed with manual contract type identification
3. **Template Selection**: Choose templates based on your intended contract functionality
4. **Custom Guidance**: Apply general testing principles from documentation

## Expected Outcomes

### For New Projects (Starting from Scratch)
**After 2-4 weeks of systematic testing development**:
- **Reliable Contract Analysis**: Accurate contract classification and risk assessment without external dependencies
- **Structured Test Creation**: Comprehensive test suites using 6 template types with proper patterns
- **Quality Assurance**: AI failure detection prevents common testing mistakes
- **Security Focus**: Contract-type-specific security testing priorities
- **Maintainable Code**: Helper utilities and standardized patterns reducing duplication
- **Coverage Goals**: Target 85-90% coverage (exact measurement depends on environment)

### For Existing Projects (Enhancement)
**After 2-4 weeks of targeted improvements**:
- **Improved Classification**: Better understanding of contract types and risk priorities
- **Quality Improvement**: Elimination of AI failure patterns (circular logic, mock cheating)
- **Security Enhancement**: Addition of contract-type-specific security scenarios
- **Systematic Structure**: Refactored tests using templates and helper utilities
- **Coverage Expansion**: Improved test coverage through systematic gap identification
- **Production Readiness**: Enhanced test suite quality suitable for audit preparation

### Realistic Expectations
- **Environment-Independent**: Core analysis and template generation work reliably across all environments
- **Coverage Analysis**: May require manual forge commands in restricted environments
- **AST Enhancement**: Optional feature that provides additional insights when available
- **Directory Configuration**: May require manual setup in some MCP client configurations
- **Template Customization**: Requires developer effort to adapt templates to specific contracts

### Long-term Benefits
- **Development Confidence**: Well-structured tests enable confident code changes
- **Security Awareness**: Contract-type-specific testing catches vulnerabilities early
- **Audit Preparation**: Systematic testing approach speeds security audit onboarding
- **Team Standardization**: Clear patterns enable consistent testing practices
- **Maintenance Efficiency**: Template-based approach reduces technical debt

## Next Steps After Implementation

### Development Workflow Integration
- **Manual Coverage Monitoring**: Use `forge coverage` directly in development workflow
- **Template Standardization**: Establish team conventions for template usage and customization
- **Quality Reviews**: Regular use of AI failure detection to maintain test quality
- **Security Focus**: Prioritize security testing for high-risk contracts identified through analysis

### Ongoing Maintenance
- **Systematic Updates**: Update tests using templates when contracts change
- **Pattern Evolution**: Evolve testing patterns based on project needs and learned experiences
- **Regular Assessment**: Periodic project analysis to identify new testing needs
- **Team Knowledge**: Document contract-specific testing decisions and rationale

### Production Readiness Validation
- **Manual Verification**: Validate coverage meets requirements using direct forge commands
- **Security Review**: Ensure all contract-type-specific security scenarios are covered
- **Test Quality**: Verify no AI failure patterns remain in production test suite
- **Documentation**: Maintain clear testing documentation for audit and team reference

### Advanced Integration (Optional)
- **CI/CD Integration**: Include forge test and coverage in automated pipelines
- **Environment Optimization**: Configure development environments for full MCP functionality
- **Tool Enhancement**: Consider additional security analysis tool integration
- **Team Training**: Establish training on testing patterns and quality assurance practices

## Summary

This systematic approach provides reliable smart contract testing assistance through regex-based analysis, comprehensive templates, and quality assurance. The system works consistently across different environments while providing optional enhancements when available, ensuring teams can build robust test suites regardless of development constraints. 