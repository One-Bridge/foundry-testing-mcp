// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {TransparentUpgradeableProxy} from "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import {ProxyAdmin} from "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";
import "../src/{{IMPLEMENTATION_CONTRACT}}.sol";
import "../src/{{IMPLEMENTATION_V2_CONTRACT}}.sol";

/**
 * @title {{CONTRACT_NAME}}ProxyTest
 * @dev Comprehensive proxy pattern testing suite
 * @notice Tests proxy upgrade mechanisms, state preservation, and access controls
 * @author Smart Contract Testing MCP Server
 * 
 * CRITICAL TESTING RULE: Always interact with proxy address, never implementation directly
 */
contract {{CONTRACT_NAME}}ProxyTest is Test {
    
    // Proxy contracts
    {{PROXY_TYPE}} public proxy;
    ProxyAdmin public proxyAdmin; // For Transparent proxies
    
    // Implementation contracts
    {{IMPLEMENTATION_CONTRACT}} public implementation;
    {{IMPLEMENTATION_CONTRACT}} public implementationV2;
    
    // Proxy interface instances (ABI of implementation, address of proxy)
    {{IMPLEMENTATION_CONTRACT}} public proxyContract;
    
    // Test accounts
    address public owner = makeAddr("owner");
    address public admin = makeAddr("admin");  
    address public user = makeAddr("user");
    address public attacker = makeAddr("attacker");
    
    // Test constants
    uint256 public constant INITIAL_VALUE = 1000;
    uint256 public constant UPGRADE_VALUE = 2000;
    
    // EIP-1967 Storage Slots for verification
    bytes32 private constant IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;
    bytes32 private constant ADMIN_SLOT = 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6107;
    
    function setUp() public {
        vm.startPrank(owner);
        
        // Deploy implementation contracts
        implementation = new {{IMPLEMENTATION_CONTRACT}}();
        implementationV2 = new {{IMPLEMENTATION_V2_CONTRACT}}();
        
        {{PROXY_SETUP}}
        
        vm.stopPrank();
        
        // Fund test accounts
        vm.deal(user, 10 ether);
        vm.deal(attacker, 5 ether);
    }
    
    // =============================================================
    //                    TRANSPARENT PROXY SETUP
    // =============================================================
    
    function _setupTransparentProxy() internal {
        // Deploy ProxyAdmin
        proxyAdmin = new ProxyAdmin();
        
        // Encode initialization call
        bytes memory initData = abi.encodeWithSelector(
            {{IMPLEMENTATION_CONTRACT}}.initialize.selector,
            {{INITIALIZATION_PARAMS}}
        );
        
        // Deploy Transparent proxy
        proxy = TransparentUpgradeableProxy(payable(address(new TransparentUpgradeableProxy(
            address(implementation),
            address(proxyAdmin),
            initData
        ))));
        
        // Create interface to interact with proxy using implementation ABI
        proxyContract = {{IMPLEMENTATION_CONTRACT}}(address(proxy));
    }
    
    // =============================================================
    //                       UUPS PROXY SETUP  
    // =============================================================
    
    function _setupUUPSProxy() internal {
        // Encode initialization call
        bytes memory initData = abi.encodeWithSelector(
            {{IMPLEMENTATION_CONTRACT}}.initialize.selector,
            {{INITIALIZATION_PARAMS}}
        );
        
        // Deploy ERC1967Proxy (UUPS)
        proxy = ERC1967Proxy(payable(address(new ERC1967Proxy(
            address(implementation),
            initData
        ))));
        
        // Create interface to interact with proxy using implementation ABI
        proxyContract = {{IMPLEMENTATION_CONTRACT}}(address(proxy));
    }
    
    // =============================================================
    //                     DIAMOND PROXY SETUP
    // =============================================================
    
    function _setupDiamondProxy() internal {
        // Diamond setup is more complex - implement based on your diamond standard
        {{DIAMOND_SETUP_CODE}}
    }
    
    // =============================================================
    //                    INITIALIZATION TESTS
    // =============================================================
    
    function test_initialization_stateSetCorrectly() public {
        // Verify initial state through proxy
        assertEq(proxyContract.{{STATE_GETTER}}(), {{EXPECTED_INITIAL_STATE}});
        assertEq(proxyContract.owner(), owner);
    }
    
    function test_initialization_cannotBeCalledTwice() public {
        // Attempting to initialize again should revert
        vm.expectRevert("Initializable: contract is already initialized");
        proxyContract.initialize({{INITIALIZATION_PARAMS}});
    }
    
    function test_implementation_cannotBeInitializedDirectly() public {
        // Implementation should not be initializable after proxy deployment
        vm.expectRevert("Initializable: contract is already initialized");
        implementation.initialize({{INITIALIZATION_PARAMS}});
    }
    
    // =============================================================
    //                    PROXY FUNCTIONALITY TESTS
    // =============================================================
    
    function test_proxyDelegatesToImplementation() public {
        uint256 newValue = 500;
        
        vm.prank(user);
        proxyContract.{{SETTER_FUNCTION}}(newValue);
        
        // Verify state change through proxy
        assertEq(proxyContract.{{STATE_GETTER}}(), newValue);
    }
    
    function test_proxyMaintainsOwnStorage() public {
        uint256 newValue = 750;
        
        // Change state through proxy
        vm.prank(user);
        proxyContract.{{SETTER_FUNCTION}}(newValue);
        
        // Implementation contract should not have this state
        assertEq(implementation.{{STATE_GETTER}}(), 0); // Default value
        
        // But proxy should have the state
        assertEq(proxyContract.{{STATE_GETTER}}(), newValue);
    }
    
    // =============================================================
    //                      UPGRADE TESTS
    // =============================================================
    
    function test_upgradePreservesState() public {
        // Set state through proxy before upgrade
        vm.prank(user);
        proxyContract.{{SETTER_FUNCTION}}(INITIAL_VALUE);
        
        // Verify initial state
        assertEq(proxyContract.{{STATE_GETTER}}(), INITIAL_VALUE);
        
        // Perform upgrade
        _performUpgrade();
        
        // Cast to V2 interface for new functionality
        {{IMPLEMENTATION_V2_CONTRACT}} proxyV2 = {{IMPLEMENTATION_V2_CONTRACT}}(address(proxy));
        
        // Verify state is preserved
        assertEq(proxyV2.{{STATE_GETTER}}(), INITIAL_VALUE);
        
        // Verify new functionality works
        proxyV2.{{NEW_FUNCTION}}(UPGRADE_VALUE);
        assertEq(proxyV2.{{NEW_STATE_GETTER}}(), UPGRADE_VALUE);
    }
    
    function test_upgradeChangesImplementation() public {
        // Get current implementation address
        address currentImpl = _getImplementationAddress();
        assertEq(currentImpl, address(implementation));
        
        // Perform upgrade
        _performUpgrade();
        
        // Verify implementation changed
        address newImpl = _getImplementationAddress();
        assertEq(newImpl, address(implementationV2));
        assertNotEq(newImpl, currentImpl);
    }
    
    function test_onlyAuthorizedCanUpgrade() public {
        vm.prank(attacker);
        vm.expectRevert({{UNAUTHORIZED_UPGRADE_ERROR}});
        {{UPGRADE_FUNCTION_CALL}}
    }
    
    // =============================================================
    //                  TRANSPARENT PROXY SPECIFIC TESTS
    // =============================================================
    
    function test_transparent_adminCannotCallImplementation() public {
        // Admin should not be able to call implementation functions
        vm.prank(address(proxyAdmin));
        {{ADMIN_CALL_RESTRICTION_TEST}}
    }
    
    function test_transparent_changeAdmin() public {
        address newAdmin = makeAddr("newAdmin");
        
        vm.prank(owner);
        proxyAdmin.changeProxyAdmin(proxy, newAdmin);
        
        // Verify admin change
        assertEq(_getAdminAddress(), newAdmin);
    }
    
    // =============================================================
    //                     UUPS SPECIFIC TESTS
    // =============================================================
    
    function test_uups_authorizeUpgradeAccess() public {
        vm.prank(attacker);
        vm.expectRevert("Ownable: caller is not the owner");
        proxyContract.upgradeTo(address(implementationV2));
    }
    
    function test_uups_upgradeToAndCall() public {
        bytes memory initData = abi.encodeWithSelector(
            {{IMPLEMENTATION_V2_CONTRACT}}.{{POST_UPGRADE_FUNCTION}}.selector,
            {{POST_UPGRADE_PARAMS}}
        );
        
        vm.prank(owner);
        proxyContract.upgradeToAndCall(address(implementationV2), initData);
        
        // Verify upgrade and initialization
        {{IMPLEMENTATION_V2_CONTRACT}} proxyV2 = {{IMPLEMENTATION_V2_CONTRACT}}(address(proxy));
        {{POST_UPGRADE_VERIFICATION}}
    }
    
    // =============================================================
    //                   DIAMOND SPECIFIC TESTS
    // =============================================================
    
    function test_diamond_addFacet() public {
        {{DIAMOND_ADD_FACET_TEST}}
    }
    
    function test_diamond_replaceFacet() public {
        {{DIAMOND_REPLACE_FACET_TEST}}
    }
    
    function test_diamond_removeFacet() public {
        {{DIAMOND_REMOVE_FACET_TEST}}
    }
    
    function test_diamond_loupeFunctions() public {
        {{DIAMOND_LOUPE_TEST}}
    }
    
    // =============================================================
    //                      SECURITY TESTS
    // =============================================================
    
    function test_implementationIsolation() public {
        // Implementation should not have proxy's state
        uint256 proxyState = proxyContract.{{STATE_GETTER}}();
        uint256 implState = implementation.{{STATE_GETTER}}();
        
        // They should be different (proxy has state, implementation doesn't)
        assertNotEq(proxyState, implState);
    }
    
    function test_noDirectImplementationCalls() public {
        // Direct calls to implementation should not affect proxy state
        uint256 initialProxyState = proxyContract.{{STATE_GETTER}}();
        
        // Call implementation directly
        implementation.{{SETTER_FUNCTION}}(999);
        
        // Proxy state should be unchanged
        assertEq(proxyContract.{{STATE_GETTER}}(), initialProxyState);
    }
    
    function test_storageCollisionResistance() public {
        // Test that proxy storage doesn't collide with implementation storage
        {{STORAGE_COLLISION_TEST}}
    }
    
    // =============================================================
    //                       HELPER FUNCTIONS
    // =============================================================
    
    function _performUpgrade() internal {
        {{UPGRADE_IMPLEMENTATION}}
    }
    
    function _getImplementationAddress() internal view returns (address) {
        return address(uint160(uint256(vm.load(address(proxy), IMPLEMENTATION_SLOT))));
    }
    
    function _getAdminAddress() internal view returns (address) {
        return address(uint160(uint256(vm.load(address(proxy), ADMIN_SLOT))));
    }
    
    function _verifyEIP1967Compliance() internal view {
        // Verify proxy follows EIP-1967 standard
        address impl = _getImplementationAddress();
        assertTrue(impl != address(0), "Implementation address should not be zero");
        
        {{EIP1967_COMPLIANCE_CHECKS}}
    }
    
    // =============================================================
    //                     UPGRADE SCENARIOS
    // =============================================================
    
    function test_multipleUpgrades() public {
        // Test multiple sequential upgrades
        {{MULTIPLE_UPGRADE_TEST}}
    }
    
    function test_upgradeWithStorageChanges() public {
        // Test upgrade that changes storage layout (dangerous scenario)
        {{STORAGE_LAYOUT_CHANGE_TEST}}
    }
    
    function test_upgradeRollback() public {
        // Test downgrading to previous implementation
        {{UPGRADE_ROLLBACK_TEST}}
    }
    
    // =============================================================
    //                    EDGE CASE TESTS
    // =============================================================
    
    function test_proxyWithZeroImplementation() public {
        // Test behavior with zero implementation address
        {{ZERO_IMPLEMENTATION_TEST}}
    }
    
    function test_upgradeToSelfDestruct() public {
        // Test upgrade to self-destructing implementation
        {{SELFDESTRUCT_IMPLEMENTATION_TEST}}
    }
    
    function test_reentrancyDuringUpgrade() public {
        // Test reentrancy protection during upgrade
        {{REENTRANCY_UPGRADE_TEST}}
    }
} 