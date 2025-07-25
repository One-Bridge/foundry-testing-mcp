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
        self.completed_phases = []  # Track completed phases
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
            "completed_phases": self.completed_phases,
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
                
                # 🎯 NEW: MANDATORY DOMAIN ANALYSIS INTEGRATION
                logger.info("🎯 MANDATORY: Running domain analysis for workflow customization...")
                try:
                    project_sources = await self._extract_project_sources(resolved_project_path)
                    test_sources = await self._extract_test_sources(resolved_project_path)
                    
                    domain_analysis = await self._call_domain_analysis_prompt(project_sources, test_sources)
                    logger.info(f"✅ Domain analysis complete: {domain_analysis.get('primary_domain', 'General')}")
                    
                except Exception as e:
                    logger.warning(f"Domain analysis failed, using defaults: {e}")
                    domain_analysis = {
                        "primary_domain": "General",
                        "secondary_domains": [],
                        "contextual_quality_score": 0.5,
                        "missing_patterns": ["Domain analysis failed"],
                        "recommendations": ["Retry domain analysis"]
                    }
                
                # Create enhanced session with rich project context
                session_id = str(uuid.uuid4())
                session = TestingSession(session_id, resolved_project_path)
                session.project_state = project_state  # Store full project state
                session.analysis_mode = analysis_mode
                session.domain_analysis = domain_analysis  # Store domain analysis results
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
                    "domain_analysis": domain_analysis,  # NEW: LLM-driven domain classification
                    "contextual_workflows": contextual_workflows,
                    "intelligent_guidance": intelligent_guidance,
                    "session_capabilities": {
                        "ast_analysis": True,
                        "ai_failure_detection": True,
                        "contextual_workflows": True,
                        "semantic_understanding": True,
                        "llm_driven_domain_analysis": True,  # NEW capability
                        "mock_sophistication_analysis": True  # NEW capability
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
                
                # AI failure detection - run even for projects without tests
                if include_ai_failure_detection:
                    ai_failures = []
                    
                    if project_state.test_files:
                        # Analyze existing test files
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
                    
                    # Generate failure report (includes guidance for projects without tests)
                    failure_report = await self.ai_failure_detector.generate_failure_report(ai_failures)
                    
                    # Add guidance for projects without tests
                    if not project_state.test_files:
                        failure_report["no_tests_guidance"] = {
                            "status": "ready_for_testing",
                            "message": "No tests found - AI failure detection will run during test creation",
                            "prevention_strategies": [
                                "Use templates provided by the workflow to avoid common AI failures",
                                "Follow test structure patterns that prevent circular logic",
                                "Implement proper mock contracts with realistic behaviors",
                                "Add comprehensive edge case and security scenario testing"
                            ]
                        }
                    
                    analysis_result["ai_failure_analysis"] = failure_report
                
                # Generate improvement plan
                if generate_improvement_plan:
                    improvement_plan = await self._generate_comprehensive_improvement_plan(
                        project_state,
                        analysis_result.get("ai_failure_analysis", {})
                    )
                    analysis_result["improvement_plan"] = improvement_plan
                
                # Enhance recommendations based on contract analysis
                if project_state.contracts:
                    contract_specific_guidance = self._generate_contract_specific_guidance(project_state.contracts)
                    analysis_result["contract_specific_guidance"] = contract_specific_guidance
                
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
            include_branches: bool = True,
            project_path: str = ""
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
                resolved_project_path = self._resolve_project_path(project_path)
                
                # Validate project
                validation = self._validate_foundry_project(resolved_project_path)
                if not validation["is_valid"]:
                    return {
                        "status": "validation_failed",
                        "validation": validation
                    }
                
                # Generate coverage report
                coverage_result = await self.foundry_adapter.generate_coverage_report(
                    resolved_project_path, format="lcov"
                )
                
                if not coverage_result["success"]:
                    # Enhanced error analysis with specific solutions
                    error_analysis = self._analyze_coverage_failure(coverage_result)
                    
                    return {
                        "status": "error",
                        "error": "Failed to generate coverage report",
                        "details": coverage_result["stderr"],
                        "error_analysis": error_analysis,
                        "specific_solutions": error_analysis.get("solutions", []),
                        "foundry_config_suggestions": error_analysis.get("config_suggestions", {}),
                        "immediate_fix": error_analysis.get("immediate_fix", ""),
                        "suggestions": [
                            "Ensure tests exist in the test/ directory",
                            "Run 'forge test' first to verify tests work",
                            "Check that contracts exist in the src/ directory"
                        ],
                        "prevention_for_future": error_analysis.get("prevention_guidance", "")
                    }                
                analysis = {
                    "status": "success",
                    "project_path": resolved_project_path,
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
        
        # Foundry configuration validation tool
        @mcp.tool(
            name="validate_foundry_config",
            description="""
            🔧 Validate and fix foundry.toml configuration to prevent compilation errors
            
            WHEN TO USE:
            - Before running coverage analysis on complex contracts
            - After encountering "Stack too deep" compilation errors
            - Setting up new projects with optimization requirements
            - Proactive prevention of common foundry compilation issues
            
            WHAT IT DOES:
            - Checks existing foundry.toml configuration
            - Detects missing viaIR and optimizer settings
            - Provides ready-to-use foundry.toml configuration
            - Offers specific commands to fix compilation issues
            
            OUTPUTS:
            - Configuration analysis with specific recommendations
            - Ready-to-use foundry.toml content
            - Specific commands to resolve issues
            """
        )
        async def validate_foundry_config(
            prevent_stack_errors: bool = True,
            project_path: str = ""
        ) -> Dict[str, Any]:
            """
            Validate foundry.toml configuration and provide fixes for compilation issues.
            
            Args:
                prevent_stack_errors: Whether to ensure viaIR and optimizer are enabled
                project_path: Optional path to project directory
                
            Returns:
                Dictionary containing configuration analysis and recommendations
            """
            try:
                resolved_project_path = self._resolve_project_path(project_path)
                foundry_toml_path = os.path.join(resolved_project_path, "foundry.toml")
                
                analysis = {
                    "status": "analyzed",
                    "project_path": resolved_project_path,
                    "foundry_toml_exists": os.path.exists(foundry_toml_path),
                    "current_config": {},
                    "issues_found": [],
                    "recommendations": [],
                    "ready_to_use_config": "",
                    "immediate_commands": []
                }
                
                # Read existing foundry.toml if it exists
                if analysis["foundry_toml_exists"]:
                    try:
                        with open(foundry_toml_path, 'r') as f:
                            import toml
                            config = toml.load(f)
                            analysis["current_config"] = config
                    except Exception as e:
                        analysis["issues_found"].append(f"Could not parse foundry.toml: {e}")
                else:
                    analysis["issues_found"].append("foundry.toml does not exist")
                
                # Check for stack-too-deep prevention requirements
                if prevent_stack_errors:
                    default_profile = analysis["current_config"].get("profile", {}).get("default", {})
                    
                    via_ir_enabled = default_profile.get("via_ir", False)
                    optimizer_enabled = default_profile.get("optimizer", False)
                    
                    if not via_ir_enabled:
                        analysis["issues_found"].append("via_ir not enabled - required for stack-too-deep prevention")
                        analysis["recommendations"].append("Add 'via_ir = true' to [profile.default] section")
                    
                    if not optimizer_enabled:
                        analysis["issues_found"].append("optimizer not enabled - recommended for complex contracts")
                        analysis["recommendations"].append("Add 'optimizer = true' to [profile.default] section")
                
                # Generate ready-to-use configuration
                if analysis["issues_found"] or not analysis["foundry_toml_exists"]:
                    analysis["ready_to_use_config"] = """
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
via_ir = true
optimizer = true
optimizer_runs = 200
solc_version = "0.8.20"

[profile.default.fuzz]
runs = 1000

[profile.default.invariant]
runs = 1000
depth = 100
                    """.strip()
                    
                    # Commands to test the configuration
                    analysis["immediate_commands"] = [
                        "forge build --via-ir",
                        "forge test --via-ir",
                        "forge coverage --via-ir"
                    ]
                
                # Overall status
                if not analysis["issues_found"]:
                    analysis["status"] = "optimal"
                    analysis["message"] = "✅ Foundry configuration is optimal for complex contracts"
                elif analysis["foundry_toml_exists"]:
                    analysis["status"] = "needs_update"
                    analysis["message"] = f"⚠️ Found {len(analysis['issues_found'])} configuration issues"
                else:
                    analysis["status"] = "missing_config"
                    analysis["message"] = "❌ foundry.toml missing - configuration required"
                
                # Specific stack-too-deep prevention guidance
                if prevent_stack_errors:
                    analysis["stack_too_deep_prevention"] = {
                        "via_ir_enabled": analysis["current_config"].get("profile", {}).get("default", {}).get("via_ir", False),
                        "optimizer_enabled": analysis["current_config"].get("profile", {}).get("default", {}).get("optimizer", False),
                        "prevention_complete": len([r for r in analysis["recommendations"] if "via_ir" in r or "optimizer" in r]) == 0
                    }
                
                return analysis
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Error analyzing foundry configuration"
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
        
        # =================================================================
        # IMMEDIATE MCP RESOURCE ACCESS TOOL (NEW)
        # =================================================================
        @mcp.tool(
            name="get_mcp_resources_content",
            description="""
            📚 Get immediate access to all MCP resource content - DIRECT RESOURCE ACCESS
            
            WHEN TO USE:
            - Need immediate access to actual MCP resource content
            - Want concrete templates, patterns, and documentation
            - Replacing abstract testing:// references with real content
            - Quick resource lookup during development
            
            WHAT IT DOES:
            - Provides immediate access to all MCP resource content
            - Returns actual template code, testing patterns, security guidelines
            - Eliminates need for abstract testing:// URI references
            - Gives AI agents concrete, actionable content
            
            INPUTS:
            - resource_type: "all" (default), "templates", "patterns", "security", "documentation"
            
            OUTPUTS:
            - Complete MCP resource content with actual code and patterns
            - Template content with usage instructions
            - Security testing patterns and guidelines
            - Testing documentation and best practices
            
            WORKFLOW: Use anytime you need actual MCP resource content instead of references.
            """
        )
        async def get_mcp_resources_content(
            resource_type: str = "all"
        ) -> Dict[str, Any]:
            """
            Get immediate access to all MCP resource content.
            
            Args:
                resource_type: Type of resources to retrieve ("all", "templates", "patterns", "security", "documentation")
                
            Returns:
                Dictionary containing all requested MCP resource content
            """
            try:
                logger.info(f"🔍 Retrieving MCP resource content: {resource_type}")
                
                resource_content = {
                    "status": "success",
                    "resource_type": resource_type,
                    "usage_note": "✅ Use this actual content instead of abstract testing:// references",
                    "content": {}
                }
                
                if not self.testing_resources:
                    return {
                        "status": "error",
                        "error": "TestingResources not initialized",
                        "fallback_guidance": [
                            "Testing resources are not available",
                            "Use embedded_mcp_resources from workflow outputs instead",
                            "Check server initialization logs for resource loading issues"
                        ]
                    }
                
                # Get templates content directly from filesystem
                if resource_type in ["all", "templates"]:
                    try:
                        templates_content = await self._get_all_templates()
                        resource_content["content"]["templates"] = templates_content
                        logger.info("✅ Templates content loaded successfully from filesystem")
                    except Exception as e:
                        logger.warning(f"Could not load templates: {e}")
                        resource_content["content"]["templates"] = {"error": str(e)}
                
                # Get foundry patterns content
                if resource_type in ["all", "patterns"]:
                    try:
                        patterns_content = await self._get_foundry_patterns()
                        resource_content["content"]["foundry_patterns"] = patterns_content
                        logger.info("✅ Foundry patterns content loaded successfully")
                    except Exception as e:
                        logger.warning(f"Could not load foundry patterns: {e}")
                        resource_content["content"]["foundry_patterns"] = {"error": str(e)}
                
                # Get security patterns content
                if resource_type in ["all", "security"]:
                    try:
                        security_content = await self._get_security_patterns()
                        resource_content["content"]["security_patterns"] = security_content
                        logger.info("✅ Security patterns content loaded successfully")
                    except Exception as e:
                        logger.warning(f"Could not load security patterns: {e}")
                        resource_content["content"]["security_patterns"] = {"error": str(e)}
                
                # Get documentation content
                if resource_type in ["all", "documentation"]:
                    try:
                        documentation_content = await self._get_testing_documentation()
                        resource_content["content"]["documentation"] = documentation_content
                        logger.info("✅ Documentation content loaded successfully")
                    except Exception as e:
                        logger.warning(f"Could not load documentation: {e}")
                        resource_content["content"]["documentation"] = {"error": str(e)}
                
                # Add usage instructions
                resource_content["usage_instructions"] = {
                    "templates": "Use content.templates.{template_name}.content for actual template code",
                    "foundry_patterns": "Reference content.foundry_patterns.content.{pattern_category} for specific patterns",
                    "security_patterns": "Use content.security_patterns.categories.{security_type} for security guidelines",
                    "documentation": "Reference content.documentation.sections.{section_name} for testing guidance",
                    "best_practice": "🎯 ALWAYS use this actual content instead of abstract testing:// URIs"
                }
                
                # Add quick access examples
                resource_content["quick_access_examples"] = [
                    "📋 Template access: content.templates.unit.content",
                    "🏗️ File structure: content.foundry_patterns.content.test_organization.file_structure_pattern",
                    "🛡️ Security tests: content.security_patterns.categories.reentrancy.test_patterns",
                    "📚 Best practices: content.documentation.sections.testing_best_practices",
                    "🔒 Proxy testing: content.security_patterns.categories.proxy_patterns.test_patterns",
                    "🔄 Proxy template: content.templates.proxy.content"
                ]
                
                logger.info(f"✅ Successfully loaded {resource_type} MCP resources")
                return resource_content
                
            except Exception as e:
                logger.error(f"Error retrieving MCP resources: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "fallback_guidance": [
                        "Check that TestingResources is properly initialized",
                        "Verify that MCP resource files are accessible",
                        "Use embedded_mcp_resources from workflow outputs as alternative",
                        "Check server logs for resource loading errors"
                    ]
                }
        
        logger.info("Testing tools registered successfully")
    
    # Template access helper methods
    async def _get_template_content(self, template_type: str) -> Dict[str, Any]:
        """Get template content from actual template files in templates/ directory."""
        try:
            # Map template types to actual file names in your templates/ directory
            template_files = {
                "unit": "test_contract_template.sol",
                "integration": "integration_test_template.sol", 
                "invariant": "invariant_test_template.sol",
                "helper": "test_helper_template.sol",
                "proxy": "proxy_test_template.sol"
                # Add more as you create them: "security", "fork", etc.
            }
            
            template_file = template_files.get(template_type)
            if not template_file:
                return {
                    "name": f"{template_type.title()} Template",
                    "content": f"# Template type '{template_type}' not found",
                    "placeholders": [],
                    "usage_instructions": ["Template not available"],
                    "error": f"No template file mapped for type: {template_type}"
                }
            
            # Build path to template file (MCP root/templates/)
            mcp_root = os.path.dirname(os.path.dirname(__file__))  # Go up from components/
            template_path = os.path.join(mcp_root, "templates", template_file)
            
            if not os.path.exists(template_path):
                return {
                    "name": f"{template_type.title()} Template",
                    "content": f"# Template file not found: {template_path}",
                    "placeholders": [],
                    "usage_instructions": ["Template file missing"],
                    "error": f"Template file does not exist: {template_path}"
                }
            
            # Read the actual template file
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Extract placeholders from the template content
            import re
            placeholders = list(set(re.findall(r'\{\{([^}]+)\}\}', template_content)))
            
            return {
                "name": f"{template_type.title()} Test Template",
                "description": f"Production-ready template for {template_type} testing scenarios from {template_file}",
                "template_type": template_type,
                "content": template_content,
                "placeholders": sorted(placeholders),  # Sort for consistency
                "usage_instructions": self._get_template_usage_instructions(template_type),
                "source_file": template_path,
                "file_size": len(template_content),
                "placeholder_count": len(placeholders)
            }
            
        except Exception as e:
            logger.warning(f"Could not load {template_type} template: {e}")
            return {
                "name": f"{template_type.title()} Template",
                "content": f"# Template loading error: {e}",
                "placeholders": [],
                "usage_instructions": ["Template could not be loaded"],
                "error": str(e)
            }

    async def _get_all_templates(self) -> Dict[str, Any]:
        """Get all available test templates with their content."""
        try:
            templates = {}
            template_types = ["unit", "integration", "invariant", "helper", "proxy"]
            
            for template_type in template_types:
                try:
                    template_content = await self._get_template_content(template_type)
                    templates[template_type] = template_content
                except Exception as e:
                    logger.warning(f"Could not load {template_type} template: {e}")
                    templates[template_type] = {"error": str(e)}
            
            return {
                "name": "Available Test Templates",
                "description": "Comprehensive test templates for different testing scenarios",
                "templates": templates,
                "usage_note": "Use templates[template_type].content for the actual Solidity code"
            }
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return {"error": str(e)}
    
    async def _get_security_patterns(self) -> Dict[str, Any]:
        """Get security testing patterns and guidelines."""
        return {
            "name": "Security Testing Patterns",
            "description": "Comprehensive security testing patterns for smart contract auditing",
            "categories": {
                "reentrancy": {
                    "description": "Testing for reentrancy vulnerabilities",
                    "test_patterns": [
                        "Mock external contracts to simulate reentrancy attacks",
                        "Test function state before and after external calls",
                        "Verify reentrancy guards block recursive calls",
                        "Test cross-function reentrancy scenarios"
                    ],
                    "example_test": '''
function test_transfer_reentrancyAttack_shouldRevert() public {
    // Setup malicious contract that attempts reentrancy
    MaliciousReceiver attacker = new MaliciousReceiver(address(token));
    
    vm.expectRevert("ReentrancyGuard: reentrant call");
    attacker.initiateAttack();
}'''
                },
                "access_control": {
                    "description": "Testing access control mechanisms",
                    "test_patterns": [
                        "Test unauthorized access attempts",
                        "Verify role-based permissions", 
                        "Test privilege escalation scenarios",
                        "Validate ownership transfer security"
                    ]
                },
                "oracle_manipulation": {
                    "description": "Testing oracle price manipulation resistance",
                    "test_patterns": [
                        "Mock oracle to return extreme prices",
                        "Test time-weighted average price (TWAP) resistance",
                        "Verify circuit breakers activate",
                        "Test oracle failure scenarios"
                    ]
                },
                "flash_loan_attacks": {
                    "description": "Testing flash loan attack resistance",
                    "test_patterns": [
                        "Simulate large flash loan operations",
                        "Test price manipulation via flash loans",
                        "Verify borrowing limits and restrictions",
                        "Test arbitrage protection mechanisms"
                    ]
                },
                "proxy_patterns": {
                    "description": "Testing proxy pattern implementations",
                    "test_patterns": [
                        "Test proxy upgrade mechanisms",
                        "Verify state preservation across upgrades",
                        "Test admin access controls for upgrades",
                        "Verify implementation contract isolation"
                    ]
                }
            }
        }
    
    async def _get_testing_documentation(self) -> Dict[str, Any]:
        """Get comprehensive testing documentation and best practices."""
        return {
            "name": "Smart Contract Testing Documentation",
            "description": "Comprehensive guide for professional smart contract testing",
            "sections": {
                "testing_best_practices": {
                    "title": "Testing Best Practices",
                    "content": [
                        "Write descriptive test names that explain what is being tested",
                        "Use the AAA pattern: Arrange, Act, Assert",
                        "Test both positive and negative scenarios",
                        "Mock external dependencies appropriately",
                        "Aim for high code coverage but focus on critical paths",
                        "Use property-based testing for complex logic",
                        "Test edge cases and boundary conditions"
                    ]
                },
                "coverage_guidelines": {
                    "title": "Coverage Guidelines", 
                    "content": [
                        "Aim for 90%+ line coverage on critical contracts",
                        "Prioritize branch coverage over line coverage",
                        "Focus coverage on business logic and security-critical functions",
                        "Don't ignore uncovered error paths",
                        "Use integration tests to cover cross-contract interactions"
                    ]
                },
                "security_testing": {
                    "title": "Security Testing Methodology",
                    "content": [
                        "Follow the OWASP Smart Contract Security Testing methodology",
                        "Test for common vulnerabilities: reentrancy, overflow, access control",
                        "Use invariant testing for critical system properties",
                        "Simulate economic attacks and arbitrage scenarios",
                        "Test with realistic attacker models and capabilities"
                    ]
                },
                "proxy_testing": {
                    "title": "Proxy Pattern Testing",
                    "content": [
                        "Always test through the proxy address, not implementation",
                        "Test state preservation across upgrades",
                        "Verify admin controls for upgrade functions",
                        "Test initialization functions can only be called once",
                        "For Diamond patterns, test facet addition/removal/replacement"
                    ]
                }
            }
        }
    
    def _get_template_usage_instructions(self, template_type: str) -> List[str]:
        """Get usage instructions for a template type."""
        instructions = {
            "unit": [
                "Replace {{CONTRACT_NAME}} with your contract name",
                "Replace {{CONTRACT_INSTANCE}} with lowercase instance name", 
                "Fill in {{CONSTRUCTOR_ARGS}} with actual constructor parameters",
                "Add specific test functions for your contract's methods",
                "Update {{CORE_FUNCTION_TESTS}} with your actual function tests",
                "Customize {{INITIAL_STATE_ASSERTIONS}} for your contract's initial state"
            ],
            "integration": [
                "Replace {{PRIMARY_CONTRACT}} and {{SECONDARY_CONTRACT}} with actual contract names",
                "Update import paths to match your project structure",
                "Customize {{PRIMARY_CONSTRUCTOR_ARGS}} and {{SECONDARY_CONSTRUCTOR_ARGS}}",
                "Define {{ADDITIONAL_CONTRACT_INSTANCES}} if you have more contracts",
                "Add your specific workflow logic in the test functions"
            ],
            "invariant": [
                "Replace {{CONTRACT_NAME}} with your contract name",
                "Fill in {{CONSTRUCTOR_ARGS}} with actual constructor parameters",
                "Define specific invariants in the invariant functions",
                "Add targeted functions for fuzz testing",
                "Customize {{STATE_CONSISTENCY_CHECKS}} for your business logic"
            ],
            "helper": [
                "Replace {{CONTRACT_NAME}} with your contract name",
                "Define {{TEST_DATA_TYPE}} structure for your test data",
                "Customize scenario setups ({{SCENARIO_1_SETUP}}, etc.)",
                "Add your specific {{STATE_ASSERTIONS}} logic",
                "Define workflow steps for your contract's operations"
            ],
            "proxy": [
                "Replace {{IMPLEMENTATION_CONTRACT}} with your implementation contract name",
                "Replace {{IMPLEMENTATION_V2_CONTRACT}} with your V2 contract for upgrade testing",
                "Choose {{PROXY_TYPE}} (TransparentUpgradeableProxy, ERC1967Proxy, or Diamond)",
                "Fill in {{PROXY_SETUP}} with the appropriate setup function call",
                "Define {{INITIALIZATION_PARAMS}} for your contract's initialize function",
                "Customize {{STATE_GETTER}} and {{SETTER_FUNCTION}} for your contract's interface",
                "CRITICAL: Always test through proxy address, never implementation directly"
            ]
        }
        
        return instructions.get(template_type, [
            f"Customize the {template_type} template for your specific use case",
            "Replace placeholder values with your contract details",
            "Add test logic specific to your contract's functionality"
        ])
    
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
        
        # =================================================================
        # INJECT ACTUAL MCP RESOURCE CONTENT (NO MORE ABSTRACT REFERENCES)
        # =================================================================
        logger.info("📚 Injecting actual MCP resource content for immediate use...")
        
        try:
            # Load all actual MCP resource content
            embedded_resources = {}
            
            if self.testing_resources:
                # Get actual foundry patterns content
                try:
                    foundry_patterns_content = await self.testing_resources.get_foundry_testing_patterns()
                    embedded_resources["foundry_patterns"] = foundry_patterns_content
                except Exception as e:
                    logger.warning(f"Could not load foundry patterns: {e}")
                    embedded_resources["foundry_patterns"] = {"error": str(e)}
                
                # Get actual security patterns content
                try:
                    security_patterns_content = await self.testing_resources.get_security_testing_patterns()
                    embedded_resources["security_patterns"] = security_patterns_content
                except Exception as e:
                    logger.warning(f"Could not load security patterns: {e}")
                    embedded_resources["security_patterns"] = {"error": str(e)}
                
                # Get actual available templates content
                try:
                    templates_content = await self.testing_resources.get_available_templates()
                    embedded_resources["available_templates"] = templates_content
                except Exception as e:
                    logger.warning(f"Could not load templates: {e}")
                    embedded_resources["available_templates"] = {"error": str(e)}
                
                # Get testing documentation content
                try:
                    documentation_content = await self.testing_resources.get_testing_documentation()
                    embedded_resources["testing_documentation"] = documentation_content
                except Exception as e:
                    logger.warning(f"Could not load documentation: {e}")
                    embedded_resources["testing_documentation"] = {"error": str(e)}
            
            # Add embedded resources to base plan
            base_plan["embedded_mcp_resources"] = {
                "usage_note": "🎯 CRITICAL: Use this actual content instead of abstract testing:// references",
                "foundry_patterns_content": embedded_resources.get("foundry_patterns", {}),
                "security_patterns_content": embedded_resources.get("security_patterns", {}),
                "available_templates_content": embedded_resources.get("available_templates", {}),
                "testing_documentation_content": embedded_resources.get("testing_documentation", {}),
                "resource_access_instructions": [
                    "✅ DO: Reference specific patterns from foundry_patterns_content.content",
                    "✅ DO: Use actual template content from available_templates_content.templates",
                    "✅ DO: Follow security patterns from security_patterns_content.categories",
                    "❌ DON'T: Reference abstract testing://foundry-patterns URIs",
                    "❌ DON'T: Use placeholder template references",
                    "🎯 EXAMPLE: Use foundry_patterns_content.content.test_organization.file_structure_pattern"
                ]
            }
            
            logger.info("✅ MCP resource content successfully embedded in workflow plan")
            
        except Exception as e:
            logger.error(f"Failed to inject MCP resource content: {e}")
            base_plan["embedded_mcp_resources"] = {
                "error": str(e),
                "fallback_note": "Resource injection failed - using fallback guidance"
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
        """Execute a specific workflow phase with MANDATORY MCP tool integration and AI failure prevention."""
        phase_number = phase.get("phase", 0)
        phase_title = phase.get('title', 'Unknown')
        logger.info(f"🚀 Executing phase {phase_number}: {phase_title}")
        
        # Initialize enhanced validation results
        validation_results = {}
        mandatory_tool_results = {}
        ai_failure_guidance = {}
        
        # =================================================================
        # PHASE 1: MANDATORY AI FAILURE PREVENTION INJECTION (BEGINNING)
        # =================================================================
        if phase_number == 1:
            logger.info("🛡️ MANDATORY: Injecting AI failure prevention guidance...")
            try:
                # Get AI failure prevention strategies before any test writing
                ai_prevention_analysis = await self.analyze_project_context(
                    include_ai_failure_detection=True,
                    generate_improvement_plan=False,  # Just need prevention guidance
                    project_path=session.project_path
                )
                
                # Extract prevention strategies
                prevention_strategies = []
                if "ai_failure_analysis" in ai_prevention_analysis:
                    failure_report = ai_prevention_analysis["ai_failure_analysis"]
                    if "no_tests_guidance" in failure_report:
                        prevention_strategies = failure_report["no_tests_guidance"].get("prevention_strategies", [])
                
                ai_failure_guidance["prevention_injection"] = {
                    "status": "mandatory_guidance_provided",
                    "critical_prevention_strategies": prevention_strategies or [
                        "Use templates provided by the workflow to avoid common AI failures",
                        "Follow test structure patterns that prevent circular logic", 
                        "Implement proper mock contracts with realistic behaviors",
                        "Add comprehensive edge case and security scenario testing"
                    ],
                    "anti_patterns_to_avoid": [
                        "❌ NEVER test contract methods against themselves (circular logic)",
                        "❌ NEVER create mocks that always return expected values",
                        "❌ NEVER skip error condition testing",
                        "❌ NEVER use assertTrue(true) or similar always-passing assertions"
                    ],
                    "enforcement_note": "These guidelines MUST be followed during test creation"
                }
                mandatory_tool_results["ai_prevention_analysis"] = ai_prevention_analysis
                
            except Exception as e:
                logger.warning(f"AI failure prevention injection failed: {e}")
                ai_failure_guidance["prevention_injection"] = {"error": str(e)}
        
        # =================================================================
        # PHASE 2: MANDATORY PRE-TEST AI FAILURE DETECTION + MOCK ANALYSIS
        # =================================================================
        if phase_number == 2:  # Core Unit Test Implementation
            logger.info("🔍 MANDATORY: Running AI failure detection before test creation...")
            try:
                ai_analysis = await self.analyze_project_context(
                    include_ai_failure_detection=True,
                    generate_improvement_plan=True,
                    project_path=session.project_path
                )
                
                # Extract actionable guidance for test creation
                ai_failure_guidance["pre_test_analysis"] = {
                    "status": ai_analysis.get("ai_failure_analysis", {}).get("status", "unknown"),
                    "critical_requirements": [
                        "🎯 USE INDEPENDENT EXPECTED VALUES: Calculate expected results outside the contract",
                        "🎯 CREATE REALISTIC MOCKS: Mocks must be configurable and can fail",
                        "🎯 TEST ERROR CONDITIONS: Every function needs failure scenario tests",
                        "🎯 AVOID CIRCULAR LOGIC: Never validate contract methods against themselves"
                    ],
                    "template_enforcement": "Use provided templates exactly - they prevent common AI failures",
                    "quality_gate": "All tests will be reviewed for AI failure patterns at completion"
                }
                mandatory_tool_results["pre_test_ai_analysis"] = ai_analysis
                
            except Exception as e:
                logger.error(f"CRITICAL: Pre-test AI analysis failed: {e}")
                ai_failure_guidance["pre_test_analysis"] = {"error": str(e)}
            
            # 🛡️ NEW: MANDATORY MOCK SOPHISTICATION QUALITY GATE
            logger.info("🛡️ MANDATORY: Running mock sophistication analysis quality gate...")
            try:
                mock_contracts = await self._extract_mock_contracts(session.project_path)
                target_contracts = await self._extract_project_sources(session.project_path)
                
                mock_analysis = await self._call_mock_analysis_prompt(
                    mock_contracts=mock_contracts,
                    target_contracts=target_contracts,
                    test_context="Core Unit Test Implementation - Phase 2"
                )
                
                sophistication_score = mock_analysis.get("overall_sophistication_score", 0.0)
                logger.info(f"🛡️ Mock sophistication score: {sophistication_score:.2f}")
                
                # QUALITY GATE: Block progression if mocks are insufficient
                if sophistication_score < 0.6:
                    ai_failure_guidance["mock_quality_gate"] = {
                        "status": "BLOCKED",
                        "reason": f"Mock contracts below quality threshold (score: {sophistication_score:.2f}, required: 0.6)",
                        "critical_issues": mock_analysis.get("critical_gaps", []),
                        "required_actions": mock_analysis.get("immediate_actions", []),
                        "cannot_proceed_until": "Mock sophistication score >= 0.6",
                        "blocking_severity": "CRITICAL"
                    }
                    logger.warning(f"🚨 QUALITY GATE BLOCKED: Mock sophistication {sophistication_score:.2f} < 0.6")
                else:
                    ai_failure_guidance["mock_quality_gate"] = {
                        "status": "PASSED",
                        "score": sophistication_score,
                        "message": "Mock contracts meet quality standards for production testing"
                    }
                    logger.info(f"✅ Mock quality gate PASSED: {sophistication_score:.2f}")
                
                mandatory_tool_results["mock_sophistication_analysis"] = mock_analysis
                
            except Exception as e:
                logger.error(f"CRITICAL: Mock analysis failed: {e}")
                ai_failure_guidance["mock_quality_gate"] = {
                    "status": "ERROR",
                    "error": str(e),
                    "message": "Mock analysis failed - proceed with caution"
                }
        
        # =================================================================
        # EXECUTE EXISTING VALIDATION STEPS
        # =================================================================
        if "validation_steps" in phase:
            for step_name, step_config in phase["validation_steps"].items():
                try:
                    validation_results[step_name] = await self._execute_validation_step(
                        step_config, session.project_path
                    )
                except Exception as e:
                    logger.warning(f"Validation step {step_name} failed: {e}")
                    validation_results[step_name] = {"error": str(e)}
        
        # =================================================================
        # MANDATORY COVERAGE VALIDATION AFTER TEST CREATION
        # =================================================================
        if phase_number in [2, 3, 4]:  # After any test creation phase
            logger.info("📊 MANDATORY: Running coverage analysis...")
            try:
                coverage_analysis = await self.analyze_current_test_coverage(
                    target_coverage=90,
                    include_branches=True,
                    project_path=session.project_path
                )
                
                mandatory_tool_results["coverage_validation"] = coverage_analysis
                
                # Add coverage enforcement guidance
                coverage_pct = coverage_analysis.get("coverage_data", {}).get("coverage_percentage", 0)
                ai_failure_guidance["coverage_enforcement"] = {
                    "current_coverage": f"{coverage_pct}%",
                    "target_coverage": "90%",
                    "status": "meets_target" if coverage_pct >= 90 else "needs_improvement",
                    "next_action": "Continue to next phase" if coverage_pct >= 80 else "Add more tests before proceeding"
                }
                
            except Exception as e:
                logger.info(f"Coverage analysis not available yet: {e}")
                ai_failure_guidance["coverage_enforcement"] = {"status": "not_available", "reason": str(e)}
        
        # =================================================================
        # PHASE 4: COMPREHENSIVE AI FAILURE REVIEW (END-TO-END)
        # =================================================================
        if phase_number == 4:  # Coverage Validation & Quality Assurance
            logger.info("🔬 MANDATORY: Comprehensive AI failure detection on completed test suite...")
            try:
                comprehensive_ai_review = await self.analyze_project_context(
                    include_ai_failure_detection=True,
                    generate_improvement_plan=True,
                    project_path=session.project_path
                )
                
                # Extract comprehensive failure analysis
                failure_report = comprehensive_ai_review.get("ai_failure_analysis", {})
                ai_failure_guidance["comprehensive_review"] = {
                    "status": failure_report.get("status", "unknown"),
                    "total_failures": failure_report.get("total_failures", 0),
                    "critical_failures": failure_report.get("critical_count", 0),
                    "high_priority_failures": failure_report.get("high_count", 0),
                    "quality_verdict": self._determine_test_quality_verdict(failure_report),
                    "improvement_requirements": failure_report.get("top_recommendations", []),
                    "auto_fixable_count": failure_report.get("auto_fixable_count", 0)
                }
                
                mandatory_tool_results["comprehensive_ai_review"] = comprehensive_ai_review
                
            except Exception as e:
                logger.error(f"CRITICAL: Comprehensive AI review failed: {e}")
                ai_failure_guidance["comprehensive_review"] = {"error": str(e)}
        
        # =================================================================
        # BASELINE COVERAGE (EXISTING LOGIC)
        # =================================================================
        if phase_number == 1:
            try:
                baseline_coverage = await self._get_baseline_coverage(session.project_path)
                validation_results["baseline_coverage"] = baseline_coverage
            except Exception as e:
                logger.info(f"No baseline coverage available: {e}")
        
        # Enhanced phase execution with real deliverables
        session.completed_phases.append(phase_number)
        session.current_phase = phase_number + 1
        
        # =================================================================
        # ENHANCED RESULT WITH MANDATORY TOOL INTEGRATION
        # =================================================================
        result = {
            "phase": phase_number,
            "title": phase_title,
            "status": "completed",
            "actions_completed": phase.get("actions", []),
            "deliverables_generated": phase.get("deliverables", []),
            "validation_results": validation_results,
            "mandatory_tool_results": mandatory_tool_results,
            "ai_failure_guidance": ai_failure_guidance,
            "success": True,
            "tool_integration_note": "This phase executed mandatory MCP tool calls for enhanced quality assurance",
            "next_phase_todo_list": self._generate_next_phase_todo_list(phase_number, session)
        }
        
        # Add template content if available
        if "template_content" in phase:
            result["template_content"] = phase["template_content"]
        
        return result
    
    def _determine_test_quality_verdict(self, failure_report: Dict[str, Any]) -> str:
        """Determine overall test quality verdict based on AI failure analysis."""
        status = failure_report.get("status", "unknown")
        critical_count = failure_report.get("critical_count", 0)
        total_failures = failure_report.get("total_failures", 0)
        
        if status == "clean":
            return "🟢 EXCELLENT: No AI failures detected"
        elif critical_count == 0 and total_failures <= 3:
            return "🟡 GOOD: Minor issues detected, easily fixable"
        elif critical_count <= 2:
            return "🟠 NEEDS IMPROVEMENT: Some critical issues require attention"
        else:
            return "🔴 POOR: Multiple critical failures require immediate fixes"
    
    async def _execute_validation_step(self, step_config: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Execute a validation step using the specified tool."""
        tool_name = step_config.get("tool")
        parameters = step_config.get("parameters", {})
        
        if tool_name == "analyze_current_test_coverage":
            # Call the coverage analysis tool
            return await self.analyze_current_test_coverage(
                target_coverage=parameters.get("target_coverage", 90),
                include_branches=parameters.get("include_branches", True),
                project_path=project_path
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
                return await self.analyze_current_test_coverage(target_coverage=80, project_path=project_path)
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
    

    def _analyze_coverage_failure(self, coverage_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze specific coverage failure types and provide targeted solutions.
        
        This method detects common compilation errors like "Stack too deep" and
        provides specific solutions including foundry.toml configuration fixes.
        
        Args:
            coverage_result: The failed coverage result from foundry_adapter
            
        Returns:
            Detailed error analysis with specific solutions
        """
        stderr = coverage_result.get("stderr", "")
        
        # Stack too deep detection
        if "Stack too deep" in stderr:
            location = self._extract_error_location(stderr)
            return {
                "error_type": "stack_too_deep",
                "severity": "critical", 
                "description": "Solidity compilation failed due to too many local variables",
                "specific_location": location,
                "solutions": [
                    "Add 'via_ir = true' to foundry.toml [profile.default] section",
                    "Enable optimizer with 'optimizer = true' in foundry.toml",
                    "Use 'forge coverage --ir-minimum' for minimal optimization",
                    f"Refactor contract function at {location} to reduce local variables"
                ],
                "config_suggestions": {
                    "foundry_toml": {
                        "profile.default.via_ir": True,
                        "profile.default.optimizer": True,
                        "profile.default.optimizer_runs": 200
                    }
                },
                "prevention_guidance": "Add foundry.toml optimization settings before contract development",
                "immediate_fix": """
Create or update foundry.toml with:

[profile.default]
via_ir = true
optimizer = true
optimizer_runs = 200

Then run: forge coverage --via-ir
                """.strip()
            }
        
        # Compiler version issues  
        elif "nightly build" in stderr:
            return {
                "error_type": "nightly_version_warning",
                "severity": "medium",
                "description": "Using Foundry nightly build instead of stable version",
                "solutions": [
                    "Set FOUNDRY_DISABLE_NIGHTLY_WARNING=true environment variable",
                    "Switch to stable Foundry version: foundryup --version nightly",
                    "Add environment variable to shell profile for permanent fix"
                ],
                "immediate_fix": "export FOUNDRY_DISABLE_NIGHTLY_WARNING=true"
            }
        
        # Optimizer disabled warning
        elif "optimizer settings" in stderr and "disabled for accurate coverage" in stderr:
            return {
                "error_type": "optimizer_disabled_for_coverage",
                "severity": "low",
                "description": "Foundry automatically disabled optimizer for coverage accuracy",
                "solutions": [
                    "This is normal behavior for coverage analysis",
                    "Use --ir-minimum if encountering stack too deep errors",
                    "Enable viaIR in foundry.toml for complex contracts"
                ]
            }
            
        # Generic compilation errors
        elif "Compiler run failed" in stderr:
            return {
                "error_type": "compilation_error",
                "severity": "high", 
                "description": "General Solidity compilation failure",
                "solutions": [
                    "Check contract syntax and imports",
                    "Verify Solidity version compatibility in foundry.toml",
                    "Review compiler warnings in the error output",
                    "Try compiling with 'forge build' first to isolate the issue"
                ]
            }
        
        # Default analysis for unknown errors
        return {
            "error_type": "unknown_coverage_error",
            "severity": "medium",
            "description": "Coverage analysis failed for unknown reasons",
            "solutions": [
                "Ensure tests exist in test/ directory",
                "Run 'forge test' first to verify tests compile and pass",
                "Check that contracts exist in src/ directory",
                "Verify foundry.toml configuration is valid"
            ]
        }
    
    def _extract_error_location(self, stderr: str) -> str:
        """Extract specific file and line location from compiler error."""
        import re
        
        # Look for --> file:line:column pattern
        location_match = re.search(r'-->s+([^:]+):(d+):(d+)', stderr)
        if location_match:
            file_path, line_num, col_num = location_match.groups()
            return f"{file_path}:{line_num}:{col_num}"
        
        # Look for Error in contract pattern  
        contract_match = re.search(r'Error.*?([A-Z][a-zA-Z0-9]+.sol)', stderr)
        if contract_match:
            return contract_match.group(1)
            
        return "Unknown location"
    
    def _get_stack_too_deep_solutions(self, location: str = "") -> Dict[str, Any]:
        """Get specific solutions for stack too deep errors."""
        base_location = location.split(":")[ 0] if location else "affected contract"
        
        return {
            "immediate_fixes": [
                {
                    "method": "foundry_config",
                    "description": "Add viaIR and optimizer to foundry.toml",
                    "config": """
[profile.default]
via_ir = true
optimizer = true
optimizer_runs = 200
solc_version = "0.8.20"
                    """.strip(),
                    "command": "forge coverage --via-ir"
                },
                {
                    "method": "minimal_ir",
                    "description": "Use minimal IR optimization",
                    "command": "forge coverage --ir-minimum"
                }
            ],
            "code_refactoring": [
                f"Reduce local variables in {base_location}",
                "Split complex functions into smaller ones",
                "Use function parameters instead of local variables",
                "Consider using structs to group related variables"
            ],
            "prevention": [
                "Set up foundry.toml with viaIR from project start",
                "Use --via-ir flag in development workflow",
                "Monitor function complexity during development"
            ]
        }
    def _generate_contract_specific_guidance(self, contracts: List) -> Dict[str, Any]:
        """Generate specific testing guidance based on contract analysis."""
        guidance = {
            "contract_types_detected": [],
            "security_priorities": [],
            "testing_strategies": [],
            "risk_assessment": "low"
        }
        
        high_risk_contracts = []
        defi_contracts = []
        
        for contract in contracts:
            guidance["contract_types_detected"].append({
                "name": contract.contract_name,
                "type": contract.contract_type,
                "risk_score": contract.risk_score,
                "security_patterns": contract.security_patterns
            })
            
            # Track high-risk contracts
            if contract.risk_score > 0.6:
                high_risk_contracts.append(contract)
            
            # Track DeFi contracts for specific guidance
            if contract.contract_type == "defi":
                defi_contracts.append(contract)
        
        # Generate risk assessment
        max_risk = max((c.risk_score for c in contracts), default=0.1)
        if max_risk > 0.7:
            guidance["risk_assessment"] = "critical"
        elif max_risk > 0.5:
            guidance["risk_assessment"] = "high" 
        elif max_risk > 0.3:
            guidance["risk_assessment"] = "medium"
        else:
            guidance["risk_assessment"] = "low"
        
        # Generate security priorities
        all_patterns = set()
        for contract in contracts:
            all_patterns.update(contract.security_patterns)
        
        priority_map = {
            "flash_loans": "Critical: Test flash loan attack vectors and reentrancy protection",
            "oracle_usage": "High: Test oracle manipulation and price feed validation",
            "access_control": "High: Test role-based access control and privilege escalation",
            "reentrancy": "Critical: Verify reentrancy protection in all state-changing functions",
            "governance": "Medium: Test governance mechanisms and voting processes"
        }
        
        for pattern in all_patterns:
            if pattern in priority_map:
                guidance["security_priorities"].append(priority_map[pattern])
        
        # Generate testing strategies based on contract types
        if defi_contracts:
            guidance["testing_strategies"].extend([
                "Implement comprehensive fuzz testing for financial calculations",
                "Test deposit/withdrawal workflows with edge cases",
                "Verify slippage protection and MEV resistance",
                "Test integration with external price feeds and oracles",
                "Implement invariant testing for core financial properties"
            ])
        
        if any(c.contract_type == "governance" for c in contracts):
            guidance["testing_strategies"].extend([
                "Test voting mechanisms and quorum requirements",
                "Verify timelock and execution delays",
                "Test delegation and vote weight calculations"
            ])
        
        if any(c.contract_type == "token" for c in contracts):
            guidance["testing_strategies"].extend([
                "Test ERC20 compliance and standard functions",
                "Verify mint/burn mechanics and total supply consistency",
                "Test approval and allowance mechanisms"
            ])
        
        return guidance
    
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
        """Generate intelligent next steps with MANDATORY tool sequences and enforcement."""
        
        # =================================================================
        # MANDATORY TOOL SEQUENCE GENERATION (NEW APPROACH)
        # =================================================================
        base_next_steps = {
            "immediate_priority": "",
            "recommended_tool": "",
            "specific_actions": [],
            "alternative_paths": [],
            "mandatory_tool_sequence": [],
            "enforcement_note": "🚨 CRITICAL: All tools in mandatory_tool_sequence MUST be called. Do not skip any step.",
            "resource_enforcement": "Use embedded_mcp_resources content provided in workflow outputs instead of abstract testing:// references",
            "cursor_ai_todo_list": {
                "title": "🚨 MANDATORY TODO LIST - Smart Contract Testing Workflow",
                "instructions": "✅ Complete each todo item sequentially. Each tool call provides data for subsequent steps.",
                "phase_todos": []
            }
        }
        
        # =================================================================
        # PHASE-BASED MANDATORY TOOL SEQUENCES
        # =================================================================
        
        if project_state.testing_phase == TestingPhase.NONE:
            base_next_steps.update({
                "immediate_priority": "Execute comprehensive testing initialization sequence",
                "recommended_tool": "MANDATORY SEQUENCE: Follow all 3 steps below",
                "mandatory_tool_sequence": [
                    {
                        "step": 1,
                        "tool_name": "analyze_project_context",
                        "parameters": {
                            "include_ai_failure_detection": True,
                            "generate_improvement_plan": True
                        },
                        "mandatory": True,
                        "reason": "🛡️ CRITICAL: Get AI failure prevention guidance before any test creation",
                        "expected_output": "AI failure analysis with prevention strategies",
                        "success_criteria": "Must receive ai_failure_analysis section with prevention strategies"
                    },
                    {
                        "step": 2,
                        "tool_name": "execute_testing_workflow",
                        "parameters": {
                            "workflow_type": "from_scratch",
                            "objectives": "Create comprehensive test suite with 90% coverage and AI failure prevention",
                            "scope": "comprehensive"
                        },
                        "mandatory": True,
                        "reason": "🎯 IMPLEMENTATION: Execute structured testing with embedded MCP resources",
                        "expected_output": "4-phase workflow with embedded templates and patterns",
                        "success_criteria": "Must receive embedded_mcp_resources content for immediate use"
                    },
                    {
                        "step": 3,
                        "tool_name": "analyze_current_test_coverage",
                        "parameters": {
                            "target_coverage": 90,
                            "include_branches": True
                        },
                        "mandatory": True,
                        "reason": "📊 VALIDATION: Ensure coverage targets are achieved",
                        "expected_output": "Coverage report with gap analysis",
                        "success_criteria": "Must validate coverage progress against 90% target"
                    }
                ],
                "specific_actions": [
                    "🚨 MUST FOLLOW: Execute all 3 mandatory tools in sequence",
                    "🎯 USE ACTUAL CONTENT: Reference embedded_mcp_resources from workflow output",
                    "🛡️ AI FAILURE PREVENTION: Follow prevention strategies from step 1 analysis",
                    "📊 COVERAGE VALIDATION: Achieve 90% target with step 3 validation"
                ],
                "alternative_paths": ["❌ NO ALTERNATIVES: This sequence is mandatory for projects with no testing"],
                "cursor_ai_todo_list": {
                    "title": "🚨 MANDATORY TODO LIST - New Project Testing Setup",
                    "instructions": "✅ Complete these todos sequentially. Each MCP tool call provides essential data for the next step.",
                    "phase_todos": [
                        {
                            "phase": "Analysis & AI Failure Prevention",
                            "todos": [
                                {
                                    "id": 0,
                                    "description": "**Call `validate_foundry_config` to prevent compilation errors**",
                                    "tool_call": "validate_foundry_config(prevent_stack_errors=True)",
                                    "expected_output": "Foundry configuration analysis with ready-to-use foundry.toml",
                                    "success_criteria": "✅ Receive foundry.toml with via_ir=true and optimizer enabled",
                                    "why_mandatory": "🛡️ PREVENTS: Stack too deep compilation errors before any testing",
                                    "next_action": "Apply foundry.toml configuration to prevent compilation failures"
                                },
                                {
                                    "id": 1,
                                    "description": "**Call `analyze_project_context` for AI failure prevention**",
                                    "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                    "expected_output": "AI failure analysis with prevention strategies",
                                    "success_criteria": "✅ Receive ai_failure_analysis section with prevention_strategies",
                                    "why_mandatory": "🛡️ CRITICAL: Prevents common AI test generation failures before writing any tests",
                                    "next_action": "Use prevention_strategies from output in subsequent test creation"
                                }
                            ]
                        },
                        {
                            "phase": "Workflow Implementation", 
                            "todos": [
                                {
                                    "id": 2,
                                    "description": "**Call `execute_testing_workflow` with comprehensive scope**",
                                    "tool_call": "execute_testing_workflow(workflow_type='from_scratch', objectives='Create comprehensive test suite with 90% coverage and AI failure prevention', scope='comprehensive')",
                                    "expected_output": "4-phase workflow with embedded_mcp_resources containing actual template content",
                                    "success_criteria": "✅ Receive embedded_mcp_resources with foundry_patterns_content and available_templates_content",
                                    "why_mandatory": "🎯 IMPLEMENTATION: Provides structured testing workflow with concrete templates",
                                    "next_action": "Use embedded_mcp_resources content for actual test implementation (no abstract testing:// references)"
                                }
                            ]
                        },
                        {
                            "phase": "Coverage Validation",
                            "todos": [
                                {
                                    "id": 3,
                                    "description": "**Call `analyze_current_test_coverage` to validate progress**",
                                    "tool_call": "analyze_current_test_coverage(target_coverage=90, include_branches=True)",
                                    "expected_output": "Coverage analysis with gap identification and specific recommendations",
                                    "success_criteria": "✅ Validate coverage progress toward 90% target",
                                    "why_mandatory": "📊 VALIDATION: Ensures testing implementation meets quality targets",
                                    "next_action": "Address any coverage gaps identified in the analysis"
                                }
                            ]
                        },
                        {
                            "phase": "Resource Access (If Needed)",
                            "todos": [
                                {
                                    "id": 4,
                                    "description": "**Call `get_mcp_resources_content` for direct template access**",
                                    "tool_call": "get_mcp_resources_content(resource_type='all')",
                                    "expected_output": "Complete MCP resource content with actual template code",
                                    "success_criteria": "✅ Receive concrete template content instead of abstract references",
                                    "why_mandatory": "📚 RESOURCE ACCESS: Provides immediate access to actual template code",
                                    "next_action": "Use content.templates.{template_name}.content for specific implementations"
                                }
                            ]
                        }
                    ],
                    "completion_note": "🎯 **Workflow Complete**: All mandatory MCP tools called with prevention strategies applied",
                    "success_indicators": [
                        "✅ AI failure prevention strategies received and applied",
                        "✅ Embedded MCP resources with actual template content available", 
                        "✅ Coverage validation confirms progress toward targets",
                        "✅ No abstract testing:// references used"
                    ]
                }
            })
        
        elif project_state.security_level == SecurityLevel.NONE and len(project_state.contracts) > 0:
            base_next_steps.update({
                "immediate_priority": "CRITICAL: Execute mandatory security testing sequence",
                "recommended_tool": "MANDATORY SEQUENCE: Security-first approach required",
                "mandatory_tool_sequence": [
                    {
                        "step": 1,
                        "tool_name": "analyze_project_context",
                        "parameters": {
                            "include_ai_failure_detection": True,
                            "generate_improvement_plan": True
                        },
                        "mandatory": True,
                        "reason": "🔍 SECURITY AUDIT: Identify security vulnerabilities and AI failure risks",
                        "expected_output": "Contract risk analysis with security patterns",
                        "success_criteria": "Must receive contract_analysis with risk_score > 0.5 flagged"
                    },
                    {
                        "step": 2,
                        "tool_name": "execute_testing_workflow", 
                        "parameters": {
                            "workflow_type": "security_focus",
                            "objectives": "Implement comprehensive security testing for high-risk contracts",
                            "scope": "security"
                        },
                        "mandatory": True,
                        "reason": "🛡️ SECURITY IMPLEMENTATION: Deploy security-focused testing workflow",
                        "expected_output": "Security testing phases with attack scenarios",
                        "success_criteria": "Must include security test templates and attack simulations"
                    },
                    {
                        "step": 3,
                        "tool_name": "analyze_current_test_coverage",
                        "parameters": {
                            "target_coverage": 85,
                            "include_branches": True
                        },
                        "mandatory": True,
                        "reason": "🎯 SECURITY VALIDATION: Ensure security tests provide adequate coverage",
                        "expected_output": "Coverage report focused on security test effectiveness",
                        "success_criteria": "Must validate security test coverage for all high-risk functions"
                    }
                ],
                "specific_actions": [
                    "🚨 SECURITY CRITICAL: All 3 tools MUST be executed for security compliance",
                    "🔍 HIGH-RISK FOCUS: Prioritize contracts with risk_score > 0.7 from step 1",
                    "🛡️ ATTACK SCENARIOS: Implement actual attack contracts from step 2 templates",
                    "📊 SECURITY COVERAGE: Validate security function coverage in step 3"
                ],
                "alternative_paths": ["❌ NO ALTERNATIVES: Security testing is mandatory for contracts with security_level=NONE"],
                "cursor_ai_todo_list": {
                    "title": "🚨 MANDATORY TODO LIST - Critical Security Testing",
                    "instructions": "⚠️ SECURITY CRITICAL: These todos are mandatory for contracts with no security testing",
                    "phase_todos": [
                        {
                            "phase": "Security Risk Assessment",
                            "todos": [
                                {
                                    "id": 1,
                                    "description": "**Call `analyze_project_context` for security vulnerability analysis**",
                                    "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                    "expected_output": "Contract analysis with risk_score and security_patterns identified",
                                    "success_criteria": "✅ Receive contract_analysis with risk scores and security vulnerability patterns",
                                    "why_mandatory": "🔍 SECURITY AUDIT: Identifies high-risk contracts requiring immediate security testing",
                                    "next_action": "Prioritize contracts with risk_score > 0.7 for immediate security testing"
                                }
                            ]
                        },
                        {
                            "phase": "Security Testing Implementation",
                            "todos": [
                                {
                                    "id": 2,
                                    "description": "**Call `execute_testing_workflow` with security focus**",
                                    "tool_call": "execute_testing_workflow(workflow_type='security_focus', objectives='Implement comprehensive security testing for high-risk contracts', scope='security')",
                                    "expected_output": "Security-focused workflow with attack scenario templates and security test patterns",
                                    "success_criteria": "✅ Receive embedded_mcp_resources with security_patterns_content and attack scenario templates",
                                    "why_mandatory": "🛡️ SECURITY IMPLEMENTATION: Provides concrete security test templates for identified vulnerabilities",
                                    "next_action": "Use security_patterns_content for specific attack scenarios (reentrancy, access control, etc.)"
                                }
                            ]
                        },
                        {
                            "phase": "Security Coverage Validation",
                            "todos": [
                                {
                                    "id": 3,
                                    "description": "**Call `analyze_current_test_coverage` for security test validation**",
                                    "tool_call": "analyze_current_test_coverage(target_coverage=85, include_branches=True)",
                                    "expected_output": "Coverage analysis focused on security test effectiveness for high-risk functions",
                                    "success_criteria": "✅ Validate security test coverage for all high-risk functions identified in step 1",
                                    "why_mandatory": "🎯 SECURITY VALIDATION: Ensures security tests provide adequate protection",
                                    "next_action": "Address any security coverage gaps, especially for functions with risk_score > 0.7"
                                }
                            ]
                        }
                    ],
                    "completion_note": "🛡️ **Security Testing Complete**: All high-risk contracts have comprehensive security testing",
                    "success_indicators": [
                        "✅ Security vulnerabilities identified and tested",
                        "✅ Attack scenarios implemented for all high-risk functions",
                        "✅ Security test coverage validated for critical functions",
                        "✅ No contracts with security_level=NONE remaining"
                    ]
                }
            })
        
        elif project_state.testing_phase == TestingPhase.BASIC:
            base_next_steps.update({
                "immediate_priority": "Execute mandatory test enhancement sequence",
                "recommended_tool": "MANDATORY SEQUENCE: Systematic test improvement required",
                "mandatory_tool_sequence": [
                    {
                        "step": 1,
                        "tool_name": "analyze_current_test_coverage",
                        "parameters": {
                            "target_coverage": 90,
                            "include_branches": True
                        },
                        "mandatory": True,
                        "reason": "📊 BASELINE ASSESSMENT: Identify current coverage gaps",
                        "expected_output": "Detailed coverage analysis with specific gaps",
                        "success_criteria": "Must identify specific functions/branches with low coverage"
                    },
                    {
                        "step": 2,
                        "tool_name": "analyze_project_context",
                        "parameters": {
                            "include_ai_failure_detection": True,
                            "generate_improvement_plan": True
                        },
                        "mandatory": True,
                        "reason": "🔍 QUALITY AUDIT: Assess existing test quality and identify AI failures",
                        "expected_output": "AI failure analysis and improvement plan",
                        "success_criteria": "Must receive specific improvement recommendations"
                    },
                    {
                        "step": 3,
                        "tool_name": "execute_testing_workflow",
                        "parameters": {
                            "workflow_type": "enhance_coverage",
                            "objectives": "Fill coverage gaps and eliminate AI failure patterns",
                            "scope": "comprehensive"
                        },
                        "mandatory": True,
                        "reason": "⚡ ENHANCEMENT IMPLEMENTATION: Apply systematic improvements",
                        "expected_output": "Enhanced testing workflow addressing identified gaps",
                        "success_criteria": "Must target specific gaps from steps 1 & 2"
                    }
                ],
                "specific_actions": [
                    "📊 COVERAGE ANALYSIS: Start with step 1 to identify specific gaps",
                    "🔍 QUALITY AUDIT: Use step 2 to find and fix AI failure patterns",
                    "⚡ SYSTEMATIC IMPROVEMENT: Apply step 3 workflow to address all findings",
                    "🎯 TARGET ACHIEVEMENT: Reach 90% coverage with high-quality tests"
                ],
                "alternative_paths": ["⚠️ LIMITED ALTERNATIVES: May focus on security_enhancement if high-risk contracts detected"]
            })
        
        elif project_state.testing_phase in [TestingPhase.INTERMEDIATE, TestingPhase.ADVANCED]:
            if len(project_state.identified_gaps) > 0:
                base_next_steps.update({
                    "immediate_priority": "Execute targeted improvement sequence for identified gaps",
                    "recommended_tool": "MANDATORY SEQUENCE: Gap-focused enhancement",
                    "mandatory_tool_sequence": [
                        {
                            "step": 1,
                            "tool_name": "analyze_project_context",
                            "parameters": {
                                "include_ai_failure_detection": True,
                                "generate_improvement_plan": True
                            },
                            "mandatory": True,
                            "reason": "🎯 GAP ANALYSIS: Deep dive into specific identified gaps",
                            "expected_output": "Detailed analysis of current gaps with prioritization",
                            "success_criteria": "Must provide specific recommendations for each identified gap"
                        },
                        {
                            "step": 2,
                            "tool_name": "execute_testing_workflow",
                            "parameters": {
                                "workflow_type": "targeted_improvement",
                                "objectives": f"Address identified gaps: {', '.join(project_state.identified_gaps[:3])}",
                                "scope": "comprehensive"
                            },
                            "mandatory": True,
                            "reason": "🔧 TARGETED FIXES: Implement specific improvements for identified gaps",
                            "expected_output": "Targeted workflow addressing specific gaps",
                            "success_criteria": "Must include specific actions for each gap"
                        }
                    ],
                    "specific_actions": [
                        f"🎯 FOCUS AREAS: Address {', '.join(project_state.identified_gaps[:2])}",
                        "🔍 DETAILED ANALYSIS: Use step 1 for comprehensive gap understanding",
                        "🔧 TARGETED IMPLEMENTATION: Apply step 2 for specific gap resolution",
                        "📊 VALIDATION: Ensure each gap is properly addressed"
                    ],
                    "alternative_paths": ["🔄 ITERATIVE: May repeat sequence if additional gaps are discovered"]
                })
            else:
                base_next_steps.update({
                    "immediate_priority": "Execute advanced testing enhancement sequence",
                    "recommended_tool": "MANDATORY SEQUENCE: Advanced testing techniques",
                    "mandatory_tool_sequence": [
                        {
                            "step": 1,
                            "tool_name": "analyze_current_test_coverage",
                            "parameters": {
                                "target_coverage": 95,
                                "include_branches": True
                            },
                            "mandatory": True,
                            "reason": "🎯 EXCELLENCE ASSESSMENT: Evaluate current testing against excellence standards",
                            "expected_output": "Comprehensive coverage analysis for advanced project",
                            "success_criteria": "Must achieve 95%+ coverage for advanced phase"
                        },
                        {
                            "step": 2,
                            "tool_name": "execute_testing_workflow",
                            "parameters": {
                                "workflow_type": "audit_prep",
                                "objectives": "Prepare for professional security audit with advanced testing",
                                "scope": "comprehensive"
                            },
                            "mandatory": True,
                            "reason": "🏆 AUDIT PREPARATION: Implement audit-ready testing standards",
                            "expected_output": "Audit-ready testing workflow with formal verification prep",
                            "success_criteria": "Must meet professional audit standards"
                        }
                    ],
                    "specific_actions": [
                        "🏆 EXCELLENCE STANDARD: Target 95%+ coverage with step 1 validation",
                        "🔍 AUDIT PREPARATION: Use step 2 for professional-grade testing",
                        "📋 FORMAL STANDARDS: Implement audit-ready documentation and testing",
                        "🎯 PROFESSIONAL QUALITY: Meet institutional testing standards"
                    ],
                    "alternative_paths": ["🎓 ADVANCED: Consider formal verification or research collaboration"]
                })
        
        # =================================================================
        # ADD CONTRACT-SPECIFIC URGENT REQUIREMENTS
        # =================================================================
        high_risk_contracts = [c for c in project_state.contracts if c.risk_score > 0.7]
        if high_risk_contracts:
            base_next_steps["urgent_attention"] = {
                "status": "CRITICAL_SECURITY_REQUIRED",
                "message": f"High-risk contracts detected: {', '.join(c.contract_name for c in high_risk_contracts[:3])}",
                "mandatory_security_action": "Security testing is MANDATORY before any other testing activities",
                "risk_mitigation": "Use security_focus workflow in mandatory_tool_sequence"
            }
        
        return base_next_steps

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
    
    def _generate_next_phase_todo_list(self, current_phase: int, session: TestingSession) -> Dict[str, Any]:
        """Generate todo list for the next workflow phase with embedded MCP tool calls."""
        next_phase = current_phase + 1
        
        # Define phase-specific todo lists
        phase_todo_templates = {
            2: {  # After Phase 1 (Setup) → Phase 2 (Core Unit Tests)
                "title": "🚨 NEXT PHASE TODO - Core Unit Test Implementation",
                "instructions": "✅ Implement core unit tests with AI failure prevention",
                "phase_todos": [
                    {
                        "phase": "Pre-Implementation Analysis",
                        "todos": [
                            {
                                "id": 1,
                                "description": "**Call `analyze_project_context` for test quality assessment**",
                                "tool_call": "analyze_project_context(include_ai_failure_detection=True, generate_improvement_plan=True)",
                                "expected_output": "Current test quality analysis and AI failure patterns",
                                "success_criteria": "✅ Receive specific guidance on avoiding AI test failures",
                                "why_mandatory": "🛡️ Ensures test implementation follows best practices and avoids common AI failures"
                            }
                        ]
                    },
                    {
                        "phase": "Core Implementation",
                        "todos": [
                            {
                                "id": 2,
                                "description": "**Create unit tests using embedded MCP templates**",
                                "implementation_guidance": "Use template content from embedded_mcp_resources",
                                "success_criteria": "✅ Unit tests created with proper structure and patterns",
                                "why_mandatory": "🎯 Templates prevent common mistakes and ensure consistency"
                            }
                        ]
                    }
                ]
            }
        }
        
        return phase_todo_templates.get(next_phase, {
            "title": f"🚨 PHASE {next_phase} TODO LIST",
            "instructions": "Continue with next phase implementation",
            "phase_todos": []
        })

    # =================================================================
    # NEW: HELPER METHODS FOR LLM-DRIVEN ANALYSIS INTEGRATION
    # =================================================================
    
    async def _extract_project_sources(self, project_path: str) -> str:
        """Extract and format project source contracts for LLM analysis."""
        try:
            contracts_content = []
            src_path = Path(project_path) / "src"
            
            if src_path.exists():
                for contract_file in src_path.rglob("*.sol"):
                    try:
                        with open(contract_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            relative_path = contract_file.relative_to(project_path)
                            contracts_content.append(f"// FILE: {relative_path}\n{content}")
                    except Exception as e:
                        logger.warning(f"Could not read contract file {contract_file}: {e}")
            
            return "\n\n" + "="*80 + "\n\n".join(contracts_content) if contracts_content else "No contracts found in src/ directory"
            
        except Exception as e:
            logger.error(f"Error extracting project sources: {e}")
            return f"Error extracting sources: {str(e)}"

    async def _extract_test_sources(self, project_path: str) -> str:
        """Extract and format test sources for LLM analysis."""
        try:
            test_content = []
            test_path = Path(project_path) / "test"
            
            if test_path.exists():
                for test_file in test_path.rglob("*.sol"):
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            relative_path = test_file.relative_to(project_path)
                            test_content.append(f"// FILE: {relative_path}\n{content}")
                    except Exception as e:
                        logger.warning(f"Could not read test file {test_file}: {e}")
            
            return "\n\n" + "="*80 + "\n\n".join(test_content) if test_content else "No test files found in test/ directory"
            
        except Exception as e:
            logger.error(f"Error extracting test sources: {e}")
            return f"Error extracting test sources: {str(e)}"

    async def _extract_mock_contracts(self, project_path: str) -> str:
        """Extract mock contract content from test files for analysis."""
        try:
            mock_content = []
            test_path = Path(project_path) / "test"
            
            if test_path.exists():
                for test_file in test_path.rglob("*.sol"):
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Look for mock contracts
                            if "mock" in content.lower() or "Mock" in content:
                                relative_path = test_file.relative_to(project_path)
                                mock_content.append(f"// MOCK FILE: {relative_path}\n{content}")
                    except Exception as e:
                        logger.warning(f"Could not read test file {test_file}: {e}")
            
            return "\n\n" + "="*80 + "\n\n".join(mock_content) if mock_content else "No mock contracts found in test files"
            
        except Exception as e:
            logger.error(f"Error extracting mock contracts: {e}")
            return f"Error extracting mocks: {str(e)}"

    async def _call_domain_analysis_prompt(self, project_sources: str, test_sources: str) -> Dict[str, Any]:
        """Call the domain analysis prompt and return structured results."""
        try:
            if not hasattr(self, 'testing_prompts') or not self.testing_prompts:
                logger.warning("Testing prompts not available for domain analysis")
                return {
                    "primary_domain": "General",
                    "secondary_domains": [],
                    "contextual_quality_score": 0.5,
                    "missing_patterns": ["Domain analysis unavailable"],
                    "recommendations": ["Set up testing_prompts integration"]
                }
            
            # This would be called via the MCP prompt system in actual usage
            # For now, return a structured result that matches expected format
            return {
                "primary_domain": "General",  # Will be determined by LLM
                "secondary_domains": [],
                "contextual_quality_score": 0.0,
                "missing_patterns": [],
                "recommendations": [],
                "analysis_note": "Domain analysis prompt ready for LLM integration"
            }
            
        except Exception as e:
            logger.error(f"Error calling domain analysis prompt: {e}")
            return {
                "primary_domain": "General",
                "secondary_domains": [],
                "contextual_quality_score": 0.0,
                "missing_patterns": [f"Domain analysis error: {str(e)}"],
                "recommendations": ["Retry domain analysis after fixing integration"]
            }

    async def _call_mock_analysis_prompt(self, mock_contracts: str, target_contracts: str, test_context: str) -> Dict[str, Any]:
        """Call the mock analysis prompt and return structured results."""
        try:
            if not hasattr(self, 'testing_prompts') or not self.testing_prompts:
                logger.warning("Testing prompts not available for mock analysis")
                return {
                    "overall_sophistication_score": 0.5,
                    "mock_analyses": [],
                    "critical_gaps": ["Mock analysis unavailable"],
                    "immediate_actions": ["Set up testing_prompts integration"]
                }
            
            # This would be called via the MCP prompt system in actual usage
            # For now, return a structured result that matches expected format
            return {
                "overall_sophistication_score": 0.0,  # Will be determined by LLM
                "mock_analyses": [],
                "suite_level_assessment": {
                    "mock_coverage_completeness": 0.0,
                    "cross_mock_consistency": 0.0,
                    "integration_test_readiness": 0.0,
                    "security_test_enablement": 0.0
                },
                "critical_gaps": [],
                "immediate_actions": [],
                "enhancement_roadmap": [],
                "analysis_note": "Mock analysis prompt ready for LLM integration"
            }
            
        except Exception as e:
            logger.error(f"Error calling mock analysis prompt: {e}")
            return {
                "overall_sophistication_score": 0.0,
                "mock_analyses": [],
                "critical_gaps": [f"Mock analysis error: {str(e)}"],
                "immediate_actions": ["Retry mock analysis after fixing integration"]
            }