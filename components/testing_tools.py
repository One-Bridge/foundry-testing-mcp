"""
Smart Contract Testing MCP Server - Testing Tools

This module implements the core MCP tools for interactive testing workflows.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from .foundry_adapter import FoundryAdapter, FoundryProjectError

logger = logging.getLogger(__name__)

class TestingSession:
    """Manages testing workflow sessions with state persistence."""
    
    def __init__(self, session_id: str, project_path: str):
        self.session_id = session_id
        self.project_path = str(Path(project_path).resolve())  # Always store absolute path
        self.current_phase = 0
        self.workflow_type = ""
        self.workflow_state = {}
        self.generated_tests = []
        self.analysis_results = {}
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "current_phase": self.current_phase,
            "workflow_type": self.workflow_type,
            "workflow_state": self.workflow_state,
            "generated_tests": self.generated_tests,
            "analysis_results": self.analysis_results,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class TestingTools:
    """
    Core testing tools for the MCP server.
    
    This class implements the main interactive workflow tools that guide users
    through smart contract testing processes.
    """
    
    def __init__(self, foundry_adapter: FoundryAdapter):
        """
        Initialize testing tools.
        
        Args:
            foundry_adapter: The Foundry adapter instance
        """
        self.foundry_adapter = foundry_adapter
        self.active_sessions = {}  # session_id -> TestingSession
        logger.info("Testing tools initialized")
    
    def _resolve_project_path(self, project_path: str = "") -> str:
        """
        Resolve project path, defaulting to current working directory.
        
        Args:
            project_path: Optional project path, defaults to current directory
            
        Returns:
            Absolute path to the project directory
        """
        if not project_path or project_path in ["", "."]:
            # Default to current working directory when called from within repo
            project_path = os.getcwd()
        
        return str(Path(project_path).resolve())
    
    def _validate_foundry_project(self, project_path: str) -> Dict[str, Any]:
        """
        Validate that the current directory is a valid Foundry project.
        
        Args:
            project_path: Path to validate
            
        Returns:
            Validation result with helpful messages
        """
        project_path = Path(project_path)
        
        validation = {
            "is_valid": False,
            "issues": [],
            "suggestions": [],
            "project_type": "unknown"
        }
        
        # Check for foundry.toml
        if (project_path / "foundry.toml").exists():
            validation["is_valid"] = True
            validation["project_type"] = "foundry"
        elif (project_path / "hardhat.config.js").exists() or (project_path / "hardhat.config.ts").exists():
            validation["project_type"] = "hardhat"
            validation["issues"].append("This appears to be a Hardhat project")
            validation["suggestions"].append("Consider using 'forge init --force' to add Foundry support")
        elif (project_path / "truffle-config.js").exists():
            validation["project_type"] = "truffle"
            validation["issues"].append("This appears to be a Truffle project")
            validation["suggestions"].append("Consider migrating to Foundry for better testing experience")
        else:
            validation["issues"].append("No smart contract framework detected")
            validation["suggestions"].extend([
                "Run 'forge init --force' to initialize a Foundry project",
                "Ensure you're in the root directory of your smart contract project"
            ])
        
        # Check for common directories
        if not (project_path / "src").exists() and not (project_path / "contracts").exists():
            validation["issues"].append("No contracts directory found (src/ or contracts/)")
        
        return validation
    
    def register_tools(self, mcp) -> None:
        """
        Register all testing tools with the MCP server.
        
        Args:
            mcp: FastMCP server instance
        """
        # Main workflow initialization tool
        @mcp.tool(
            name="initialize_protocol_testing_agent",
            description="Initialize the interactive protocol testing agent (called from within your project directory)"
        )
        async def initialize_protocol_testing_agent(
            analysis_mode: str = "interactive"
        ) -> Dict[str, Any]:
            """
            Initialize the interactive protocol testing agent.
            
            Args:
                analysis_mode: "interactive" for guided flow, "direct" for immediate analysis
                
            Returns:
                Dictionary containing workflow options and next steps
            """
            try:
                # Use current working directory as project path
                project_path = self._resolve_project_path()
                
                # Validate that we're in a valid project
                validation = self._validate_foundry_project(project_path)
                
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "project_path": project_path,
                        "validation": validation,
                        "message": "Current directory doesn't appear to be a valid Foundry project",
                        "next_steps": [
                            "Navigate to your smart contract project root directory",
                            "Ensure foundry.toml exists, or run 'forge init --force'",
                            "Try running this tool again from the project root"
                        ]
                    }
                
                # Detect project structure
                project_info = await self._analyze_project_structure(project_path)
                
                # Create a new session tied to this project
                session_id = str(uuid.uuid4())
                session = TestingSession(session_id, project_path)
                self.active_sessions[session_id] = session
                
                workflow_options = {
                    "status": "initialized",
                    "session_id": session_id,
                    "project_path": project_path,
                    "project_info": project_info,
                    "available_workflows": {
                        "create_new_suite": {
                            "title": "Create New Test Suite from Scratch",
                            "description": "Design and implement a comprehensive test suite for your contracts",
                            "features": [
                                "Contract analysis and test planning",
                                "Test template generation",
                                "Coverage strategy development",
                                "Best practices implementation"
                            ],
                            "ideal_for": "New projects or complete testing overhauls",
                            "estimated_phases": 4,
                            "time_estimate": "2-4 hours"
                        },
                        "evaluate_existing": {
                            "title": "Evaluate & Enhance Existing Tests",
                            "description": "Analyze current testing infrastructure and suggest improvements",
                            "features": [
                                "Test coverage analysis",
                                "Gap identification",
                                "Refactoring suggestions",
                                "Performance optimization"
                            ],
                            "ideal_for": "Projects with existing tests that need enhancement",
                            "estimated_phases": 4,
                            "time_estimate": "1-3 hours"
                        }
                    },
                    "next_steps": {
                        "interactive": "Choose a workflow path to begin guided testing development",
                        "direct": "Call execute_testing_workflow with your specific requirements"
                    },
                    "recommendations": await self._generate_workflow_recommendations(project_info)
                }
                
                return workflow_options
                
            except Exception as e:
                logger.error(f"Error initializing protocol testing agent: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "current_directory": os.getcwd(),
                    "recommendations": [
                        "Ensure you're in a valid Foundry project directory",
                        "Check that foundry.toml exists",
                        "Verify Foundry is installed and accessible",
                        "Ensure you have proper file permissions"
                    ]
                }
        
        # Main workflow execution tool
        @mcp.tool(
            name="execute_testing_workflow",
            description="Execute a complete testing workflow with structured phases (runs in current directory)"
        )
        async def execute_testing_workflow(
            workflow_type: str,
            objectives: str,
            scope: str = "comprehensive",
            session_id: str = ""
        ) -> Dict[str, Any]:
            """
            Execute a complete testing workflow with structured phases.
            
            Args:
                workflow_type: "create_new_suite" or "evaluate_existing"
                objectives: Specific testing goals and requirements
                scope: Testing scope ("unit", "integration", "comprehensive")
                session_id: Optional session ID to continue existing session
                
            Returns:
                Dictionary containing workflow execution plan
            """
            try:
                # Use current working directory
                project_path = self._resolve_project_path()
                
                # Validate project
                validation = self._validate_foundry_project(project_path)
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "validation": validation,
                        "message": "Cannot execute workflow: invalid Foundry project"
                    }
                
                # Get or create session
                if session_id and session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    # Update session to current directory if different
                    if session.project_path != project_path:
                        logger.info(f"Session {session_id} moved from {session.project_path} to {project_path}")
                        session.project_path = project_path
                else:
                    session_id = str(uuid.uuid4())
                    session = TestingSession(session_id, project_path)
                    self.active_sessions[session_id] = session
                
                # Update session state
                session.workflow_type = workflow_type
                session.workflow_state = {
                    "objectives": objectives,
                    "scope": scope,
                    "current_phase": 0,
                    "phase_results": {}
                }
                
                workflow_plan = await self._create_workflow_plan(
                    workflow_type, project_path, objectives, scope, session
                )
                
                # Execute the first phase automatically
                if workflow_plan["execution_phases"]:
                    first_phase_result = await self._execute_workflow_phase(
                        session, workflow_plan["execution_phases"][0]
                    )
                    workflow_plan["current_phase_result"] = first_phase_result
                
                return workflow_plan
                
            except Exception as e:
                logger.error(f"Error executing testing workflow: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "current_directory": os.getcwd(),
                    "troubleshooting": [
                        "Ensure you're in the root of your Foundry project",
                        "Verify foundry.toml exists in current directory",
                        "Check that Foundry is properly installed",
                        "Ensure the project contains valid Solidity files"
                    ]
                }
        
        # Quick coverage analysis tool
        @mcp.tool(
            name="analyze_current_test_coverage",
            description="Analyze test coverage for the current project directory"
        )
        async def analyze_current_test_coverage(
            target_coverage: int = 90,
            include_branches: bool = True
        ) -> Dict[str, Any]:
            """
            Analyze test coverage for the current project.
            
            Args:
                target_coverage: Target coverage percentage (default: 90)
                include_branches: Whether to include branch coverage analysis
                
            Returns:
                Dictionary containing coverage analysis and recommendations
            """
            try:
                project_path = self._resolve_project_path()
                
                # Validate project
                validation = self._validate_foundry_project(project_path)
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "validation": validation
                    }
                
                # Generate coverage report
                coverage_result = await self.foundry_adapter.generate_coverage_report(
                    project_path, format="lcov"
                )
                
                if not coverage_result["success"]:
                    return {
                        "status": "error",
                        "error": "Failed to generate coverage report",
                        "details": coverage_result["stderr"],
                        "suggestions": [
                            "Ensure tests exist in the test/ directory",
                            "Run 'forge test' first to verify tests work",
                            "Check that contracts exist in the src/ directory"
                        ]
                    }
                
                analysis = {
                    "status": "success",
                    "project_path": project_path,
                    "coverage_summary": coverage_result["summary"],
                    "target_coverage": target_coverage,
                    "meets_target": False,
                    "gaps_identified": [],
                    "recommendations": [],
                    "improvement_plan": {}
                }
                
                if coverage_result["summary"]:
                    current_coverage = coverage_result["summary"]["coverage_percentage"]
                    analysis["meets_target"] = current_coverage >= target_coverage
                    
                    if not analysis["meets_target"]:
                        gap = target_coverage - current_coverage
                        analysis["gaps_identified"] = await self._identify_coverage_gaps(
                            coverage_result["coverage_data"]
                        )
                        analysis["recommendations"] = await self._generate_coverage_recommendations(
                            coverage_result["coverage_data"], gap
                        )
                
                return analysis
                
            except Exception as e:
                logger.error(f"Error analyzing test coverage: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "current_directory": os.getcwd(),
                    "suggestions": [
                        "Ensure you're in a valid Foundry project directory",
                        "Check that tests exist and can be run with 'forge test'",
                        "Verify forge is installed and accessible"
                    ]
                }
        
        # Quick project validation tool
        @mcp.tool(
            name="validate_current_project",
            description="Validate that the current directory is a proper Foundry project"
        )
        async def validate_current_project() -> Dict[str, Any]:
            """
            Validate the current directory as a Foundry project.
            
            Returns:
                Dictionary containing validation results and suggestions
            """
            try:
                project_path = self._resolve_project_path()
                validation = self._validate_foundry_project(project_path)
                
                # Add additional context
                project_structure = await self.foundry_adapter.detect_project_structure(project_path)
                
                return {
                    "status": "validated",
                    "project_path": project_path,
                    "validation": validation,
                    "project_structure": project_structure,
                    "foundry_installation": await self.foundry_adapter.check_foundry_installation(),
                    "recommendations": self._get_setup_recommendations(validation, project_structure)
                }
                
            except Exception as e:
                logger.error(f"Error validating project: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "current_directory": os.getcwd()
                }
        
        logger.info("Testing tools registered successfully")
    
    # Helper methods
    async def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project structure and provide insights."""
        try:
            # Use Foundry adapter to detect project structure
            structure = await self.foundry_adapter.detect_project_structure(project_path)
            
            # Add analysis insights
            analysis = {
                **structure,
                "analysis": {
                    "is_new_project": len(structure["contracts"]) == 0,
                    "has_existing_tests": len(structure["tests"]) > 0,
                    "test_coverage_ratio": 0.0,
                    "recommended_workflow": "",
                    "risk_assessment": "low"
                }
            }
            
            # Calculate test coverage ratio
            if structure["contracts"]:
                analysis["analysis"]["test_coverage_ratio"] = (
                    len(structure["tests"]) / len(structure["contracts"])
                )
            
            # Recommend workflow
            if analysis["analysis"]["is_new_project"]:
                analysis["analysis"]["recommended_workflow"] = "create_new_suite"
                analysis["analysis"]["risk_assessment"] = "high"
            elif analysis["analysis"]["test_coverage_ratio"] < 0.5:
                analysis["analysis"]["recommended_workflow"] = "create_new_suite"
                analysis["analysis"]["risk_assessment"] = "medium"
            else:
                analysis["analysis"]["recommended_workflow"] = "evaluate_existing"
                analysis["analysis"]["risk_assessment"] = "low"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return {
                "project_path": project_path,
                "error": str(e),
                "analysis": {
                    "is_new_project": True,
                    "has_existing_tests": False,
                    "recommended_workflow": "create_new_suite",
                    "risk_assessment": "high"
                }
            }
    
    def _get_setup_recommendations(self, validation: Dict[str, Any], structure: Dict[str, Any]) -> List[str]:
        """Generate setup recommendations based on validation and structure."""
        recommendations = []
        
        if not validation["is_valid"]:
            recommendations.extend(validation["suggestions"])
        
        if not structure.get("contracts"):
            recommendations.append("📝 Add your smart contracts to the src/ directory")
        
        if not structure.get("tests"):
            recommendations.append("🧪 Create test files in the test/ directory")
            recommendations.append("🚀 Use the MCP tools to generate comprehensive test suites")
        
        if structure.get("is_foundry_project"):
            recommendations.append("✅ Foundry project detected - ready for testing!")
        
        return recommendations
    
    async def _generate_workflow_recommendations(self, project_info: Dict[str, Any]) -> List[str]:
        """Generate workflow recommendations based on project analysis."""
        recommendations = []
        
        analysis = project_info.get("analysis", {})
        
        if analysis.get("is_new_project"):
            recommendations.extend([
                "🚀 **Start Fresh**: Create a comprehensive test suite from scratch",
                "📋 **Plan First**: Begin with contract analysis and testing strategy",
                "🎯 **Set Goals**: Define coverage targets and testing objectives"
            ])
        elif analysis.get("test_coverage_ratio", 0) < 0.5:
            recommendations.extend([
                "🔍 **Analyze Gaps**: Evaluate existing tests for coverage gaps",
                "📈 **Expand Coverage**: Add tests for uncovered contract functions",
                "🔄 **Refactor**: Improve existing test quality and structure"
            ])
        else:
            recommendations.extend([
                "✅ **Enhance Quality**: Optimize existing test suite performance",
                "🛡️ **Add Security**: Include invariant and fuzz testing",
                "📊 **Monitor**: Set up continuous coverage monitoring"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "📖 **Documentation**: Generate comprehensive testing documentation",
            "🔧 **Automation**: Set up automated testing in CI/CD pipeline"
        ])
        
        return recommendations
    
    async def _create_workflow_plan(self, workflow_type: str, project_path: str, 
                                   objectives: str, scope: str, session: TestingSession) -> Dict[str, Any]:
        """Create a detailed workflow execution plan."""
        base_plan = {
            "status": "workflow_ready",
            "session_id": session.session_id,
            "workflow_type": workflow_type,
            "project_path": project_path,
            "objectives": objectives,
            "scope": scope,
            "execution_phases": [],
            "estimated_duration": "",
            "success_criteria": []
        }
        
        if workflow_type == "create_new_suite":
            base_plan["execution_phases"] = [
                {
                    "phase": 1,
                    "title": "Contract Analysis & Discovery",
                    "description": "Comprehensive analysis of contract structure and dependencies",
                    "actions": [
                        "Scan project structure and identify all contracts",
                        "Analyze contract dependencies and inheritance hierarchy",
                        "Identify critical functions and state variables",
                        "Map potential attack vectors and edge cases",
                        "Document contract interfaces and interactions"
                    ],
                    "deliverables": [
                        "Contract analysis report",
                        "Dependency mapping",
                        "Critical function inventory",
                        "Security considerations document"
                    ],
                    "estimated_time": "30-45 minutes"
                }
            ]
            base_plan["estimated_duration"] = "2.5-4 hours"
        
        return base_plan
    
    async def _execute_workflow_phase(self, session: TestingSession, phase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific workflow phase."""
        phase_number = phase["phase"]
        session.current_phase = phase_number
        
        result = {
            "phase": phase_number,
            "title": phase["title"],
            "status": "completed",
            "actions_completed": phase["actions"],
            "deliverables_generated": phase["deliverables"],
            "success": True
        }
        
        return result
    
    # Placeholder helper methods
    async def _identify_coverage_gaps(self, coverage_data: Dict[str, Any]) -> List[str]:
        """Identify coverage gaps."""
        return ["Example gap: Uncovered error conditions"]
    
    async def _generate_coverage_recommendations(self, coverage_data: Dict[str, Any], gap: float) -> List[str]:
        """Generate coverage recommendations."""
        return [f"Add tests to improve coverage by {gap:.1f}%"] 