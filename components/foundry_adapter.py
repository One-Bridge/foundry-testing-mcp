"""
Smart Contract Testing MCP Server - Foundry Adapter

This module provides deep integration with the Foundry toolchain for smart contract testing.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import tempfile
import shutil

logger = logging.getLogger(__name__)

class FoundryError(Exception):
    """Base exception for Foundry-related errors."""
    pass

class FoundryNotFoundError(FoundryError):
    """Raised when Foundry is not found on the system."""
    pass

class FoundryProjectError(FoundryError):
    """Raised when there's an issue with the Foundry project structure."""
    pass

class FoundryAdapter:
    """
    Adapter for integrating with the Foundry toolchain.
    
    This class provides methods for running tests, analyzing coverage,
    generating reports, and managing Foundry projects.
    """
    
    def __init__(self):
        """Initialize the Foundry adapter."""
        self.forge_path = self._find_forge_executable()
        self.cast_path = self._find_cast_executable()
        self.anvil_path = self._find_anvil_executable()
        
        if not self.forge_path:
            raise FoundryNotFoundError("Forge executable not found. Please install Foundry.")
        
        logger.info(f"Foundry adapter initialized with forge at: {self.forge_path}")
    
    def _find_forge_executable(self) -> Optional[str]:
        """Find the forge executable in the system PATH."""
        return shutil.which("forge")
    
    def _find_cast_executable(self) -> Optional[str]:
        """Find the cast executable in the system PATH."""
        return shutil.which("cast")
    
    def _find_anvil_executable(self) -> Optional[str]:
        """Find the anvil executable in the system PATH."""
        return shutil.which("anvil")
    
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
    
    async def _run_command(self, command: List[str], cwd: str = None) -> Tuple[int, str, str]:
        """
        Run a command and return the return code, stdout, and stderr.
        
        Args:
            command: Command to run as a list of strings
            cwd: Working directory for the command
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if cwd is None:
            cwd = self._resolve_project_path()
        
        try:
            logger.debug(f"Running command: {' '.join(command)} in {cwd}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return (
                process.returncode,
                stdout.decode('utf-8', errors='ignore'),
                stderr.decode('utf-8', errors='ignore')
            )
            
        except Exception as e:
            logger.error(f"Error running command {' '.join(command)}: {e}")
            return (1, "", str(e))
    
    async def check_foundry_installation(self) -> Dict[str, Any]:
        """
        Check if Foundry is properly installed and return version info.
        
        Returns:
            Dictionary containing installation status and version info
        """
        result = {
            "installed": False,
            "forge_version": None,
            "cast_version": None,
            "anvil_version": None,
            "installation_path": None
        }
        
        try:
            # Check forge version
            if self.forge_path:
                returncode, stdout, stderr = await self._run_command([self.forge_path, "--version"])
                if returncode == 0:
                    result["installed"] = True
                    result["forge_version"] = stdout.strip()
                    result["installation_path"] = self.forge_path
            
            # Check cast version
            if self.cast_path:
                returncode, stdout, stderr = await self._run_command([self.cast_path, "--version"])
                if returncode == 0:
                    result["cast_version"] = stdout.strip()
            
            # Check anvil version
            if self.anvil_path:
                returncode, stdout, stderr = await self._run_command([self.anvil_path, "--version"])
                if returncode == 0:
                    result["anvil_version"] = stdout.strip()
            
        except Exception as e:
            logger.error(f"Error checking Foundry installation: {e}")
        
        return result
    
    async def detect_project_structure(self, project_path: str = "") -> Dict[str, Any]:
        """
        Analyze the project structure and detect Foundry configuration.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            
        Returns:
            Dictionary containing project structure analysis
        """
        project_path = Path(self._resolve_project_path(project_path))
        
        if not project_path.exists():
            raise FoundryProjectError(f"Project path does not exist: {project_path}")
        
        structure = {
            "project_path": str(project_path),
            "is_foundry_project": False,
            "foundry_toml": None,
            "contracts": [],
            "tests": [],
            "scripts": [],
            "dependencies": [],
            "remappings": [],
            "profile": "default"
        }
        
        # Check for foundry.toml
        foundry_toml_path = project_path / "foundry.toml"
        if foundry_toml_path.exists():
            structure["is_foundry_project"] = True
            structure["foundry_toml"] = str(foundry_toml_path)
            
            # Parse foundry.toml for configuration
            try:
                with open(foundry_toml_path, 'r') as f:
                    import toml
                    config = toml.load(f)
                    structure["profile"] = config.get("profile", {}).get("default", "default")
                    if "dependencies" in config:
                        structure["dependencies"] = list(config["dependencies"].keys())
                    if "remappings" in config:
                        structure["remappings"] = config["remappings"]
            except Exception as e:
                logger.warning(f"Could not parse foundry.toml: {e}")
        
        # Scan for contracts
        src_dir = project_path / "src"
        if src_dir.exists():
            for sol_file in src_dir.rglob("*.sol"):
                structure["contracts"].append(str(sol_file.relative_to(project_path)))
        
        # Scan for tests
        test_dir = project_path / "test"
        if test_dir.exists():
            for test_file in test_dir.rglob("*.sol"):
                structure["tests"].append(str(test_file.relative_to(project_path)))
        
        # Scan for scripts
        script_dir = project_path / "script"
        if script_dir.exists():
            for script_file in script_dir.rglob("*.sol"):
                structure["scripts"].append(str(script_file.relative_to(project_path)))
        
        return structure
    
    async def run_tests(self, project_path: str = "", test_pattern: str = "", 
                       coverage: bool = False, gas_report: bool = False) -> Dict[str, Any]:
        """
        Run Foundry tests with optional coverage and gas reporting.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            test_pattern: Optional pattern to filter tests
            coverage: Whether to generate coverage report
            gas_report: Whether to generate gas report
            
        Returns:
            Dictionary containing test results and reports
        """
        project_path = self._resolve_project_path(project_path)
        
        command = [self.forge_path, "test"]
        
        if test_pattern:
            command.extend(["--match-test", test_pattern])
        
        if coverage:
            command.append("--coverage")
        
        if gas_report:
            command.append("--gas-report")
        
        # Add verbose output for better parsing
        command.extend(["-vvvvv", "--json"])
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        result = {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "test_results": None,
            "coverage_report": None,
            "gas_report": None
        }
        
        # Parse JSON output if available
        try:
            if stdout.strip():
                # Try to parse as JSON
                lines = stdout.strip().split('\n')
                json_lines = [line for line in lines if line.strip().startswith('{')]
                if json_lines:
                    result["test_results"] = [json.loads(line) for line in json_lines]
        except Exception as e:
            logger.warning(f"Could not parse test output as JSON: {e}")
        
        return result
    
    async def generate_coverage_report(self, project_path: str = "", 
                                     format: str = "lcov") -> Dict[str, Any]:
        """
        Generate a detailed coverage report using actual forge coverage output.
        
        This addresses the tool integration disconnect by properly parsing
        and using real Foundry coverage data rather than generic analysis.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            format: Coverage report format (lcov, summary, json)
            
        Returns:
            Dictionary containing comprehensive coverage analysis
        """
        project_path = self._resolve_project_path(project_path)
        
        # First, run tests to ensure coverage data is available
        test_result = await self.run_tests(project_path, coverage=True)
        
        # Then generate the coverage report
        command = [self.forge_path, "coverage"]
        
        if format == "summary":
            command.extend(["--report", "summary"])
        elif format == "lcov":
            command.extend(["--report", "lcov"])
        elif format == "json":
            command.extend(["--report", "json"])
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        result = {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "coverage_data": None,
            "summary": None,
            "test_execution": test_result
        }
        
        if returncode == 0:
            # Parse coverage data based on format
            try:
                if format == "lcov":
                    result["coverage_data"] = self._parse_lcov_coverage(stdout)
                elif format == "summary":
                    result["coverage_data"] = self._parse_summary_coverage(stdout)
                elif format == "json":
                    result["coverage_data"] = json.loads(stdout)
                
                # Generate enhanced summary statistics
                result["summary"] = self._generate_coverage_summary(result["coverage_data"])
                
            except Exception as e:
                logger.warning(f"Could not parse coverage data: {e}")
                # Try to extract basic coverage info from stderr
                result["summary"] = self._extract_basic_coverage_info(stderr)
        
        return result
    
    def _parse_lcov_coverage(self, lcov_output: str) -> Dict[str, Any]:
        """Parse LCOV coverage output."""
        coverage_data = {
            "files": [],
            "totals": {
                "functions": {"hit": 0, "found": 0},
                "lines": {"hit": 0, "found": 0},
                "branches": {"hit": 0, "found": 0}
            }
        }
        
        # Simple LCOV parsing
        current_file = None
        for line in lcov_output.split('\n'):
            if line.startswith('SF:'):
                current_file = {"file": line[3:], "lines": []}
                coverage_data["files"].append(current_file)
            elif line.startswith('LH:'):
                coverage_data["totals"]["lines"]["hit"] += int(line[3:])
            elif line.startswith('LF:'):
                coverage_data["totals"]["lines"]["found"] += int(line[3:])
            elif line.startswith('FNH:'):
                coverage_data["totals"]["functions"]["hit"] += int(line[4:])
            elif line.startswith('FNF:'):
                coverage_data["totals"]["functions"]["found"] += int(line[4:])
            elif line.startswith('BRH:'):
                coverage_data["totals"]["branches"]["hit"] += int(line[4:])
            elif line.startswith('BRF:'):
                coverage_data["totals"]["branches"]["found"] += int(line[4:])
        
        return coverage_data
    
    def _parse_summary_coverage(self, summary_output: str) -> Dict[str, Any]:
        """
        Parse forge coverage --report summary output.
        
        This addresses the tool integration disconnect by parsing actual
        Foundry summary output format rather than generic coverage data.
        """
        coverage_data = {
            "files": [],
            "totals": {
                "functions": {"hit": 0, "found": 0},
                "lines": {"hit": 0, "found": 0},
                "branches": {"hit": 0, "found": 0}
            },
            "format": "summary"
        }
        
        lines = summary_output.split('\n')
        in_file_section = False
        
        for line in lines:
            line = line.strip()
            
            # Look for file coverage information
            if line.startswith('|') and '.sol' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        file_name = parts[0]
                        lines_pct = self._extract_percentage(parts[1])
                        functions_pct = self._extract_percentage(parts[2]) if len(parts) > 2 else 0
                        branches_pct = self._extract_percentage(parts[3]) if len(parts) > 3 else 0
                        
                        coverage_data["files"].append({
                            "file": file_name,
                            "lines_pct": lines_pct,
                            "functions_pct": functions_pct,
                            "branches_pct": branches_pct
                        })
                    except (ValueError, IndexError):
                        continue
            
            # Look for total coverage information
            elif "Total" in line or "Overall" in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2:
                    try:
                        total_pct = self._extract_percentage(parts[1])
                        coverage_data["totals"]["overall_percentage"] = total_pct
                    except (ValueError, IndexError):
                        continue
        
        return coverage_data
    
    def _extract_percentage(self, text: str) -> float:
        """Extract percentage value from text like '85.5%' or '85.5% (17/20)'."""
        import re
        match = re.search(r'(\d+\.?\d*)%', text)
        if match:
            return float(match.group(1))
        return 0.0
    
    def _extract_basic_coverage_info(self, stderr_output: str) -> Dict[str, Any]:
        """
        Extract basic coverage info from stderr when detailed parsing fails.
        
        Foundry sometimes outputs coverage summary to stderr.
        """
        summary = {
            "coverage_percentage": 0,
            "analysis": "Could not parse detailed coverage data",
            "source": "stderr_extraction"
        }
        
        lines = stderr_output.split('\n')
        for line in lines:
            # Look for coverage percentage in various formats
            if '%' in line and any(keyword in line.lower() for keyword in ['coverage', 'total', 'overall']):
                try:
                    percentage = self._extract_percentage(line)
                    if percentage > 0:
                        summary["coverage_percentage"] = percentage
                        summary["analysis"] = f"Basic coverage extracted: {percentage}%"
                        break
                except:
                    continue
        
        return summary
    
    def _generate_coverage_summary(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate enhanced coverage summary statistics with context awareness.
        
        This addresses the context blindness issue by providing nuanced analysis
        that recognizes different levels of coverage achievement.
        """
        if not coverage_data:
            return {"coverage_percentage": 0, "analysis": "No coverage data available"}
        
        # Handle different coverage data formats
        if coverage_data.get("format") == "summary":
            # Parse summary format data
            overall_pct = coverage_data.get("totals", {}).get("overall_percentage", 0)
            files = coverage_data.get("files", [])
            
            # Calculate detailed metrics from file data
            if files:
                avg_lines = sum(f.get("lines_pct", 0) for f in files) / len(files)
                avg_functions = sum(f.get("functions_pct", 0) for f in files) / len(files)
                avg_branches = sum(f.get("branches_pct", 0) for f in files) / len(files)
            else:
                avg_lines = avg_functions = avg_branches = overall_pct
            
            return {
                "coverage_percentage": round(overall_pct, 2),
                "lines_coverage": round(avg_lines, 2),
                "functions_coverage": round(avg_functions, 2),
                "branches_coverage": round(avg_branches, 2),
                "files_analyzed": len(files),
                "analysis": self._generate_contextual_coverage_analysis(overall_pct, files),
                "format": "summary"
            }
        
        elif coverage_data.get("totals"):
            # Handle LCOV format data
            totals = coverage_data["totals"]
            
            # Calculate line coverage percentage
            lines_found = totals["lines"]["found"]
            lines_hit = totals["lines"]["hit"]
            
            coverage_percentage = (lines_hit / lines_found * 100) if lines_found > 0 else 0
            
            return {
                "coverage_percentage": round(coverage_percentage, 2),
                "lines_covered": lines_hit,
                "lines_total": lines_found,
                "functions_covered": totals["functions"]["hit"],
                "functions_total": totals["functions"]["found"],
                "branches_covered": totals["branches"]["hit"],
                "branches_total": totals["branches"]["found"],
                "analysis": self._generate_contextual_coverage_analysis(coverage_percentage, []),
                "format": "lcov"
            }
        
        else:
            # Handle basic or unknown format
            coverage_pct = coverage_data.get("coverage_percentage", 0)
            return {
                "coverage_percentage": coverage_pct,
                "analysis": coverage_data.get("analysis", "Basic coverage data"),
                "format": "basic"
            }
    
    def _generate_contextual_coverage_analysis(self, coverage_percentage: float, 
                                              files: List[Dict[str, Any]] = None) -> str:
        """
        Generate contextual coverage analysis that recognizes good work.
        
        This addresses the context blindness issue by providing appropriate
        feedback based on actual coverage levels rather than generic responses.
        """
        files = files or []
        
        # Enhanced analysis based on coverage levels
        if coverage_percentage >= 95:
            analysis = f"Excellent coverage achieved ({coverage_percentage}%)! "
            if files:
                low_coverage_files = [f for f in files if f.get("lines_pct", 0) < 90]
                if low_coverage_files:
                    analysis += f"Consider addressing {len(low_coverage_files)} files with lower coverage for completeness."
                else:
                    analysis += "Consider adding property-based testing and formal verification for production readiness."
            else:
                analysis += "Ready for production deployment. Consider adding invariant and integration tests."
                
        elif coverage_percentage >= 90:
            analysis = f"Very good coverage ({coverage_percentage}%)! "
            if files:
                uncovered_areas = len([f for f in files if f.get("lines_pct", 0) < 85])
                analysis += f"Focus on improving coverage in {uncovered_areas} remaining areas and add security testing."
            else:
                analysis += "Add edge cases, security tests, and integration scenarios to reach production standards."
                
        elif coverage_percentage >= 80:
            analysis = f"Good coverage foundation ({coverage_percentage}%). "
            analysis += "Add tests for uncovered functions, edge cases, and security scenarios to reach professional standards."
            
        elif coverage_percentage >= 70:
            analysis = f"Moderate coverage ({coverage_percentage}%). "
            analysis += "Systematic testing expansion needed - focus on critical functions and error conditions first."
            
        elif coverage_percentage >= 50:
            analysis = f"Basic coverage present ({coverage_percentage}%). "
            analysis += "Significant testing expansion needed for production readiness."
            
        elif coverage_percentage >= 30:
            analysis = f"Limited coverage ({coverage_percentage}%). "
            analysis += "Comprehensive testing strategy required - start with critical functions."
            
        else:
            analysis = f"Minimal coverage ({coverage_percentage}%). "
            analysis += "Begin with unit tests for core contract functions and build systematically."
        
        return analysis
    
    async def run_invariant_tests(self, project_path: str = "", 
                                 contract_name: str = "") -> Dict[str, Any]:
        """
        Run invariant tests for a specific contract or all contracts.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            contract_name: Optional contract name to filter tests
            
        Returns:
            Dictionary containing invariant test results
        """
        project_path = self._resolve_project_path(project_path)
        
        command = [self.forge_path, "test", "--invariant"]
        
        if contract_name:
            command.extend(["--match-contract", contract_name])
        
        command.extend(["-vvv", "--json"])
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        return {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "invariant_results": self._parse_invariant_results(stdout) if returncode == 0 else None
        }
    
    def _parse_invariant_results(self, output: str) -> Dict[str, Any]:
        """Parse invariant test results."""
        results = {
            "total_invariants": 0,
            "passed_invariants": 0,
            "failed_invariants": 0,
            "details": []
        }
        
        # Parse JSON output for invariant results
        try:
            lines = output.strip().split('\n')
            json_lines = [line for line in lines if line.strip().startswith('{')]
            for line in json_lines:
                data = json.loads(line)
                if "invariant" in data:
                    results["details"].append(data)
                    results["total_invariants"] += 1
                    if data.get("success", False):
                        results["passed_invariants"] += 1
                    else:
                        results["failed_invariants"] += 1
        except Exception as e:
            logger.warning(f"Could not parse invariant results: {e}")
        
        return results
    
    async def analyze_gas_usage(self, project_path: str = "", 
                               function_name: str = "") -> Dict[str, Any]:
        """
        Analyze gas usage for contracts and functions.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            function_name: Optional function name to filter analysis
            
        Returns:
            Dictionary containing gas usage analysis
        """
        project_path = self._resolve_project_path(project_path)
        
        command = [self.forge_path, "test", "--gas-report"]
        
        if function_name:
            command.extend(["--match-test", function_name])
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        return {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "gas_analysis": self._parse_gas_report(stdout) if returncode == 0 else None
        }
    
    def _parse_gas_report(self, output: str) -> Dict[str, Any]:
        """Parse gas report output."""
        analysis = {
            "contracts": [],
            "functions": [],
            "summary": {
                "total_gas_used": 0,
                "average_gas_per_call": 0,
                "high_gas_functions": []
            }
        }
        
        # Parse gas report format
        lines = output.split('\n')
        for line in lines:
            if '│' in line and 'gas' in line.lower():
                # Parse gas usage information
                parts = [part.strip() for part in line.split('│')]
                if len(parts) >= 3:
                    try:
                        gas_usage = int(parts[1].replace(',', ''))
                        analysis["summary"]["total_gas_used"] += gas_usage
                    except (ValueError, IndexError):
                        continue
        
        return analysis
    
    async def initialize_project(self, project_path: str = "", 
                                project_name: str = "") -> Dict[str, Any]:
        """
        Initialize a new Foundry project.
        
        Args:
            project_path: Path where the project should be created (defaults to current directory)
            project_name: Optional project name
            
        Returns:
            Dictionary containing initialization results
        """
        project_path = self._resolve_project_path(project_path)
        
        command = [self.forge_path, "init"]
        
        if project_name:
            command.append(project_name)
        else:
            command.append(".")
        
        command.append("--force")  # Force initialization
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        result = {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "project_path": project_path
        }
        
        if returncode == 0:
            # Verify project structure was created
            result["project_structure"] = await self.detect_project_structure(project_path)
        
        return result
    
    async def cleanup(self) -> None:
        """Cleanup resources used by the adapter."""
        # Cleanup any temporary files or processes
        logger.info("Foundry adapter cleanup completed")
    
    async def get_forge_config(self, project_path: str = "") -> Dict[str, Any]:
        """
        Get the current forge configuration.
        
        Args:
            project_path: Path to the project directory (defaults to current directory)
            
        Returns:
            Dictionary containing forge configuration
        """
        project_path = self._resolve_project_path(project_path)
        
        command = [self.forge_path, "config"]
        
        returncode, stdout, stderr = await self._run_command(command, cwd=project_path)
        
        result = {
            "success": returncode == 0,
            "return_code": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "config": None
        }
        
        if returncode == 0:
            try:
                # Parse JSON config output
                result["config"] = json.loads(stdout)
            except Exception as e:
                logger.warning(f"Could not parse forge config: {e}")
        
        return result 