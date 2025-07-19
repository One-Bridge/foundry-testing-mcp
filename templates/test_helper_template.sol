// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {IERC20} from "forge-std/interfaces/IERC20.sol";

/**
 * @title TestHelper
 * @dev Centralized helper functions for smart contract testing
 * @notice Provides common utilities to reduce code duplication across test files
 * @author Smart Contract Testing MCP Server
 */
contract TestHelper is Test {
    
    // ====== ACCOUNT MANAGEMENT HELPERS ======
    
    /**
     * @dev Create and fund multiple test accounts
     * @param count Number of accounts to create
     * @param ethAmount ETH amount to give each account
     * @return Array of funded account addresses
     */
    function createAndFundAccounts(uint256 count, uint256 ethAmount) internal returns (address[] memory) {
        address[] memory accounts = new address[](count);
        
        for (uint256 i = 0; i < count; i++) {
            accounts[i] = makeAddr(string(abi.encodePacked("user", i)));
            vm.deal(accounts[i], ethAmount);
        }
        
        return accounts;
    }
    
    /**
     * @dev Give ERC20 tokens to a user using deal cheatcode
     * @param token The ERC20 token contract
     * @param user The user to give tokens to
     * @param amount The amount of tokens to give
     */
    function giveTokens(IERC20 token, address user, uint256 amount) internal {
        deal(address(token), user, amount);
    }
    
    /**
     * @dev Setup standard test accounts with predictable names and funding
     * @return owner, admin, user1, user2, attacker addresses
     */
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
        
        // Fund accounts with standard amounts
        vm.deal(owner, 100 ether);
        vm.deal(admin, 50 ether);
        vm.deal(user1, 10 ether);
        vm.deal(user2, 10 ether);
        vm.deal(attacker, 5 ether);
    }
    
    // ====== BALANCE AND STATE HELPERS ======
    
    /**
     * @dev Helper to give user shares/tokens for {{CONTRACT_NAME}}
     * @param {{CONTRACT_INSTANCE}} The contract instance
     * @param user The user address
     * @param shares The amount of shares to give
     */
    function giveUserShares(address {{CONTRACT_INSTANCE}}, address user, uint256 shares) internal {
        // Use deal to set token balance directly
        deal({{CONTRACT_INSTANCE}}, user, shares);
    }
    
    /**
     * @dev Setup a test scenario with predefined state
     * @param scenario The scenario ID to setup
     * @param {{CONTRACT_INSTANCE}} The contract to configure
     */
    function setupTestScenario(uint256 scenario, address {{CONTRACT_INSTANCE}}) internal {
        if (scenario == 1) {
            // Scenario 1: Normal operation state
            {{SCENARIO_1_SETUP}}
        } else if (scenario == 2) {
            // Scenario 2: Edge case state
            {{SCENARIO_2_SETUP}}
        } else if (scenario == 3) {
            // Scenario 3: Stress test state
            {{SCENARIO_3_SETUP}}
        }
        // Add more scenarios as needed
    }
    
    /**
     * @dev Assert contract state matches expected values
     * @param {{CONTRACT_INSTANCE}} The contract to check
     * @param expectedValue1 First expected value
     * @param expectedValue2 Second expected value
     */
    function assertContractState(
        address {{CONTRACT_INSTANCE}},
        uint256 expectedValue1,
        uint256 expectedValue2
    ) internal {
        // Add your specific state assertions here
        {{STATE_ASSERTIONS}}
    }
    
    // ====== TEST DATA GENERATION ======
    
    /**
     * @dev Generate test data based on a seed
     * @param seed Seed for deterministic random generation
     * @return Generated test data struct
     */
    function generateTestData(uint256 seed) internal pure returns ({{TEST_DATA_TYPE}}) {
        // Use seed to generate deterministic but varied test data
        uint256 amount = (seed % 1000000) * 1e18; // Random amount up to 1M tokens
        address beneficiary = address(uint160(seed % type(uint160).max));
        uint256 timestamp = 1000000000 + (seed % 100000000); // Reasonable timestamp range
        
        return {{TEST_DATA_TYPE}}({
            amount: amount,
            beneficiary: beneficiary,
            timestamp: timestamp
            {{ADDITIONAL_DATA_FIELDS}}
        });
    }
    
    /**
     * @dev Generate array of test amounts for comprehensive testing
     * @param count Number of amounts to generate
     * @return Array of test amounts including edge cases
     */
    function generateTestAmounts(uint256 count) internal pure returns (uint256[] memory) {
        uint256[] memory amounts = new uint256[](count);
        
        // Include important edge cases
        amounts[0] = 0; // Zero amount
        amounts[1] = 1; // Minimum non-zero
        amounts[2] = 1e18; // Standard unit
        amounts[3] = type(uint256).max; // Maximum value
        
        // Fill remaining with varied amounts
        for (uint256 i = 4; i < count; i++) {
            amounts[i] = (i * 12345) % 1000000 * 1e18;
        }
        
        return amounts;
    }
    
    // ====== COMMON INTERACTION PATTERNS ======
    
    /**
     * @dev Execute a standard deposit workflow
     * @param {{CONTRACT_INSTANCE}} The contract to interact with
     * @param user The user performing the deposit
     * @param amount The amount to deposit
     */
    function executeDepositWorkflow(
        address {{CONTRACT_INSTANCE}},
        address user,
        uint256 amount
    ) internal {
        vm.startPrank(user);
        
        // Standard deposit pattern
        {{DEPOSIT_WORKFLOW_STEPS}}
        
        vm.stopPrank();
    }
    
    /**
     * @dev Execute a standard withdrawal workflow
     * @param {{CONTRACT_INSTANCE}} The contract to interact with
     * @param user The user performing the withdrawal
     * @param amount The amount to withdraw
     */
    function executeWithdrawalWorkflow(
        address {{CONTRACT_INSTANCE}},
        address user,
        uint256 amount
    ) internal {
        vm.startPrank(user);
        
        // Standard withdrawal pattern
        {{WITHDRAWAL_WORKFLOW_STEPS}}
        
        vm.stopPrank();
    }
    
    // ====== ASSERTION HELPERS ======
    
    /**
     * @dev Assert that two addresses have proportional balances
     * @param token The ERC20 token to check
     * @param user1 First user address
     * @param user2 Second user address
     * @param ratio Expected ratio (user1 balance / user2 balance)
     * @param tolerance Acceptable deviation (in basis points, e.g., 100 = 1%)
     */
    function assertProportionalBalances(
        IERC20 token,
        address user1,
        address user2,
        uint256 ratio,
        uint256 tolerance
    ) internal {
        uint256 balance1 = token.balanceOf(user1);
        uint256 balance2 = token.balanceOf(user2);
        
        if (balance2 == 0) {
            assertEq(balance1, 0, "Both balances should be zero");
            return;
        }
        
        uint256 actualRatio = (balance1 * 10000) / balance2;
        uint256 expectedRatio = ratio * 10000;
        
        assertApproxEqRel(
            actualRatio,
            expectedRatio,
            tolerance * 1e14, // Convert basis points to 18-decimal precision
            "Balance ratio outside tolerance"
        );
    }
    
    /**
     * @dev Assert event was emitted with specific parameters
     * @param emitter The contract that should emit the event
     * @param eventSignature The event signature to check
     */
    function expectEventEmission(address emitter, bytes32 eventSignature) internal {
        vm.expectEmit(true, true, true, true, emitter);
        // Emit the expected event in the calling test
    }
    
    // ====== TIME AND BLOCK HELPERS ======
    
    /**
     * @dev Fast forward time and mine blocks
     * @param timeInSeconds Seconds to advance
     * @param blocks Number of blocks to mine
     */
    function timeWarpAndMine(uint256 timeInSeconds, uint256 blocks) internal {
        vm.warp(block.timestamp + timeInSeconds);
        vm.roll(block.number + blocks);
    }
    
    /**
     * @dev Setup a specific block state for testing
     * @param blockNumber Target block number
     * @param timestamp Target timestamp
     */
    function setupBlockState(uint256 blockNumber, uint256 timestamp) internal {
        vm.roll(blockNumber);
        vm.warp(timestamp);
    }
    
    // ====== ERROR TESTING HELPERS ======
    
    /**
     * @dev Test that a function reverts with expected error
     * @param target The contract to call
     * @param callData The function call data
     * @param expectedError The expected error selector
     */
    function expectSpecificRevert(
        address target,
        bytes memory callData,
        bytes4 expectedError
    ) internal {
        vm.expectRevert(expectedError);
        (bool success,) = target.call(callData);
        // The revert expectation should catch the error
        if (success) {
            revert("Expected revert did not occur");
        }
    }
    
    // ====== GAS TESTING HELPERS ======
    
    /**
     * @dev Measure gas usage of a function call
     * @param target The contract to call
     * @param callData The function call data
     * @return gasUsed The amount of gas consumed
     */
    function measureGasUsage(
        address target,
        bytes memory callData
    ) internal returns (uint256 gasUsed) {
        uint256 gasBefore = gasleft();
        (bool success,) = target.call(callData);
        require(success, "Function call failed");
        gasUsed = gasBefore - gasleft();
    }
    
    // ====== LOGGING AND DEBUGGING ======
    
    /**
     * @dev Log contract state for debugging
     * @param {{CONTRACT_INSTANCE}} The contract to inspect
     * @param label Description label for the log
     */
    function logContractState(address {{CONTRACT_INSTANCE}}, string memory label) internal view {
        console.log("=== Contract State:", label, "===");
        {{STATE_LOGGING_CODE}}
        console.log("=====================================");
    }
    
    /**
     * @dev Log user balances for debugging
     * @param token The ERC20 token to check
     * @param users Array of user addresses
     * @param label Description label for the log
     */
    function logUserBalances(
        IERC20 token,
        address[] memory users,
        string memory label
    ) internal view {
        console.log("=== User Balances:", label, "===");
        for (uint256 i = 0; i < users.length; i++) {
            console.log("User", i, "balance:", token.balanceOf(users[i]));
        }
        console.log("====================================");
    }
} 