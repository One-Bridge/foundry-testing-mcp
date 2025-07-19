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
from .project_analyzer import ProjectAnalyzer, ProjectState
from .ai_failure_detector import AIFailureDetector

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
        self.project_analyzer = ProjectAnalyzer(foundry_adapter)
        self.ai_failure_detector = AIFailureDetector()
        self.active_sessions = {}  # session_id -> TestingSession
        logger.info("Testing tools initialized with context analysis and AI failure detection")
    
    def _resolve_project_path(self, project_path: str = "") -> str:
        """
        Simple project path resolution - uses current directory or explicit path.
        
        Args:
            project_path: Optional explicit project path
            
        Returns:
            Absolute path to the project directory
        """
        # If explicit path provided, use it
        if project_path and project_path not in ["", "."]:
            resolved_path = str(Path(project_path).resolve())
            logger.debug(f"Using explicit project path: {resolved_path}")
            return resolved_path
        
        # Check for MCP_CLIENT_CWD (set by MCP client)
        mcp_client_cwd = os.getenv("MCP_CLIENT_CWD")
        if mcp_client_cwd:
            resolved_path = str(Path(mcp_client_cwd).resolve())
            logger.debug(f"Using MCP client directory: {resolved_path}")
            return resolved_path
        
        # Use current working directory
        resolved_path = str(Path.cwd().resolve())
        logger.debug(f"Using current working directory: {resolved_path}")
        return resolved_path
    
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
            mcp: The FastMCP server instance
        """
        logger.info("Registering testing tools...")
        # Main workflow initialization tool
        @mcp.tool(
            name="initialize_protocol_testing_agent",
            description="""
            🚀 STEP 1: Initialize smart contract testing workflow - START HERE for any testing project
            
            WHEN TO USE:
            - Beginning work on a Foundry project (new or existing)
            - User wants to start testing or improve existing tests
            - First interaction with any smart contract project
            - When you need to understand project structure and recommend next steps
            
            WHAT IT DOES:
            - Analyzes current project structure and testing maturity
            - Validates Foundry project setup
            - Recommends appropriate workflow (new test suite vs enhance existing)
            - Creates testing session for workflow continuity
            - Provides specific next steps based on project state
            
            INPUTS:
            - analysis_mode: "interactive" (guided) or "direct" (immediate analysis)
            - project_path: Optional path to project directory (auto-detects if not provided)
            
            OUTPUTS:
            - Project structure analysis
            - Available workflow options with detailed descriptions
            - Specific recommendations based on current state
            - Session ID for continuing work
            
            WORKFLOW: This is always the FIRST tool to call. Based on results, use execute_testing_workflow or analyze_project_context next.
            """
        )
        async def initialize_protocol_testing_agent(
            analysis_mode: str = "interactive",
            project_path: str = ""
        ) -> Dict[str, Any]:
            """
            Initialize the interactive protocol testing agent.
            
            Args:
                analysis_mode: "interactive" for guided flow, "direct" for immediate analysis
                
            Returns:
                Dictionary containing workflow options and next steps
            """
            try:
                # Use provided project path or detect current working directory
                resolved_project_path = self._resolve_project_path(project_path)
                
                # Validate that we're in a valid project
                validation = self._validate_foundry_project(resolved_project_path)
                
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "project_path": resolved_project_path,
                        "validation": validation,
                        "message": "Current directory doesn't appear to be a valid Foundry project",
                        "next_steps": [
                            "Navigate to your smart contract project root directory",
                            "Ensure foundry.toml exists, or run 'forge init --force'",
                            "Try running this tool again from the project root"
                        ]
                    }
                
                # Detect project structure
                project_info = await self._analyze_project_structure(resolved_project_path)
                
                # Create a new session tied to this project
                session_id = str(uuid.uuid4())
                session = TestingSession(session_id, resolved_project_path)
                self.active_sessions[session_id] = session
                
                # Generate contextual workflow options based on current state
                available_workflows = await self._generate_contextual_workflows(project_info)
                
                workflow_options = {
                    "status": "initialized",
                    "session_id": session_id,
                    "project_path": resolved_project_path,
                    "project_info": project_info,
                    "available_workflows": available_workflows,
                    "current_state_summary": {
                        "testing_phase": project_info.get("testing_phase", "unknown"),
                        "test_count": project_info.get("test_count", 0),
                        "coverage_estimate": project_info.get("coverage_estimate", 0),
                        "identified_patterns": project_info.get("identified_patterns", [])
                    },
                    "next_steps": {
                        "interactive": "Choose a workflow path tailored to your current testing maturity",
                        "direct": "Call execute_testing_workflow with specific objectives based on your current state"
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
        
        # Context-aware project analysis tool
        @mcp.tool(
            name="analyze_project_context",
            description="""
            🔍 STEP 2: Deep project analysis with AI failure detection - Use for detailed assessment
            
            WHEN TO USE:
            - After initialize_protocol_testing_agent suggests detailed analysis
            - User has existing tests and wants quality assessment
            - Debugging test quality issues or low coverage
            - Before major testing improvements
            - When tests seem comprehensive but aren't working well
            
            WHAT IT DOES:
            - Analyzes current testing phase (none/basic/intermediate/advanced/production)
            - Evaluates security testing maturity level
            - Detects AI-generated test failures (circular logic, mock cheating, etc.)
            - Assesses contract risk scores and security patterns
            - Generates prioritized improvement plan with effort estimates
            
            INPUTS:
            - include_ai_failure_detection: true (recommended) - detects problematic AI-generated tests
            - generate_improvement_plan: true (recommended) - creates actionable improvement roadmap
            - project_path: Optional path to project directory (auto-detects if not provided)
            
            OUTPUTS:
            - Current testing phase and security level assessment
            - AI failure detection report (critical for AI-generated code)
            - Contract risk analysis with security patterns
            - Comprehensive improvement plan with priorities and timelines
            
            WORKFLOW: Use after initialize_protocol_testing_agent. Results guide execute_testing_workflow parameters.
            """
        )
        async def analyze_project_context(
            include_ai_failure_detection: bool = True,
            generate_improvement_plan: bool = True,
            project_path: str = ""
        ) -> Dict[str, Any]:
            """
            Perform comprehensive context-aware analysis of the current project.
            
            Args:
                include_ai_failure_detection: Whether to analyze tests for AI failures
                generate_improvement_plan: Whether to generate improvement recommendations
                
            Returns:
                Dictionary containing comprehensive project analysis
            """
            try:
                resolved_project_path = self._resolve_project_path(project_path)
                
                # Validate project
                validation = self._validate_foundry_project(resolved_project_path)
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "validation": validation,
                        "message": "Cannot analyze project: invalid Foundry project"
                    }
                
                # Perform comprehensive project analysis
                project_state = await self.project_analyzer.analyze_project(resolved_project_path)
                
                analysis_result = {
                    "status": "success",
                    "project_path": resolved_project_path,
                    "project_analysis": {
                        "project_type": project_state.project_type,
                        "testing_phase": project_state.testing_phase.value,
                        "security_level": project_state.security_level.value,
                        "contracts_analyzed": len(project_state.contracts),
                        "test_files_analyzed": len(project_state.test_files),
                        "total_tests": sum(tf.test_count for tf in project_state.test_files),
                        "coverage_data": project_state.coverage_data,
                        "identified_gaps": project_state.identified_gaps,
                        "recommendations": project_state.next_recommendations
                    },
                    "contract_analysis": [
                        {
                            "name": contract.contract_name,
                            "type": contract.contract_type,
                            "risk_score": contract.risk_score,
                            "security_patterns": contract.security_patterns,
                            "function_count": len(contract.functions)
                        }
                        for contract in project_state.contracts
                    ],
                    "test_analysis": [
                        {
                            "file": tf.path,
                            "test_count": tf.test_count,
                            "patterns": tf.test_patterns,
                            "uses_fuzzing": tf.uses_fuzzing,
                            "uses_invariants": tf.uses_invariants,
                            "uses_mocks": tf.uses_mocks,
                            "complexity_score": tf.complexity_score
                        }
                        for tf in project_state.test_files
                    ]
                }
                
                # AI failure detection
                if include_ai_failure_detection and project_state.test_files:
                    ai_failures = []
                    for test_file in project_state.test_files:
                        try:
                            with open(test_file.path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            failures = await self.ai_failure_detector.analyze_test_file(
                                test_file.path, content
                            )
                            ai_failures.extend(failures)
                        except Exception as e:
                            logger.warning(f"Could not analyze {test_file.path} for AI failures: {e}")
                    
                    # Generate failure report
                    failure_report = await self.ai_failure_detector.generate_failure_report(ai_failures)
                    analysis_result["ai_failure_analysis"] = failure_report
                
                # Generate improvement plan
                if generate_improvement_plan:
                    improvement_plan = await self._generate_comprehensive_improvement_plan(
                        project_state,
                        analysis_result.get("ai_failure_analysis", {})
                    )
                    analysis_result["improvement_plan"] = improvement_plan
                
                return analysis_result
                
            except Exception as e:
                logger.error(f"Error analyzing project context: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "current_directory": os.getcwd(),
                    "troubleshooting": [
                        "Ensure you're in the root of your Foundry project",
                        "Verify foundry.toml exists in current directory",
                        "Check that contracts and tests are properly structured"
                    ]
                }
        
        # Main workflow execution tool
        @mcp.tool(
            name="execute_testing_workflow",
            description="""
            ⚡ STEP 3: Execute structured testing workflow - Main implementation tool
            
            WHEN TO USE:
            - After initialize_protocol_testing_agent provides workflow recommendations
            - User wants to implement comprehensive testing strategy
            - Creating new test suite from scratch
            - Enhancing existing test infrastructure
            - Following specific testing objectives
            
            WHAT IT DOES:
            - Executes context-aware, multi-phase testing workflows
            - Adapts to current project state (doesn't restart from scratch if tests exist)
            - Provides phase-by-phase guidance with specific deliverables
            - Integrates security best practices and professional methodologies
            - Tracks progress through testing maturity levels
            
            INPUTS:
            - workflow_type: "create_new_suite" (new projects), "evaluate_existing" (enhance), "comprehensive" (full scope)
            - objectives: Specific testing goals (e.g., "achieve 90% coverage with security testing")
            - scope: "unit", "integration", "comprehensive" (recommended), "security"
            - session_id: From initialize_protocol_testing_agent (maintains context)
            - project_path: Optional path to project directory (auto-detects if not provided)
            
            OUTPUTS:
            - Detailed execution plan with 4 structured phases
            - Phase-specific actions and deliverables
            - Success criteria and validation metrics
            - Current phase execution results
            
            WORKFLOW: Use after initialize_protocol_testing_agent. Optionally run analyze_project_context first for detailed planning.
            """
        )
        async def execute_testing_workflow(
            workflow_type: str,
            objectives: str,
            scope: str = "comprehensive",
            session_id: str = "",
            project_path: str = ""
        ) -> Dict[str, Any]:
            """
            Execute a complete testing workflow with structured phases.
            
            Args:
                workflow_type: "create_new_suite", "comprehensive", or "evaluate_existing"
                objectives: Specific testing goals and requirements
                scope: Testing scope ("unit", "integration", "comprehensive")
                session_id: Optional session ID to continue existing session
                
            Returns:
                Dictionary containing workflow execution plan with detailed phases
            """
            try:
                # Use provided project path or detect current working directory
                resolved_project_path = self._resolve_project_path(project_path)
                
                # Validate project
                validation = self._validate_foundry_project(resolved_project_path)
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
                    if session.project_path != resolved_project_path:
                        logger.info(f"Session {session_id} moved from {session.project_path} to {resolved_project_path}")
                        session.project_path = resolved_project_path
                else:
                    session_id = str(uuid.uuid4())
                    session = TestingSession(session_id, resolved_project_path)
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
                    workflow_type, resolved_project_path, objectives, scope, session
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
            description="""
            📊 Coverage analysis and gap identification - Use for quick coverage assessment
            
            WHEN TO USE:
            - User asks about test coverage percentages
            - Checking if coverage meets targets before deployment
            - Identifying specific areas needing more tests
            - Monitoring progress during test development
            - Quick health check of existing test suite
            
            WHAT IT DOES:
            - Runs Foundry coverage analysis on current project
            - Calculates line, branch, and function coverage percentages
            - Identifies uncovered code paths and gaps
            - Compares against target coverage goals
            - Provides specific recommendations for improvement
            
            INPUTS:
            - target_coverage: Target percentage (default 90) - use 80 for basic, 95 for production
            - include_branches: true (recommended) for comprehensive branch coverage analysis
            
            OUTPUTS:
            - Current coverage percentages (line, branch, function)
            - Gap analysis with specific uncovered areas
            - Recommendations for reaching target coverage
            - Pass/fail against target coverage goals
            
            WORKFLOW: Use standalone for quick checks, or after execute_testing_workflow to validate progress.
            
            REQUIREMENTS: Project must have existing tests that can run with 'forge test'
            """
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
        
        # Simple project validation tool
        @mcp.tool(
            name="validate_current_directory",
            description="""
            ✅ Validate current directory as a Foundry project
            
            WHEN TO USE:
            - Check if current directory is a valid Foundry project
            - Troubleshoot project setup issues
            - Verify before running other tools
            
            WHAT IT DOES:
            - Checks for foundry.toml, src/, and test/ directories
            - Validates Foundry installation
            - Provides clear setup guidance if invalid
            
            OUTPUTS:
            - Simple pass/fail validation
            - Clear error messages and next steps
            """
        )
        async def validate_current_directory() -> Dict[str, Any]:
            """
            Validate the current directory as a Foundry project.
            
            Returns:
                Dictionary containing validation results
            """
            try:
                project_path = self._resolve_project_path()
                validation = self._validate_foundry_project(project_path)
                
                if validation["is_valid"]:
                    # Get basic project info
                    project_structure = await self.foundry_adapter.detect_project_structure(project_path)
                    
                    return {
                        "status": "valid",
                        "project_path": project_path,
                        "message": "✅ Valid Foundry project detected",
                        "contracts": len(project_structure.get("contracts", [])),
                        "tests": len(project_structure.get("tests", [])),
                        "ready_for_testing": True
                    }
                else:
                    return {
                        "status": "invalid",
                        "project_path": project_path,
                        "message": "❌ Not a valid Foundry project",
                        "issues": validation["issues"],
                        "suggestions": validation["suggestions"],
                        "ready_for_testing": False
                    }
                    
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Error validating directory"
                }
        
        # Directory detection debugging tool
        @mcp.tool(
            name="debug_directory_detection",
            description="""
            🐛 Advanced troubleshooting for directory/path issues - Use when MCP can't find project
            
            WHEN TO USE:
            - MCP tools report working in wrong directory (like home directory)
            - Tools can't find contracts or foundry.toml despite them existing
            - Getting "directory detection may be incorrect" warnings
            - MCP client and server seem to be in different directories
            - Environment variable or working directory issues
            
            WHAT IT DOES:
            - Analyzes directory detection logic and environment variables
            - Shows resolved paths vs actual working directories
            - Identifies MCP client/server directory mismatches
            - Provides specific configuration fixes for MCP clients
            - Generates troubleshooting guidance with examples
            
            INPUTS:
            - None required (analyzes current environment)
            
            OUTPUTS:
            - Directory detection analysis and accuracy assessment
            - Environment variable inspection (MCP_CLIENT_CWD, etc.)
            - Path resolution debugging information
            - Specific MCP client configuration examples
            - Step-by-step troubleshooting instructions
            
            WORKFLOW: Use when validate_current_project or other tools report wrong directory.
            
            FIXES: MCP client configuration, environment variables, working directory issues
            """
        )
        async def debug_directory_detection() -> Dict[str, Any]:
            """
            Debug directory detection and provide troubleshooting guidance.
            
            Returns:
                Dictionary containing directory detection analysis and troubleshooting tips
            """
            try:
                # Get current directory detection
                resolved_path = self._resolve_project_path()
                
                # Collect debugging information
                debug_info = {
                    "resolved_project_path": resolved_path,
                    "server_cwd": os.getcwd(),
                    "environment_variables": {
                        "MCP_CLIENT_CWD": os.getenv("MCP_CLIENT_CWD"),
                        "MCP_PROJECT_PATH": os.getenv("MCP_PROJECT_PATH"),
                        "PWD": os.getenv("PWD"),
                        "OLDPWD": os.getenv("OLDPWD")
                    },
                    "path_analysis": {
                        "is_home_directory": resolved_path == os.path.expanduser("~"),
                        "is_parent_of_home": resolved_path in os.path.expanduser("~"),
                        "contains_foundry_toml": (Path(resolved_path) / "foundry.toml").exists(),
                        "contains_src_dir": (Path(resolved_path) / "src").exists(),
                        "contains_test_dir": (Path(resolved_path) / "test").exists()
                    }
                }
                
                # Determine if directory detection is likely correct
                likely_correct = (
                    debug_info["path_analysis"]["contains_foundry_toml"] or
                    (debug_info["path_analysis"]["contains_src_dir"] and 
                     debug_info["path_analysis"]["contains_test_dir"])
                )
                
                # Generate troubleshooting recommendations
                recommendations = []
                
                if not likely_correct:
                    recommendations.extend([
                        "❌ Directory detection appears incorrect",
                        "🔍 The detected directory doesn't look like a Foundry project",
                        "",
                        "💡 Solutions:",
                        "1. Set MCP_CLIENT_CWD environment variable to your project directory",
                        "2. Set MCP_PROJECT_PATH environment variable to your project directory",
                        "3. Configure your MCP client to set the working directory",
                        "4. Pass the project path explicitly to MCP tools",
                        "",
                        "📋 Example MCP client configuration:",
                        "```",
                        "servers:",
                        "  foundry-testing:",
                        "    command: python",
                        "    args: ['/path/to/run_clean.py']",
                        "    cwd: /path/to/your/project",
                        "    env:",
                        "      MCP_CLIENT_CWD: /path/to/your/project",
                        "```"
                    ])
                else:
                    recommendations.extend([
                        "✅ Directory detection appears correct",
                        "🎯 The detected directory looks like a valid Foundry project"
                    ])
                
                return {
                    "status": "debug_complete",
                    "directory_detection_correct": likely_correct,
                    "debug_info": debug_info,
                    "recommendations": recommendations
                }
                
            except Exception as e:
                logger.error(f"Error debugging directory detection: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "recommendations": [
                        "❌ Error occurred during directory detection debugging",
                        "🔍 Check server logs for more details",
                        "💡 Try setting MCP_CLIENT_CWD environment variable"
                    ]
                }
        
        # Project discovery tool for AI agents
        @mcp.tool(
            name="discover_foundry_projects",
            description="""
            🔍 Project discovery for AI agents - Find available Foundry projects automatically
            
            WHEN TO USE:
            - AI agent needs to find available Foundry projects
            - Auto-detection is failing and need to see project options
            - Want to switch between multiple projects
            - Initial exploration of user's project structure
            
            WHAT IT DOES:
            - Scans common directories for Foundry projects
            - Returns list of discovered projects with metadata
            - Helps AI agents choose the correct project path
            - Provides project summary information
            
            INPUTS:
            - None required (automatic discovery)
            
            OUTPUTS:
            - List of discovered Foundry projects
            - Project metadata (name, contracts, tests)
            - Recommended project paths for other tools
            
            WORKFLOW: Use when auto-detection fails or when exploring available projects.
            """
        )
        async def discover_foundry_projects() -> Dict[str, Any]:
            """
            Discover available Foundry projects for AI agents.
            
            Returns:
                Dictionary containing discovered projects and guidance
            """
            try:
                # This tool is now deprecated as project discovery is handled by initialize_protocol_testing_agent
                # and the project_path parameter.
                # For now, we'll return a placeholder message.
                return {
                    "status": "deprecated",
                    "message": "Project discovery is now handled within initialize_protocol_testing_agent. "
                               "Use that tool to specify a project path.",
                    "recommended_command": "initialize_protocol_testing_agent(project_path=\"/path/to/your/project\")"
                }
                
            except Exception as e:
                logger.error(f"Error discovering projects: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "fallback_guidance": [
                        "Use explicit project paths in tool calls",
                        "Ensure you're in a Foundry project directory",
                        "Check that foundry.toml exists in your project"
                    ]
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
        """
        Create a contextual workflow execution plan that builds on existing work.
        
        This addresses the workflow rigidity issue by analyzing current state
        and providing progressive guidance rather than generic phase templates.
        """
        # Analyze current project state for contextual planning
        try:
            project_state = await self.project_analyzer.analyze_project(project_path)
            current_context = {
                "testing_phase": project_state.testing_phase.value,
                "security_level": project_state.security_level.value,
                "test_count": sum(tf.test_count for tf in project_state.test_files),
                "coverage_pct": project_state.coverage_data.get("coverage_percentage", 0),
                "has_security_tests": any(tf.security_tests for tf in project_state.test_files),
                "contract_types": list(set(c.contract_type for c in project_state.contracts))
            }
        except Exception as e:
            logger.warning(f"Could not analyze project state: {e}")
            current_context = {}
        
        base_plan = {
            "status": "workflow_ready",
            "session_id": session.session_id,
            "workflow_type": workflow_type,
            "project_path": project_path,
            "objectives": objectives,
            "scope": scope,
            "current_context": current_context,
            "execution_phases": [],
            "success_criteria": []
        }
        
        # Generate contextual phases based on workflow type and current state
        if workflow_type == "enhance_security_testing":
            base_plan["execution_phases"] = await self._generate_security_focused_phases(current_context)
            base_plan["success_criteria"] = [
                "All security vulnerability patterns tested",
                "Attack vector simulations implemented",
                "Fuzz testing coverage for critical functions",
                "Invariant testing for system properties",
                "Integration security scenarios validated"
            ]
            
        elif workflow_type == "expand_test_coverage":
            base_plan["execution_phases"] = await self._generate_coverage_expansion_phases(current_context)
            base_plan["success_criteria"] = [
                f"Test coverage increased to 80%+ (current: {current_context.get('coverage_pct', 0):.1f}%)",
                "Edge cases and error conditions covered",
                "Mock implementations for external dependencies",
                "Integration testing for contract interactions"
            ]
            
        elif workflow_type == "defi_security_testing":
            base_plan["execution_phases"] = await self._generate_defi_security_phases(current_context)
            base_plan["success_criteria"] = [
                "Flash loan attack resistance validated",
                "Oracle manipulation protection tested",
                "MEV protection mechanisms verified",
                "Economic attack scenarios covered",
                "Liquidity and slippage testing complete"
            ]
            
        elif workflow_type == "integration_testing_focus":
            base_plan["execution_phases"] = await self._generate_integration_phases(current_context)
            base_plan["success_criteria"] = [
                "All contract interactions tested",
                "User journey workflows validated",
                "State consistency across contracts verified",
                "Performance and gas optimization validated"
            ]
            
        elif workflow_type == "comprehensive_audit_prep":
            base_plan["execution_phases"] = await self._generate_audit_prep_phases(current_context)
            base_plan["success_criteria"] = [
                "95%+ line coverage with 90%+ branch coverage",
                "Comprehensive security testing complete",
                "Formal verification ready",
                "Audit documentation packages prepared",
                "Professional standards compliance verified"
            ]
            
        elif workflow_type == "evaluate_existing":
            base_plan["execution_phases"] = [
                {
                    "phase": 1,
                    "title": "Existing Test Analysis",
                    "description": "Comprehensive evaluation of current testing infrastructure",
                    "actions": [
                        "Analyze existing test file structure and organization",
                        "Evaluate test coverage metrics and gaps",
                        "Review test quality and best practices adherence",
                        "Identify performance bottlenecks",
                        "Assess security testing completeness"
                    ],
                    "deliverables": [
                        "Current test analysis report",
                        "Coverage gap identification",
                        "Quality assessment results",
                        "Performance analysis",
                        "Security testing audit"
                    ]
                },
                {
                    "phase": 2,
                    "title": "Enhancement Strategy Design", 
                    "description": "Design strategy for improving existing tests",
                    "actions": [
                        "Prioritize testing gaps by criticality",
                        "Design refactoring strategy for existing tests",
                        "Plan additional test categories needed",
                        "Create enhancement roadmap with timelines",
                        "Define improved coverage targets"
                    ],
                    "deliverables": [
                        "Enhancement strategy document",
                        "Prioritized improvement plan",
                        "Refactoring roadmap",
                        "Updated coverage targets",
                        "Implementation timeline"
                    ]
                },
                {
                    "phase": 3,
                    "title": "Test Enhancement Implementation",
                    "description": "Implement improvements and fill identified gaps",
                    "actions": [
                        "Refactor existing tests for better organization",
                        "Add missing unit and integration tests",
                        "Implement security and edge case testing",
                        "Add performance and gas optimization tests",
                        "Enhance test documentation and comments"
                    ],
                    "deliverables": [
                        "Refactored test suite",
                        "Additional test implementations",
                        "Enhanced security testing",
                        "Performance test additions",
                        "Improved documentation"
                    ]
                },
                {
                    "phase": 4,
                    "title": "Validation & Final Optimization",
                    "description": "Validate improvements and optimize final test suite",
                    "actions": [
                        "Run comprehensive coverage validation",
                        "Performance test and optimize test execution",
                        "Validate security test effectiveness",
                        "Generate final documentation",
                        "Setup maintenance and monitoring"
                    ],
                    "deliverables": [
                        "Final coverage validation report",
                        "Performance optimization results",
                        "Security validation results",
                        "Complete documentation update",
                        "Monitoring and maintenance setup"
                    ]
                }
            ]
            base_plan["success_criteria"] = [
                "Coverage improved by 20%+ from baseline",
                "All identified critical gaps addressed",
                "Test execution performance optimized",
                "Security testing comprehensive",
                "Documentation updated and complete",
                "Monitoring system functional"
            ]
        
        else:
            # Fallback for legacy or unrecognized workflow types
            base_plan["execution_phases"] = await self._generate_contextual_phases(workflow_type, current_context)
            base_plan["success_criteria"] = [
                "Workflow objectives achieved",
                "Testing implementation complete",
                "Quality standards met"
            ]
        
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
    
    async def _generate_contextual_workflows(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate context-aware workflow options based on current project state.
        
        This addresses workflow rigidity by providing specific, targeted workflows
        rather than generic options that ignore existing progress.
        """
        analysis = project_info.get("analysis", {})
        test_count = len(project_info.get("tests", []))
        contract_count = len(project_info.get("contracts", []))
        has_tests = test_count > 0
        coverage_ratio = analysis.get("test_coverage_ratio", 0)
        
        workflows = {}
        
        # Determine primary workflow based on current state
        if not has_tests:
            # No existing tests - foundational workflows
            workflows["create_foundational_suite"] = {
                "title": "Create Foundational Test Suite",
                "description": "Establish comprehensive testing infrastructure from scratch",
                "features": [
                    "Contract analysis and risk assessment", 
                    "Test architecture design",
                    "Core unit test implementation",
                    "Coverage monitoring setup"
                ],
                "ideal_for": "Projects with no existing tests",
                "phases": 3,
                "estimated_effort": "1-2 weeks"
            }
            
        elif test_count < 10 or coverage_ratio < 0.5:
            # Basic tests exist - enhancement workflows
            workflows["expand_test_coverage"] = {
                "title": "Expand Test Coverage & Quality",
                "description": "Build on existing tests to achieve comprehensive coverage",
                "features": [
                    "Gap analysis of existing tests",
                    "Edge case and error condition testing",
                    "Mock implementation and integration tests",
                    "Security testing foundation"
                ],
                "ideal_for": "Projects with basic tests needing expansion",
                "phases": 3,
                "estimated_effort": "1 week"
            }
            
        else:
            # Good test foundation - advanced workflows
            workflows["enhance_security_testing"] = {
                "title": "Advanced Security & Integration Testing",
                "description": "Add sophisticated security testing and integration scenarios",
                "features": [
                    "Security vulnerability testing",
                    "Fuzz testing implementation", 
                    "Invariant and property-based testing",
                    "Integration and cross-contract testing"
                ],
                "ideal_for": "Projects with solid test foundation needing security focus",
                "phases": 4,
                "estimated_effort": "1-2 weeks"
            }
        
        # Add specialized workflows based on contract types
        if contract_count > 1:
            workflows["integration_testing_focus"] = {
                "title": "Multi-Contract Integration Testing",
                "description": "Comprehensive testing for contract interactions and workflows",
                "features": [
                    "Cross-contract interaction testing",
                    "User journey and workflow testing",
                    "State consistency validation",
                    "Performance and gas optimization"
                ],
                "ideal_for": "Multi-contract systems needing integration validation",
                "phases": 3,
                "estimated_effort": "1 week"
            }
        
        # Add DeFi-specific workflows if applicable
        if any("defi" in str(contract).lower() for contract in project_info.get("contracts", [])):
            workflows["defi_security_testing"] = {
                "title": "DeFi Protocol Security Testing",
                "description": "Specialized testing for DeFi-specific vulnerabilities and scenarios",
                "features": [
                    "Flash loan attack simulation",
                    "Oracle manipulation testing",
                    "MEV protection validation",
                    "Economic attack scenarios"
                ],
                "ideal_for": "DeFi protocols requiring specialized security testing",
                "phases": 4,
                "estimated_effort": "2-3 weeks"
            }
        
        # Always offer comprehensive workflow for advanced users
        workflows["comprehensive_audit_prep"] = {
            "title": "Comprehensive Audit Preparation",
            "description": "Complete testing suite preparation for professional security audits",
            "features": [
                "Full security testing coverage",
                "Formal verification preparation",
                "Documentation and evidence packages",
                "Professional audit standards compliance"
            ],
            "ideal_for": "Production-ready protocols preparing for security audits",
            "phases": 5,
            "estimated_effort": "2-4 weeks"
        }
        
        return workflows

    async def _generate_comprehensive_improvement_plan(self, project_state: ProjectState, 
                                                     ai_failure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive improvement plan based on project analysis."""
        
        # Determine priority levels based on current state
        priority_levels = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Testing phase improvements
        if project_state.testing_phase.value == "none":
            priority_levels["critical"].append({
                "category": "Testing Foundation",
                "item": "Create basic unit tests for core contract functions",
                "effort": "2-3 days",
                "impact": "Establishes testing foundation"
            })
        elif project_state.testing_phase.value == "basic":
            priority_levels["high"].append({
                "category": "Testing Maturity",
                "item": "Add comprehensive edge case testing and error conditions",
                "effort": "3-5 days",
                "impact": "Improves test reliability and coverage"
            })
        elif project_state.testing_phase.value == "intermediate":
            priority_levels["medium"].append({
                "category": "Advanced Testing",
                "item": "Implement fuzz testing and invariant testing",
                "effort": "5-7 days",
                "impact": "Enhances security and robustness"
            })
        
        # Security level improvements
        if project_state.security_level.value in ["none", "basic"]:
            priority_levels["critical"].append({
                "category": "Security Testing",
                "item": "Add security-focused test scenarios and attack vectors",
                "effort": "3-5 days",
                "impact": "Critical for production readiness"
            })
        
        # AI failure improvements
        if ai_failure_analysis.get("status") in ["critical", "poor"]:
            priority_levels["critical"].append({
                "category": "Test Quality",
                "item": "Fix AI-generated test failures and improve test quality",
                "effort": "1-2 days",
                "impact": "Ensures test reliability and effectiveness"
            })
        
        # Contract-specific improvements
        high_risk_contracts = [c for c in project_state.contracts if c.risk_score > 0.7]
        if high_risk_contracts:
            priority_levels["high"].append({
                "category": "Risk Mitigation",
                "item": f"Add intensive testing for high-risk contracts: {', '.join(c.contract_name for c in high_risk_contracts[:3])}",
                "effort": "2-4 days",
                "impact": "Reduces deployment risks"
            })
        
        # Coverage improvements
        coverage_pct = project_state.coverage_data.get("coverage_percentage", 0)
        if coverage_pct < 80:
            priority_levels["high"].append({
                "category": "Coverage",
                "item": f"Improve test coverage from {coverage_pct}% to 80%+",
                "effort": "2-3 days",
                "impact": "Ensures comprehensive testing"
            })
        
        # Gap-specific improvements
        for gap in project_state.identified_gaps:
            if "security" in gap.lower():
                priority_levels["high"].append({
                    "category": "Security Gap",
                    "item": f"Address security gap: {gap}",
                    "effort": "1-2 days",
                    "impact": "Improves security posture"
                })
            elif "coverage" in gap.lower():
                priority_levels["medium"].append({
                    "category": "Coverage Gap",
                    "item": f"Address coverage gap: {gap}",
                    "effort": "1-2 days",
                    "impact": "Improves test comprehensiveness"
                })
        
        # Generate timeline
        total_effort_days = 0
        for priority, items in priority_levels.items():
            for item in items:
                # Extract effort in days (rough estimate)
                effort_str = item["effort"]
                if "day" in effort_str:
                    days = int(effort_str.split("-")[0])
                    total_effort_days += days
        
        return {
            "current_state": {
                "testing_phase": project_state.testing_phase.value,
                "security_level": project_state.security_level.value,
                "ai_failure_status": ai_failure_analysis.get("status", "unknown"),
                "coverage_percentage": coverage_pct
            },
            "priority_improvements": priority_levels,
            "estimated_timeline": {
                "total_effort_days": total_effort_days,
                "critical_path_days": len(priority_levels["critical"]) * 2,
                "phases": {
                    "phase_1_critical": "Address critical issues first (1-2 weeks)",
                    "phase_2_high": "Implement high-priority improvements (2-3 weeks)",
                    "phase_3_medium": "Add medium-priority enhancements (1-2 weeks)",
                    "phase_4_low": "Polish and optimize (1 week)"
                }
            },
            "success_metrics": {
                "testing_phase_target": "production",
                "security_level_target": "audit_ready",
                "coverage_target": "90%+",
                "ai_failure_target": "clean"
            },
            "next_steps": project_state.next_recommendations[:3]
        }
    
    # Contextual workflow phase generators
    async def _generate_security_focused_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security-focused workflow phases based on current context."""
        return [
            {
                "phase": 1,
                "title": "Security Assessment & Gap Analysis",
                "description": f"Evaluate current security testing (Level: {context.get('security_level', 'unknown')})",
                "actions": [
                    "Audit existing security tests for completeness",
                    "Identify missing attack vector coverage",
                    "Assess contract risk patterns and vulnerabilities",
                    "Map security requirements to contract types"
                ],
                "deliverables": [
                    "Security gap analysis report",
                    "Attack vector coverage matrix", 
                    "Risk-prioritized testing plan"
                ]
            },
            {
                "phase": 2,
                "title": "Vulnerability Testing Implementation",
                "description": "Implement comprehensive security test scenarios",
                "actions": [
                    "Add access control and privilege escalation tests",
                    "Implement reentrancy attack simulations",
                    "Create oracle manipulation test scenarios",
                    "Add flash loan attack resistance testing"
                ],
                "deliverables": [
                    "Complete access control test suite",
                    "Reentrancy protection validation",
                    "Oracle manipulation resistance tests"
                ]
            },
            {
                "phase": 3,
                "title": "Advanced Security Testing",
                "description": "Add fuzz testing and invariant validation for security properties",
                "actions": [
                    "Implement property-based security testing",
                    "Add invariant tests for critical security properties",
                    "Create fuzz tests for input validation",
                    "Add economic attack scenario testing"
                ],
                "deliverables": [
                    "Property-based security test suite",
                    "Invariant validation framework",
                    "Economic attack resistance validation"
                ]
            }
        ]
    
    async def _generate_coverage_expansion_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate coverage expansion phases that build on existing tests."""
        current_coverage = context.get('coverage_pct', 0)
        return [
            {
                "phase": 1,
                "title": f"Coverage Gap Analysis (Current: {current_coverage:.1f}%)",
                "description": "Identify specific areas lacking test coverage",
                "actions": [
                    "Run comprehensive coverage analysis",
                    "Identify uncovered functions and branches",
                    "Prioritize coverage gaps by criticality",
                    "Plan targeted test additions"
                ],
                "deliverables": [
                    "Detailed coverage gap report",
                    "Prioritized testing roadmap",
                    "Function-specific test requirements"
                ]
            },
            {
                "phase": 2,
                "title": "Systematic Test Implementation",
                "description": "Add tests for uncovered areas and edge cases",
                "actions": [
                    "Implement tests for uncovered functions",
                    "Add edge case and boundary condition testing",
                    "Create error condition and revert testing",
                    "Add integration tests for contract interactions"
                ],
                "deliverables": [
                    "Expanded unit test coverage",
                    "Edge case test scenarios",
                    "Integration test implementations"
                ]
            },
            {
                "phase": 3,
                "title": "Quality Enhancement & Validation",
                "description": "Improve test quality and validate coverage improvements",
                "actions": [
                    "Enhance existing test assertions and validation",
                    "Add mock implementations for dependencies",
                    "Optimize test performance and organization",
                    "Validate coverage target achievement"
                ],
                "deliverables": [
                    "Enhanced test quality metrics",
                    "Mock implementation framework",
                    "Coverage validation report"
                ]
            }
        ]
    
    async def _generate_defi_security_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate DeFi-specific security testing phases."""
        return [
            {
                "phase": 1,
                "title": "DeFi Risk Assessment",
                "description": "Assess DeFi-specific vulnerabilities and attack vectors",
                "actions": [
                    "Identify flash loan attack surfaces",
                    "Map oracle dependencies and manipulation risks",
                    "Assess MEV extraction vulnerabilities",
                    "Analyze liquidity and slippage risks"
                ],
                "deliverables": [
                    "DeFi risk assessment report",
                    "Attack vector prioritization",
                    "Economic model vulnerability analysis"
                ]
            },
            {
                "phase": 2,
                "title": "Economic Attack Testing",
                "description": "Implement testing for economic attack scenarios",
                "actions": [
                    "Create flash loan attack simulations",
                    "Implement oracle manipulation testing",
                    "Add MEV extraction resistance testing",
                    "Test liquidation and arbitrage mechanics"
                ],
                "deliverables": [
                    "Flash loan attack test suite",
                    "Oracle manipulation resistance validation",
                    "MEV protection verification"
                ]
            },
            {
                "phase": 3,
                "title": "DeFi Integration Security",
                "description": "Test cross-protocol interactions and composability",
                "actions": [
                    "Test external protocol integrations",
                    "Validate cross-chain bridge security",
                    "Add governance attack scenario testing",
                    "Test protocol upgrade mechanisms"
                ],
                "deliverables": [
                    "Integration security test suite",
                    "Cross-protocol vulnerability assessment",
                    "Governance security validation"
                ]
            }
        ]
    
    async def _generate_integration_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integration testing phases for multi-contract systems."""
        return [
            {
                "phase": 1,
                "title": "Integration Architecture Analysis",
                "description": "Map contract interactions and integration points",
                "actions": [
                    "Document contract interaction patterns",
                    "Identify integration dependencies",
                    "Map user journey workflows",
                    "Assess state consistency requirements"
                ],
                "deliverables": [
                    "Integration architecture map",
                    "Contract dependency analysis",
                    "User workflow documentation"
                ]
            },
            {
                "phase": 2,
                "title": "Cross-Contract Testing Implementation",
                "description": "Implement comprehensive integration test scenarios",
                "actions": [
                    "Create multi-contract workflow tests",
                    "Add state consistency validation",
                    "Implement user journey testing",
                    "Test error propagation and handling"
                ],
                "deliverables": [
                    "Multi-contract workflow tests",
                    "State consistency validation suite",
                    "User journey test scenarios"
                ]
            },
            {
                "phase": 3,
                "title": "Performance & Optimization Testing",
                "description": "Validate performance and gas optimization",
                "actions": [
                    "Add gas usage optimization testing",
                    "Test transaction batching and efficiency",
                    "Validate scalability under load",
                    "Optimize integration test performance"
                ],
                "deliverables": [
                    "Gas optimization validation",
                    "Performance benchmark results",
                    "Scalability test reports"
                ]
            }
        ]
    
    async def _generate_audit_prep_phases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive audit preparation phases."""
        return [
            {
                "phase": 1,
                "title": "Comprehensive Test Coverage Review",
                "description": "Ensure audit-ready test coverage and documentation",
                "actions": [
                    "Achieve 95%+ line and branch coverage",
                    "Document all test scenarios and rationale",
                    "Create comprehensive test evidence packages",
                    "Validate test quality and effectiveness"
                ],
                "deliverables": [
                    "Complete coverage validation report",
                    "Test evidence documentation",
                    "Quality assurance metrics"
                ]
            },
            {
                "phase": 2,
                "title": "Security Testing Validation",
                "description": "Comprehensive security testing for audit standards",
                "actions": [
                    "Complete security vulnerability testing",
                    "Implement formal verification where applicable",
                    "Add stress testing and edge case coverage",
                    "Validate all attack vector protections"
                ],
                "deliverables": [
                    "Security testing validation report",
                    "Formal verification results",
                    "Attack vector protection evidence"
                ]
            },
            {
                "phase": 3,
                "title": "Documentation & Evidence Preparation",
                "description": "Prepare comprehensive audit documentation packages",
                "actions": [
                    "Create audit-ready documentation",
                    "Generate test result evidence packages",
                    "Document security assumptions and mitigations",
                    "Prepare known issues and resolution documentation"
                ],
                "deliverables": [
                    "Audit documentation package",
                    "Security assumptions documentation",
                    "Known issues and mitigations report"
                ]
            }
        ]
    
    async def _generate_contextual_phases(self, workflow_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual phases for legacy or custom workflow types."""
        return [
            {
                "phase": 1,
                "title": f"Contextual Analysis for {workflow_type}",
                "description": f"Analyze requirements and plan approach for {workflow_type}",
                "actions": [
                    "Assess current project state and requirements",
                    "Identify specific objectives for this workflow",
                    "Plan implementation strategy",
                    "Define success criteria and metrics"
                ],
                "deliverables": [
                    "Requirements analysis report",
                    "Implementation strategy document",
                    "Success metrics definition"
                ]
            }
        ]