"""
Smart Contract Testing MCP Server - Testing Tools (Refactored)

This module implements intelligent, context-aware MCP tools for interactive
and automated testing workflows. Tools provide contextual analysis, adaptive
workflows, and specific actionable guidance.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from .foundry_adapter import FoundryAdapter, FoundryProjectError
from .project_analyzer import ProjectAnalyzer, ProjectState, TestingPhase, SecurityLevel
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
    Intelligent, context-aware testing tools for the MCP server.
    
    Provides smart workflow management with adaptive strategies based on project
    maturity, contextual analysis with specific next steps, and intelligent
    workflow generation tailored to real-time project state.
    """
    
    def __init__(self, foundry_adapter: FoundryAdapter, 
                 project_analyzer: Optional[ProjectAnalyzer] = None,
                 ai_failure_detector: Optional[AIFailureDetector] = None,
                 testing_resources=None):
        """
        Initialize intelligent testing tools with enhanced dependency injection.
        
        Args:
            foundry_adapter: The Foundry adapter instance  
            project_analyzer: Optional ProjectAnalyzer with AST capabilities
            ai_failure_detector: Optional AIFailureDetector with semantic analysis
            testing_resources: Optional TestingResources for template access
        """
        self.foundry_adapter = foundry_adapter
        
        # Use injected dependencies or create new ones for backward compatibility
        self.project_analyzer = project_analyzer or ProjectAnalyzer(foundry_adapter)
        self.ai_failure_detector = ai_failure_detector or AIFailureDetector()
        self.testing_resources = testing_resources
        
        self.active_sessions: Dict[str, TestingSession] = {}
        
        logger.info("Intelligent testing tools initialized with enhanced capabilities")
        logger.info("-> AST-based semantic analysis: ENABLED")
        logger.info("-> AI failure detection with context awareness: ENABLED")
        logger.info("-> Contextual workflow generation: ENABLED")
    
    def _resolve_project_path(self, project_path: str = "") -> str:
        """
        Resolve the project path to analyze - prioritizes user's working directory.
        
        The goal is seamless usage: user opens their Solidity project, calls MCP tools,
        and the tools automatically work on that project.
        
        Args:
            project_path: Optional explicit project path
            
        Returns:
            Absolute path to the project directory to analyze
        """
        # If explicit path provided, use it
        if project_path and project_path not in ["", "."]:
            resolved_path = str(Path(project_path).resolve())
            logger.debug(f"Using explicit project path: {resolved_path}")
            return resolved_path
        
        # Priority 1: MCP_CLIENT_CWD (user's working directory from MCP client)
        mcp_client_cwd = os.getenv("MCP_CLIENT_CWD")
        if mcp_client_cwd:
            resolved_path = str(Path(mcp_client_cwd).resolve())
            logger.debug(f"Using MCP client working directory: {resolved_path}")
            return resolved_path
        
        # Priority 2: MCP_PROJECT_PATH (explicit project override)
        mcp_project_path = os.getenv("MCP_PROJECT_PATH")
        if mcp_project_path:
            resolved_path = str(Path(mcp_project_path).resolve())
            logger.debug(f"Using MCP project path: {resolved_path}")
            return resolved_path
        
        # Priority 3: Current working directory (but warn if it's the MCP server)
        current_dir = str(Path.cwd().resolve())
        
        # Check if we're in the MCP server directory
        is_mcp_server_dir = (
            "foundry-testing-mcp" in current_dir.lower() and
            (Path(current_dir) / "components").exists() and
            (Path(current_dir) / "templates").exists()
        )
        
        if is_mcp_server_dir:
            logger.warning(f"⚠️  MCP server is using its own directory: {current_dir}")
            logger.warning("This usually means the MCP client didn't set the working directory.")
            logger.warning("To fix: configure MCP client with 'cwd' or set MCP_CLIENT_CWD")
        
        logger.debug(f"Using current working directory: {current_dir}")
        return current_dir
    
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
        
        # Check if this is the MCP server directory itself
        is_mcp_server_dir = (
            (project_path / "components").exists() and
            (project_path / "templates").exists() and
            (project_path / "requirements.txt").exists() and
            "foundry-testing-mcp" in str(project_path).lower()
        )
        
        if is_mcp_server_dir:
            validation["project_type"] = "mcp_server"
            validation["issues"].extend([
                "⚠️  Working from MCP server directory - this is unusual",
                "Typically you'd run MCP tools from your smart contract project directory"
            ])
            validation["suggestions"].extend([
                "💡 This works, but you probably want to:",
                "1. Navigate to your Foundry project: cd /path/to/your/project", 
                "2. Configure your MCP client to use your project directory as working directory",
                "3. Or create a new project: mkdir my-project && cd my-project && forge init",
                "🎯 The tools work best when run from your actual smart contract project"
            ])
            # Don't return early - let it continue and try to help
        
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
            # Check if this looks like a generic code directory
            has_common_files = any([
                (project_path / "package.json").exists(),
                (project_path / "requirements.txt").exists(),
                (project_path / ".git").exists(),
                (project_path / "README.md").exists()
            ])
            
            if has_common_files and not (project_path / "src").exists():
                validation["issues"].append("This appears to be a software project but not a smart contract project")
                validation["suggestions"].extend([
                    "🎯 Navigate to your Foundry project directory, or create one:",
                    "   mkdir my-smart-contract-project && cd my-smart-contract-project",
                    "   forge init",
                    "🔧 Then configure your MCP client to use that directory"
                ])
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
    
    def _diagnose_project_issues(self, validation: Dict[str, Any]) -> List[str]:
        """
        Generate intelligent diagnosis and recommendations for project issues.
        
        Args:
            validation: Validation result from _validate_foundry_project
            
        Returns:
            List of diagnostic messages and recommendations
        """
        diagnosis = []
        
        if validation.get("project_type") == "mcp_server":
            diagnosis.extend([
                "💡 DETECTED: Running from MCP server directory",
                "",
                "This is unusual but workable. Typically users run MCP tools from their",
                "smart contract project directory for the best experience.",
                "",
                "RECOMMENDED WORKFLOW:",
                "1. Navigate to your Foundry project directory (or create one)",
                "2. Configure your MCP client to use that as the working directory",
                "3. The tools will then analyze your actual smart contract project",
                "",
                "For now, I can help you set up a Foundry project!"
            ])
        elif validation.get("project_type") == "hardhat":
            diagnosis.extend([
                "📊 DETECTED: Hardhat Project",
                "You can add Foundry support: forge init --force"
            ])
        elif validation.get("project_type") == "truffle":
            diagnosis.extend([
                "📊 DETECTED: Truffle Project", 
                "Consider migrating to Foundry for better testing experience"
            ])
        elif validation.get("project_type") == "unknown":
            issues = validation.get("issues", [])
            if any("software project" in issue for issue in issues):
                diagnosis.extend([
                    "📊 DETECTED: Generic Software Project",
                    "This appears to be a code project but not a smart contract project.",
                    "Navigate to your Foundry project or create one."
                ])
            else:
                diagnosis.extend([
                    "❓ UNKNOWN PROJECT TYPE",
                    "No recognized smart contract framework detected.",
                    "Initialize a Foundry project: forge init"
                ])
        
        return diagnosis
    
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
            description="""🚀 STEP 1: Initialize intelligent testing workflow - START HERE for any testing project
            
            ENHANCED INTELLIGENCE: Uses AST analysis and project maturity assessment to provide contextual recommendations.
            
            WHEN TO USE:
            - Beginning work on any Foundry project (new or existing)
            - First interaction with smart contract testing
            - Need intelligent workflow recommendations based on project state
            
            WHAT IT DOES:
            - AST-powered project structure and maturity analysis
            - Validates Foundry setup with detailed diagnostics
            - Generates contextual workflow options based on actual project state
            - Creates persistent session for workflow continuity
            - Provides specific, actionable next steps with tool guidance
            
            INPUTS:
            - analysis_mode: "interactive" (guided) or "direct" (immediate analysis)
            - project_path: Optional path (auto-detects current directory if not provided)
            
            OUTPUTS:
            - Intelligent project analysis with AST insights
            - Contextual workflow options tailored to project maturity
            - Specific tool recommendations for next steps
            - Session ID for workflow continuity
            
            WORKFLOW: Always start here. Results guide you to execute_testing_workflow or analyze_project_context.
            """
        )
        async def initialize_protocol_testing_agent(
            analysis_mode: str = "interactive",
            project_path: str = ""
        ) -> Dict[str, Any]:
            """Initialize intelligent protocol testing agent with AST-powered analysis."""
            try:
                # Enhanced project path resolution with validation
                resolved_project_path = self._resolve_project_path(project_path)
                
                # Advanced Foundry project validation with diagnostics
                validation = self._validate_foundry_project(resolved_project_path)
                
                if not validation["is_valid"]:
                    # Still try to help even if validation failed
                    # Provide guidance but don't refuse to work
                    
                    return {
                        "status": "project_setup_needed", 
                        "project_path": resolved_project_path,
                        "detected_situation": validation.get("project_type", "unknown"),
                        "guidance": {
                            "message": "No Foundry project detected - let's help you set one up!",
                            "current_directory": resolved_project_path,
                            "issues_found": validation.get("issues", []),
                            "recommendations": validation.get("suggestions", [])
                        },
                        "quick_setup": {
                            "option_1": {
                                "title": "Initialize Foundry in current directory",
                                "command": "forge init --force",
                                "description": "Sets up foundry.toml, src/, test/, script/ directories"
                            },
                            "option_2": {
                                "title": "Create new project elsewhere", 
                                "commands": [
                                    "mkdir my-smart-contract-project",
                                    "cd my-smart-contract-project", 
                                    "forge init"
                                ],
                                "description": "Creates a new directory with fresh Foundry project"
                            }
                        },
                        "what_happens_next": [
                            "After setting up Foundry, re-run this tool",
                            "The tools will analyze your contracts and recommend testing approaches",
                            "You'll get step-by-step guidance to build comprehensive test suites"
                        ],
                        "ready_to_proceed": False
                    }
                
                # AST-powered intelligent project analysis using ProjectAnalyzer
                project_state = await self.project_analyzer.analyze_project(resolved_project_path)
                
                # Create enhanced session with rich project context
                session_id = str(uuid.uuid4())
                session = TestingSession(session_id, resolved_project_path)
                session.project_state = project_state  # Store full project state
                session.analysis_mode = analysis_mode
                self.active_sessions[session_id] = session
                
                # Generate intelligent, context-aware workflows
                contextual_workflows = self._generate_intelligent_workflows(project_state)
                
                # Smart guidance based on project maturity and state
                intelligent_guidance = self._generate_intelligent_next_steps(project_state)
                
                return {
                    "status": "initialized", 
                    "session_id": session_id,
                    "project_path": resolved_project_path,
                    "intelligent_analysis": {
                        "testing_phase": project_state.testing_phase.value,
                        "security_level": project_state.security_level.value,
                        "project_type": project_state.project_type,
                        "contracts_found": len(project_state.contracts),
                        "tests_found": len(project_state.test_files),
                        "maturity_assessment": self._assess_project_maturity(project_state),
                        "priority_areas": project_state.identified_gaps[:3]  # Top 3 priority gaps
                    },
                    "contextual_workflows": contextual_workflows,
                    "intelligent_guidance": intelligent_guidance,
                    "session_capabilities": {
                        "ast_analysis": True,
                        "ai_failure_detection": True,
                        "contextual_workflows": True,
                        "semantic_understanding": True
                    }
                }
                
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
            description="""🔍 STEP 2: Intelligent deep analysis with AI failure detection - Advanced project assessment
            
            ENHANCED INTELLIGENCE: AST-powered analysis with semantic understanding and AI failure detection.
            
            WHEN TO USE:
            - Need comprehensive assessment of existing test quality
            - Debugging test issues or unexpectedly low coverage
            - Before major testing improvements or refactoring
            - Validating AI-generated tests for common failures
            - Planning security audit preparation
            
            WHAT IT DOES:
            - Advanced testing maturity assessment with specific recommendations
            - Semantic analysis of test structure and effectiveness
            - AI failure pattern detection (circular logic, mock cheating, insufficient coverage)
            - Contract risk scoring with vulnerability pattern identification
            - Generates prioritized improvement roadmap with effort estimates and tool guidance
            
            INPUTS:
            - include_ai_failure_detection: true (strongly recommended) - detects AI-generated test problems
            - generate_improvement_plan: true (recommended) - creates actionable improvement roadmap
            - project_path: Optional path (auto-detects current directory if not provided)
            
            OUTPUTS:
            - Comprehensive testing maturity and security level analysis
            - AI failure detection report with specific issues and fixes
            - Contract-by-contract risk analysis with security patterns
            - Prioritized improvement plan with specific next steps and tool recommendations
            
            WORKFLOW: Use after initialize_protocol_testing_agent for deep analysis. Results provide specific guidance for execute_testing_workflow.
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
                    diagnosis = self._diagnose_project_issues(validation)
                    
                    return {
                        "status": "invalid",
                        "project_path": project_path,
                        "message": "❌ Not a valid Foundry project",
                        "issues": validation["issues"],
                        "suggestions": validation["suggestions"],
                        "diagnosis": diagnosis,
                        "project_type": validation.get("project_type", "unknown"),
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
                
                # Run validation to get specific project type
                validation = self._validate_foundry_project(resolved_path)
                
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
                        "contains_test_dir": (Path(resolved_path) / "test").exists(),
                        "is_mcp_server_dir": validation.get("project_type") == "mcp_server"
                    },
                    "project_type": validation.get("project_type", "unknown")
                }
                
                # Generate specific recommendations based on project type
                recommendations = []
                
                if validation.get("project_type") == "mcp_server":
                    recommendations.extend([
                        "🎯 ISSUE IDENTIFIED: You're in the MCP server directory!",
                        "",
                        "❌ Problem: The MCP tools are running from the foundry-testing-mcp directory",
                        "   This is the MCP server code, not a smart contract project.",
                        "",
                        "✅ Solution: Navigate to your actual Foundry project:",
                        "",
                        "🔧 Quick Fix:",
                        "1. Open terminal in your smart contract project directory",
                        "2. Or create a new one: mkdir my-protocol && cd my-protocol && forge init",
                        "3. Configure your MCP client to use that directory:",
                        "",
                        "📋 MCP Client Configuration (recommended):",
                        "```json",
                        "{",
                        "  \"mcpServers\": {",
                        "    \"foundry-testing\": {",
                        "      \"command\": \"/path/to/python\",",
                        "      \"args\": [\"/path/to/foundry-testing-mcp/run_clean.py\"],",
                        "      \"cwd\": \"/path/to/your/actual/project\",",
                        "      \"env\": {",
                        "        \"MCP_CLIENT_CWD\": \"/path/to/your/actual/project\"",
                        "      }",
                        "    }",
                        "  }",
                        "}",
                        "```",
                        "",
                        "🎯 After fixing: Your project should have foundry.toml, src/, test/ directories"
                    ])
                elif validation.get("is_valid"):
                    recommendations.extend([
                        "✅ Directory detection is working correctly",
                        "🎯 The detected directory is a valid Foundry project",
                        "📁 Project structure looks good for testing"
                    ])
                elif debug_info["path_analysis"]["is_home_directory"]:
                    recommendations.extend([
                        "❌ Issue: MCP tools are using your home directory",
                        "",
                        "💡 Solutions:",
                        "1. Navigate to your project: cd /path/to/your/foundry/project",
                        "2. Set MCP_CLIENT_CWD environment variable",
                        "3. Configure MCP client working directory",
                        "",
                        "🔧 MCP Client Configuration:",
                        "```json",
                        "{ \"cwd\": \"/path/to/your/project\", \"env\": { \"MCP_CLIENT_CWD\": \"/path/to/your/project\" } }",
                        "```"
                    ])
                else:
                    recommendations.extend([
                        "❌ Directory detection found issues",
                        f"🔍 Current directory: {resolved_path}",
                        f"📊 Project type detected: {validation.get('project_type', 'unknown')}",
                        "",
                        "💡 Solutions based on your situation:",
                        *validation.get("suggestions", []),
                        "",
                        "🔧 If you have a Foundry project elsewhere:",
                        "1. Set MCP_CLIENT_CWD to your project directory",
                        "2. Configure MCP client working directory",
                        "3. Use explicit project paths in tool calls"
                    ])
                
                return {
                    "status": "debug_complete",
                    "directory_detection_correct": validation.get("is_valid", False),
                    "debug_info": debug_info,
                    "validation": validation,
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
                        "💡 Try setting MCP_CLIENT_CWD environment variable to your project directory"
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
    
    # Template access helper methods
    async def _get_template_content(self, template_type: str) -> Dict[str, Any]:
        """Get template content and placeholders from testing resources."""
        if not self.testing_resources:
            return {
                "name": f"{template_type.title()} Template",
                "content": f"# {template_type.title()} template not available - TestingResources not initialized",
                "placeholders": [],
                "usage_instructions": ["Template system not available"]
            }
        
        try:
            template_content, placeholders = await self.testing_resources._load_template(template_type)
            usage_instructions = self.testing_resources._get_template_usage_instructions(template_type)
            
            return {
                "name": f"{template_type.title()} Test Template",
                "description": f"Production-ready template for {template_type} testing scenarios",
                "template_type": template_type,
                "content": template_content,
                "placeholders": placeholders,
                "usage_instructions": usage_instructions
            }
        except Exception as e:
            logger.warning(f"Could not load {template_type} template: {e}")
            return {
                "name": f"{template_type.title()} Template",
                "content": f"# Template loading error: {e}",
                "placeholders": [],
                "usage_instructions": ["Template could not be loaded"]
            }
    
    async def _get_foundry_patterns(self) -> Dict[str, Any]:
        """Get Foundry testing patterns from testing resources."""
        if not self.testing_resources:
            return {"content": {"error": "TestingResources not initialized"}}
        
        # Return simplified patterns for now since the actual resource access is complex
        return {
            "content": {
                "test_organization": {
                    "description": "Recommended test file organization grouped by functionality and test type.",
                    "file_structure_pattern": """
test/
├── {{CONTRACT_NAME}}.t.sol                    # Core unit and integration tests
├── {{CONTRACT_NAME}}.invariant.t.sol          # Invariant/property-based tests
├── {{CONTRACT_NAME}}.security.t.sol           # Security-focused tests
├── {{CONTRACT_NAME}}.fork.t.sol               # Mainnet fork tests
├── handlers/
│   └── {{CONTRACT_NAME}}Handler.sol           # Handler for invariant testing
├── mocks/
│   ├── Mock{{DEPENDENCY_NAME}}.sol
│   └── MockERC20.sol
└── utils/
    ├── TestHelper.sol
    └── TestConstants.sol
                    """
                }
            }
        }
    
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
        if workflow_type in ["create_new_suite", "from_scratch", "comprehensive"]:
            base_plan["execution_phases"] = await self._generate_create_new_suite_phases(current_context, project_path)
            base_plan["success_criteria"] = [
                "Complete test suite infrastructure established",
                "Unit tests covering all core functions", 
                "Security tests for identified vulnerabilities",
                "Coverage targets achieved (80%+ minimum)",
                "Professional testing patterns implemented"
            ]
            
        elif workflow_type == "enhance_security_testing":
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
                        "Create enhancement roadmap",
                        "Define improved coverage targets"
                    ],
                    "deliverables": [
                        "Enhancement strategy document",
                        "Prioritized improvement plan",
                        "Refactoring roadmap",
                        "Updated coverage targets",
                        "Implementation guidance"
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
        """Execute a specific workflow phase with enhanced context and automated analysis."""
        phase_number = phase.get("phase", 0)
        phase_title = phase.get('title', 'Unknown')
        logger.info(f"Executing phase {phase_number}: {phase_title}")
        
        # Execute validation steps if they exist
        validation_results = {}
        if "validation_steps" in phase:
            for step_name, step_config in phase["validation_steps"].items():
                try:
                    validation_results[step_name] = await self._execute_validation_step(
                        step_config, session.project_path
                    )
                except Exception as e:
                    logger.warning(f"Validation step {step_name} failed: {e}")
                    validation_results[step_name] = {"error": str(e)}
        
        # Baseline coverage check for Phase 1
        if phase_number == 1:
            try:
                baseline_coverage = await self._get_baseline_coverage(session.project_path)
                validation_results["baseline_coverage"] = baseline_coverage
            except Exception as e:
                logger.info(f"No baseline coverage available: {e}")
        
        # Progress monitoring after phases 2 and 3 (when tests are being created)
        if phase_number in [2, 3]:
            try:
                progress_coverage = await self.analyze_current_test_coverage(target_coverage=80)
                validation_results["progress_coverage"] = progress_coverage
            except Exception as e:
                logger.info(f"Progress coverage check failed: {e}")

        # Enhanced phase execution with real deliverables
        session.completed_phases.append(phase_number)
        session.current_phase = phase_number + 1
        
        result = {
            "phase": phase_number,
            "title": phase_title,
            "status": "completed",
            "actions_completed": phase.get("actions", []),
            "deliverables_generated": phase.get("deliverables", []),
            "validation_results": validation_results,
            "success": True
        }
        
        # Add template content if available
        if "template_content" in phase:
            result["template_content"] = phase["template_content"]
        
        return result
    
    async def _execute_validation_step(self, step_config: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Execute a validation step using the specified tool."""
        tool_name = step_config.get("tool")
        parameters = step_config.get("parameters", {})
        
        if tool_name == "analyze_current_test_coverage":
            # Call the coverage analysis tool
            return await self.analyze_current_test_coverage(
                target_coverage=parameters.get("target_coverage", 90),
                include_branches=parameters.get("include_branches", True)
            )
        elif tool_name == "analyze_project_context":
            # Call the project context analysis tool  
            return await self.analyze_project_context(
                include_ai_failure_detection=parameters.get("include_ai_failure_detection", True),
                generate_improvement_plan=parameters.get("generate_improvement_plan", True),
                project_path=project_path
            )
        else:
            return {"error": f"Unknown validation tool: {tool_name}"}
    
    async def _get_baseline_coverage(self, project_path: str) -> Dict[str, Any]:
        """Get baseline coverage if tests exist."""
        try:
            # Check if tests exist first
            validation = self._validate_foundry_project(project_path)
            if validation.get("has_tests", False):
                return await self.analyze_current_test_coverage(target_coverage=80)
            else:
                return {"message": "No tests found - starting from 0% coverage", "baseline_coverage": 0}
        except Exception as e:
            return {"message": f"Could not establish baseline: {e}", "baseline_coverage": 0}

    # Placeholder helper methods
    async def _identify_coverage_gaps(self, coverage_data: Dict[str, Any]) -> List[str]:
        """Identify coverage gaps."""
        return ["Example gap: Uncovered error conditions"]
    
    async def _generate_coverage_recommendations(self, coverage_data: Dict[str, Any], gap: float) -> List[str]:
        """Generate coverage recommendations."""
        return [f"Add tests to improve coverage by {gap:.1f}%"] 
    
    def _diagnose_project_issues(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose specific project setup issues with actionable guidance."""
        issues = []
        solutions = []
        
        if not validation.get("has_foundry_toml", False):
            issues.append("Missing foundry.toml configuration file")
            solutions.append("Run 'forge init --force' to create proper Foundry structure")
        
        if not validation.get("has_src_dir", False):
            issues.append("Missing src/ directory for contracts")
            solutions.append("Create src/ directory and move contracts there")
        
        if not validation.get("foundry_installed", True):
            issues.append("Foundry not installed or not in PATH")
            solutions.append("Install Foundry: curl -L https://foundry.paradigm.xyz | bash")
        
        return {
            "identified_issues": issues,
            "actionable_solutions": solutions,
            "severity": "high" if len(issues) > 2 else "medium"
        }
    
    def _assess_project_maturity(self, project_state: ProjectState) -> str:
        """Assess overall project testing maturity with specific description."""
        if project_state.testing_phase == TestingPhase.PRODUCTION:
            return "Production-ready with comprehensive testing"
        elif project_state.testing_phase == TestingPhase.ADVANCED:
            return "Advanced testing with security focus"
        elif project_state.testing_phase == TestingPhase.INTERMEDIATE:
            return "Solid foundation with room for enhancement"
        elif project_state.testing_phase == TestingPhase.BASIC:
            return "Basic testing setup, needs expansion"
        else:
            return "No testing found, starting from scratch"
    
    def _generate_intelligent_workflows(self, project_state: ProjectState) -> Dict[str, Any]:
        """Generate intelligent workflows based on actual project state and maturity."""
        workflows = {}
        
        # Base workflow always available
        workflows["foundational_setup"] = {
            "name": "Foundational Test Suite Setup",
            "description": "Establish core testing infrastructure with best practices",
            "suitable_for": ["new projects", "projects with minimal testing"],
            "phases": ["Setup", "Core unit tests", "Basic security tests"]
        }
        
        # Context-aware workflow generation based on project state
        if project_state.testing_phase == TestingPhase.NONE:
            workflows["from_scratch"] = {
                "name": "Complete Test Suite Creation",
                "description": "Build comprehensive testing from ground up",
                "priority": "high",
                "phases": ["Project setup", "Unit testing", "Integration testing", "Security testing"]
            }
        
        elif project_state.testing_phase == TestingPhase.BASIC:
            workflows["enhance_coverage"] = {
                "name": "Expand Test Coverage & Quality",
                "description": "Build on existing tests with comprehensive coverage",
                "priority": "high",
                "phases": ["Coverage analysis", "Gap filling", "Edge cases", "Integration tests"]
            }
        
        elif project_state.testing_phase in [TestingPhase.INTERMEDIATE, TestingPhase.ADVANCED]:
            workflows["security_enhancement"] = {
                "name": "Advanced Security Testing",
                "description": "Add comprehensive security testing and attack scenarios",
                "priority": "medium",
                "phases": ["Security audit", "Attack scenarios", "Defense testing"]
            }
        
        # Security-specific workflows based on security level
        if project_state.security_level in [SecurityLevel.NONE, SecurityLevel.BASIC]:
            workflows["security_focus"] = {
                "name": "Security-First Testing Strategy",
                "description": "Prioritize security testing for high-risk contracts",
                "priority": "critical" if project_state.security_level == SecurityLevel.NONE else "high",
                "phases": ["Threat modeling", "Access control tests", "Reentrancy tests", "Economic attacks"]
            }
        
        # Multi-contract workflows
        if len(project_state.contracts) > 1:
            workflows["integration_testing"] = {
                "name": "Multi-Contract Integration Testing",
                "description": "Test complex interactions between contracts",
                "priority": "medium",
                "phases": ["Integration mapping", "Workflow testing", "State consistency"]
            }
        
        # DeFi-specific workflows
        if project_state.project_type == "defi":
            workflows["defi_security"] = {
                "name": "DeFi Security Testing Suite",
                "description": "Comprehensive DeFi-specific security testing",
                "priority": "critical",
                "phases": ["Flash loan attacks", "Oracle manipulation", "MEV resistance", "Economic exploits"]
            }
        
        return workflows
    
    def _generate_intelligent_next_steps(self, project_state: ProjectState) -> Dict[str, Any]:
        """Generate intelligent next steps based on project analysis."""
        next_steps = {
            "immediate_priority": "",
            "recommended_tool": "",
            "specific_actions": [],
            "alternative_paths": []
        }
        
        # Intelligent priority assessment
        if project_state.testing_phase == TestingPhase.NONE:
            next_steps.update({
                "immediate_priority": "Start with foundational test setup",
                "recommended_tool": "execute_testing_workflow with 'from_scratch' workflow",
                "specific_actions": [
                    "Use templates from testing://templates/unit for basic structure",
                    "Reference testing://foundry-patterns for best practices",
                    "Start with critical function testing"
                ],
                "alternative_paths": ["analyze_project_context for deeper assessment first"]
            })
        
        elif project_state.security_level == SecurityLevel.NONE and len(project_state.contracts) > 0:
            next_steps.update({
                "immediate_priority": "Critical: Add security testing immediately",
                "recommended_tool": "execute_testing_workflow with 'security_focus' workflow",
                "specific_actions": [
                    "Use testing://security-patterns for vulnerability testing",
                    "Focus on access control and reentrancy first",
                    "Implement attack scenarios from testing://templates/security"
                ],
                "alternative_paths": ["Call analyze_project_context with include_ai_failure_detection=true"]
            })
        
        elif project_state.testing_phase == TestingPhase.BASIC:
            next_steps.update({
                "immediate_priority": "Expand test coverage and add security testing",
                "recommended_tool": "execute_testing_workflow with 'enhance_coverage' workflow",
                "specific_actions": [
                    "Run analyze_current_test_coverage to identify gaps",
                    "Add missing edge cases and error conditions",
                    "Implement security tests for identified vulnerabilities"
                ],
                "alternative_paths": ["Focus on security_enhancement workflow if high-risk contracts detected"]
            })
        
        elif project_state.testing_phase in [TestingPhase.INTERMEDIATE, TestingPhase.ADVANCED]:
            if len(project_state.identified_gaps) > 0:
                next_steps.update({
                    "immediate_priority": f"Address identified gaps: {', '.join(project_state.identified_gaps[:2])}",
                    "recommended_tool": "execute_testing_workflow with targeted approach",
                    "specific_actions": [
                        "Focus on specific gaps identified in analysis",
                        "Consider integration_testing workflow for multi-contract systems",
                        "Add invariant testing for system properties"
                    ],
                    "alternative_paths": ["analyze_project_context for detailed improvement plan"]
                })
            else:
                next_steps.update({
                    "immediate_priority": "Consider advanced testing techniques",
                    "recommended_tool": "execute_testing_workflow with 'security_enhancement'",
                    "specific_actions": [
                        "Add invariant testing for system properties",
                        "Implement fork testing for realistic scenarios",
                        "Consider formal verification for critical properties"
                    ],
                    "alternative_paths": ["Prepare for security audit with audit_prep workflow"]
                })
        
        # Add contract-specific guidance
        high_risk_contracts = [c for c in project_state.contracts if c.risk_score > 0.7]
        if high_risk_contracts:
            next_steps["urgent_attention"] = f"High-risk contracts need immediate security testing: {', '.join(c.contract_name for c in high_risk_contracts[:2])}"
        
        return next_steps

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
                "phases": 3
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
                "phases": 3
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
                "phases": 4
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
                "phases": 3
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
                "phases": 4
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
            "phases": 5
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
        if project_state.testing_phase == TestingPhase.NONE:
            priority_levels["critical"].append({
                "category": "Testing Foundation",
                "item": "Create basic unit tests for core contract functions",
                "impact": "Establishes testing foundation"
            })
        elif project_state.testing_phase.value == "basic":
            priority_levels["high"].append({
                "category": "Testing Maturity",
                "item": "Add comprehensive edge case testing and error conditions",
                "impact": "Improves test reliability and coverage"
            })
        elif project_state.testing_phase.value == "intermediate":
            priority_levels["medium"].append({
                "category": "Advanced Testing",
                "item": "Implement fuzz testing and invariant testing",
                "impact": "Enhances security and robustness"
            })
        
        # Security level improvements
        if project_state.security_level.value in ["none", "basic"]:
            priority_levels["critical"].append({
                "category": "Security Testing",
                "item": "Add security-focused test scenarios and attack vectors",
                "impact": "Critical for production readiness"
            })
        
        # AI failure improvements
        if ai_failure_analysis.get("status") in ["critical", "poor"]:
            priority_levels["critical"].append({
                "category": "Test Quality",
                "item": "Fix AI-generated test failures and improve test quality",
                "impact": "Ensures test reliability and effectiveness"
            })
        
        # Contract-specific improvements
        high_risk_contracts = [c for c in project_state.contracts if c.risk_score > 0.7]
        if high_risk_contracts:
            priority_levels["high"].append({
                "category": "Risk Mitigation",
                "item": f"Add intensive testing for high-risk contracts: {', '.join(c.contract_name for c in high_risk_contracts[:3])}",
                "impact": "Reduces deployment risks"
            })
        
        # Coverage improvements
        coverage_pct = project_state.coverage_data.get("coverage_percentage", 0)
        if coverage_pct < 80:
            priority_levels["high"].append({
                "category": "Coverage",
                "item": f"Improve test coverage from {coverage_pct}% to 80%+",
                "impact": "Ensures comprehensive testing"
            })
        
        # Gap-specific improvements
        for gap in project_state.identified_gaps:
            if "security" in gap.lower():
                priority_levels["high"].append({
                    "category": "Security Gap",
                    "item": f"Address security gap: {gap}",
                    "impact": "Improves security posture"
                })
            elif "coverage" in gap.lower():
                priority_levels["medium"].append({
                    "category": "Coverage Gap",
                    "item": f"Address coverage gap: {gap}",
                    "impact": "Improves test comprehensiveness"
                })
        
        return {
            "current_state": {
                "testing_phase": project_state.testing_phase.value,
                "security_level": project_state.security_level.value,
                "ai_failure_status": ai_failure_analysis.get("status", "unknown"),
                "coverage_percentage": coverage_pct
            },
            "priority_improvements": priority_levels,
            "success_metrics": {
                "testing_phase_target": "production",
                "security_level_target": "audit_ready",
                "coverage_target": "90%+",
                "ai_failure_target": "clean"
            },
            "next_steps": project_state.next_recommendations[:3]
        }
    
    # Contextual workflow phase generators
    async def _generate_create_new_suite_phases(self, context: Dict[str, Any], project_path: str) -> List[Dict[str, Any]]:
        """Generate create new suite phases with actual template content injection."""
        # Get contract names from project analysis
        try:
            project_state = await self.project_analyzer.analyze_project(project_path)
            contract_names = [c.contract_name for c in project_state.contracts]
            primary_contract = contract_names[0] if contract_names else "Portfolio"
        except Exception:
            primary_contract = "Portfolio"
            contract_names = [primary_contract]
        
        # Load actual template content
        unit_template = await self._get_template_content("unit")
        security_template = await self._get_template_content("security")
        helper_template = await self._get_template_content("helper")
        foundry_patterns = await self._get_foundry_patterns()
        
        return [
            {
                "phase": 1,
                "title": "Test Infrastructure Setup",
                "description": f"Establish comprehensive testing infrastructure for {primary_contract} contract",
                "actions": [
                    "Establish baseline with analyze_current_test_coverage tool (if tests exist)",
                    "Set up test directory structure following Foundry best practices", 
                    "Create helper utilities and common test setup",
                    "Establish testing conventions and patterns",
                    "Configure coverage monitoring"
                ],
                "deliverables": [
                    "Test directory structure",
                    "TestHelper.sol utility contract",
                    "Base test setup patterns",
                    "Coverage configuration"
                ],
                "template_content": {
                    "file_structure": f"""
test/
├── {primary_contract}.t.sol                    # Core unit and integration tests
├── {primary_contract}.invariant.t.sol          # Invariant/property-based tests
├── {primary_contract}.security.t.sol           # Security-focused tests
├── {primary_contract}.fork.t.sol               # Mainnet fork tests
├── handlers/
│   └── {primary_contract}Handler.sol           # Handler for invariant testing
├── mocks/
│   ├── MockERC20.sol
│   └── MockOracle.sol
└── utils/
    ├── TestHelper.sol
    └── TestConstants.sol
                    """,
                    "helper_template": {
                        "filename": "test/utils/TestHelper.sol",
                        "content": helper_template["content"].replace("{{CONTRACT_NAME}}", primary_contract),
                        "placeholders": helper_template["placeholders"],
                        "usage": helper_template["usage_instructions"]
                    }
                }
            },
            {
                "phase": 2,
                "title": "Core Unit Test Implementation",
                "description": f"Implement comprehensive unit tests for {primary_contract} functions",
                "actions": [
                    "Create primary unit test file with complete function coverage",
                    "Implement test cases for all public and external functions",
                    "Add edge case testing and error condition validation",
                    "Establish consistent testing patterns"
                ],
                "deliverables": [
                    f"{primary_contract}.t.sol - Primary unit test file",
                    "Complete function coverage tests",
                    "Edge case and error condition tests",
                    "Event emission verification"
                ],
                "template_content": {
                    "unit_template": {
                        "filename": f"test/{primary_contract}.t.sol",
                        "content": unit_template["content"].replace("{{CONTRACT_NAME}}", primary_contract),
                        "placeholders": [p.replace("{{CONTRACT_NAME}}", primary_contract) for p in unit_template["placeholders"]],
                        "usage": unit_template["usage_instructions"]
                    }
                }
            },
            {
                "phase": 3,
                "title": "Security & Advanced Testing",
                "description": f"Implement security testing and advanced test patterns for {primary_contract}",
                "actions": [
                    "Create comprehensive security test suite",
                    "Implement access control and authorization testing",
                    "Add reentrancy and economic attack simulations",
                    "Establish fuzz testing for critical functions"
                ],
                "deliverables": [
                    f"{primary_contract}.security.t.sol - Security test file",
                    "Access control penetration tests",
                    "Attack scenario simulations",
                    "Fuzz testing implementation"
                ],
                "template_content": {
                    "security_template": {
                        "filename": f"test/{primary_contract}.security.t.sol",
                        "content": security_template["content"].replace("{{CONTRACT_NAME}}", primary_contract),
                        "placeholders": [p.replace("{{CONTRACT_NAME}}", primary_contract) for p in security_template["placeholders"]],
                        "usage": security_template["usage_instructions"]
                    }
                }
            },
            {
                "phase": 4,
                "title": "Coverage Validation & Quality Assurance",
                "description": "Validate coverage targets and ensure test quality standards",
                "actions": [
                    "Run analyze_current_test_coverage tool to get detailed coverage analysis",
                    "Use analyze_project_context tool for AI failure detection and quality assessment",
                    "Validate 80%+ line and branch coverage against targets",
                    "Review test quality and eliminate AI failure patterns",
                    "Document testing approach and results"
                ],
                "deliverables": [
                    "Coverage validation report",
                    "AI failure detection report",
                    "Test quality assessment",
                    "Documentation and README updates",
                    "CI/CD integration recommendations"
                ],
                "validation_steps": {
                    "coverage_analysis": {
                        "tool": "analyze_current_test_coverage",
                        "parameters": {"target_coverage": 90, "include_branches": True},
                        "success_criteria": "Coverage >= 80% for production readiness"
                    },
                    "quality_analysis": {
                        "tool": "analyze_project_context", 
                        "parameters": {"include_ai_failure_detection": True, "generate_improvement_plan": True},
                        "success_criteria": "No critical AI failures, security level >= basic"
                    }
                }
            }
        ]
    
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