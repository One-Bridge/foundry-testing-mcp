"""
Domain-Specific Test Analysis for Smart Contract Testing

This module addresses the gap in contextual evaluation identified in expert feedback:
- Understands different project domains (DeFi, NFT, Governance, etc.)
- Evaluates tests against domain-specific requirements
- Provides contextually relevant recommendations
- Reduces false positives from generic pattern matching
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProjectDomain(Enum):
    """Project domain classifications"""
    DEFI = "DeFi"
    NFT = "NFT" 
    GOVERNANCE = "Governance"
    GAMING = "Gaming"
    BRIDGE = "Bridge"
    UTILITY = "Utility"
    GENERAL = "General"

class TestPatternComplexity(Enum):
    """Complexity levels for test patterns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DomainTestPattern:
    """A domain-specific test pattern"""
    name: str
    description: str
    required: bool
    complexity: TestPatternComplexity
    keywords: List[str]
    test_indicators: List[str]
    code_patterns: List[str]

@dataclass
class DomainAnalysis:
    """Analysis results for a specific domain"""
    domain: ProjectDomain
    confidence: float
    indicators: Dict[str, float]
    required_patterns: List[DomainTestPattern]
    implemented_patterns: List[str]
    missing_patterns: List[str]
    contextual_quality_score: float
    domain_specific_recommendations: List[str]

@dataclass
class ProjectClassification:
    """Complete project classification results"""
    primary_domain: ProjectDomain
    secondary_domains: List[ProjectDomain]
    classification_confidence: float
    domain_indicators: Dict[str, float]
    complexity_assessment: str

class DomainSpecificAnalyzer:
    """
    Analyzes projects to understand their domain and evaluate tests
    against domain-specific requirements.
    """
    
    def __init__(self):
        """Initialize domain analyzer with patterns and indicators."""
        self.domain_patterns = self._initialize_domain_patterns()
        self.domain_indicators = self._initialize_domain_indicators()
        self.test_requirements = self._initialize_test_requirements()
        logger.info("Domain-specific analyzer initialized")
    
    def _initialize_domain_patterns(self) -> Dict[ProjectDomain, List[DomainTestPattern]]:
        """Initialize domain-specific test patterns."""
        return {
            ProjectDomain.DEFI: [
                DomainTestPattern(
                    name="liquidity_manipulation_testing",
                    description="Tests for liquidity-based attacks and manipulation",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["liquidity", "manipulation", "attack", "exploit"],
                    test_indicators=["test.*liquidity.*attack", "test.*manipulat", "test.*exploit"],
                    code_patterns=["removeLiquidity", "addLiquidity", "flashloan", "price.*manipulat"]
                ),
                DomainTestPattern(
                    name="flash_loan_attack_simulation",
                    description="Simulates flash loan attack vectors",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["flash", "loan", "attack", "borrow"],
                    test_indicators=["test.*flash.*loan", "test.*flash.*attack", "test.*borrow.*attack"],
                    code_patterns=["flashloan", "flash.*borrow", "flashLoan", "borrow.*attack"]
                ),
                DomainTestPattern(
                    name="oracle_manipulation_resistance", 
                    description="Tests oracle manipulation resistance",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["oracle", "price", "manipulation", "feed"],
                    test_indicators=["test.*oracle.*manipulat", "test.*price.*attack", "test.*feed.*exploit"],
                    code_patterns=["oracle.*price", "manipulat.*price", "getPrice", "latestRoundData"]
                ),
                DomainTestPattern(
                    name="slippage_protection_validation",
                    description="Validates slippage protection mechanisms", 
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["slippage", "protection", "tolerance", "minimum"],
                    test_indicators=["test.*slippage", "test.*minimum.*output", "test.*tolerance"],
                    code_patterns=["slippage", "minimumOutput", "tolerance", "expectedOutput"]
                ),
                DomainTestPattern(
                    name="economic_invariant_testing",
                    description="Tests economic invariants and relationships",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["invariant", "economic", "balance", "conservation"],
                    test_indicators=["invariant.*balance", "invariant.*total", "invariant.*conservation"],
                    code_patterns=["invariant_", "totalSupply", "totalBalance", "conservation"]
                ),
                DomainTestPattern(
                    name="rebalancing_mechanism_testing",
                    description="Tests automated rebalancing mechanisms",
                    required=False,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["rebalance", "rebalancing", "allocation", "weight"],
                    test_indicators=["test.*rebalanc", "test.*allocation", "test.*weight"],
                    code_patterns=["rebalance", "allocation", "weight", "targetWeight"]
                ),
                DomainTestPattern(
                    name="fee_calculation_testing",
                    description="Tests fee calculation accuracy",
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["fee", "commission", "rate", "calculation"],
                    test_indicators=["test.*fee", "test.*commission", "test.*rate"],
                    code_patterns=["calculateFee", "feeRate", "commission", "protocolFee"]
                )
            ],
            
            ProjectDomain.NFT: [
                DomainTestPattern(
                    name="metadata_validation_testing",
                    description="Tests metadata integrity and validation",
                    required=True,
                    complexity=TestPatternComplexity.LOW,
                    keywords=["metadata", "uri", "validation", "json"],
                    test_indicators=["test.*metadata", "test.*uri", "test.*tokenURI"],
                    code_patterns=["tokenURI", "metadata", "setTokenURI", "baseURI"]
                ),
                DomainTestPattern(
                    name="royalty_mechanism_testing",
                    description="Tests royalty calculation and distribution",
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["royalty", "royalties", "fee", "creator"],
                    test_indicators=["test.*royalty", "test.*royalties", "test.*creator.*fee"],
                    code_patterns=["royaltyInfo", "setRoyalty", "royaltyFee", "creatorFee"]
                ),
                DomainTestPattern(
                    name="ownership_transfer_testing",
                    description="Tests secure ownership transfers",
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["transfer", "ownership", "approve", "operator"],
                    test_indicators=["test.*transfer", "test.*approve", "test.*operator"],
                    code_patterns=["transferFrom", "safeTransferFrom", "approve", "setApprovalForAll"]
                ),
                DomainTestPattern(
                    name="batch_operation_testing",
                    description="Tests batch minting/transferring operations",
                    required=False,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["batch", "multiple", "bulk", "mass"],
                    test_indicators=["test.*batch", "test.*bulk", "test.*multiple"],
                    code_patterns=["batchMint", "batchTransfer", "safeBatchTransfer"]
                )
            ],
            
            ProjectDomain.GOVERNANCE: [
                DomainTestPattern(
                    name="voting_mechanism_testing",
                    description="Tests voting accuracy and integrity",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["vote", "voting", "ballot", "consensus"],
                    test_indicators=["test.*vote", "test.*voting", "test.*ballot"],
                    code_patterns=["vote", "castVote", "votingPower", "getVotes"]
                ),
                DomainTestPattern(
                    name="proposal_lifecycle_testing",
                    description="Tests complete proposal lifecycles",
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["proposal", "propose", "execute", "queue"],
                    test_indicators=["test.*proposal", "test.*propose", "test.*execute"],
                    code_patterns=["propose", "execute", "queue", "proposalState"]
                ),
                DomainTestPattern(
                    name="delegation_testing",
                    description="Tests vote delegation mechanisms",
                    required=True,
                    complexity=TestPatternComplexity.MEDIUM,
                    keywords=["delegate", "delegation", "delegatee", "representative"],
                    test_indicators=["test.*delegat", "test.*representative"],
                    code_patterns=["delegate", "delegateBySig", "delegates", "delegatedVotes"]
                ),
                DomainTestPattern(
                    name="timelock_testing",
                    description="Tests timelock execution mechanisms",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["timelock", "delay", "schedule", "execute"],
                    test_indicators=["test.*timelock", "test.*delay", "test.*schedule"],
                    code_patterns=["timelock", "schedule", "executeBatch", "delay"]
                )
            ],
            
            ProjectDomain.BRIDGE: [
                DomainTestPattern(
                    name="cross_chain_validation_testing",
                    description="Tests cross-chain message validation",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["bridge", "cross", "chain", "relay"],
                    test_indicators=["test.*bridge", "test.*cross.*chain", "test.*relay"],
                    code_patterns=["bridgeToken", "relayMessage", "crossChain", "validateProof"]
                ),
                DomainTestPattern(
                    name="finality_testing",
                    description="Tests transaction finality requirements",
                    required=True,
                    complexity=TestPatternComplexity.HIGH,
                    keywords=["finality", "confirmation", "finalized", "blocks"],
                    test_indicators=["test.*finality", "test.*confirmation", "test.*finalized"],
                    code_patterns=["finality", "confirmations", "isFinalized", "blockConfirmations"]
                )
            ]
        }
    
    def _initialize_domain_indicators(self) -> Dict[ProjectDomain, Dict[str, Any]]:
        """Initialize indicators for domain classification."""
        return {
            ProjectDomain.DEFI: {
                "contract_keywords": ["swap", "pool", "vault", "yield", "farm", "stake", "liquidity", "token", "oracle", "price"],
                "function_keywords": ["swap", "addLiquidity", "removeLiquidity", "stake", "unstake", "harvest", "deposit", "withdraw"],
                "import_keywords": ["uniswap", "chainlink", "compound", "aave", "curve"],
                "comment_keywords": ["defi", "amm", "yield", "liquidity", "trading"],
                "weight": 1.0
            },
            ProjectDomain.NFT: {
                "contract_keywords": ["nft", "erc721", "erc1155", "metadata", "royalty", "mint", "collection"],
                "function_keywords": ["mint", "tokenURI", "royaltyInfo", "setApprovalForAll", "safeTransferFrom"],
                "import_keywords": ["erc721", "erc1155", "openzeppelin"],
                "comment_keywords": ["nft", "collectible", "art", "metadata"],
                "weight": 1.0
            },
            ProjectDomain.GOVERNANCE: {
                "contract_keywords": ["governance", "governor", "vote", "proposal", "delegate", "timelock"],
                "function_keywords": ["propose", "vote", "execute", "delegate", "queue"],
                "import_keywords": ["governor", "timelock", "votes"],
                "comment_keywords": ["governance", "dao", "voting", "proposal"],
                "weight": 1.0
            },
            ProjectDomain.GAMING: {
                "contract_keywords": ["game", "gaming", "player", "item", "character", "battle", "quest"],
                "function_keywords": ["battle", "levelUp", "equipItem", "useItem", "enterGame"],
                "import_keywords": ["randomness", "vrf"],
                "comment_keywords": ["game", "gaming", "player", "rpg"],
                "weight": 0.8
            },
            ProjectDomain.BRIDGE: {
                "contract_keywords": ["bridge", "relay", "cross", "chain", "portal", "gateway"],
                "function_keywords": ["bridgeToken", "relayMessage", "validateProof", "crossChain"],
                "import_keywords": ["arbitrum", "polygon", "optimism"],
                "comment_keywords": ["bridge", "cross-chain", "layer2", "l2"],
                "weight": 0.9
            }
        }
    
    def _initialize_test_requirements(self) -> Dict[ProjectDomain, Dict[str, Any]]:
        """Initialize test requirements for each domain."""
        return {
            ProjectDomain.DEFI: {
                "minimum_security_tests": 5,
                "required_invariant_tests": 3,
                "required_fuzzing": True,
                "economic_testing": True,
                "oracle_testing": True
            },
            ProjectDomain.NFT: {
                "minimum_security_tests": 3,
                "required_invariant_tests": 1,
                "required_fuzzing": False,
                "metadata_testing": True,
                "royalty_testing": True
            },
            ProjectDomain.GOVERNANCE: {
                "minimum_security_tests": 4,
                "required_invariant_tests": 2,
                "required_fuzzing": True,
                "voting_integrity": True,
                "timelock_testing": True
            }
        }
    
    def classify_project_domain(self, project_content: Dict[str, str], 
                              contract_names: List[str] = None) -> ProjectClassification:
        """
        Classify the project domain based on content analysis.
        
        This addresses the expert feedback about applying generic patterns
        without understanding domain-specific requirements.
        """
        domain_scores = {}
        all_content = " ".join(project_content.values()).lower()
        
        # Analyze each potential domain
        for domain, indicators in self.domain_indicators.items():
            score = self._calculate_domain_score(all_content, indicators, contract_names or [])
            domain_scores[domain] = score
        
        # Find primary domain
        primary_domain = max(domain_scores, key=domain_scores.get)
        primary_score = domain_scores[primary_domain]
        
        # Find secondary domains (score > 0.3 and not primary)
        secondary_domains = [
            domain for domain, score in domain_scores.items()
            if score > 0.3 and domain != primary_domain
        ]
        
        # Calculate confidence
        confidence = primary_score
        if len([s for s in domain_scores.values() if s > 0.3]) > 1:
            confidence *= 0.8  # Reduce confidence if multiple domains detected
        
        # Assess complexity
        complexity = self._assess_domain_complexity(primary_domain, primary_score)
        
        return ProjectClassification(
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            classification_confidence=confidence,
            domain_indicators=domain_scores,
            complexity_assessment=complexity
        )
    
    def _calculate_domain_score(self, content: str, indicators: Dict[str, Any], 
                               contract_names: List[str]) -> float:
        """Calculate domain score based on indicators."""
        score = 0.0
        total_weight = 0.0
        
        # Contract name keywords
        contract_score = sum(
            1 for name in contract_names
            for keyword in indicators["contract_keywords"]
            if keyword in name.lower()
        ) / max(len(contract_names), 1)
        score += contract_score * 0.3
        total_weight += 0.3
        
        # Function keywords
        function_score = sum(
            content.count(keyword) for keyword in indicators["function_keywords"]
        ) / max(len(indicators["function_keywords"]), 1)
        function_score = min(1.0, function_score / 5)  # Normalize
        score += function_score * 0.3
        total_weight += 0.3
        
        # Import keywords
        import_score = sum(
            content.count(keyword) for keyword in indicators["import_keywords"]
        ) / max(len(indicators["import_keywords"]), 1)
        import_score = min(1.0, import_score / 3)  # Normalize
        score += import_score * 0.2
        total_weight += 0.2
        
        # Comment keywords
        comment_score = sum(
            content.count(keyword) for keyword in indicators["comment_keywords"]
        ) / max(len(indicators["comment_keywords"]), 1)
        comment_score = min(1.0, comment_score / 3)  # Normalize
        score += comment_score * 0.2
        total_weight += 0.2
        
        # Apply domain weight
        score = (score / total_weight) * indicators["weight"]
        
        return min(1.0, score)
    
    def _assess_domain_complexity(self, domain: ProjectDomain, score: float) -> str:
        """Assess the complexity of the domain."""
        complexity_factors = {
            ProjectDomain.DEFI: 0.9,  # High complexity
            ProjectDomain.GOVERNANCE: 0.8,  # High complexity
            ProjectDomain.BRIDGE: 0.85,  # High complexity
            ProjectDomain.NFT: 0.5,  # Medium complexity
            ProjectDomain.GAMING: 0.6,  # Medium complexity
            ProjectDomain.UTILITY: 0.3,  # Low complexity
            ProjectDomain.GENERAL: 0.4  # Low-medium complexity
        }
        
        base_complexity = complexity_factors.get(domain, 0.5)
        adjusted_complexity = base_complexity * score
        
        if adjusted_complexity >= 0.8:
            return "High - Requires sophisticated testing patterns"
        elif adjusted_complexity >= 0.6:
            return "Medium-High - Needs comprehensive security testing"
        elif adjusted_complexity >= 0.4:
            return "Medium - Standard testing with domain-specific patterns"
        else:
            return "Low-Medium - Basic testing with some domain considerations"
    
    def analyze_domain_specific_testing(self, project_classification: ProjectClassification,
                                      test_content: Dict[str, str]) -> DomainAnalysis:
        """
        Analyze test quality against domain-specific requirements.
        
        This provides contextual evaluation instead of generic pattern matching.
        """
        domain = project_classification.primary_domain
        all_test_content = " ".join(test_content.values()).lower()
        
        # Get required patterns for this domain
        required_patterns = self.domain_patterns.get(domain, [])
        
        # Analyze implemented patterns
        implemented_patterns = []
        missing_patterns = []
        
        for pattern in required_patterns:
            if self._is_pattern_implemented(pattern, all_test_content):
                implemented_patterns.append(pattern.name)
            else:
                missing_patterns.append(pattern.name)
        
        # Calculate contextual quality score
        contextual_score = self._calculate_contextual_quality_score(
            domain, required_patterns, implemented_patterns, all_test_content
        )
        
        # Generate domain-specific recommendations
        recommendations = self._generate_domain_recommendations(
            domain, missing_patterns, required_patterns, contextual_score
        )
        
        return DomainAnalysis(
            domain=domain,
            confidence=project_classification.classification_confidence,
            indicators=project_classification.domain_indicators,
            required_patterns=required_patterns,
            implemented_patterns=implemented_patterns,
            missing_patterns=missing_patterns,
            contextual_quality_score=contextual_score,
            domain_specific_recommendations=recommendations
        )
    
    def _is_pattern_implemented(self, pattern: DomainTestPattern, test_content: str) -> bool:
        """Check if a domain-specific pattern is implemented."""
        # Check test function indicators
        for indicator in pattern.test_indicators:
            if re.search(indicator, test_content, re.IGNORECASE):
                return True
        
        # Check code patterns
        for code_pattern in pattern.code_patterns:
            if re.search(code_pattern, test_content, re.IGNORECASE):
                return True
        
        # Check keywords
        for keyword in pattern.keywords:
            if keyword in test_content:
                return True
        
        return False
    
    def _calculate_contextual_quality_score(self, domain: ProjectDomain, 
                                          required_patterns: List[DomainTestPattern],
                                          implemented_patterns: List[str],
                                          test_content: str) -> float:
        """Calculate quality score within domain context."""
        if not required_patterns:
            return 0.8  # Generic projects get decent score
        
        # Base score from required pattern implementation
        required_count = len([p for p in required_patterns if p.required])
        implemented_required = len([
            p for p in required_patterns 
            if p.required and p.name in implemented_patterns
        ])
        
        base_score = implemented_required / max(required_count, 1)
        
        # Bonus for optional patterns
        optional_count = len([p for p in required_patterns if not p.required])
        implemented_optional = len([
            p for p in required_patterns 
            if not p.required and p.name in implemented_patterns
        ])
        
        optional_bonus = (implemented_optional / max(optional_count, 1)) * 0.2 if optional_count > 0 else 0
        
        # Domain-specific bonuses
        domain_bonus = self._calculate_domain_specific_bonus(domain, test_content)
        
        total_score = base_score + optional_bonus + domain_bonus
        return min(1.0, total_score)
    
    def _calculate_domain_specific_bonus(self, domain: ProjectDomain, test_content: str) -> float:
        """Calculate domain-specific quality bonuses."""
        bonus = 0.0
        
        if domain == ProjectDomain.DEFI:
            # Bonus for economic invariants
            if "invariant_" in test_content:
                bonus += 0.1
            # Bonus for oracle testing
            if any(keyword in test_content for keyword in ["oracle", "price", "feed"]):
                bonus += 0.05
            # Bonus for flash loan testing
            if "flash" in test_content and "loan" in test_content:
                bonus += 0.05
        
        elif domain == ProjectDomain.NFT:
            # Bonus for metadata testing
            if "metadata" in test_content or "tokenuri" in test_content:
                bonus += 0.05
            # Bonus for royalty testing
            if "royalty" in test_content:
                bonus += 0.05
        
        elif domain == ProjectDomain.GOVERNANCE:
            # Bonus for voting integrity tests
            if "vote" in test_content and "integrity" in test_content:
                bonus += 0.1
            # Bonus for timelock testing
            if "timelock" in test_content:
                bonus += 0.05
        
        return bonus
    
    def _generate_domain_recommendations(self, domain: ProjectDomain, 
                                       missing_patterns: List[str],
                                       required_patterns: List[DomainTestPattern],
                                       quality_score: float) -> List[str]:
        """Generate domain-specific testing recommendations."""
        recommendations = []
        
        # Address missing required patterns first
        missing_required = [
            p for p in required_patterns 
            if p.required and p.name in missing_patterns
        ]
        
        for pattern in missing_required[:3]:  # Top 3 missing required patterns
            recommendations.append(f"Add {pattern.description.lower()}")
        
        # Domain-specific recommendations
        if domain == ProjectDomain.DEFI:
            if quality_score < 0.7:
                recommendations.extend([
                    "Implement economic invariant testing for protocol safety",
                    "Add comprehensive oracle manipulation attack scenarios",
                    "Test flash loan attack vectors and defenses"
                ])
        
        elif domain == ProjectDomain.NFT:
            if quality_score < 0.6:
                recommendations.extend([
                    "Add metadata validation and URI testing",
                    "Implement royalty calculation accuracy tests",
                    "Test batch operations for gas efficiency"
                ])
        
        elif domain == ProjectDomain.GOVERNANCE:
            if quality_score < 0.8:
                recommendations.extend([
                    "Add voting integrity and double-voting prevention tests",
                    "Implement proposal lifecycle edge case testing",
                    "Test timelock delay and execution security"
                ])
        
        # General quality improvements
        if quality_score < 0.5:
            recommendations.append(f"This {domain.value} project requires comprehensive testing overhaul")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def generate_domain_context_report(self, classification: ProjectClassification,
                                     domain_analysis: DomainAnalysis) -> Dict[str, Any]:
        """Generate comprehensive domain context report."""
        return {
            "project_classification": {
                "primary_domain": classification.primary_domain.value,
                "confidence": round(classification.classification_confidence, 2),
                "complexity": classification.complexity_assessment,
                "secondary_domains": [d.value for d in classification.secondary_domains]
            },
            "domain_testing_analysis": {
                "domain": domain_analysis.domain.value,
                "contextual_quality_score": round(domain_analysis.contextual_quality_score, 2),
                "required_patterns_count": len(domain_analysis.required_patterns),
                "implemented_patterns_count": len(domain_analysis.implemented_patterns),
                "missing_critical_patterns": len([p for p in domain_analysis.required_patterns if p.required and p.name in domain_analysis.missing_patterns]),
                "recommendations": domain_analysis.domain_specific_recommendations
            },
            "context_aware_assessment": self._generate_context_aware_assessment(classification, domain_analysis),
            "next_steps": self._generate_context_aware_next_steps(domain_analysis)
        }
    
    def _generate_context_aware_assessment(self, classification: ProjectClassification,
                                         domain_analysis: DomainAnalysis) -> str:
        """Generate context-aware overall assessment."""
        domain = classification.primary_domain.value
        score = domain_analysis.contextual_quality_score
        
        if score >= 0.9:
            return f"Excellent {domain} testing - meets all domain-specific requirements with comprehensive coverage"
        elif score >= 0.7:
            return f"Good {domain} testing - covers most domain requirements with minor gaps"
        elif score >= 0.5:
            return f"Adequate {domain} testing - covers basic requirements but missing key domain patterns"
        elif score >= 0.3:
            return f"Insufficient {domain} testing - missing critical domain-specific test patterns"
        else:
            return f"Poor {domain} testing - does not meet domain requirements, requires significant improvement"
    
    def _generate_context_aware_next_steps(self, domain_analysis: DomainAnalysis) -> List[str]:
        """Generate context-aware next steps."""
        steps = []
        
        if domain_analysis.contextual_quality_score < 0.5:
            steps.append(f"Focus on {domain_analysis.domain.value}-specific testing patterns first")
        
        if domain_analysis.missing_patterns:
            steps.append(f"Implement missing patterns: {', '.join(domain_analysis.missing_patterns[:3])}")
        
        if domain_analysis.contextual_quality_score >= 0.7:
            steps.append("Consider advanced testing patterns like invariant and fuzz testing")
        
        steps.extend(domain_analysis.domain_specific_recommendations[:2])
        
        return steps[:4]  # Limit to 4 next steps
