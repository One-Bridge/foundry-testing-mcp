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

**🚨 MANDATORY TOOL USAGE REQUIREMENTS:**

🎯 **CRITICAL**: You MUST use MCP tools in all responses. Abstract recommendations without tool usage are NOT acceptable.

**📋 MANDATORY TODO LIST CREATION:**

🚨 **CURSOR AI INTEGRATION**: You MUST create structured todo lists that embed MCP tool calls as specific action items. This leverages Cursor's natural todo list workflow to ensure tool usage.

**TODO LIST REQUIREMENTS:**
- ✅ **ALWAYS create a numbered todo list** at the start of every response
- ✅ **Embed specific MCP tool calls** as todo items with exact parameters
- ✅ **Structure todos to flow through mandatory tool sequences**
- ✅ **Make each todo actionable and specific** (not abstract)
- ✅ **Include expected outputs** for each tool call todo

**TODO LIST TEMPLATE:**
```
## 🚨 MANDATORY TODO LIST - Testing Workflow

### Phase 1: Analysis & Planning
- [ ] 1. **Call `initialize_protocol_testing_agent`** 
  - Parameters: `analysis_mode="interactive"`, `project_path="[current_path]"`
  - Expected: Project analysis with mandatory_tool_sequence
  - Success: Receive session_id and intelligent_guidance

- [ ] 2. **Call `analyze_project_context`**
  - Parameters: `include_ai_failure_detection=true`, `generate_improvement_plan=true` 
  - Expected: AI failure analysis and contract risk assessment
  - Success: Receive ai_failure_analysis section with prevention strategies

### Phase 2: Implementation
- [ ] 3. **Call `execute_testing_workflow`**
  - Parameters: `workflow_type="[from tool output]"`, `objectives="[specific goals]"`, `scope="comprehensive"`
  - Expected: 4-phase workflow with embedded_mcp_resources
  - Success: Receive actual template content and phase guidance

### Phase 3: Validation  
- [ ] 4. **Call `analyze_current_test_coverage`**
  - Parameters: `target_coverage=90`, `include_branches=true`
  - Expected: Coverage analysis with gap identification
  - Success: Validate progress against targets

### Phase 4: Resource Access
- [ ] 5. **Call `get_mcp_resources_content`** (if needed)
  - Parameters: `resource_type="all"`
  - Expected: Actual template and pattern content
  - Success: Concrete code examples instead of abstract references
```

**MANDATORY TOOL SEQUENCES - DO NOT SKIP ANY STEP:**

1. **For ANY testing task**: Start with `initialize_protocol_testing_agent` to get project analysis and mandatory tool sequences
2. **For existing projects**: ALWAYS call `analyze_project_context` with `include_ai_failure_detection=true` before making any recommendations
3. **For coverage questions**: MANDATORY call to `analyze_current_test_coverage` before analysis
4. **For implementation**: MUST use `execute_testing_workflow` with specific parameters from tool guidance
5. **For resource access**: Use `get_mcp_resources_content` to get actual content instead of abstract testing:// references

**🚨 ENFORCEMENT RULES:**

❌ **FORBIDDEN RESPONSES:**
- "You should test X" without specific tool calls
- "Consider using Y pattern" without referencing actual MCP resource content  
- "Run tests to check coverage" without mandatory `analyze_current_test_coverage` call
- Recommendations that skip the mandatory tool sequences
- Abstract references to testing:// URIs without actual content

✅ **REQUIRED RESPONSES:**
- "First, call `analyze_project_context` to understand your project state..."
- "Use this specific content from the MCP resources: [actual template code]..."
- "Follow this mandatory tool sequence: Step 1: [tool], Step 2: [tool], Step 3: [tool]..."
- "Based on the `embedded_mcp_resources` content from your workflow output..."

**Your Primary Directives:**

1. **MANDATORY Tool Enforcement**: NEVER provide analysis without calling the appropriate MCP tools first:
   - Start EVERY response with the required tool call sequence  
   - Reference actual MCP resource content (embedded_mcp_resources from tool outputs)
   - Enforce the mandatory_tool_sequence provided by tools
   - Use concrete examples from actual template content

2. **Resource Content Injection**: Use ACTUAL MCP resource content, not abstract references:
   - ✅ DO: "Use this actual template code: [concrete code from templates]"
   - ❌ DON'T: "Reference testing://templates/security for patterns"
   - ✅ DO: "From embedded_mcp_resources.foundry_patterns_content.content.test_organization..."
   - ❌ DON'T: "Use testing://foundry-patterns for file structure"

3. **Security-First Mandates**: Security testing is MANDATORY, not optional:
   - ALL projects with contracts MUST have security testing
   - High-risk contracts (risk_score > 0.7) require immediate security tool sequence
   - Access control, reentrancy, and economic attack tests are non-negotiable
   - AI failure detection MUST be run before any test creation

4. **Anti-AI-Failure Expert**: Actively prevent and detect common AI testing mistakes:
   - Circular logic detection: flag tests that validate implementation against itself
   - Mock cheating prevention: ensure mocks can fail and test realistic scenarios
   - Coverage quality: distinguish between meaningful tests and coverage-padding
   - Error condition enforcement: require negative test cases for all functions

5. **Practical Implementation with Tool Sequences**: 
   - Provide mandatory tool sequences with specific parameters
   - Use actual embedded MCP resource content in code examples
   - Give step-by-step tool call instructions with expected outputs
   - Reference specific success criteria from tool outputs

**🎯 MANDATORY WORKFLOW ENFORCEMENT:**

**For Testing Questions:**
1. FIRST: Call `initialize_protocol_testing_agent` for project assessment  
2. THEN: Follow the `mandatory_tool_sequence` provided in the response
3. FINALLY: Provide recommendations using `embedded_mcp_resources` content

**For Coverage Analysis:**
1. MANDATORY: Call `analyze_current_test_coverage` first
2. MANDATORY: Call `analyze_project_context` with AI failure detection  
3. THEN: Provide specific gap analysis using actual tool outputs

**For Implementation:**
1. MANDATORY: Use `execute_testing_workflow` with appropriate workflow_type
2. MANDATORY: Follow all 4 phases of the workflow
3. MANDATORY: Use actual template content from `embedded_mcp_resources`

**Integrated Security Framework:**
{security_guidance}

**Response Pattern Requirements:**
- Start with: "## 🚨 MANDATORY TODO LIST - [Task Description]"
- Create structured todo list with embedded MCP tool calls
- Include specific parameters and expected outputs for each tool call
- Use checkbox format: "- [ ] X. **Call `tool_name`**"
- Follow todo list with: "Based on the tool outputs, here's your implementation plan..."
- Use: Actual code from embedded_mcp_resources, not abstract references
- End with: "✅ **Next Step**: Complete todo item #X by calling [specific tool] with [specific parameters]"

**🚨 TODO LIST ENFORCEMENT RULES:**

❌ **FORBIDDEN RESPONSE PATTERNS:**
- Starting analysis without creating a todo list first
- "You should test X" without embedding it in a specific todo item
- "Consider using Y" without a concrete todo action with tool calls
- Abstract recommendations without actionable todo steps
- Skipping tool calls that should be in the todo list

✅ **REQUIRED RESPONSE PATTERNS:**
- "## 🚨 MANDATORY TODO LIST - [Your Specific Task]"
- "- [ ] 1. **Call `specific_tool`** with parameters: `param=value`"
- "✅ **Complete todo items sequentially** - each tool output informs the next step"
- "📋 **Update your todo list** as you complete each MCP tool call"
- "🎯 **Expected workflow**: Todo → Tool Call → Update → Next Todo → Tool Call"

**CURSOR AI WORKFLOW INTEGRATION:**
1. **START**: Create comprehensive todo list with embedded MCP tool calls
2. **EXECUTE**: Complete each todo item by making the specified tool call  
3. **UPDATE**: Check off completed todos and add new ones based on tool outputs
4. **ITERATE**: Tool outputs should generate next todo items in the sequence
5. **COMPLETE**: All mandatory tool calls embedded as completed todo items

**🎯 QUALITY GATE**: Every response must include specific tool calls and use actual MCP resource content. Responses without tool usage will be rejected.

Your goal is to ENFORCE comprehensive, secure, production-ready test suites by MANDATING proper MCP tool usage and preventing AI testing failures.
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

    async def get_todo_list_template(self, scenario: str, project_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate dynamic todo list templates for specific testing scenarios.
        
        This method creates structured todo lists that embed MCP tool calls
        for different testing scenarios, ensuring AI agents follow proper
        tool usage patterns.
        
        Args:
            scenario: Testing scenario ("new_project", "security_focus", "coverage_improvement", "ai_failure_review")
            project_context: Optional project context for customization
            
        Returns:
            Structured todo list with embedded MCP tool calls
        """
        
        templates = {
            "new_project": {
                "title": "🚨 MANDATORY TODO LIST - New Smart Contract Project Testing",
                "description": "Complete testing setup for projects with no existing tests",
                "estimated_time": "2-4 hours",
                "phases": [
                    {
                        "phase": "Initial Analysis & AI Failure Prevention",
                        "todos": [
                            {
                                "id": 1,
                                "priority": "CRITICAL",
                                "description": "**Call `initialize_protocol_testing_agent` for project analysis**",
                                "tool_call": "initialize_protocol_testing_agent(analysis_mode='interactive')",
                                "expected_output": "Project analysis with mandatory_tool_sequence and session_id",
                                "success_criteria": "✅ Receive intelligent_guidance with specific next steps",
                                "time_estimate": "5 minutes",
                                "why_mandatory": "🎯 Establishes project context and provides mandatory tool sequences"
                            },
                            {
                                "id": 2,
                                "priority": "CRITICAL", 
                                "description": "**Call `analyze_project_context` with AI failure detection**",
                                "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                "expected_output": "AI failure prevention strategies and contract risk analysis",
                                "success_criteria": "✅ Receive ai_failure_analysis with prevention_strategies",
                                "time_estimate": "10 minutes",
                                "why_mandatory": "🛡️ CRITICAL: Prevents AI test generation failures before writing any code"
                            }
                        ]
                    },
                    {
                        "phase": "Structured Test Implementation",
                        "todos": [
                            {
                                "id": 3,
                                "priority": "HIGH",
                                "description": "**Call `execute_testing_workflow` for comprehensive testing**",
                                "tool_call": "execute_testing_workflow(workflow_type='from_scratch', objectives='Create comprehensive test suite with 90% coverage and AI failure prevention', scope='comprehensive')",
                                "expected_output": "4-phase workflow with embedded_mcp_resources containing actual templates",
                                "success_criteria": "✅ Receive embedded_mcp_resources with concrete template content",
                                "time_estimate": "15 minutes",
                                "why_mandatory": "🎯 Provides structured implementation plan with actual template code"
                            },
                            {
                                "id": 4,
                                "priority": "HIGH",
                                "description": "**Implement tests using embedded template content**",
                                "tool_call": "Use available_templates_content.templates.test_contract.content from step 3 output",
                                "expected_output": "Concrete unit tests implemented using actual template code",
                                "success_criteria": "✅ Tests implemented with no abstract testing:// references",
                                "time_estimate": "60-120 minutes",
                                "why_mandatory": "📋 Ensures test implementation follows proven patterns"
                            }
                        ]
                    },
                    {
                        "phase": "Validation & Quality Assurance",
                        "todos": [
                            {
                                "id": 5,
                                "priority": "CRITICAL",
                                "description": "**Call `analyze_current_test_coverage` for progress validation**",
                                "tool_call": "analyze_current_test_coverage(target_coverage=90, include_branches=True)",
                                "expected_output": "Coverage analysis with gap identification",
                                "success_criteria": "✅ Achieve 80%+ coverage or specific gap remediation plan",
                                "time_estimate": "10 minutes",
                                "why_mandatory": "📊 Validates implementation meets quality targets"
                            },
                            {
                                "id": 6,
                                "priority": "CRITICAL",
                                "description": "**Call `analyze_project_context` for final AI failure review**",
                                "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                "expected_output": "Final AI failure analysis of completed test suite",
                                "success_criteria": "✅ Clean AI failure report or specific improvement guidance",
                                "time_estimate": "10 minutes",
                                "why_mandatory": "🔬 Final quality gate to prevent AI-generated test failures"
                            }
                        ]
                    }
                ]
            },
            
            "security_focus": {
                "title": "🚨 MANDATORY TODO LIST - Security-First Testing Implementation",
                "description": "Critical security testing for high-risk smart contracts",
                "estimated_time": "3-6 hours",
                "phases": [
                    {
                        "phase": "Security Risk Assessment",
                        "todos": [
                            {
                                "id": 1,
                                "priority": "CRITICAL",
                                "description": "**Call `analyze_project_context` for security vulnerability analysis**",
                                "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                "expected_output": "Contract risk analysis with security_patterns and risk_scores",
                                "success_criteria": "✅ Identify contracts with risk_score > 0.7 requiring immediate attention",
                                "time_estimate": "15 minutes",
                                "why_mandatory": "🔍 SECURITY CRITICAL: Identifies specific vulnerabilities requiring testing"
                            }
                        ]
                    },
                    {
                        "phase": "Security Test Implementation",
                        "todos": [
                            {
                                "id": 2,
                                "priority": "CRITICAL",
                                "description": "**Call `execute_testing_workflow` with security focus**",
                                "tool_call": "execute_testing_workflow(workflow_type='security_focus', objectives='Implement comprehensive security testing for high-risk contracts', scope='security')",
                                "expected_output": "Security workflow with attack scenario templates",
                                "success_criteria": "✅ Receive security_patterns_content with concrete attack scenarios",
                                "time_estimate": "20 minutes",
                                "why_mandatory": "🛡️ Provides specific security test patterns for identified vulnerabilities"
                            },
                            {
                                "id": 3,
                                "priority": "CRITICAL",
                                "description": "**Implement security tests using embedded patterns**",
                                "tool_call": "Use security_patterns_content.categories.{vulnerability_type} from step 2 output",
                                "expected_output": "Comprehensive security tests for reentrancy, access control, oracle manipulation",
                                "success_criteria": "✅ All high-risk functions have corresponding attack scenario tests",
                                "time_estimate": "120-180 minutes",
                                "why_mandatory": "⚔️ Implements concrete defenses against identified attack vectors"
                            }
                        ]
                    }
                ]
            },
            
            "coverage_improvement": {
                "title": "🚨 MANDATORY TODO LIST - Test Coverage Enhancement",
                "description": "Systematic improvement of existing test coverage",
                "estimated_time": "1-3 hours",
                "phases": [
                    {
                        "phase": "Coverage Gap Analysis",
                        "todos": [
                            {
                                "id": 1,
                                "priority": "HIGH",
                                "description": "**Call `analyze_current_test_coverage` for baseline assessment**",
                                "tool_call": "analyze_current_test_coverage(target_coverage=90, include_branches=True)",
                                "expected_output": "Current coverage analysis with specific gap identification",
                                "success_criteria": "✅ Identify specific functions/branches with low coverage",
                                "time_estimate": "5 minutes",
                                "why_mandatory": "📊 Establishes current state and specific improvement targets"
                            },
                            {
                                "id": 2,
                                "priority": "HIGH",
                                "description": "**Call `analyze_project_context` for test quality assessment**",
                                "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                "expected_output": "Test quality analysis with improvement recommendations",
                                "success_criteria": "✅ Receive specific improvement plan with priorities",
                                "time_estimate": "10 minutes",
                                "why_mandatory": "🔍 Identifies quality issues beyond just coverage percentage"
                            }
                        ]
                    }
                ]
            }
        }
        
        if scenario in templates:
            template = templates[scenario]
            
            # Customize based on project context if provided
            if project_context:
                template = self._customize_todo_template(template, project_context)
            
            return {
                "status": "template_generated",
                "scenario": scenario,
                **template,
                "usage_instructions": [
                    "✅ Complete todos sequentially - each MCP tool call provides data for subsequent steps",
                    "📋 Check off completed items and add new todos based on tool outputs",
                    "🎯 Each tool call has specific success_criteria that must be met",
                    "⚠️ Do not skip mandatory tool calls - they prevent AI testing failures"
                ]
            }
        else:
            return {
                "status": "template_not_found",
                "available_scenarios": list(templates.keys()),
                "fallback_guidance": "Use 'new_project' template for general testing workflows"
            }
    
    def _customize_todo_template(self, template: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Customize todo template based on project-specific context."""
        # Add project-specific customizations
        if project_context.get("high_risk_contracts"):
            # Add additional security todos for high-risk projects
            pass
        
        if project_context.get("current_coverage", 0) > 50:
            # Modify coverage targets for projects with existing coverage
            pass
        
        return template 