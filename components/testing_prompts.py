"""
Smart Contract Testing MCP Server - Testing Prompts

This module provides guided prompts for testing workflows and analysis.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TestingPrompts:
    """
    Guided prompts for testing workflows and analysis.
    
    This class provides structured prompts that guide users through different
    testing scenarios and analysis tasks.
    """
    
    def __init__(self):
        """Initialize testing prompts."""
        logger.info("Testing prompts initialized")
    
    def register_prompts(self, mcp) -> None:
        """
        Register all testing prompts with the MCP server.
        
        Args:
            mcp: FastMCP server instance
        """
        # Contract analysis prompt
        @mcp.prompt(
            name="analyze-contract-for-testing",
            description="Analyze a contract and provide comprehensive testing recommendations"
        )
        async def analyze_contract_for_testing(contract_path: str) -> List[Dict[str, Any]]:
            """
            Analyze a contract and provide testing recommendations.
            
            Args:
                contract_path: Path to the contract file to analyze
                
            Returns:
                List of prompt messages for contract analysis
            """
            return [
                {
                    "role": "system",
                    "content": await self._get_contract_analysis_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Please analyze the contract at: {contract_path}

Provide a comprehensive testing analysis including:

1. **Contract Overview**
   - Contract purpose and functionality
   - Key state variables and their roles
   - Main functions and their interactions
   - Inheritance hierarchy and dependencies

2. **Testing Strategy**
   - Critical functions that need testing
   - Edge cases and boundary conditions
   - Error scenarios and revert conditions
   - State transition testing needs

3. **Security Considerations**
   - Access control mechanisms
   - Potential attack vectors
   - Reentrancy concerns
   - Integer overflow/underflow risks

4. **Test Categories Required**
   - Unit tests for individual functions
   - Integration tests for function interactions
   - Invariant tests for system properties
   - Fuzz tests for robustness

5. **Specific Test Recommendations**
   - High-priority test cases
   - Mock and fixture requirements
   - Gas optimization test scenarios
   - Event emission testing

Generate specific, actionable test cases with expected outcomes.
                    """
                }
            ]
        
        # Test strategy design prompt
        @mcp.prompt(
            name="design-test-strategy",
            description="Design comprehensive testing strategy for smart contracts"
        )
        async def design_test_strategy(
            contracts: str,
            risk_profile: str = "medium",
            coverage_target: int = 90
        ) -> List[Dict[str, Any]]:
            """
            Design comprehensive testing strategy for smart contracts.
            
            Args:
                contracts: Contract names or descriptions to analyze
                risk_profile: Risk assessment level (low, medium, high)
                coverage_target: Target coverage percentage
                
            Returns:
                List of prompt messages for strategy design
            """
            return [
                {
                    "role": "system",
                    "content": await self._get_test_strategy_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Design a comprehensive testing strategy for the following contracts: {contracts}

Parameters:
- Risk Profile: {risk_profile}
- Coverage Target: {coverage_target}%

Please provide a detailed strategy including:

1. **Testing Framework Setup**
   - Foundry configuration recommendations
   - Test file organization structure
   - Dependency and mock management
   - Continuous integration setup

2. **Test Categories & Priorities**
   - Unit testing approach and priorities
   - Integration testing scenarios
   - Invariant testing for system properties
   - Fuzz testing for edge cases
   - Security testing requirements

3. **Coverage Strategy**
   - Line coverage targets by contract
   - Branch coverage requirements
   - Function coverage priorities
   - Path coverage for critical flows

4. **Risk-Based Testing**
   - High-risk areas requiring extra attention
   - Security vulnerability testing
   - Economic attack vector testing
   - Gas optimization verification

5. **Implementation Timeline**
   - Phased testing implementation plan
   - Resource allocation recommendations
   - Milestone definitions and success criteria
   - Maintenance and update procedures

6. **Quality Assurance**
   - Test quality metrics
   - Review and validation processes
   - Documentation requirements
   - Performance benchmarking

Provide specific, actionable recommendations with code examples where helpful.
                    """
                }
            ]
        
        # Coverage review prompt
        @mcp.prompt(
            name="review-test-coverage",
            description="Review current test coverage and suggest improvements (analyze current directory)"
        )
        async def review_test_coverage() -> List[Dict[str, Any]]:
            """
            Review current test coverage and suggest improvements.
            
            Returns:
                List of prompt messages for coverage review
            """
            return [
                {
                    "role": "system",
                    "content": await self._get_coverage_review_system_prompt()
                },
                {
                    "role": "user",
                    "content": """
Please review the test coverage for the current project directory.

Analyze and provide recommendations for:

1. **Current Coverage Analysis**
   - Line coverage assessment
   - Branch coverage gaps
   - Function coverage completeness
   - Critical path coverage

2. **Gap Identification**
   - Uncovered code paths
   - Missing edge cases
   - Untested error conditions
   - Integration gaps

3. **Quality Assessment**
   - Test quality and maintainability
   - Test organization effectiveness
   - Performance of existing tests
   - Anti-pattern identification

4. **Improvement Recommendations**
   - Specific tests to add
   - Refactoring opportunities
   - Coverage enhancement strategies
   - Performance optimizations

5. **Implementation Priority**
   - High-priority missing tests
   - Quick wins for coverage improvement
   - Long-term enhancement plan
   - Resource allocation suggestions

Use the analyze_current_test_coverage tool first to get current coverage data, then provide specific, actionable recommendations with code examples where appropriate.
                    """
                }
            ]
        
        # Security testing prompt
        @mcp.prompt(
            name="design-security-tests",
            description="Design security-focused test scenarios for smart contracts"
        )
        async def design_security_tests(
            contract_types: str = "general",
            threat_model: str = "comprehensive"
        ) -> List[Dict[str, Any]]:
            """
            Design security-focused test scenarios.
            
            Args:
                contract_types: Types of contracts (DeFi, NFT, governance, etc.)
                threat_model: Threat model scope (basic, comprehensive, advanced)
                
            Returns:
                List of prompt messages for security testing
            """
            return [
                {
                    "role": "system",
                    "content": await self._get_security_testing_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Design comprehensive security testing scenarios for {contract_types} contracts.

Threat Model: {threat_model}

Please provide security testing recommendations for:

1. **Access Control Testing**
   - Role-based access control verification
   - Unauthorized access prevention
   - Privilege escalation prevention
   - Multi-signature validation

2. **Reentrancy Testing**
   - Single-function reentrancy
   - Cross-function reentrancy
   - Cross-contract reentrancy
   - Read-only reentrancy

3. **Economic Attack Testing**
   - Front-running scenarios
   - MEV exploitation vectors
   - Flash loan attacks
   - Oracle manipulation

4. **Input Validation Testing**
   - Boundary value testing
   - Malformed input handling
   - Integer overflow/underflow
   - Type confusion attacks

5. **State Manipulation Testing**
   - Invariant violation attempts
   - State transition attacks
   - Storage collision testing
   - Proxy upgrade security

6. **Integration Security Testing**
   - External contract interactions
   - Dependency security validation
   - Composability security risks
   - Third-party integration testing

Provide specific test cases with attack scenarios and expected defensive behaviors.
                    """
                }
            ]
        
        # Test optimization prompt
        @mcp.prompt(
            name="optimize-test-performance",
            description="Optimize test suite performance and efficiency"
        )
        async def optimize_test_performance(
            performance_issues: str = "general",
            optimization_goals: str = "speed and coverage"
        ) -> List[Dict[str, Any]]:
            """
            Optimize test suite performance and efficiency.
            
            Args:
                performance_issues: Specific performance issues to address
                optimization_goals: Optimization objectives
                
            Returns:
                List of prompt messages for test optimization
            """
            return [
                {
                    "role": "system",
                    "content": await self._get_test_optimization_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Optimize the test suite performance focusing on: {optimization_goals}

Current performance issues: {performance_issues}

Please provide optimization recommendations for:

1. **Test Execution Speed**
   - Parallel test execution strategies
   - Test setup and teardown optimization
   - Mock and fixture efficiency
   - State management optimization

2. **Coverage Efficiency**
   - Eliminate redundant tests
   - Optimize test case selection
   - Improve test coverage per execution time
   - Strategic test prioritization

3. **Resource Optimization**
   - Memory usage optimization
   - Gas cost reduction in tests
   - Network interaction minimization
   - Computation efficiency improvements

4. **Test Organization**
   - Logical test grouping
   - Shared setup optimization
   - Test dependency management
   - Modular test design

5. **CI/CD Integration**
   - Parallel pipeline execution
   - Selective test execution
   - Caching strategies
   - Incremental testing approaches

6. **Monitoring and Metrics**
   - Performance benchmarking
   - Regression detection
   - Quality metrics tracking
   - Continuous improvement processes

Provide specific, actionable optimizations with implementation examples.
                    """
                }
            ]
        
        logger.info("Testing prompts registered successfully")
    
    # System prompt generators
    async def _get_contract_analysis_system_prompt(self) -> str:
        """Generate system prompt for contract analysis."""
        return """
You are an expert smart contract testing advisor with deep knowledge of Solidity, Foundry, and security best practices.

Your role is to:
1. Analyze smart contracts for testability and security
2. Identify critical testing requirements
3. Recommend comprehensive testing strategies
4. Provide specific, actionable test cases
5. Consider security implications and edge cases

Always provide:
- Clear, actionable recommendations
- Specific test case examples
- Security considerations
- Performance implications
- Best practices alignment

Focus on practical, implementable advice that improves code quality and security.
        """
    
    async def _get_test_strategy_system_prompt(self) -> str:
        """Generate system prompt for test strategy design."""
        return """
You are a senior smart contract testing strategist with expertise in comprehensive testing methodologies.

Your expertise includes:
- Foundry testing framework mastery
- Risk-based testing approaches
- Security-first testing strategies
- Performance optimization
- CI/CD integration

Provide strategies that are:
- Comprehensive yet practical
- Risk-appropriate
- Implementable with available resources
- Aligned with industry best practices
- Scalable and maintainable

Always consider the full testing lifecycle from development to production.
        """
    
    async def _get_coverage_review_system_prompt(self) -> str:
        """Generate system prompt for coverage review."""
        return """
You are a quality assurance expert specializing in smart contract test coverage analysis.

Your focus areas:
- Coverage gap identification
- Quality assessment of existing tests
- Improvement prioritization
- Refactoring recommendations
- Performance optimization

Provide reviews that:
- Identify critical coverage gaps
- Assess test quality and maintainability
- Prioritize improvements by impact
- Suggest specific enhancements
- Balance coverage with efficiency

Always provide actionable, prioritized recommendations.
        """
    
    async def _get_security_testing_system_prompt(self) -> str:
        """Generate system prompt for security testing."""
        return """
You are a smart contract security expert with deep knowledge of common vulnerabilities and attack vectors.

Your security expertise covers:
- OWASP Smart Contract Top 10
- DeFi-specific attack vectors
- Reentrancy and access control
- Economic and governance attacks
- Cross-contract interaction risks

Design security tests that:
- Cover known vulnerability patterns
- Test defensive mechanisms
- Validate access controls
- Simulate real-world attacks
- Ensure proper error handling

Always provide comprehensive security test scenarios with clear attack vectors and expected defenses.
        """
    
    async def _get_test_optimization_system_prompt(self) -> str:
        """Generate system prompt for test optimization."""
        return """
You are a performance optimization expert specializing in smart contract testing efficiency.

Your optimization focus:
- Test execution speed
- Resource utilization
- Coverage efficiency
- CI/CD integration
- Maintenance overhead

Provide optimizations that:
- Reduce execution time
- Improve resource efficiency
- Maintain or improve coverage
- Enhance maintainability
- Scale with project growth

Always balance speed with coverage and quality.
        """ 