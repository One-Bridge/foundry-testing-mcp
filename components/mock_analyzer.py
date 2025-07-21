"""
Mock Sophistication Analyzer for Smart Contract Testing

This module addresses the critical gap in mock analysis identified in expert feedback:
- Distinguishes sophisticated mocks from simple cheating
- Evaluates mock realism and capabilities 
- Provides context-aware mock quality assessment
- Reduces false positives in AI failure detection
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MockingStrategy(Enum):
    """Different mocking strategies"""
    STATIC_MOCK = "static_mock"
    SIMPLE_OVERRIDE = "simple_override" 
    FAILURE_MODE_SIMULATION = "failure_mode_simulation"
    SOPHISTICATED_SIMULATION = "sophisticated_simulation"

class MockSophisticationLevel(Enum):
    """Mock sophistication levels"""
    MINIMAL = "minimal"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SOPHISTICATED = "sophisticated"

@dataclass
class MockFeatures:
    """Features detected in a mock contract"""
    has_transfer_blocking: bool = False
    has_revert_toggling: bool = False
    has_balance_manipulation: bool = False
    has_custom_decimals: bool = False
    has_ownership_controls: bool = False
    has_event_emission: bool = False
    has_blacklist_support: bool = False
    has_price_oracle: bool = False
    has_access_control: bool = False
    has_state_tracking: bool = False
    has_configurable_params: bool = False
    has_realistic_failures: bool = False

@dataclass
class MockQualityAssessment:
    """Assessment of mock quality vs cheating"""
    is_cheating: bool
    sophistication_level: MockSophisticationLevel
    cheating_indicators: List[str]
    sophistication_indicators: List[str]
    realism_score: float
    recommendation: str

@dataclass
class MockAnalysis:
    """Complete analysis of a mock contract"""
    mock_name: str
    mock_type: str  # ERC20, ERC721, Oracle, etc.
    features: MockFeatures
    configurability: float
    state_tracking: bool
    failure_modes: List[str]
    realism_score: float
    sophistication_level: MockSophisticationLevel
    mocking_strategy: MockingStrategy
    quality_assessment: MockQualityAssessment
    improvements_suggested: List[str]

class MockSophisticationAnalyzer:
    """
    Analyzes mock contracts to distinguish sophisticated simulation 
    from simple cheating patterns.
    """
    
    def __init__(self):
        """Initialize mock analyzer with sophistication patterns."""
        self.sophistication_patterns = self._initialize_sophistication_patterns()
        self.cheating_patterns = self._initialize_cheating_patterns()
        self.mock_types = self._initialize_mock_types()
        logger.info("Mock sophistication analyzer initialized")
    
    def _initialize_sophistication_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate sophisticated mocking."""
        return {
            "configurability": [
                "setTransferBlocked", "setShouldRevert", "setBalance", 
                "setDecimals", "setBlacklisted", "setPrice", "configure"
            ],
            "state_tracking": [
                "balances", "allowances", "totalSupply", "paused",
                "blacklisted", "lastUpdate", "state", "history"
            ],
            "realistic_failures": [
                "InsufficientBalance", "TransferBlocked", "Blacklisted",
                "Paused", "ExceedsAllowance", "InvalidAddress"
            ],
            "event_emission": [
                "emit Transfer", "emit Approval", "emit", "Transfer(", "Approval("
            ],
            "access_control": [
                "onlyOwner", "require(owner", "require(authorized", "_checkRole"
            ],
            "complex_logic": [
                "if", "else", "for", "while", "mapping", "struct", "modifier"
            ]
        }
    
    def _initialize_cheating_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate mock cheating."""
        return {
            "always_returns_success": [
                "return true;", "returns (bool) { return true; }",
                "success = true;", "result = true;"
            ],
            "ignores_input_validation": [
                "// ignore", "// TODO", "return amount;", "return _amount;"
            ],
            "no_state_tracking": [
                "return 0;", "return address(0);", "return \"\";",
                "pure", "view returns"
            ],
            "unrealistic_behavior": [
                "return type(uint256).max;", "return 1e18;", 
                "always returns", "fixed return"
            ],
            "missing_error_conditions": [
                "never reverts", "no validation", "no checks"
            ]
        }
    
    def _initialize_mock_types(self) -> Dict[str, Dict[str, Any]]:
        """Initialize expected features for different mock types."""
        return {
            "ERC20": {
                "required_functions": ["transfer", "approve", "balanceOf", "totalSupply"],
                "expected_features": ["balance_tracking", "allowance_system", "transfer_validation"],
                "common_failures": ["insufficient_balance", "transfer_blocked", "paused"]
            },
            "ERC721": {
                "required_functions": ["ownerOf", "approve", "transferFrom", "tokenURI"],
                "expected_features": ["ownership_tracking", "approval_system", "metadata"],
                "common_failures": ["not_owner", "not_approved", "invalid_token"]
            },
            "Oracle": {
                "required_functions": ["getPrice", "latestRoundData", "decimals"],
                "expected_features": ["price_feeds", "staleness_checks", "decimals_handling"],
                "common_failures": ["stale_price", "invalid_round", "negative_price"]
            },
            "AccessControl": {
                "required_functions": ["hasRole", "grantRole", "revokeRole"],
                "expected_features": ["role_management", "permission_checks"],
                "common_failures": ["unauthorized", "invalid_role", "role_admin_only"]
            }
        }
    
    def analyze_mock_contract(self, contract_content: str, contract_name: str) -> MockAnalysis:
        """
        Perform comprehensive analysis of a mock contract.
        
        This addresses the expert feedback about flagging sophisticated mocks
        as "cheating" without understanding their capabilities.
        """
        # Detect mock type
        mock_type = self._detect_mock_type(contract_content, contract_name)
        
        # Analyze features
        features = self._analyze_mock_features(contract_content)
        
        # Calculate configurability
        configurability = self._calculate_configurability(contract_content, features)
        
        # Detect state tracking
        state_tracking = self._detect_state_tracking(contract_content)
        
        # Identify failure modes
        failure_modes = self._identify_failure_modes(contract_content)
        
        # Calculate realism score
        realism_score = self._calculate_realism_score(contract_content, mock_type, features)
        
        # Determine sophistication level
        sophistication_level = self._determine_sophistication_level(realism_score, features)
        
        # Identify mocking strategy
        mocking_strategy = self._identify_mocking_strategy(features, configurability)
        
        # Assess quality vs cheating
        quality_assessment = self._assess_mock_quality(contract_content, features, realism_score)
        
        # Generate improvement suggestions
        improvements = self._generate_improvement_suggestions(mock_type, features, quality_assessment)
        
        return MockAnalysis(
            mock_name=contract_name,
            mock_type=mock_type,
            features=features,
            configurability=configurability,
            state_tracking=state_tracking,
            failure_modes=failure_modes,
            realism_score=realism_score,
            sophistication_level=sophistication_level,
            mocking_strategy=mocking_strategy,
            quality_assessment=quality_assessment,
            improvements_suggested=improvements
        )
    
    def _detect_mock_type(self, content: str, name: str) -> str:
        """Detect the type of mock contract."""
        name_lower = name.lower()
        
        if "erc20" in name_lower or "token" in name_lower:
            return "ERC20"
        elif "erc721" in name_lower or "nft" in name_lower:
            return "ERC721"
        elif "oracle" in name_lower or "price" in name_lower or "feed" in name_lower:
            return "Oracle"
        elif "access" in name_lower or "role" in name_lower:
            return "AccessControl"
        elif "vault" in name_lower or "strategy" in name_lower:
            return "Vault"
        else:
            return "Generic"
    
    def _analyze_mock_features(self, content: str) -> MockFeatures:
        """Analyze features present in the mock contract."""
        features = MockFeatures()
        
        # Check for transfer blocking
        features.has_transfer_blocking = any(
            pattern in content for pattern in 
            ["setTransferBlocked", "transferBlocked", "blockTransfer"]
        )
        
        # Check for revert toggling
        features.has_revert_toggling = any(
            pattern in content for pattern in 
            ["setShouldRevert", "shouldRevert", "revertEnabled"]
        )
        
        # Check for balance manipulation
        features.has_balance_manipulation = any(
            pattern in content for pattern in 
            ["setBalance", "mint", "burn", "addBalance"]
        )
        
        # Check for custom decimals
        features.has_custom_decimals = any(
            pattern in content for pattern in 
            ["setDecimals", "decimals =", "_decimals"]
        )
        
        # Check for ownership controls
        features.has_ownership_controls = any(
            pattern in content for pattern in 
            ["onlyOwner", "Ownable", "owner =", "_owner"]
        )
        
        # Check for event emission
        features.has_event_emission = any(
            pattern in content for pattern in 
            ["emit ", "Transfer(", "Approval(", "event "]
        )
        
        # Check for blacklist support
        features.has_blacklist_support = any(
            pattern in content for pattern in 
            ["blacklist", "blacklisted", "setBlacklisted"]
        )
        
        # Check for price oracle features
        features.has_price_oracle = any(
            pattern in content for pattern in 
            ["setPrice", "price =", "latestRoundData", "getPrice"]
        )
        
        # Check for access control
        features.has_access_control = any(
            pattern in content for pattern in 
            ["hasRole", "grantRole", "revokeRole", "_checkRole"]
        )
        
        # Check for state tracking
        features.has_state_tracking = any(
            pattern in content for pattern in 
            ["mapping", "balances", "allowances", "state"]
        )
        
        # Check for configurable parameters
        features.has_configurable_params = any(
            pattern in content for pattern in 
            ["set", "configure", "update", "change"]
        )
        
        # Check for realistic failures
        features.has_realistic_failures = any(
            pattern in content for pattern in 
            ["require(", "revert(", "if (", "InsufficientBalance"]
        )
        
        return features
    
    def _calculate_configurability(self, content: str, features: MockFeatures) -> float:
        """Calculate how configurable the mock is."""
        configurable_functions = 0
        
        # Count setter functions
        setter_patterns = [
            r'function\s+set\w+',
            r'function\s+configure\w*',
            r'function\s+update\w+',
            r'function\s+toggle\w+'
        ]
        
        for pattern in setter_patterns:
            configurable_functions += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Bonus for specific features
        if features.has_transfer_blocking:
            configurable_functions += 1
        if features.has_revert_toggling:
            configurable_functions += 1
        if features.has_balance_manipulation:
            configurable_functions += 1
        
        # Normalize to 0-1 scale
        return min(1.0, configurable_functions / 5)
    
    def _detect_state_tracking(self, content: str) -> bool:
        """Check if mock tracks state realistically."""
        state_indicators = [
            "mapping", "balances", "allowances", "totalSupply",
            "paused", "blacklisted", "nonces", "state"
        ]
        
        return any(indicator in content for indicator in state_indicators)
    
    def _identify_failure_modes(self, content: str) -> List[str]:
        """Identify different failure modes the mock can simulate."""
        failure_modes = []
        
        failure_patterns = {
            "insufficient_balance": ["InsufficientBalance", "balance <", "balanceOf("],
            "transfer_blocked": ["TransferBlocked", "transferBlocked", "blocked"],
            "paused": ["Paused", "paused", "whenNotPaused"],
            "blacklisted": ["Blacklisted", "blacklisted", "isBlacklisted"],
            "invalid_address": ["InvalidAddress", "address(0)", "zero address"],
            "exceeds_allowance": ["ExceedsAllowance", "allowance <", "approve"],
            "unauthorized": ["Unauthorized", "onlyOwner", "hasRole"],
            "stale_price": ["StalePrice", "stale", "updatedAt"],
            "invalid_round": ["InvalidRound", "roundId", "round"]
        }
        
        for mode, patterns in failure_patterns.items():
            if any(pattern in content for pattern in patterns):
                failure_modes.append(mode)
        
        return failure_modes
    
    def _calculate_realism_score(self, content: str, mock_type: str, features: MockFeatures) -> float:
        """Calculate how realistic the mock behavior is."""
        score = 0.0
        
        # Base score from features
        feature_scores = [
            features.has_state_tracking,
            features.has_realistic_failures,
            features.has_event_emission,
            features.has_configurable_params,
            features.has_access_control
        ]
        score += sum(feature_scores) / len(feature_scores) * 0.4
        
        # Type-specific realism
        if mock_type in self.mock_types:
            type_info = self.mock_types[mock_type]
            required_functions = type_info["required_functions"]
            
            # Check if required functions are present
            functions_present = sum(
                1 for func in required_functions 
                if f"function {func}" in content or f"function _{func}" in content
            )
            score += (functions_present / len(required_functions)) * 0.3
        
        # Complexity bonus
        complexity_indicators = ["if (", "require(", "mapping", "modifier", "struct"]
        complexity_score = min(1.0, sum(content.count(indicator) for indicator in complexity_indicators) / 10)
        score += complexity_score * 0.3
        
        return min(1.0, score)
    
    def _determine_sophistication_level(self, realism_score: float, features: MockFeatures) -> MockSophisticationLevel:
        """Determine the sophistication level of the mock."""
        if realism_score >= 0.8:
            return MockSophisticationLevel.SOPHISTICATED
        elif realism_score >= 0.6:
            return MockSophisticationLevel.ADVANCED
        elif realism_score >= 0.4:
            return MockSophisticationLevel.INTERMEDIATE
        elif realism_score >= 0.2:
            return MockSophisticationLevel.BASIC
        else:
            return MockSophisticationLevel.MINIMAL
    
    def _identify_mocking_strategy(self, features: MockFeatures, configurability: float) -> MockingStrategy:
        """Identify the mocking strategy being used."""
        if features.has_state_tracking and features.has_realistic_failures and configurability > 0.6:
            return MockingStrategy.SOPHISTICATED_SIMULATION
        elif features.has_realistic_failures and configurability > 0.3:
            return MockingStrategy.FAILURE_MODE_SIMULATION
        elif configurability > 0.1 or features.has_configurable_params:
            return MockingStrategy.SIMPLE_OVERRIDE
        else:
            return MockingStrategy.STATIC_MOCK
    
    def _assess_mock_quality(self, content: str, features: MockFeatures, realism_score: float) -> MockQualityAssessment:
        """Assess whether mock is sophisticated or cheating."""
        sophistication_indicators = []
        cheating_indicators = []
        
        # Check sophistication indicators
        if features.has_state_tracking:
            sophistication_indicators.append("Tracks state realistically")
        if features.has_realistic_failures:
            sophistication_indicators.append("Simulates realistic failure conditions")
        if features.has_configurable_params:
            sophistication_indicators.append("Configurable for different test scenarios")
        if features.has_event_emission:
            sophistication_indicators.append("Emits events like real contracts")
        if features.has_access_control:
            sophistication_indicators.append("Implements access control patterns")
        
        # Check cheating indicators
        if "return true;" in content and content.count("return true;") > 2:
            cheating_indicators.append("Always returns true without validation")
        if "return 0;" in content and content.count("return 0;") > 3:
            cheating_indicators.append("Always returns zero without logic")
        if content.count("// TODO") > 2:
            cheating_indicators.append("Multiple unimplemented functions")
        if "ignore" in content.lower():
            cheating_indicators.append("Explicitly ignores input validation")
        
        # Determine if cheating
        sophistication_score = len(sophistication_indicators)
        cheating_score = len(cheating_indicators)
        is_cheating = cheating_score > sophistication_score and realism_score < 0.3
        
        # Generate recommendation
        if is_cheating:
            recommendation = "This mock shows cheating patterns. Add realistic state tracking and failure modes."
        elif realism_score >= 0.7:
            recommendation = "Sophisticated mock with realistic behavior. Good for comprehensive testing."
        elif realism_score >= 0.4:
            recommendation = "Decent mock. Consider adding more configurable failure modes for edge case testing."
        else:
            recommendation = "Basic mock. Add state tracking and realistic failure conditions for better testing."
        
        return MockQualityAssessment(
            is_cheating=is_cheating,
            sophistication_level=self._determine_sophistication_level(realism_score, features),
            cheating_indicators=cheating_indicators,
            sophistication_indicators=sophistication_indicators,
            realism_score=realism_score,
            recommendation=recommendation
        )
    
    def _generate_improvement_suggestions(self, mock_type: str, features: MockFeatures, 
                                        quality_assessment: MockQualityAssessment) -> List[str]:
        """Generate specific improvement suggestions for the mock."""
        suggestions = []
        
        if not features.has_state_tracking:
            suggestions.append("Add state tracking (balances, allowances) for realistic behavior")
        
        if not features.has_realistic_failures:
            suggestions.append("Add realistic failure modes (insufficient balance, unauthorized access)")
        
        if not features.has_event_emission:
            suggestions.append("Emit events to match real contract behavior")
        
        if not features.has_configurable_params:
            suggestions.append("Add configuration functions to test different scenarios")
        
        if quality_assessment.is_cheating:
            suggestions.append("Replace hardcoded return values with conditional logic")
            suggestions.append("Add input validation and error conditions")
        
        # Type-specific suggestions
        if mock_type == "ERC20" and not features.has_balance_manipulation:
            suggestions.append("Add mint/burn functions for balance testing")
        
        if mock_type == "Oracle" and not features.has_price_oracle:
            suggestions.append("Add price manipulation functions for oracle testing")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def analyze_mock_suite(self, test_content: str) -> Dict[str, MockAnalysis]:
        """Analyze all mocks in a test suite."""
        mocks = {}
        
        # Find mock contracts
        mock_pattern = r'contract\s+(Mock\w+|.*Mock)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        mock_matches = re.findall(mock_pattern, test_content, re.DOTALL)
        
        for mock_name, mock_body in mock_matches:
            try:
                analysis = self.analyze_mock_contract(mock_body, mock_name)
                mocks[mock_name] = analysis
            except Exception as e:
                logger.warning(f"Could not analyze mock {mock_name}: {e}")
        
        return mocks
    
    def generate_mock_quality_report(self, mock_analyses: Dict[str, MockAnalysis]) -> Dict[str, Any]:
        """Generate overall mock quality report."""
        if not mock_analyses:
            return {
                "status": "no_mocks",
                "message": "No mock contracts found"
            }
        
        sophisticated_mocks = [
            name for name, analysis in mock_analyses.items()
            if analysis.sophistication_level in [MockSophisticationLevel.ADVANCED, MockSophisticationLevel.SOPHISTICATED]
        ]
        
        cheating_mocks = [
            name for name, analysis in mock_analyses.items()
            if analysis.quality_assessment.is_cheating
        ]
        
        avg_realism = sum(analysis.realism_score for analysis in mock_analyses.values()) / len(mock_analyses)
        
        return {
            "status": "analyzed",
            "total_mocks": len(mock_analyses),
            "sophisticated_mocks": sophisticated_mocks,
            "cheating_mocks": cheating_mocks,
            "average_realism_score": round(avg_realism, 2),
            "overall_quality": self._determine_overall_mock_quality(avg_realism, len(sophisticated_mocks), len(cheating_mocks)),
            "recommendations": self._generate_suite_recommendations(mock_analyses)
        }
    
    def _determine_overall_mock_quality(self, avg_realism: float, sophisticated_count: int, cheating_count: int) -> str:
        """Determine overall mock suite quality."""
        if cheating_count > sophisticated_count:
            return "Poor - Multiple cheating mocks detected"
        elif avg_realism >= 0.7:
            return "Excellent - Sophisticated and realistic mocks"
        elif avg_realism >= 0.5:
            return "Good - Decent mock quality with room for improvement"
        else:
            return "Needs Improvement - Basic mocks lacking realism"
    
    def _generate_suite_recommendations(self, mock_analyses: Dict[str, MockAnalysis]) -> List[str]:
        """Generate recommendations for the entire mock suite."""
        recommendations = []
        
        cheating_mocks = [name for name, analysis in mock_analyses.items() if analysis.quality_assessment.is_cheating]
        if cheating_mocks:
            recommendations.append(f"Fix cheating patterns in: {', '.join(cheating_mocks)}")
        
        basic_mocks = [
            name for name, analysis in mock_analyses.items()
            if analysis.sophistication_level == MockSophisticationLevel.MINIMAL
        ]
        if basic_mocks:
            recommendations.append(f"Enhance basic mocks: {', '.join(basic_mocks)}")
        
        no_state_mocks = [
            name for name, analysis in mock_analyses.items()
            if not analysis.state_tracking
        ]
        if len(no_state_mocks) > len(mock_analyses) / 2:
            recommendations.append("Add state tracking to most mocks for realistic behavior")
        
        return recommendations[:3]  # Top 3 recommendations
