"""
Smart Contract Testing MCP Server - Project Analyzer

This module provides comprehensive project state analysis and context awareness
for intelligent testing workflow guidance.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .ast_analyzer import ASTAnalyzer, SemanticAnalysis, SecurityPattern, NodeType

logger = logging.getLogger(__name__)

class TestingPhase(Enum):
    """Testing maturity phases"""
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PRODUCTION = "production"

class SecurityLevel(Enum):
    """Security testing maturity levels"""
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    AUDIT_READY = "audit_ready"

@dataclass
class TestFileAnalysis:
    """Analysis of a test file"""
    path: str
    test_count: int
    test_patterns: List[str]
    security_tests: List[str]
    coverage_targets: List[str]
    uses_mocks: bool
    uses_fuzzing: bool
    uses_invariants: bool
    complexity_score: float

@dataclass
class ContractAnalysis:
    """Analysis of a contract file"""
    path: str
    contract_name: str
    contract_type: str  # "defi", "nft", "governance", "bridge", "utility"
    functions: List[str]
    state_variables: List[str]
    security_patterns: List[str]
    risk_score: float
    dependencies: List[str]
    mock_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProjectState:
    """Complete project state analysis"""
    project_path: str
    project_type: str
    testing_phase: TestingPhase
    security_level: SecurityLevel
    test_files: List[TestFileAnalysis]
    contracts: List[ContractAnalysis]
    coverage_data: Dict[str, Any]
    foundry_config: Dict[str, Any]
    identified_gaps: List[str]
    next_recommendations: List[str]

class ProjectAnalyzer:
    """
    Analyzes project state to provide context-aware testing guidance.
    
    This addresses the "context blindness" issue by understanding:
    - Current testing progress and maturity
    - Existing test patterns and coverage
    - Contract types and risk profiles
    - Security testing gaps
    """
    
    def __init__(self, foundry_adapter):
        """Initialize project analyzer with Foundry adapter and AST analyzer."""
        self.foundry_adapter = foundry_adapter
        self.ast_analyzer = ASTAnalyzer()
        
        # Security patterns from our audit guidance
        self.security_patterns = {
            "access_control": [
                "onlyOwner", "onlyRole", "modifier", "require.*msg.sender",
                "AccessControl", "Ownable"
            ],
            "reentrancy": [
                "nonReentrant", "ReentrancyGuard", "call{value:", "external.*payable"
            ],
            "oracle_usage": [
                "oracle", "price", "getPrice", "latestAnswer", "Chainlink",
                "Uniswap", "TWAP"
            ],
            "flash_loans": [
                "flashLoan", "flashBorrow", "IFlashLoanReceiver", "AAVE",
                "dYdX", "Uniswap"
            ],
            "governance": [
                "Governor", "Timelock", "propose", "execute", "vote",
                "delegation"
            ]
        }
        
        # Test patterns for analysis
        self.test_patterns = {
            "unit_testing": [
                "function test", "test_", "testFuzz", "testInvariant"
            ],
            "integration_testing": [
                "integration", "workflow", "scenario", "end.*end"
            ],
            "fuzz_testing": [
                "testFuzz", "bound\\(", "fuzz", "random"
            ],
            "invariant_testing": [
                "testInvariant", "invariant_", "property", "assert"
            ],
            "mock_usage": [
                "mock", "Mock", "stub", "fake", "vm\\."
            ],
            "security_testing": [
                "attack", "exploit", "malicious", "reentrancy", "overflow"
            ]
        }
        
        logger.info("Project analyzer initialized")
    
    async def analyze_project(self, project_path: str) -> ProjectState:
        """
        Perform comprehensive project analysis.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Complete project state analysis
        """
        project_path = Path(project_path)
        
        # Analyze project structure
        project_type = await self._detect_project_type(project_path)
        
        # Analyze contracts
        contracts = await self._analyze_contracts(project_path)
        if contracts is None:
            contracts = []
        
        # Analyze test files
        test_files = await self._analyze_test_files(project_path)
        if test_files is None:
            test_files = []
        
        # Get coverage data
        coverage_data = await self._get_coverage_data(project_path)
        if coverage_data is None:
            coverage_data = {}
        
        # Analyze Foundry configuration
        foundry_config = await self._analyze_foundry_config(project_path)
        if foundry_config is None:
            foundry_config = {}
        
        # Determine testing phase and security level
        testing_phase = self._determine_testing_phase(test_files, coverage_data)
        security_level = self._determine_security_level(test_files, contracts)
        
        # Identify gaps and generate recommendations
        gaps = self._identify_gaps(contracts, test_files, coverage_data)
        if gaps is None:
            gaps = []
        
        recommendations = self._generate_recommendations(
            testing_phase, security_level, gaps, contracts
        )
        if recommendations is None:
            recommendations = []
        
        return ProjectState(
            project_path=str(project_path),
            project_type=project_type,
            testing_phase=testing_phase,
            security_level=security_level,
            test_files=test_files,
            contracts=contracts,
            coverage_data=coverage_data,
            foundry_config=foundry_config,
            identified_gaps=gaps,
            next_recommendations=recommendations
        )
    
    async def _detect_project_type(self, project_path: Path) -> str:
        """Detect the type of project (DeFi, NFT, governance, etc.)"""
        contract_content = ""
        
        # Read all contract files
        src_dir = project_path / "src"
        if src_dir.exists():
            for sol_file in src_dir.rglob("*.sol"):
                try:
                    with open(sol_file, 'r', encoding='utf-8') as f:
                        contract_content += f.read().lower()
                except Exception as e:
                    logger.warning(f"Could not read {sol_file}: {e}")
        
        # Analyze content for project type indicators with improved logic
        type_indicators = {
            "defi": ["swap", "liquidity", "pool", "vault", "lending", "borrow", "yield", "farm", "portfolio", "strategy", "allocat", "rebalance"],
            "nft": ["erc721", "erc1155", "tokenuri", "metadata", "collectible", "art", "game"],
            "governance": ["governor", "proposal", "vote", "delegate", "timelock", "dao"],
            "bridge": ["bridge", "crosschain", "layer2", "relay", "validator", "merkle"],
            "utility": ["utility", "library", "helper", "tool"]
        }
        
        # Strong indicators that override others
        strong_nft_indicators = ["erc721", "erc1155", "tokenuri", "nft"]
        strong_defi_indicators = ["vault", "portfolio", "strategy", "liquidity", "pool", "farm", "yield"]
        
        scores = {}
        for project_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in contract_content)
            scores[project_type] = score
        
        # Apply enhanced logic to resolve conflicts
        has_strong_nft = any(indicator in contract_content for indicator in strong_nft_indicators)
        has_strong_defi = any(indicator in contract_content for indicator in strong_defi_indicators)
        
        # If we have both mint/burn AND strong DeFi indicators, it's DeFi not NFT
        if has_strong_defi:
            scores["defi"] += 3  # Boost DeFi score significantly
        
        # Only classify as NFT if we have strong NFT indicators
        if not has_strong_nft and "nft" in scores:
            scores["nft"] = 0  # Remove NFT classification without strong indicators
        
        # Return the type with highest score, or "general" if no clear type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"
    
    async def _analyze_contracts(self, project_path: Path) -> List[ContractAnalysis]:
        """Analyze all contract files in the project"""
        contracts = []
        src_dir = project_path / "src"
        
        if not src_dir.exists():
            return contracts
        
        for sol_file in src_dir.rglob("*.sol"):
            try:
                analysis = await self._analyze_contract_file(sol_file)
                if analysis:
                    contracts.append(analysis)
            except Exception as e:
                logger.warning(f"Could not analyze {sol_file}: {e}")
        
        return contracts
    
    async def _analyze_contract_file(self, file_path: Path) -> Optional[ContractAnalysis]:
        """
        Analyze a single contract file using regex-first approach for reliability.
        
        Uses comprehensive regex patterns as primary analysis method with optional
        AST enhancement when available. This provides predictable, deterministic results.
        """
        try:
            # PRIMARY: Comprehensive regex-based analysis
            analysis = await self._comprehensive_regex_analysis(file_path)
            
            if not analysis:
                return None
        
            # ENHANCEMENT: Add AST insights if available (optional)
            if hasattr(self, 'ast_analyzer') and self.ast_analyzer and self.ast_analyzer.solc_path:
                try:
                    semantic_analysis = await self.ast_analyzer.analyze_solidity_file(str(file_path))
                    analysis = self._enhance_with_ast_insights(analysis, semantic_analysis)
                    logger.debug(f"Enhanced {file_path.name} analysis with AST insights")
                except Exception as ast_error:
                    # AST enhancement failed - no problem, regex analysis is complete
                    logger.debug(f"AST enhancement failed for {file_path.name}: {ast_error}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Contract analysis failed for {file_path}: {e}")
            return None
    
    def _enhance_with_ast_insights(self, regex_analysis: ContractAnalysis, 
                                  semantic_analysis) -> ContractAnalysis:
        """
        Enhance regex-based analysis with AST insights when available.
        
        This is optional enhancement that doesn't change core results but can
        add additional context and validation.
        """
        try:
            # Extract additional insights from AST
            ast_security_patterns = self._convert_ast_security_patterns(
                semantic_analysis.security_patterns
            )
            
            # Merge security patterns (union of regex and AST findings)
            combined_patterns = list(set(regex_analysis.security_patterns + ast_security_patterns))
            
            # Use AST function count for validation
            ast_function_nodes = [node for node in semantic_analysis.ast_nodes 
                                if hasattr(node, 'node_type') and str(node.node_type) == 'NodeType.FUNCTION']
            
            # If AST found significantly more functions, use that count
            if len(ast_function_nodes) > len(regex_analysis.functions):
                ast_functions = [node.name for node in ast_function_nodes]
                combined_functions = list(set(regex_analysis.functions + ast_functions))
            else:
                combined_functions = regex_analysis.functions
            
            # Return enhanced analysis
            return ContractAnalysis(
                path=regex_analysis.path,
                contract_name=regex_analysis.contract_name,
                contract_type=regex_analysis.contract_type,  # Keep regex classification
                functions=combined_functions,
                state_variables=regex_analysis.state_variables,
                security_patterns=combined_patterns,
                risk_score=regex_analysis.risk_score,  # Keep regex risk score
                dependencies=regex_analysis.dependencies,
                mock_requirements=regex_analysis.mock_requirements  # Preserve mock requirements
            )
            
        except Exception as e:
            logger.debug(f"AST enhancement failed: {e}")
            # Return original regex analysis if enhancement fails
            return regex_analysis
    
    async def _analyze_test_files(self, project_path: Path) -> List[TestFileAnalysis]:
        """Analyze all test files in the project"""
        test_files = []
        test_dir = project_path / "test"
        
        if not test_dir.exists():
            return test_files
        
        for test_file in test_dir.rglob("*.sol"):
            try:
                analysis = await self._analyze_test_file(test_file)
                if analysis:
                    test_files.append(analysis)
            except Exception as e:
                logger.warning(f"Could not analyze {test_file}: {e}")
        
        return test_files
    
    async def _analyze_test_file(self, file_path: Path) -> Optional[TestFileAnalysis]:
        """
        Analyze a single test file using AST-based semantic analysis.
        
        This provides deeper understanding of test structure and patterns
        compared to regex-based analysis.
        """
        try:
            # Use AST analyzer for test file analysis
            semantic_analysis = await self.ast_analyzer.analyze_test_file(str(file_path))
            
            # Extract test functions from AST
            test_function_nodes = [node for node in semantic_analysis.ast_nodes 
                                 if node.node_type == NodeType.FUNCTION and 
                                 (node.name.startswith('test') or 
                                  node.attributes.get('is_test', False))]
            
            test_count = len(test_function_nodes)
            
            # Analyze test patterns semantically
            detected_patterns = self._analyze_test_patterns_from_ast(test_function_nodes)
            
            # Find security tests using semantic analysis
            security_tests = [
                node.name for node in test_function_nodes
                if any(keyword in node.name.lower() 
                      for keyword in ['attack', 'malicious', 'exploit', 'hack', 'security', 
                                    'reentrancy', 'overflow', 'underflow'])
            ]
            
            # Find coverage targets - contracts being tested
            coverage_targets = self._extract_coverage_targets_from_ast(semantic_analysis)
            
            # Calculate enhanced complexity score
            complexity_score = self._calculate_ast_test_complexity(
                semantic_analysis, test_function_nodes, detected_patterns
            )
            
            return TestFileAnalysis(
                path=str(file_path),
                test_count=test_count,
                test_patterns=detected_patterns,
                security_tests=security_tests,
                coverage_targets=coverage_targets,
                uses_mocks="mock_usage" in detected_patterns,
                uses_fuzzing="fuzz_testing" in detected_patterns,
                uses_invariants="invariant_testing" in detected_patterns,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            logger.warning(f"AST test analysis failed for {file_path}, falling back to regex: {e}")
            return await self._fallback_test_analysis(file_path)
    
    def _analyze_test_patterns_from_ast(self, test_function_nodes: List) -> List[str]:
        """Analyze test patterns using AST instead of regex."""
        detected_patterns = []
        
        # Check for different test types based on function names and attributes
        has_unit_tests = any(node.attributes.get('test_type') == 'unit' 
                           for node in test_function_nodes)
        has_fuzz_tests = any(node.attributes.get('test_type') == 'fuzz' or 
                           'fuzz' in node.name.lower()
                           for node in test_function_nodes)
        has_invariant_tests = any(node.attributes.get('test_type') == 'invariant' or
                                'invariant' in node.name.lower()
                                for node in test_function_nodes)
        
        # Detect integration tests by function naming patterns
        has_integration_tests = any('integration' in node.name.lower() or
                                  'workflow' in node.name.lower() or
                                  'scenario' in node.name.lower()
                                  for node in test_function_nodes)
        
        # Detect security tests
        has_security_tests = any(any(keyword in node.name.lower() 
                                   for keyword in ['attack', 'exploit', 'security', 'hack'])
                               for node in test_function_nodes)
        
        # Note: Mock usage detection would require deeper AST analysis of function bodies
        # For now, we'll use a simplified approach
        has_mock_usage = any('mock' in node.name.lower() for node in test_function_nodes)
        
        # Add detected patterns
        if has_unit_tests:
            detected_patterns.append("unit_testing")
        if has_fuzz_tests:
            detected_patterns.append("fuzz_testing")
        if has_invariant_tests:
            detected_patterns.append("invariant_testing")
        if has_integration_tests:
            detected_patterns.append("integration_testing")
        if has_security_tests:
            detected_patterns.append("security_testing")
        if has_mock_usage:
            detected_patterns.append("mock_usage")
        
        return detected_patterns
    
    def _extract_coverage_targets_from_ast(self, semantic_analysis: SemanticAnalysis) -> List[str]:
        """Extract contracts being tested from AST analysis."""
        # Look for contract instantiations or references in the test file
        # This is a simplified approach - full implementation would analyze function bodies
        contract_nodes = [node.name for node in semantic_analysis.ast_nodes 
                         if node.node_type == NodeType.CONTRACT]
        
        # Filter out test contracts themselves
        coverage_targets = [name for name in contract_nodes 
                          if not name.lower().endswith('test') and 
                             not name.lower().startswith('test')]
        
        return coverage_targets
    
    def _calculate_ast_test_complexity(self, semantic_analysis: SemanticAnalysis,
                                      test_function_nodes: List, 
                                      detected_patterns: List[str]) -> float:
        """Calculate test complexity using AST analysis."""
        score = 0.0
        
        # Base test count score
        test_count = len(test_function_nodes)
        score += min(test_count * 0.05, 0.4)
        
        # Pattern bonuses with enhanced scoring
        pattern_bonuses = {
            "fuzz_testing": 0.3,
            "invariant_testing": 0.3,
            "security_testing": 0.2,
            "integration_testing": 0.2,
            "mock_usage": 0.1,
            "unit_testing": 0.1
        }
        
        for pattern in detected_patterns:
            score += pattern_bonuses.get(pattern, 0.0)
        
        # Bonus for test function diversity
        test_types = set(node.attributes.get('test_type', 'unit') 
                        for node in test_function_nodes)
        if len(test_types) > 2:
            score += 0.2  # Bonus for test diversity
        
        return min(score, 1.0)
    
    async def _fallback_test_analysis(self, file_path: Path) -> Optional[TestFileAnalysis]:
        """Fallback to regex-based test analysis when AST fails."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return None
        
        # Count test functions
        test_functions = re.findall(r'function\s+test\w*\(', content)
        test_count = len(test_functions)
        
        # Detect test patterns
        detected_patterns = []
        for pattern_type, patterns in self.test_patterns.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                detected_patterns.append(pattern_type)
        
        # Find security tests
        security_tests = [
            func for func in test_functions 
            if any(pattern in func.lower() for pattern in ['attack', 'malicious', 'exploit', 'hack'])
        ]
        
        # Find coverage targets (contracts being tested)
        coverage_targets = re.findall(r'(\w+)\s+(?:public|private|internal)\s+\w+Contract', content)
        
        # Calculate complexity score
        complexity_score = self._calculate_test_complexity(content, test_count, detected_patterns)
        
        return TestFileAnalysis(
            path=str(file_path),
            test_count=test_count,
            test_patterns=detected_patterns,
            security_tests=security_tests,
            coverage_targets=coverage_targets,
            uses_mocks="mock_usage" in detected_patterns,
            uses_fuzzing="fuzz_testing" in detected_patterns,
            uses_invariants="invariant_testing" in detected_patterns,
            complexity_score=complexity_score
        )
    
    async def _get_coverage_data(self, project_path: Path) -> Dict[str, Any]:
        """Get coverage data for the project"""
        try:
            # Try to get coverage from Foundry adapter
            coverage_result = await self.foundry_adapter.generate_coverage_report(
                str(project_path), format="summary"
            )
            return coverage_result.get("coverage_data", {})
        except Exception as e:
            logger.warning(f"Could not get coverage data: {e}")
            return {}
    
    async def _analyze_foundry_config(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Foundry configuration"""
        config = {}
        
        foundry_toml = project_path / "foundry.toml"
        if foundry_toml.exists():
            try:
                import toml
                with open(foundry_toml, 'r') as f:
                    config = toml.load(f)
            except Exception as e:
                logger.warning(f"Could not parse foundry.toml: {e}")
        
        return config
    
    def _determine_testing_phase(self, test_files: List[TestFileAnalysis], 
                                coverage_data: Dict[str, Any]) -> TestingPhase:
        """
        Determine current testing phase based on comprehensive test analysis.
        
        This addresses the context blindness issue by properly recognizing
        advanced testing work that has already been completed.
        """
        if not test_files:
            return TestingPhase.NONE
        
        total_tests = sum(tf.test_count for tf in test_files)
        has_security_tests = any(tf.security_tests for tf in test_files)
        has_fuzzing = any(tf.uses_fuzzing for tf in test_files)
        has_invariants = any(tf.uses_invariants for tf in test_files)
        has_mocks = any(tf.uses_mocks for tf in test_files)
        
        # Get actual coverage from forge coverage if available
        coverage_pct = self._get_actual_coverage_percentage(coverage_data)
        
        # Count different types of test patterns
        security_test_count = sum(len(tf.security_tests) for tf in test_files)
        integration_tests = sum(1 for tf in test_files if "integration_testing" in tf.test_patterns)
        
        # Production-ready criteria (addresses "95 tests with 90%+ coverage" scenario)
        if (total_tests >= 50 and coverage_pct >= 85 and security_test_count >= 10 and 
            has_fuzzing and has_invariants and integration_tests >= 2):
            return TestingPhase.PRODUCTION
        
        # Advanced testing (comprehensive test suite with security focus)
        elif (total_tests >= 20 and coverage_pct >= 75 and security_test_count >= 5 and 
              (has_fuzzing or has_invariants) and has_mocks):
            return TestingPhase.ADVANCED
        
        # Intermediate (good unit tests with some advanced patterns)
        elif (total_tests >= 10 and coverage_pct >= 60 and has_mocks and 
              (security_test_count >= 2 or has_fuzzing)):
            return TestingPhase.INTERMEDIATE
        
        # Basic (some unit tests)
        elif total_tests >= 3 and coverage_pct >= 30:
            return TestingPhase.BASIC
        
        else:
            return TestingPhase.NONE
    
    def _determine_security_level(self, test_files: List[TestFileAnalysis], 
                                 contracts: List[ContractAnalysis]) -> SecurityLevel:
        """Determine security testing maturity level"""
        if not test_files:
            return SecurityLevel.NONE
        
        security_test_count = sum(len(tf.security_tests) for tf in test_files)
        has_attack_tests = any("attack" in " ".join(tf.security_tests).lower() for tf in test_files)
        has_access_control_tests = any("access" in " ".join(tf.test_patterns).lower() for tf in test_files)
        has_reentrancy_tests = any("reentrancy" in " ".join(tf.test_patterns).lower() for tf in test_files)
        
        # Check if contracts have security patterns
        high_risk_contracts = [c for c in contracts if c.risk_score > 0.7]
        
        if (security_test_count >= 20 and has_attack_tests and has_access_control_tests and 
            has_reentrancy_tests and len(high_risk_contracts) > 0):
            return SecurityLevel.AUDIT_READY
        elif security_test_count >= 10 and has_attack_tests and (has_access_control_tests or has_reentrancy_tests):
            return SecurityLevel.ADVANCED
        elif security_test_count >= 5 and has_attack_tests:
            return SecurityLevel.INTERMEDIATE
        elif security_test_count >= 2:
            return SecurityLevel.BASIC
        else:
            return SecurityLevel.NONE
    
    def _identify_gaps(self, contracts: List[ContractAnalysis], 
                      test_files: List[TestFileAnalysis], 
                      coverage_data: Dict[str, Any]) -> List[str]:
        """Identify testing gaps in the project"""
        gaps = []
        
        # Coverage gaps
        coverage_pct = coverage_data.get("coverage_percentage", 0)
        if coverage_pct < 80:
            gaps.append(f"Low test coverage: {coverage_pct}% (target: 80%+)")
        
        # Security testing gaps
        security_patterns_in_contracts = set()
        for contract in contracts:
            security_patterns_in_contracts.update(contract.security_patterns)
        
        security_patterns_in_tests = set()
        for test_file in test_files:
            security_patterns_in_tests.update(test_file.test_patterns)
        
        missing_security_tests = security_patterns_in_contracts - security_patterns_in_tests
        if missing_security_tests:
            gaps.append(f"Missing security tests for: {', '.join(missing_security_tests)}")
        
        # Advanced testing gaps
        has_fuzzing = any(tf.uses_fuzzing for tf in test_files)
        has_invariants = any(tf.uses_invariants for tf in test_files)
        
        if not has_fuzzing and len(contracts) > 0:
            gaps.append("No fuzz testing detected")
        
        if not has_invariants and len([c for c in contracts if c.risk_score > 0.5]) > 0:
            gaps.append("No invariant testing for high-risk contracts")
        
        # Integration testing gaps
        has_integration_tests = any("integration_testing" in tf.test_patterns for tf in test_files)
        if len(contracts) > 1 and not has_integration_tests:
            gaps.append("Missing integration tests for multi-contract system")
        
        return gaps
    
    def _generate_recommendations(self, testing_phase: TestingPhase, 
                                 security_level: SecurityLevel, 
                                 gaps: List[str], 
                                 contracts: List[ContractAnalysis]) -> List[str]:
        """
        Generate contextual next-step recommendations that build on completed work.
        
        This addresses workflow rigidity by providing progressive, specific guidance
        rather than generic workflows that ignore existing progress.
        """
        recommendations = []
        
        # Context-aware phase-specific recommendations
        if testing_phase == TestingPhase.PRODUCTION:
            recommendations.append("Consider formal verification for critical contract properties")
            recommendations.append("Add gas optimization tests and benchmarking")
            recommendations.append("Implement mainnet fork testing for integration scenarios")
            recommendations.append("Set up automated security monitoring and alerting")
            
        elif testing_phase == TestingPhase.ADVANCED:
            # Build on existing comprehensive testing
            recommendations.append("Add property-based testing with more complex invariants")
            recommendations.append("Implement cross-chain testing scenarios if applicable")
            recommendations.append("Add MEV protection testing and front-running resistance")
            recommendations.append("Create deployment and upgrade testing procedures")
            
        elif testing_phase == TestingPhase.INTERMEDIATE:
            # Enhance existing solid foundation
            recommendations.append("Expand fuzz testing to cover more function parameters")
            recommendations.append("Add integration testing for multi-contract workflows")
            recommendations.append("Implement attack vector testing (flash loans, oracle manipulation)")
            recommendations.append("Add gas efficiency testing and optimization validation")
            
        elif testing_phase == TestingPhase.BASIC:
            # Build on basic unit tests
            recommendations.append("Add comprehensive edge case and boundary condition testing")
            recommendations.append("Implement mock contracts for external dependencies")
            recommendations.append("Add security-focused testing for access controls")
            recommendations.append("Increase test coverage to 70%+ with targeted tests")
            
        else:  # NONE
            recommendations.append("Start with unit tests for core contract functions")
            recommendations.append("Set up proper test file structure and base contracts")
            recommendations.append("Establish coverage monitoring and target 50%+ initially")
        
        # Security-level specific enhancements
        if security_level == SecurityLevel.AUDIT_READY:
            recommendations.append("Prepare audit documentation and test evidence packages")
        elif security_level == SecurityLevel.ADVANCED:
            recommendations.append("Add economic attack testing and game theory scenarios")
        elif security_level in [SecurityLevel.INTERMEDIATE, SecurityLevel.BASIC]:
            recommendations.append("Expand security testing to cover all common vulnerability patterns")
        elif security_level == SecurityLevel.NONE:
            recommendations.append("Begin with access control and reentrancy protection testing")
        
        # Contract-type specific recommendations
        project_types = {contract.contract_type for contract in contracts}
        for project_type in project_types:
            if project_type == "defi":
                recommendations.append("Add DeFi-specific testing: slippage, liquidation, oracle manipulation")
            elif project_type == "nft":
                recommendations.append("Add NFT-specific testing: metadata, royalties, transfer restrictions")
            elif project_type == "governance":
                recommendations.append("Add governance attack testing: vote buying, proposal manipulation")
            elif project_type == "bridge":
                recommendations.append("Add cross-chain testing: message validation, replay protection")
        
        # Gap-specific immediate actions
        priority_gaps = [gap for gap in gaps if any(keyword in gap.lower() 
                        for keyword in ['security', 'coverage', 'missing'])]
        if priority_gaps:
            recommendations.append(f"Immediate priority: {priority_gaps[0]}")
        
        # High-risk contract focus
        high_risk_contracts = [c for c in contracts if c.risk_score > 0.8]
        if high_risk_contracts and testing_phase in [TestingPhase.BASIC, TestingPhase.INTERMEDIATE]:
            recommendations.append(f"Intensive testing needed for high-risk contracts: {', '.join(c.contract_name for c in high_risk_contracts[:2])}")
        
        return recommendations[:6]  # Return up to 6 contextual recommendations
    
    def _get_actual_coverage_percentage(self, coverage_data: Dict[str, Any]) -> float:
        """
        Extract actual coverage percentage from forge coverage output.
        
        This addresses the tool integration disconnect by using real Foundry data.
        """
        # Try to get from Foundry's actual coverage format
        if "summary" in coverage_data:
            summary = coverage_data["summary"]
            if "coverage_percentage" in summary:
                return float(summary["coverage_percentage"])
        
        # Try alternative formats
        if "coverage_percentage" in coverage_data:
            return float(coverage_data["coverage_percentage"])
        
        # Try to calculate from totals if available
        if "totals" in coverage_data:
            totals = coverage_data["totals"]
            lines_hit = totals.get("lines", {}).get("hit", 0)
            lines_found = totals.get("lines", {}).get("found", 1)
            if lines_found > 0:
                return (lines_hit / lines_found) * 100
        
        return 0.0
    
    def _calculate_comprehensive_risk_score(self, content: str, functions: List[str], 
                                           security_patterns: List[str], contract_type: str) -> float:
        """
        Enhanced risk score calculation with contract type awareness.
        
        Provides more accurate risk assessment based on contract type,
        security patterns, and complexity factors.
        """
        score = 0.0
        
        # Base complexity score from function count
        score += min(len(functions) * 0.02, 0.3)
        
        # Contract type base risk multipliers
        type_risk_multipliers = {
            "defi": 0.4,      # High risk - financial operations, flash loans, oracle deps
            "governance": 0.3, # Medium-high risk - system control and voting
            "bridge": 0.3,    # Medium-high risk - cross-chain vulnerabilities  
            "token": 0.2,     # Medium risk - value transfer and minting
            "nft": 0.15,      # Medium-low risk - non-fungible assets
            "utility": 0.1    # Low risk - general purpose contracts
        }
        score += type_risk_multipliers.get(contract_type, 0.1)
        
        # Security pattern analysis with nuanced scoring
        pattern_risks = {
            "access_control": 0.15,   # Privileged functions increase attack surface
            "reentrancy": 0.25,      # High risk if not properly protected
            "oracle_usage": 0.2,     # Oracle manipulation and price feed risks
            "flash_loans": 0.3,      # Flash loan attack vectors
            "governance": 0.2        # Governance attacks and vote buying
        }
        
        for pattern in security_patterns:
            risk_increase = pattern_risks.get(pattern, 0.05)
            score += risk_increase
        
        # Reentrancy protection check - reduce risk if properly protected
        if "reentrancy" in security_patterns:
            if any(guard in content for guard in ["ReentrancyGuard", "nonReentrant", "_reentrancyGuard"]):
                score -= 0.15  # Reduce risk for proper protection
            else:
                score += 0.15  # Increase risk if unprotected
        
        # Financial operation risk factors
        financial_indicators = ["payable", "transfer", "call{value:", "delegatecall", "selfdestruct"]
        financial_risk = sum(0.05 for indicator in financial_indicators if indicator in content.lower())
        score += min(financial_risk, 0.2)  # Cap financial risk addition
        
        # Upgradeable contract risk
        if any(pattern in content.lower() for pattern in ["upgradeable", "proxy", "implementation", "uups"]):
            score += 0.15  # Upgradeable contracts have additional risks
        
        # External dependency risk
        external_calls = len(re.findall(r'\.call\(|\.delegatecall\(|\.staticcall\(', content))
        score += min(external_calls * 0.03, 0.15)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_risk_score(self, content: str, functions: List[str], 
                             security_patterns: List[str]) -> float:
        """Legacy method - redirect to comprehensive method."""
        # Default to utility type for legacy calls
        return self._calculate_comprehensive_risk_score(content, functions, security_patterns, "utility")
    
    def _convert_ast_security_patterns(self, ast_patterns: List[SecurityPattern]) -> List[str]:
        """Convert AST security patterns to legacy string format for compatibility."""
        pattern_mapping = {
            SecurityPattern.ACCESS_CONTROL: "access_control",
            SecurityPattern.REENTRANCY_GUARD: "reentrancy",
            SecurityPattern.ORACLE_DEPENDENCY: "oracle_usage",
            SecurityPattern.FLASH_LOAN_RECEIVER: "flash_loans",
            SecurityPattern.TIMELOCK_CONTROL: "governance",
            SecurityPattern.UPGRADEABLE_PATTERN: "upgradeable",
            SecurityPattern.MULTI_SIG_PATTERN: "multi_sig"
        }
        
        return [pattern_mapping.get(pattern, pattern.value) for pattern in ast_patterns]
    
    def _calculate_ast_risk_score(self, semantic_analysis: SemanticAnalysis, 
                                 function_nodes: List, contract_node) -> float:
        """
        Calculate risk score using AST-based semantic analysis.
        
        This provides more accurate risk assessment than regex-based scoring
        by understanding actual contract structure and behavior.
        """
        risk_score = 0.0
        
        # Use complexity metrics from AST
        complexity = semantic_analysis.complexity_metrics
        
        # Base complexity from function count and types
        risk_score += min(complexity.get("external_functions", 0) * 0.03, 0.3)
        risk_score += min(complexity.get("payable_functions", 0) * 0.05, 0.4)
        
        # Security pattern analysis - well-protected contracts get risk reduction
        security_patterns = semantic_analysis.security_patterns
        
        if SecurityPattern.ACCESS_CONTROL in security_patterns:
            risk_score -= 0.1  # Access control reduces risk
        else:
            risk_score += 0.2  # No access control increases risk
        
        if SecurityPattern.REENTRANCY_GUARD in security_patterns:
            risk_score -= 0.1  # Reentrancy protection reduces risk
        else:
            # Check if contract has payable/external functions without protection
            if complexity.get("payable_functions", 0) > 0:
                risk_score += 0.3
        
        # Oracle dependency increases risk
        if SecurityPattern.ORACLE_DEPENDENCY in security_patterns:
            risk_score += 0.2
        
        # Flash loan receiver increases risk
        if SecurityPattern.FLASH_LOAN_RECEIVER in security_patterns:
            risk_score += 0.3
        
        # Use individual function risk factors
        for func_name, func_risk in semantic_analysis.risk_factors.items():
            risk_score += func_risk * 0.1  # Weight individual function risks
        
        return min(risk_score, 1.0)
    
    def _determine_contract_type_from_ast(self, semantic_analysis: SemanticAnalysis) -> str:
        """
        Determine contract type using semantic analysis instead of text patterns.
        
        This provides more accurate classification by understanding actual
        contract structure and interfaces rather than just text patterns.
        """
        function_names = [node.name for node in semantic_analysis.ast_nodes 
                         if node.node_type == NodeType.FUNCTION]
        
        dependencies = semantic_analysis.external_dependencies
        
        # DeFi patterns - look for actual DeFi function signatures
        defi_functions = {"swap", "addLiquidity", "removeLiquidity", "deposit", "withdraw", 
                         "borrow", "repay", "liquidate", "harvest", "compound", "stake", "unstake",
                         "allocate", "rebalance", "portfolio", "strategy"}
        if any(func in function_names for func in defi_functions):
            return "defi"
        
        # Strong NFT patterns - only classify as NFT with clear NFT interfaces
        strong_nft_functions = {"tokenURI", "setApprovalForAll", "safeTransferFrom", "ownerOf"}
        nft_dependencies = any("erc721" in dep.lower() or "erc1155" in dep.lower() 
                              for dep in dependencies)
        
        # Check for actual NFT patterns, not just mint/burn which are common in ERC20
        has_strong_nft = any(func in function_names for func in strong_nft_functions) or nft_dependencies
        
        if has_strong_nft:
            return "nft"
        
        # Governance patterns
        governance_functions = {"propose", "vote", "execute", "queue", "cancel"}
        if any(func in function_names for func in governance_functions):
            return "governance"
        
        # Bridge patterns
        bridge_functions = {"bridge", "relay", "verify", "lock", "unlock"}
        if any(func in function_names for func in bridge_functions):
            return "bridge"
        
        # Token patterns - basic ERC20
        token_functions = {"transfer", "approve", "balanceOf", "totalSupply"}
        if all(func in function_names for func in token_functions):
            return "token"
        
        return "utility"
    
    def _extract_mock_requirements(self, content: str, contract_name: str, 
                                  functions: List[str], dependencies: List[str]) -> Dict[str, Any]:
        """
        Extract specific requirements for generating working mocks.
        
        This provides context to templates so they can generate compatible mocks
        that won't fail on first test execution.
        """
        mock_requirements = {
            "erc_interface_type": self._detect_erc_interface_type(content, functions),
            "access_control_variant": self._detect_access_control_variant(content, dependencies),
            "upgradeable_pattern": self._detect_upgradeable_pattern(content, dependencies),
            "required_mock_functions": self._extract_required_mock_functions(content, functions),
            "interface_compatibility": self._check_interface_compatibility(content, dependencies),
            "circular_dependency_risks": self._detect_circular_dependency_risks(content, contract_name)
        }
        
        return mock_requirements

    def _detect_erc_interface_type(self, content: str, functions: List[str]) -> Dict[str, Any]:
        """Detect specific ERC interface requirements for mock generation."""
        
        # ERC20 detection with exact function signature requirements
        erc20_functions = {"transfer", "transferFrom", "approve", "balanceOf", "totalSupply", "allowance"}
        has_erc20_core = len(erc20_functions.intersection(set(functions))) >= 4
        
        # ERC721 detection
        erc721_functions = {"ownerOf", "approve", "transferFrom", "safeTransferFrom"}
        has_erc721_core = len(erc721_functions.intersection(set(functions))) >= 3
        
        # Detect upgradeable variants
        is_upgradeable = "upgradeable" in content.lower()
        
        return {
            "type": "erc721" if has_erc721_core else "erc20" if has_erc20_core else "custom",
            "is_upgradeable": is_upgradeable,
            "required_functions": list(erc20_functions if has_erc20_core else erc721_functions if has_erc721_core else []),
            "exact_signatures_needed": has_erc20_core or has_erc721_core
        }

    def _detect_access_control_variant(self, content: str, dependencies: List[str]) -> Dict[str, Any]:
        """Detect AccessControl variant to avoid function signature mismatches."""
        
        # Check imports for specific AccessControl variants
        has_upgradeable_ac = any("AccessControlUpgradeable" in dep for dep in dependencies)
        has_standard_ac = any("AccessControl" in dep and "Upgradeable" not in dep for dep in dependencies)
        
        # Check content patterns
        content_lower = content.lower()
        has_role_member_count = "getrolemembercount" in content_lower
        
        return {
            "variant": "upgradeable" if has_upgradeable_ac else "standard" if has_standard_ac else "none",
            "avoid_functions": ["getRoleMemberCount"] if has_upgradeable_ac else [],
            "safe_functions": ["hasRole", "grantRole", "revokeRole"],
            "uses_role_member_count": has_role_member_count
        }

    def _detect_upgradeable_pattern(self, content: str, dependencies: List[str]) -> Dict[str, Any]:
        """Detect upgrade patterns to avoid direct upgradeTo calls."""
        
        # Check for UUPS pattern
        has_uups = any("UUPSUpgradeable" in dep for dep in dependencies) or "uups" in content.lower()
        
        # Check for Transparent proxy pattern  
        has_transparent = "TransparentUpgradeableProxy" in content or "transparent" in content.lower()
        
        # Check for direct upgradeTo usage
        has_upgrade_to = "upgradeto" in content.lower()
        
        return {
            "pattern": "uups" if has_uups else "transparent" if has_transparent else "none",
            "avoid_direct_upgrade": has_uups,  # UUPS doesn't expose upgradeTo directly
            "safe_upgrade_testing": not has_upgrade_to or not has_uups
        }

    def _extract_required_mock_functions(self, content: str, functions: List[str]) -> List[Dict[str, Any]]:
        """Extract function signatures that mocks actually need to implement."""
        
        required_functions = []
        
        # Find function calls that would need mocking
        # Look for external calls that would require mocks
        external_call_pattern = r'(\w+)\.(\w+)\s*\('
        external_calls = re.findall(external_call_pattern, content)
        
        # Group by contract interface
        interface_calls = {}
        for contract_var, function_name in external_calls:
            if contract_var not in interface_calls:
                interface_calls[contract_var] = set()
            interface_calls[contract_var].add(function_name)
        
        # Convert to required mock functions with context
        for interface, function_set in interface_calls.items():
            required_functions.append({
                "interface_name": interface,
                "required_functions": list(function_set),
                "is_erc_standard": self._is_standard_erc_interface(function_set)
            })
        
        return required_functions

    def _check_interface_compatibility(self, content: str, dependencies: List[str]) -> Dict[str, Any]:
        """Check interface compatibility requirements for mocks."""
        
        # Check for interface imports that mocks need to implement
        interface_imports = [dep for dep in dependencies if "IERC" in dep or "interface" in dep.lower()]
        
        return {
            "required_interfaces": interface_imports,
            "strict_compliance_needed": len(interface_imports) > 0,
            "custom_interface_detected": "interface" in content.lower() and not interface_imports
        }

    def _detect_circular_dependency_risks(self, content: str, contract_name: str) -> Dict[str, Any]:
        """Detect patterns that could cause circular dependencies in mocks."""
        
        # Check if contract has helper functions that might be copied to mocks
        has_internal_helpers = "internal" in content and "function" in content
        
        # Check for self-referential patterns
        self_references = content.count(contract_name)
        
        return {
            "has_internal_helpers": has_internal_helpers,
            "self_reference_count": self_references,
            "risk_level": "high" if self_references > 5 else "medium" if self_references > 2 else "low",
            "avoid_helper_duplication": has_internal_helpers
        }

    def _is_standard_erc_interface(self, function_set: set) -> bool:
        """Check if function set matches standard ERC interfaces."""
        erc20_functions = {"transfer", "transferFrom", "approve", "balanceOf", "totalSupply", "allowance"}
        erc721_functions = {"ownerOf", "approve", "transferFrom", "safeTransferFrom", "tokenURI"}
        
        return (len(erc20_functions.intersection(function_set)) >= 3 or 
                len(erc721_functions.intersection(function_set)) >= 3)

    async def _comprehensive_regex_analysis(self, file_path: Path) -> Optional[ContractAnalysis]:
        """
        Comprehensive regex-based contract analysis.
        
        This is now the primary analysis method, providing reliable and deterministic
        results without external dependencies like solc.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return None
        
        # Extract contract name with better pattern matching
        contract_match = re.search(r'contract\s+(\w+)(?:\s+is\s+[\w\s,]+)?', content)
        if not contract_match:
            # Try interface or library
            contract_match = re.search(r'(?:interface|library)\s+(\w+)', content)
            if not contract_match:
                return None
        
        contract_name = contract_match.group(1)
        
        # Extract functions with better patterns
        functions = []
        # Match function definitions including visibility and modifiers
        function_matches = re.finditer(r'function\s+(\w+)\s*\([^)]*\)(?:\s+\w+)*(?:\s+returns\s*\([^)]*\))?', content)
        for match in function_matches:
            functions.append(match.group(1))
        
        # Extract state variables with improved patterns
        state_vars = []
        # Match various state variable patterns
        state_var_patterns = [
            r'(\w+)\s+(?:public|private|internal|constant|immutable)\s+\w+(?:\[\])?(?:\s*=\s*[^;]+)?;',
            r'mapping\s*\([^)]+\)\s+(?:public|private|internal)\s+(\w+);',
            r'(\w+)\[\]\s+(?:public|private|internal)\s+\w+;'
        ]
        for pattern in state_var_patterns:
            matches = re.findall(pattern, content)
            state_vars.extend(matches)
        
        # Detect security patterns with enhanced detection
        security_patterns = []
        for pattern_type, patterns in self.security_patterns.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                security_patterns.append(pattern_type)
        
        # Determine contract type using enhanced detection
        contract_type = self._determine_contract_type_comprehensive(content)
        
        # Calculate risk score with contract type awareness
        risk_score = self._calculate_comprehensive_risk_score(
            content, functions, security_patterns, contract_type
        )
        
        # Extract dependencies with better patterns
        dependencies = []
        import_patterns = [
            r'import\s+["\']([^"\']+)["\']',
            r'import\s+\{[^}]+\}\s+from\s+["\']([^"\']+)["\']',
            r'import\s+[\w\s,{}]+\s+from\s+["\']([^"\']+)["\']'
        ]
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
        
        # Extract mock requirements for better test generation
        mock_requirements = self._extract_mock_requirements(
            content, contract_name, functions, list(set(dependencies))
        )
        
        return ContractAnalysis(
            path=str(file_path),
            contract_name=contract_name,
            contract_type=contract_type,
            functions=functions,
            state_variables=list(set(state_vars)),  # Remove duplicates
            security_patterns=security_patterns,
            risk_score=risk_score,
            dependencies=list(set(dependencies)),  # Remove duplicates
            mock_requirements=mock_requirements
        )
    
    def _determine_contract_type_comprehensive(self, content: str) -> str:
        """
        Enhanced contract type detection with broader, generic patterns.
        
        Uses scoring-based classification to avoid false positives and provide
        more accurate contract type detection without hardcoded project-specific terms.
        """
        content_lower = content.lower()
        
        # Define pattern categories with scoring
        pattern_categories = {
            "defi": [
                # Asset management patterns
                "deposit", "withdraw", "vault", "strategy", "allocation", "rebalance", "portfolio",
                # Trading patterns
                "swap", "exchange", "trade", "liquidity", "pool", "amm",
                # Lending/Borrowing patterns
                "borrow", "lend", "collateral", "liquidate", "flash",
                # Yield/Staking patterns
                "stake", "unstake", "yield", "harvest", "compound", "rewards", "farming",
                # Financial calculations
                "price", "fee", "interest", "dividend"
            ],
            "token": [
                # ERC20 patterns
                "erc20", "token", "transfer", "balanceof", "totalsupply", "allowance",
                # Token operations
                "mint", "burn", "approve", "transferfrom"
            ],
            "nft": [
                # ERC721/1155 patterns
                "erc721", "erc1155", "nft", "tokenuri", "metadata", 
                # NFT operations
                "ownerof", "getapproved", "setapprovalforall", "safetransferfrom"
            ],
            "governance": [
                # Governance patterns
                "governor", "proposal", "vote", "execute", "timelock", "delegation",
                # DAO patterns
                "dao", "council", "committee", "quorum"
            ],
            "bridge": [
                # Cross-chain patterns
                "bridge", "crosschain", "relay", "lock", "unlock", "wrap", "unwrap",
                # Multi-chain patterns
                "chain", "network", "portal"
            ],
            "access": [
                # Access control patterns
                "role", "permission", "admin", "owner", "authority", "multisig"
            ]
        }
        
        # Calculate scores for each category
        scores = {}
        for category, patterns in pattern_categories.items():
            score = sum(1 for pattern in patterns if pattern in content_lower)
            scores[category] = score
        
        # Special handling for combined categories
        # If contract has both DeFi and token patterns, still classify as DeFi
        if scores.get("defi", 0) >= 2:
            return "defi"
        elif scores.get("token", 0) >= 3:
            return "token"
        elif scores.get("nft", 0) >= 2:
            return "nft"
        elif scores.get("governance", 0) >= 2:
            return "governance"
        elif scores.get("bridge", 0) >= 2:
            return "bridge"
        elif scores.get("access", 0) >= 3:
            return "utility"  # Access control utilities
        else:
            return "utility"
    
    def _determine_contract_type(self, content: str) -> str:
        """Legacy method - redirect to comprehensive method."""
        return self._determine_contract_type_comprehensive(content)
    
    def _calculate_test_complexity(self, content: str, test_count: int, 
                                  patterns: List[str]) -> float:
        """Calculate complexity score for test file"""
        score = 0.0
        
        # Base test count score
        score += min(test_count * 0.05, 0.4)
        
        # Pattern bonuses
        pattern_bonuses = {
            "fuzz_testing": 0.3,
            "invariant_testing": 0.3,
            "security_testing": 0.2,
            "integration_testing": 0.2,
            "mock_usage": 0.1
        }
        
        for pattern in patterns:
            score += pattern_bonuses.get(pattern, 0.0)
        
        return min(score, 1.0) 