"""
Smart Contract Testing MCP Server - Testing Prompts (Refactored)

This module provides focused, tool-oriented prompts to guide the AI agent's
testing workflows and analysis. Prompts are streamlined to be direct and
guide the agent to use MCP tools and resources effectively.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class TestingPrompts:
    """
    Guided prompts for testing workflows and analysis.
    
    Provides focused, tool-oriented prompts that guide AI agents to use
    the MCP's tools and resources for effective testing workflows.
    """
    
    def __init__(self):
        """Initialize testing prompts."""
        logger.info("Testing prompts initialized")
    
    def register_prompts(self, mcp) -> None:
        """Register all testing prompts with the MCP server."""
        
        # Contract analysis prompt - guides agent to comprehensive testing analysis
        @mcp.prompt(
            name="analyze-contract-for-testing",
            description="Analyze a contract and provide comprehensive testing recommendations using MCP resources"
        )
        async def analyze_contract_for_testing(contract_path: str) -> List[Dict[str, Any]]:
            """Generates a prompt to analyze a single contract for testing."""
            return [
                {
                    "role": "system",
                    "content": await self._get_master_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Analyze the contract at: `{contract_path}`

**Required Analysis:**

1. **Contract Overview**
   - Purpose and primary functionality
   - Key state variables and critical functions
   - Security risk profile (access control, external calls, value handling)

2. **Testing Strategy** 
   - Reference `testing://foundry-patterns` for best practices
   - Identify which patterns from `testing://security-patterns` apply
   - Propose 3-5 high-priority test cases with specific function targets

3. **Template Recommendations**
   - Which templates from `testing://templates` to use (`unit`, `security`, `invariant`, etc.)
   - Required mocks and test setup (MockERC20, MockOracle, etc.)
   - Specific {{PLACEHOLDER}} values for code generation

4. **Implementation Guidance**
   - Recommended test file structure following foundry-patterns
   - Security test scenarios based on identified vulnerabilities
   - Coverage targets and success criteria

Provide actionable, specific recommendations that can be immediately implemented.
                    """
                }
            ]
        
        # Test strategy design prompt - guides comprehensive planning
        @mcp.prompt(
            name="design-test-strategy", 
            description="Design comprehensive testing strategy using MCP resources and best practices"
        )
        async def design_test_strategy(
            contracts: str, 
            risk_profile: str = "medium", 
            coverage_target: int = 90
        ) -> List[Dict[str, Any]]:
            """Generates a prompt to design a complete testing strategy."""
            return [
                {
                    "role": "system", 
                    "content": await self._get_master_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Design a comprehensive testing strategy for: `{contracts}`

**Parameters:**
- Risk Profile: {risk_profile}
- Coverage Target: {coverage_target}%

**Required Strategy Components:**

1. **File Organization**
   - Use `testing://foundry-patterns` file structure
   - Map each contract to appropriate test files (unit, security, invariant, fork)

2. **Testing Priorities**
   - Phase 1: Critical function unit tests
   - Phase 2: Security tests from `testing://security-patterns` 
   - Phase 3: Integration and invariant testing
   - Phase 4: Fork testing and edge cases

3. **Security Focus** 
   - Identify applicable vulnerability patterns from `testing://security-patterns`
   - Risk-based security testing plan (high-risk areas first)
   - Attack scenario simulation requirements

4. **Implementation Plan**
   - Template usage from `testing://templates` for each test type
   - Required mock contracts and external dependencies
   - Workflow execution using `execute_testing_workflow` tool

5. **Success Metrics**
   - Coverage targets by contract and test type
   - Security testing completeness criteria
   - Quality gates and review checkpoints

Provide a concrete, actionable strategy that leverages MCP tools and resources.
                    """
                }
            ]
        
        # Coverage review prompt - guides agent to use tools first
        @mcp.prompt(
            name="review-test-coverage",
            description="Review current test coverage and suggest improvements using MCP analysis tools"
        )
        async def review_test_coverage() -> List[Dict[str, Any]]:
            """Generates a prompt to review test coverage using MCP tools."""
            return [
                {
                    "role": "system",
                    "content": await self._get_master_system_prompt()
                },
                {
                    "role": "user", 
                    "content": """
Review the current project's test coverage and provide improvement recommendations.

**Required Process:**

1. **Initial Analysis**
   - FIRST: Call `analyze_current_test_coverage` tool to get current coverage data
   - THEN: Call `analyze_project_context` for deeper project understanding

2. **Coverage Assessment**
   - Current line, branch, and function coverage percentages
   - Gap analysis: identify top 3 functions/contracts with lowest coverage
   - Quality assessment: are tests meaningful or just coverage-focused?

3. **Improvement Recommendations**
   - Specific missing test cases for each identified gap
   - Reference `testing://security-patterns` for security test gaps
   - Template recommendations from `testing://templates` for new tests

4. **Action Plan**
   - Prioritized list of tests to add (critical gaps first)
   - Recommended workflow: which `execute_testing_workflow` type to use
   - Implementation guidance and next steps

**Output Format:**
- Current coverage summary with clear metrics
- Top 3 priority improvements with specific test recommendations
- Actionable next steps using MCP tools and resources

Use the MCP tools to gather data first, then provide specific, implementable recommendations.
                    """
                }
            ]
        
        # Security testing design prompt - focuses on attack scenarios
        @mcp.prompt(
            name="design-security-tests",
            description="Design security-focused test scenarios using security patterns resource"
        )
        async def design_security_tests(
            contract_types: str = "general",
            threat_model: str = "comprehensive"
        ) -> List[Dict[str, Any]]:
            """Generates a prompt for security-focused testing design."""
            return [
                {
                    "role": "system",
                    "content": await self._get_master_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Design comprehensive security testing for {contract_types} contracts.

**Threat Model:** {threat_model}

**Required Security Analysis:**

1. **Vulnerability Assessment**
   - Reference `testing://security-patterns` for applicable attack vectors
   - Map contract functions to relevant security patterns
   - Identify high-risk areas (access control, external calls, value transfers)

2. **Attack Scenario Design**
   - Access Control: unauthorized access attempts, privilege escalation
   - Reentrancy: single-function and cross-function reentrancy attacks  
   - Economic: flash loan attacks, price manipulation, MEV exploitation
   - Input Validation: boundary testing, overflow conditions, malformed data

3. **Test Implementation**
   - Use security test template from `testing://templates/security`
   - Implement attack contracts for realistic exploit simulation
   - Add defensive testing to verify protection mechanisms work

4. **Coverage Requirements**
   - All privileged functions must have access control tests
   - All external calls must have reentrancy tests
   - All price-dependent functions must have manipulation tests
   - All user inputs must have validation tests

5. **Test Cases**
   - Provide 3-5 specific attack scenarios with expected outcomes
   - Include both "attack should fail" and "legitimate use should work" tests
   - Reference specific patterns from `testing://security-patterns`

Design comprehensive security tests that simulate real-world attacks while verifying defensive mechanisms.
                    """
                }
            ]
        
        # Test optimization prompt - focuses on improving existing tests
        @mcp.prompt(
            name="optimize-test-performance", 
            description="Optimize test suite performance and efficiency using best practices"
        )
        async def optimize_test_performance(
            performance_issues: str = "general",
            optimization_goals: str = "speed and coverage"
        ) -> List[Dict[str, Any]]:
            """Generates a prompt for test suite optimization."""
            return [
                {
                    "role": "system",
                    "content": await self._get_master_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Optimize test suite performance for: {optimization_goals}

**Current Issues:** {performance_issues}

**Required Optimization Analysis:**

1. **Performance Assessment**
   - Use `analyze_current_test_coverage` to understand current test landscape
   - Identify slow-running tests and bottlenecks
   - Assess redundant or overlapping test coverage

2. **Optimization Strategy**
   - Reference `testing://foundry-patterns` for efficient test organization
   - Eliminate redundant tests while maintaining coverage
   - Optimize test setup and common operations

3. **Implementation Improvements**
   - Parallel test execution strategies
   - Efficient mock usage and state management
   - Strategic use of fuzz testing vs exhaustive testing
   - Gas optimization in test scenarios

4. **Quality Maintenance**
   - Ensure optimizations don't reduce test effectiveness
   - Maintain comprehensive security test coverage
   - Preserve edge case and error condition testing

5. **Workflow Integration**
   - Recommend `execute_testing_workflow` improvements
   - CI/CD optimization strategies
   - Incremental testing approaches

Provide specific, actionable optimizations that improve speed while maintaining quality.
                    """
                }
            ]
        
        logger.info("Testing prompts registered successfully")
    
    async def _get_master_system_prompt(self) -> str:
        """Generate the master system prompt for consistency across all prompts."""
        security_guidance = await self._load_security_audit_guidance()
        
        return f"""
You are a world-class smart contract security engineer and testing expert specializing in Foundry-based Solidity testing. You combine deep technical expertise with practical implementation skills to create production-ready, audit-quality test suites.

**Your Core Identity:**
- Elite Ethereum security auditor with 10+ years of experience
- Expert in Foundry testing framework and advanced Solidity patterns  
- Specialist in detecting and preventing AI-generated test failures
- Focused on practical, implementable solutions over theoretical concepts

**Your Primary Directives:**

1. **Leverage MCP Resources**: Always reference and use the provided MCP resources:
   - `testing://foundry-patterns` for best practices and code snippets
   - `testing://security-patterns` for vulnerability testing approaches
   - `testing://templates` for production-ready test templates
   - `testing://documentation` for comprehensive methodologies

2. **Tool-First Approach**: Guide users to use MCP tools for analysis:
   - `initialize_protocol_testing_agent` for project setup and workflow planning
   - `analyze_project_context` for deep project understanding
   - `execute_testing_workflow` for structured implementation
   - `analyze_current_test_coverage` for coverage assessment

3. **Security-First Mindset**: Every recommendation must prioritize security:
   - Test all access controls and authorization mechanisms
   - Simulate realistic attack scenarios, not just happy paths
   - Verify defensive mechanisms actually work under attack
   - Focus on high-impact vulnerabilities first

4. **Anti-AI-Failure Expert**: Detect and prevent common AI testing mistakes:
   - Eliminate circular logic in tests (testing implementation against itself)
   - Create meaningful mocks that can fail
   - Test actual error conditions, not just happy paths
   - Use independent expected values for validation

5. **Practical Implementation**: Provide actionable, specific guidance:
   - Use {{PLACEHOLDER}} syntax for dynamic code generation
   - Reference specific templates and patterns by name
   - Give concrete next steps with tool usage
   - Focus on implementable solutions over theoretical advice

**Integrated Security Framework:**
{security_guidance}

**Response Guidelines:**
- Be direct and technical - avoid fluff or overly verbose explanations
- Always reference specific MCP resources and tools in your recommendations  
- Provide concrete code examples using templates and patterns
- Focus on practical next steps the user can immediately implement
- Maintain audit-level quality standards in all recommendations

Your goal is to guide users to create comprehensive, secure, production-ready test suites using the MCP's tools and resources effectively.
        """
    
    async def _load_security_audit_guidance(self) -> str:
        """Load security audit guidance with simplified, robust approach."""
        try:
            # Primary path: look for comprehensive security framework
            security_framework_path = Path(__file__).parent.parent / "docs" / "security-audit-guidance.md"
            
            if security_framework_path.exists():
                with open(security_framework_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract key sections for LLM context (simplified approach)
                if "## AI IDENTITY AND EXPERTISE" in content:
                    # Extract relevant sections for system prompt
                    return self._extract_key_sections(content)
                else:
                    return content[:3000]  # First 3000 chars if no clear structure
            
            else:
                logger.warning(f"Security guidance not found at {security_framework_path}")
                return self._get_fallback_security_guidance()
                
        except Exception as e:
            logger.error(f"Error loading security audit guidance: {e}")
            return self._get_fallback_security_guidance()
    
    def _extract_key_sections(self, content: str) -> str:
        """Extract key sections from security guidance for system prompt."""
        key_sections = [
            "## AI IDENTITY AND EXPERTISE",
            "## CORE SECURITY AUDIT METHODOLOGY", 
            "## AI CODING AGENT FAILURE PATTERNS",
            "## VULNERABILITY PATTERNS TO TEST"
        ]
        
        extracted = []
        lines = content.split('\n')
        current_section = None
        include_section = False
        
        for line in lines:
            # Check if this line starts a section we want
            if any(section in line for section in key_sections):
                current_section = line
                include_section = True
                extracted.append(line)
            # Check if this line starts a different section (stop including)
            elif line.startswith("## ") and include_section:
                if not any(section in line for section in key_sections):
                    include_section = False
                    current_section = None
                else:
                    # This is another section we want
                    extracted.append(line)
            # Include lines if we're in a relevant section
            elif include_section:
                extracted.append(line)
        
        # Limit to reasonable size for system prompt
        result = '\n'.join(extracted)
        return result[:4000] if len(result) > 4000 else result
    
    def _get_fallback_security_guidance(self) -> str:
        """Fallback security guidance when file loading fails."""
        return """
## SECURITY TESTING PRINCIPLES

**Access Control Testing:**
- Test unauthorized access to all privileged functions
- Verify role-based permissions work correctly
- Test privilege escalation scenarios

**Reentrancy Testing:**
- Test all functions with external calls for reentrancy
- Simulate realistic attack contracts
- Verify ReentrancyGuard protection works

**Economic Testing:**
- Test flash loan attack scenarios
- Verify oracle manipulation resistance  
- Test MEV protection mechanisms

**Input Validation:**
- Test boundary conditions and edge cases
- Verify overflow/underflow protection
- Test malformed input handling

**AI FAILURE PREVENTION:**
- Avoid circular logic in tests (testing implementation against itself)
- Create meaningful mocks that can fail
- Test actual error conditions, not just happy paths
- Use independent expected values for validation
        """ 