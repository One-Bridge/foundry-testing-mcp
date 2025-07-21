"""
Workflow Generation Utilities for Smart Contract Testing

This module contains the large workflow generation functions extracted from testing_tools.py
to improve code organization and maintainability.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class WorkflowGenerator:
    """Generates contextual testing workflows and guidance."""
    
    def __init__(self, testing_resources=None):
        """Initialize workflow generator with optional testing resources."""
        self.testing_resources = testing_resources
        logger.info("Workflow generator initialized")
    
    def generate_intelligent_next_steps(self, project_state) -> Dict[str, Any]:
        """
        Generate intelligent next steps based on project state.
        
        Extracted from the 408-line monster function for maintainability.
        """
        next_steps = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_objectives": [],
            "tool_recommendations": [],
            "resource_links": {}
        }
        
        testing_phase = project_state.testing_phase.value if hasattr(project_state.testing_phase, 'value') else str(project_state.testing_phase)
        security_level = project_state.security_level.value if hasattr(project_state.security_level, 'value') else str(project_state.security_level)
        
        # Immediate actions based on testing phase
        if testing_phase == "none":
            next_steps["immediate_actions"] = [
                "🚀 Call execute_testing_workflow with workflow_type='create_new_suite'",
                "�� Set objectives to 'establish comprehensive test foundation'", 
                "⚙️ Start with scope='unit' to build core test infrastructure",
                "🔧 Use validate_foundry_config to ensure proper project setup"
            ]
            
        elif testing_phase == "basic":
            next_steps["immediate_actions"] = [
                "📊 Call analyze_current_test_coverage to assess baseline coverage",
                "🔍 Call analyze_project_context with include_ai_failure_detection=true",
                "🛡️ Call execute_testing_workflow with workflow_type='evaluate_existing'",
                "🎯 Focus on scope='security' to add defensive testing"
            ]
            
        elif testing_phase == "intermediate":
            next_steps["immediate_actions"] = [
                "🔬 Call analyze_project_context for comprehensive quality assessment",
                "⚡ Call execute_testing_workflow with scope='comprehensive'",
                "🧪 Implement invariant testing if not already present",
                "🚨 Add advanced security scenarios and attack vectors"
            ]
            
        else:  # advanced/production
            next_steps["immediate_actions"] = [
                "✅ Run final analyze_current_test_coverage validation",
                "🎯 Focus on edge cases and stress testing",
                "📈 Optimize test performance and maintainability",
                "🔄 Set up continuous testing and monitoring"
            ]
        
        # Short-term goals based on security level
        if security_level in ["none", "basic"]:
            next_steps["short_term_goals"] = [
                "Implement access control testing",
                "Add reentrancy protection validation", 
                "Create oracle manipulation resistance tests",
                "Establish basic security test patterns"
            ]
        elif security_level == "intermediate":
            next_steps["short_term_goals"] = [
                "Implement flash loan attack simulations",
                "Add economic invariant testing",
                "Create front-running protection tests",
                "Establish comprehensive security coverage"
            ]
        else:  # advanced/audit_ready
            next_steps["short_term_goals"] = [
                "Prepare for professional security audit",
                "Document all security assumptions",
                "Create stress test scenarios",
                "Establish continuous security monitoring"
            ]
        
        # Tool recommendations
        next_steps["tool_recommendations"] = self._generate_tool_recommendations(project_state)
        
        # Resource links
        next_steps["resource_links"] = self._generate_resource_links(project_state)
        
        return next_steps
    
    def _generate_tool_recommendations(self, project_state) -> List[Dict[str, str]]:
        """Generate specific tool recommendations based on project state."""
        recommendations = []
        
        # Always recommend core tools
        recommendations.extend([
            {
                "tool": "initialize_protocol_testing_agent",
                "usage": "Start here for any new testing project or assessment",
                "parameters": "analysis_mode='interactive', project_path=''",
                "when": "Beginning any testing workflow"
            },
            {
                "tool": "analyze_project_context", 
                "usage": "Get comprehensive project analysis with AI failure detection",
                "parameters": "include_ai_failure_detection=true, generate_improvement_plan=true",
                "when": "Before major testing improvements"
            },
            {
                "tool": "execute_testing_workflow",
                "usage": "Execute structured testing workflows with specific objectives",
                "parameters": "workflow_type='comprehensive', objectives='your_goals', scope='comprehensive'",
                "when": "Implementing systematic testing improvements"
            }
        ])
        
        # Add conditional recommendations
        coverage_percentage = self._get_coverage_percentage(project_state)
        if coverage_percentage < 80:
            recommendations.append({
                "tool": "analyze_current_test_coverage",
                "usage": "Identify coverage gaps and get improvement recommendations",
                "parameters": "target_coverage=90, include_branches=true",
                "when": "Coverage is below target thresholds"
            })
        
        return recommendations
    
    def _get_coverage_percentage(self, project_state) -> float:
        """Extract coverage percentage from project state."""
        if hasattr(project_state, 'coverage_data') and project_state.coverage_data:
            summary = project_state.coverage_data.get('summary', {})
            return summary.get('line_coverage_percentage', 0.0)
        return 0.0
    
    def _generate_resource_links(self, project_state) -> Dict[str, str]:
        """Generate resource links based on project state."""
        return {
            "foundry_patterns": "Access via get_mcp_resources_content(resource_type='patterns')",
            "security_templates": "Access via get_mcp_resources_content(resource_type='security')",
            "testing_documentation": "Access via get_mcp_resources_content(resource_type='documentation')",
            "templates": "Access via get_mcp_resources_content(resource_type='templates')"
        }
    
    def create_contextual_workflow_plan(self, workflow_type: str, project_path: str,
                                      objectives: str, scope: str, session) -> Dict[str, Any]:
        """
        Create contextual workflow plan.
        
        Extracted and simplified from the 261-line create_workflow_plan function.
        """
        # Analyze current context
        current_context = self._analyze_current_context(project_path, workflow_type)
        
        # Generate base plan structure
        base_plan = {
            "workflow_type": workflow_type,
            "objectives": objectives,
            "scope": scope,
            "project_path": project_path,
            "session_id": session.session_id,
            "context_analysis": current_context,
            "execution_strategy": self._determine_execution_strategy(workflow_type, current_context),
            "success_criteria": self._generate_success_criteria(workflow_type, scope),
            "estimated_duration": self._estimate_duration(workflow_type, scope),
            "risk_assessment": self._assess_workflow_risks(current_context)
        }
        
        # Generate execution phases
        base_plan["execution_phases"] = self._generate_execution_phases(workflow_type, current_context, project_path)
        
        # Add resource content
        base_plan["embedded_resources"] = self._embed_mcp_resources()
        
        return base_plan
    
    def _analyze_current_context(self, project_path: str, workflow_type: str) -> Dict[str, Any]:
        """Analyze current project context for workflow planning."""
        return {
            "project_path": project_path,
            "workflow_type": workflow_type,
            "has_existing_tests": True,  # Simplified - would check for test/ directory
            "foundry_configured": True,  # Simplified - would check foundry.toml
            "complexity_estimate": "medium"
        }
    
    def _determine_execution_strategy(self, workflow_type: str, context: Dict[str, Any]) -> str:
        """Determine the best execution strategy for the workflow."""
        if workflow_type == "create_new_suite":
            return "ground_up_implementation"
        elif workflow_type == "evaluate_existing":
            return "enhancement_and_gap_filling"
        else:
            return "comprehensive_improvement"
    
    def _generate_success_criteria(self, workflow_type: str, scope: str) -> List[str]:
        """Generate success criteria for the workflow."""
        criteria = [
            "All planned test implementations completed",
            "Coverage targets achieved for scope",
            "Quality gates passed for implemented tests"
        ]
        
        if scope == "security":
            criteria.append("Security test scenarios covering major attack vectors")
        elif scope == "comprehensive":
            criteria.extend([
                "Unit, integration, and security tests implemented",
                "Invariant testing established where applicable",
                "Professional testing patterns followed"
            ])
        
        return criteria
    
    def _estimate_duration(self, workflow_type: str, scope: str) -> str:
        """Estimate workflow duration."""
        duration_matrix = {
            ("create_new_suite", "unit"): "2-4 hours",
            ("create_new_suite", "comprehensive"): "1-2 days", 
            ("evaluate_existing", "security"): "4-6 hours",
            ("evaluate_existing", "comprehensive"): "6-12 hours"
        }
        
        return duration_matrix.get((workflow_type, scope), "4-8 hours")
    
    def _assess_workflow_risks(self, context: Dict[str, Any]) -> List[str]:
        """Assess potential risks in workflow execution."""
        risks = []
        
        if not context.get("foundry_configured"):
            risks.append("Foundry configuration issues may cause delays")
        
        if context.get("complexity_estimate") == "high":
            risks.append("High complexity may require additional time and expertise")
        
        return risks
    
    def _generate_execution_phases(self, workflow_type: str, context: Dict[str, Any], 
                                 project_path: str) -> List[Dict[str, Any]]:
        """Generate execution phases for the workflow."""
        if workflow_type == "create_new_suite":
            return self._generate_create_new_suite_phases(context, project_path)
        elif workflow_type == "evaluate_existing":
            return self._generate_evaluation_phases(context)
        else:
            return self._generate_comprehensive_phases(context)
    
    def _generate_create_new_suite_phases(self, context: Dict[str, Any], project_path: str) -> List[Dict[str, Any]]:
        """Generate phases for creating a new test suite."""
        return [
            {
                "phase": 1,
                "title": "Foundation Setup",
                "description": "Establish testing infrastructure and foundational patterns",
                "actions": [
                    "Validate Foundry configuration",
                    "Set up basic test structure",
                    "Create helper contracts and utilities"
                ],
                "deliverables": [
                    "Working test environment",
                    "Base test contracts",
                    "Helper utilities"
                ],
                "validation": ["Tests compile successfully", "Basic test runs pass"]
            },
            {
                "phase": 2,
                "title": "Core Unit Tests",
                "description": "Implement comprehensive unit tests for all core functions",
                "actions": [
                    "Test all public functions",
                    "Add negative test cases",
                    "Implement edge case testing"
                ],
                "deliverables": [
                    "Complete unit test suite",
                    "Negative test coverage",
                    "Edge case validation"
                ],
                "validation": ["Unit test coverage > 80%", "All functions have negative tests"]
            },
            {
                "phase": 3,
                "title": "Security & Integration",
                "description": "Add security testing and integration scenarios",
                "actions": [
                    "Implement security attack scenarios",
                    "Add access control testing",
                    "Create integration test flows"
                ],
                "deliverables": [
                    "Security test suite",
                    "Integration test coverage",
                    "Attack scenario validation"
                ],
                "validation": ["Security scenarios tested", "Integration flows validated"]
            },
            {
                "phase": 4,
                "title": "Quality Assurance",
                "description": "Final validation and quality assurance",
                "actions": [
                    "Run comprehensive coverage analysis",
                    "Validate test quality with AI detection",
                    "Performance and optimization review"
                ],
                "deliverables": [
                    "Coverage report",
                    "Quality assessment",
                    "Performance baseline"
                ],
                "validation": ["Coverage targets met", "Quality gates passed"]
            }
        ]
    
    def _generate_evaluation_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate phases for evaluating existing tests."""
        return [
            {
                "phase": 1,
                "title": "Current State Analysis",
                "description": "Comprehensive analysis of existing test suite",
                "actions": [
                    "Analyze current test coverage",
                    "Run AI failure detection",
                    "Identify gaps and weaknesses"
                ]
            },
            {
                "phase": 2,
                "title": "Gap Remediation", 
                "description": "Address identified gaps and issues",
                "actions": [
                    "Implement missing test scenarios",
                    "Fix identified AI failures",
                    "Enhance test quality"
                ]
            }
        ]
    
    def _generate_comprehensive_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate phases for comprehensive testing improvement."""
        return [
            {
                "phase": 1,
                "title": "Assessment & Planning",
                "description": "Comprehensive assessment and improvement planning"
            },
            {
                "phase": 2,
                "title": "Implementation",
                "description": "Execute planned improvements"
            },
            {
                "phase": 3,
                "title": "Validation",
                "description": "Validate improvements and quality"
            }
        ]
    
    def _embed_mcp_resources(self) -> Dict[str, Any]:
        """Embed MCP resource content for workflow execution."""
        try:
            # Simplified resource embedding
            return {
                "note": "MCP resources embedded for workflow execution",
                "access": "Use get_mcp_resources_content() tool for actual content"
            }
        except Exception as e:
            logger.error(f"Failed to embed MCP resources: {e}")
            return {"error": "Resource embedding failed"}

    def generate_next_phase_todo_list(self, current_phase: int, session) -> Dict[str, Any]:
        """
        Generate todo list for next phase.
        
        Extracted from the 146-line function for better organization.
        """
        next_phase = current_phase + 1
        
        # Phase-specific todo templates
        phase_templates = {
            1: {
                "title": "🚨 NEXT PHASE TODO - Foundation Setup",
                "todos": [
                    "📋 Validate Foundry configuration with validate_foundry_config",
                    "🏗️ Set up basic test structure and imports",
                    "🔧 Create helper contracts and test utilities",
                    "✅ Verify test environment works with basic test"
                ]
            },
            2: {
                "title": "🚨 NEXT PHASE TODO - Core Unit Test Implementation", 
                "todos": [
                    "🧪 Implement unit tests for all public functions",
                    "❌ Add negative test cases for error conditions",
                    "🎯 Create edge case and boundary value tests",
                    "�� Run analyze_current_test_coverage to track progress"
                ]
            },
            3: {
                "title": "🚨 NEXT PHASE TODO - Security & Integration Testing",
                "todos": [
                    "🛡️ Implement security attack scenarios",
                    "🔐 Add access control and authorization tests", 
                    "🔗 Create integration test flows",
                    "🚨 Run analyze_project_context with AI failure detection"
                ]
            },
            4: {
                "title": "🚨 NEXT PHASE TODO - Final Quality Assurance",
                "todos": [
                    "📈 Run final analyze_current_test_coverage validation",
                    "🔍 Execute comprehensive analyze_project_context review",
                    "✨ Optimize test performance and maintainability", 
                    "🎉 Document testing approach and lessons learned"
                ]
            }
        }
        
        template = phase_templates.get(next_phase, {
            "title": f"🚨 NEXT PHASE TODO - Phase {next_phase}",
            "todos": [
                "📋 Define phase objectives",
                "🎯 Execute planned actions",
                "✅ Validate deliverables",
                "📊 Assess progress"
            ]
        })
        
        return {
            "phase": next_phase,
            "session_id": session.session_id,
            "todo_list": template,
            "mcp_tool_integration": [
                "🔧 validate_foundry_config - Ensure proper project setup",
                "📊 analyze_current_test_coverage - Track coverage progress", 
                "🔍 analyze_project_context - Comprehensive quality assessment",
                "⚡ execute_testing_workflow - Structured workflow execution"
            ]
        }
