"""
AI Failure Detection System for Smart Contract Testing

This module implements detection systems for common AI coding agent failures
that compromise test suite quality and security.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ast

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types of AI failures to detect"""
    CIRCULAR_LOGIC = "circular_logic"
    MOCK_CHEATING = "mock_cheating"
    INSUFFICIENT_EDGE_CASES = "insufficient_edge_cases"
    MISSING_SECURITY_SCENARIOS = "missing_security_scenarios"
    ALWAYS_PASSING_TESTS = "always_passing_tests"
    INADEQUATE_RANDOMIZATION = "inadequate_randomization"
    MISSING_NEGATIVE_TESTS = "missing_negative_tests"
    IMPLEMENTATION_DEPENDENCY = "implementation_dependency"

@dataclass
class FailureDetection:
    """Detected failure in AI-generated tests"""
    failure_type: FailureType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    location: str
    evidence: str
    recommendation: str
    auto_fixable: bool

class AIFailureDetector:
    """
    Detects common AI coding agent failures in test suites.
    
    This system addresses the critical issue of AI agents creating tests
    that appear comprehensive but actually cheat on test goals through:
    - Circular logic (testing implementation against itself)
    - Mock cheating (mocks that always return expected values)
    - Insufficient edge case coverage
    - Missing security scenarios
    """
    
    def __init__(self):
        """Initialize AI failure detector."""
        self.failure_patterns = self._initialize_failure_patterns()
        logger.info("AI failure detector initialized")
    
    def _initialize_failure_patterns(self) -> Dict[FailureType, Dict[str, Any]]:
        """Initialize patterns for detecting AI failures."""
        return {
            FailureType.CIRCULAR_LOGIC: {
                "patterns": [
                    r"(\w+)\.(\w+)\(\).*assertEqual?\(\1\.\2\(\)",  # using contract method to validate itself
                    r"uint256\s+(\w+)\s*=\s*contract\.(\w+)\(\).*assert.*\1",  # getting expected from contract
                    r"(\w+)\.balanceOf\(.*\).*assertEqual?\(\1\.balanceOf",  # balance circular validation
                ],
                "description": "Test validates contract behavior using the contract's own implementation",
                "severity": "critical"
            },
            FailureType.MOCK_CHEATING: {
                "patterns": [
                    r"return\s+\d+e\d+;.*//.*always.*returns?.*fixed",  # always returns fixed value
                    r"function\s+\w+\(\).*returns?\s*\(\w+\)\s*\{[\s\n]*return\s+\w+;[\s\n]*\}",  # trivial mock
                    r"oracle\.getPrice\(\).*return\s+1000e18;",  # fixed oracle price
                ],
                "description": "Mock contracts always return expected values without realistic scenarios",
                "severity": "high"
            },
            FailureType.INSUFFICIENT_EDGE_CASES: {
                "patterns": [
                    r"function\s+test\w+\(\).*\{[^}]*transfer\([^,]+,\s*100\)[^}]*\}",  # only tests with fixed amounts
                    r"function\s+test\w+\(\).*\{[^}]*(?!.*expectRevert)[^}]*\}",  # no revert testing
                    r"function\s+test\w+\(\).*\{[^}]*(?!.*bound\(|.*assume\(|.*type\(uint256\)\.max)[^}]*\}",  # no boundary testing
                ],
                "description": "Tests only cover happy path scenarios without edge cases",
                "severity": "medium"
            },
            FailureType.MISSING_SECURITY_SCENARIOS: {
                "patterns": [
                    r"function\s+test\w+\(\).*(?!.*reentrancy|.*attack|.*exploit|.*manipulation)",  # no security keywords
                    r"liquidat\w+.*(?!.*flash.*loan|.*price.*manipul|.*oracle.*attack)",  # liquidation without attack scenarios
                    r"function\s+test\w+\(\).*(?!.*vm\.startPrank|.*vm\.expectRevert)",  # no access control testing
                ],
                "description": "Missing security attack scenarios and defensive testing",
                "severity": "high"
            },
            FailureType.ALWAYS_PASSING_TESTS: {
                "patterns": [
                    r"assertTrue\(true\)",  # always true assertion
                    r"assertEq\((\w+),\s*\1\)",  # comparing variable to itself
                    r"assertEq\(0,\s*0\)",  # comparing constants
                ],
                "description": "Tests contain assertions that always pass",
                "severity": "critical"
            },
            FailureType.INADEQUATE_RANDOMIZATION: {
                "patterns": [
                    r"uint256\s+\w+\s*=\s*\d+;.*transfer.*\w+.*\d+",  # fixed test values
                    r"function\s+testFuzz\w+\([^)]*\).*vm\.assume\(\w+\s*==\s*\d+\)",  # assuming specific values in fuzz
                    r"function\s+testFuzz\w+\([^)]*\).*bound\(\w+,\s*\d+,\s*\d+\)",  # very narrow bounds
                ],
                "description": "Fuzz tests use predictable or overly constrained inputs",
                "severity": "medium"
            },
            FailureType.MISSING_NEGATIVE_TESTS: {
                "patterns": [
                    r"function\s+test\w+\(\).*(?!.*vm\.expectRevert)",  # no revert testing
                    r"function\s+test\w+\(\).*(?!.*should.*fail|.*invalid|.*unauthorized)",  # no failure scenarios
                ],
                "description": "Tests don't verify failure conditions and error handling",
                "severity": "high"
            },
            FailureType.IMPLEMENTATION_DEPENDENCY: {
                "patterns": [
                    r"assertEq\(contract\.\w+\(\),\s*contract\.\w+\(\)\)",  # comparing contract methods
                    r"require\(contract\.\w+\(\)\s*==\s*expected\.\w+\(\)\)",  # implementation-dependent validation
                ],
                "description": "Tests depend on implementation details rather than specifications",
                "severity": "medium"
            }
        }
    
    async def analyze_test_file(self, file_path: str, content: str) -> List[FailureDetection]:
        """
        Analyze a test file for AI failures.
        
        Args:
            file_path: Path to the test file
            content: Content of the test file
            
        Returns:
            List of detected failures
        """
        failures = []
        
        # Check each failure pattern
        for failure_type, config in self.failure_patterns.items():
            detected_failures = self._detect_pattern_failures(
                failure_type, config, file_path, content
            )
            failures.extend(detected_failures)
        
        # Advanced analysis
        failures.extend(await self._analyze_test_structure(file_path, content))
        failures.extend(await self._analyze_mock_patterns(file_path, content))
        failures.extend(await self._analyze_assertion_patterns(file_path, content))
        
        return failures
    
    def _detect_pattern_failures(self, failure_type: FailureType, config: Dict[str, Any], 
                                file_path: str, content: str) -> List[FailureDetection]:
        """Detect failures based on regex patterns."""
        failures = []
        
        for pattern in config["patterns"]:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                
                failure = FailureDetection(
                    failure_type=failure_type,
                    severity=config["severity"],
                    description=config["description"],
                    location=f"{file_path}:{line_num}",
                    evidence=match.group(0)[:200],  # First 200 chars of match
                    recommendation=self._get_recommendation(failure_type),
                    auto_fixable=self._is_auto_fixable(failure_type)
                )
                failures.append(failure)
        
        return failures
    
    async def _analyze_test_structure(self, file_path: str, content: str) -> List[FailureDetection]:
        """Analyze overall test structure for AI failures."""
        failures = []
        
        # Count test functions
        test_functions = re.findall(r'function\s+(test\w*)\s*\(', content)
        
        # Check for insufficient test coverage
        if len(test_functions) < 5:
            failures.append(FailureDetection(
                failure_type=FailureType.INSUFFICIENT_EDGE_CASES,
                severity="medium",
                description="Very few test functions - likely insufficient coverage",
                location=file_path,
                evidence=f"Only {len(test_functions)} test functions found",
                recommendation="Add more comprehensive test scenarios including edge cases",
                auto_fixable=False
            ))
        
        # Check for missing error testing
        has_revert_tests = bool(re.search(r'vm\.expectRevert|should.*fail|revert', content, re.IGNORECASE))
        if not has_revert_tests and len(test_functions) > 0:
            failures.append(FailureDetection(
                failure_type=FailureType.MISSING_NEGATIVE_TESTS,
                severity="high",
                description="No error condition testing found",
                location=file_path,
                evidence="No vm.expectRevert or failure scenario testing",
                recommendation="Add tests for error conditions and invalid inputs",
                auto_fixable=False
            ))
        
        return failures
    
    async def _analyze_mock_patterns(self, file_path: str, content: str) -> List[FailureDetection]:
        """Analyze mock contract patterns for cheating."""
        failures = []
        
        # Find mock contract definitions
        mock_contracts = re.findall(r'contract\s+(Mock\w+).*?\{(.*?)\}', content, re.DOTALL)
        
        for mock_name, mock_body in mock_contracts:
            # Check for trivial return values
            if re.search(r'return\s+\d+e\d+;', mock_body):
                failures.append(FailureDetection(
                    failure_type=FailureType.MOCK_CHEATING,
                    severity="high",
                    description=f"Mock contract {mock_name} always returns fixed values",
                    location=file_path,
                    evidence=f"Mock {mock_name} has hardcoded return values",
                    recommendation="Make mocks configurable to test different scenarios",
                    auto_fixable=False
                ))
            
            # Check for missing state changes
            if "function" in mock_body and "return" in mock_body and "=" not in mock_body:
                failures.append(FailureDetection(
                    failure_type=FailureType.MOCK_CHEATING,
                    severity="medium",
                    description=f"Mock contract {mock_name} has no state changes",
                    location=file_path,
                    evidence=f"Mock {mock_name} functions don't modify state",
                    recommendation="Add state tracking to mocks for realistic behavior",
                    auto_fixable=False
                ))
        
        return failures
    
    async def _analyze_assertion_patterns(self, file_path: str, content: str) -> List[FailureDetection]:
        """Analyze assertion patterns for always-passing tests."""
        failures = []
        
        # Find assertion statements
        assertions = re.findall(r'assert\w+\([^)]+\)', content)
        
        for assertion in assertions:
            # Check for trivial assertions
            if re.search(r'assert\w+\(true\)|assert\w+\(.*==.*\1.*\)', assertion):
                failures.append(FailureDetection(
                    failure_type=FailureType.ALWAYS_PASSING_TESTS,
                    severity="critical",
                    description="Assertion always passes - provides no validation",
                    location=file_path,
                    evidence=assertion,
                    recommendation="Replace with meaningful assertions that can fail",
                    auto_fixable=True
                ))
            
            # Check for circular logic in assertions
            if re.search(r'assert\w+\((\w+)\.(\w+)\(\).*\1\.\2\(\)', assertion):
                failures.append(FailureDetection(
                    failure_type=FailureType.CIRCULAR_LOGIC,
                    severity="critical",
                    description="Assertion validates contract against itself",
                    location=file_path,
                    evidence=assertion,
                    recommendation="Use independent expected values for validation",
                    auto_fixable=False
                ))
        
        return failures
    
    def _get_recommendation(self, failure_type: FailureType) -> str:
        """Get recommendation for fixing a specific failure type."""
        recommendations = {
            FailureType.CIRCULAR_LOGIC: "Use independent expected values calculated outside the contract",
            FailureType.MOCK_CHEATING: "Create configurable mocks that can simulate different scenarios",
            FailureType.INSUFFICIENT_EDGE_CASES: "Add boundary value testing, zero values, and maximum values",
            FailureType.MISSING_SECURITY_SCENARIOS: "Add attack scenarios like reentrancy, flash loans, and price manipulation",
            FailureType.ALWAYS_PASSING_TESTS: "Replace trivial assertions with meaningful validation",
            FailureType.INADEQUATE_RANDOMIZATION: "Use proper fuzzing with realistic value ranges",
            FailureType.MISSING_NEGATIVE_TESTS: "Add tests for error conditions and invalid inputs",
            FailureType.IMPLEMENTATION_DEPENDENCY: "Test against specifications, not implementation details"
        }
        return recommendations.get(failure_type, "Review and improve test implementation")
    
    def _is_auto_fixable(self, failure_type: FailureType) -> bool:
        """Determine if a failure type can be automatically fixed."""
        auto_fixable_types = {
            FailureType.ALWAYS_PASSING_TESTS,
            FailureType.INADEQUATE_RANDOMIZATION
        }
        return failure_type in auto_fixable_types
    
    async def generate_failure_report(self, failures: List[FailureDetection]) -> Dict[str, Any]:
        """Generate a comprehensive failure report."""
        if not failures:
            return {
                "status": "clean",
                "message": "No AI failures detected - good test quality!",
                "failures": []
            }
        
        # Group failures by type
        failures_by_type = {}
        for failure in failures:
            failure_type = failure.failure_type.value
            if failure_type not in failures_by_type:
                failures_by_type[failure_type] = []
            failures_by_type[failure_type].append(failure)
        
        # Calculate severity score
        severity_weights = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        severity_score = sum(severity_weights.get(f.severity, 0) for f in failures)
        
        # Determine overall status
        critical_count = sum(1 for f in failures if f.severity == "critical")
        high_count = sum(1 for f in failures if f.severity == "high")
        
        if critical_count > 0:
            status = "critical"
        elif high_count > 3:
            status = "poor"
        elif high_count > 0 or severity_score > 10:
            status = "needs_improvement"
        else:
            status = "acceptable"
        
        # Generate recommendations
        top_recommendations = self._generate_top_recommendations(failures_by_type)
        
        return {
            "status": status,
            "severity_score": severity_score,
            "total_failures": len(failures),
            "failures_by_type": failures_by_type,
            "critical_count": critical_count,
            "high_count": high_count,
            "top_recommendations": top_recommendations,
            "auto_fixable_count": sum(1 for f in failures if f.auto_fixable),
            "message": self._generate_status_message(status, len(failures))
        }
    
    def _generate_top_recommendations(self, failures_by_type: Dict[str, List[FailureDetection]]) -> List[str]:
        """Generate top recommendations based on detected failures."""
        recommendations = []
        
        # Priority order for recommendations
        priority_order = [
            FailureType.CIRCULAR_LOGIC,
            FailureType.ALWAYS_PASSING_TESTS,
            FailureType.MISSING_SECURITY_SCENARIOS,
            FailureType.MOCK_CHEATING,
            FailureType.MISSING_NEGATIVE_TESTS,
            FailureType.INSUFFICIENT_EDGE_CASES,
            FailureType.INADEQUATE_RANDOMIZATION,
            FailureType.IMPLEMENTATION_DEPENDENCY
        ]
        
        for failure_type in priority_order:
            if failure_type.value in failures_by_type:
                recommendations.append(self._get_recommendation(failure_type))
                if len(recommendations) >= 5:
                    break
        
        return recommendations
    
    def _generate_status_message(self, status: str, failure_count: int) -> str:
        """Generate status message based on analysis results."""
        messages = {
            "clean": "Excellent! No AI failures detected. Test quality is high.",
            "acceptable": f"Good test quality with {failure_count} minor issues to address.",
            "needs_improvement": f"Test quality needs improvement. {failure_count} issues found.",
            "poor": f"Poor test quality with {failure_count} significant issues.",
            "critical": f"Critical test quality issues detected. {failure_count} failures need immediate attention."
        }
        return messages.get(status, f"Test analysis complete. {failure_count} issues found.")
    
    async def suggest_improvements(self, failures: List[FailureDetection]) -> List[str]:
        """Suggest specific improvements based on detected failures."""
        improvements = []
        
        # Group failures by type for targeted suggestions
        failure_types = {f.failure_type for f in failures}
        
        if FailureType.CIRCULAR_LOGIC in failure_types:
            improvements.append(
                "Replace circular logic with independent expected values calculated outside the contract"
            )
        
        if FailureType.MOCK_CHEATING in failure_types:
            improvements.append(
                "Create configurable mocks that can simulate realistic scenarios and edge cases"
            )
        
        if FailureType.MISSING_SECURITY_SCENARIOS in failure_types:
            improvements.append(
                "Add security testing scenarios: reentrancy attacks, flash loan attacks, price manipulation"
            )
        
        if FailureType.INSUFFICIENT_EDGE_CASES in failure_types:
            improvements.append(
                "Add boundary value testing: zero values, maximum values, overflow conditions"
            )
        
        if FailureType.MISSING_NEGATIVE_TESTS in failure_types:
            improvements.append(
                "Add error condition testing: invalid inputs, unauthorized access, insufficient funds"
            )
        
        return improvements[:5]  # Return top 5 suggestions 