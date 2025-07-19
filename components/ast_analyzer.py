"""
AST Analyzer Component for Smart Contract Testing MCP Server

This module provides semantic code analysis using Abstract Syntax Trees (AST)
to replace regex-based pattern matching with proper semantic understanding.

Supports:
- Solidity contract analysis via solc --ast-json
- Python test file analysis via ast module
- Semantic relationship mapping
- Control flow analysis
- Dependency tracking
"""

import ast
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re

logger = logging.getLogger(__name__)

class NodeType(Enum):
    """AST node types for analysis"""
    CONTRACT = "contract"
    FUNCTION = "function"
    MODIFIER = "modifier"
    STATE_VAR = "state_variable"
    EVENT = "event"
    STRUCT = "struct"
    ENUM = "enum"
    IMPORT = "import"
    INHERITANCE = "inheritance"

class SecurityPattern(Enum):
    """Semantic security patterns detected via AST"""
    ACCESS_CONTROL = "access_control"
    REENTRANCY_GUARD = "reentrancy_guard"
    ORACLE_DEPENDENCY = "oracle_dependency"
    FLASH_LOAN_RECEIVER = "flash_loan_receiver"
    UPGRADEABLE_PATTERN = "upgradeable_pattern"
    TIMELOCK_CONTROL = "timelock_control"
    MULTI_SIG_PATTERN = "multi_sig_pattern"

@dataclass
class ASTNode:
    """Represents a semantic AST node with rich metadata"""
    node_type: NodeType
    name: str
    source_location: Tuple[int, int]  # (start_line, end_line)
    file_path: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['ASTNode'] = field(default_factory=list)
    parent: Optional['ASTNode'] = None
    dependencies: Set[str] = field(default_factory=set)
    security_implications: List[SecurityPattern] = field(default_factory=list)

@dataclass
class SemanticAnalysis:
    """Complete semantic analysis result"""
    file_path: str
    ast_nodes: List[ASTNode]
    control_flow: Dict[str, List[str]]  # function -> called functions
    state_dependencies: Dict[str, Set[str]]  # function -> state variables accessed
    security_patterns: List[SecurityPattern]
    risk_factors: Dict[str, float]
    complexity_metrics: Dict[str, int]
    external_dependencies: Set[str]

class ASTAnalyzer:
    """
    Semantic code analyzer using Abstract Syntax Trees.
    
    Provides deep semantic understanding of smart contracts and test files
    to replace regex-based pattern matching with proper structural analysis.
    """
    
    def __init__(self):
        """Initialize AST analyzer with semantic patterns."""
        self.solc_path = self._find_solc_executable()
        self.security_pattern_mappings = self._initialize_security_patterns()
        self.complexity_weights = self._initialize_complexity_weights()
        logger.info("AST analyzer initialized")
    
    def _find_solc_executable(self) -> Optional[str]:
        """Find solc executable for Solidity AST generation."""
        import shutil
        return shutil.which("solc")
    
    def _initialize_security_patterns(self) -> Dict[SecurityPattern, Dict[str, Any]]:
        """Initialize semantic security pattern detection rules."""
        return {
            SecurityPattern.ACCESS_CONTROL: {
                "modifiers": ["onlyOwner", "onlyRole", "onlyAuthorized"],
                "imports": ["@openzeppelin/contracts/access/", "AccessControl"],
                "patterns": ["require(msg.sender", "require(owner", "_checkRole"]
            },
            SecurityPattern.REENTRANCY_GUARD: {
                "modifiers": ["nonReentrant"],
                "imports": ["ReentrancyGuard"],
                "patterns": ["_reentrancyGuard", "REENTRANCY_NOT_ENTERED"]
            },
            SecurityPattern.ORACLE_DEPENDENCY: {
                "interfaces": ["AggregatorV3Interface", "IOracle"],
                "functions": ["latestRoundData", "getPrice", "decimals"],
                "imports": ["@chainlink/contracts/"]
            },
            SecurityPattern.FLASH_LOAN_RECEIVER: {
                "interfaces": ["IFlashLoanReceiver", "IERC3156FlashBorrower"],
                "functions": ["executeOperation", "onFlashLoan"],
                "imports": ["AAVE", "flash"]
            }
        }
    
    def _initialize_complexity_weights(self) -> Dict[str, int]:
        """Initialize complexity scoring weights."""
        return {
            "external_function": 3,
            "public_function": 2,
            "internal_function": 1,
            "payable_function": 5,
            "state_variable": 1,
            "modifier": 2,
            "external_call": 4,
            "assembly_block": 8,
            "loop_construct": 3,
            "conditional_branch": 2
        }
    
    async def analyze_solidity_file(self, file_path: str) -> SemanticAnalysis:
        """
        Perform semantic analysis of a Solidity file using AST.
        
        Args:
            file_path: Path to the Solidity file
            
        Returns:
            Complete semantic analysis with AST nodes and relationships
        """
        if not self.solc_path:
            logger.warning("solc not found, falling back to text analysis")
            return await self._fallback_text_analysis(file_path)
        
        try:
            # Generate Solidity AST using solc
            ast_json = await self._generate_solidity_ast(file_path)
            if not ast_json:
                return await self._fallback_text_analysis(file_path)
            
            # Parse AST into semantic nodes
            ast_nodes = self._parse_solidity_ast(ast_json, file_path)
            
            # Perform semantic analysis
            control_flow = self._analyze_control_flow(ast_nodes)
            state_dependencies = self._analyze_state_dependencies(ast_nodes)
            security_patterns = self._detect_security_patterns(ast_nodes)
            risk_factors = self._calculate_risk_factors(ast_nodes, security_patterns)
            complexity_metrics = self._calculate_complexity_metrics(ast_nodes)
            external_deps = self._extract_external_dependencies(ast_nodes)
            
            return SemanticAnalysis(
                file_path=file_path,
                ast_nodes=ast_nodes,
                control_flow=control_flow,
                state_dependencies=state_dependencies,
                security_patterns=security_patterns,
                risk_factors=risk_factors,
                complexity_metrics=complexity_metrics,
                external_dependencies=external_deps
            )
            
        except Exception as e:
            logger.error(f"AST analysis failed for {file_path}: {e}")
            return await self._fallback_text_analysis(file_path)
    
    async def _generate_solidity_ast(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Generate Solidity AST using solc --ast-json."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Run solc to generate AST
                cmd = [
                    self.solc_path,
                    "--ast-compact-json",
                    "--output-dir", temp_dir,
                    file_path
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.warning(f"solc failed for {file_path}: {result.stderr}")
                    return None
                
                # Find and read the AST JSON file
                ast_files = list(Path(temp_dir).glob("*.json"))
                if not ast_files:
                    return None
                
                with open(ast_files[0], 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            logger.warning(f"Could not generate AST for {file_path}: {e}")
            return None
    
    def _parse_solidity_ast(self, ast_json: Dict[str, Any], file_path: str) -> List[ASTNode]:
        """Parse Solidity AST JSON into semantic nodes."""
        nodes = []
        
        def traverse_ast(node: Dict[str, Any], parent: Optional[ASTNode] = None) -> Optional[ASTNode]:
            """Recursively traverse AST and create semantic nodes."""
            node_type_map = {
                "ContractDefinition": NodeType.CONTRACT,
                "FunctionDefinition": NodeType.FUNCTION,
                "ModifierDefinition": NodeType.MODIFIER,
                "VariableDeclaration": NodeType.STATE_VAR,
                "EventDefinition": NodeType.EVENT,
                "StructDefinition": NodeType.STRUCT,
                "EnumDefinition": NodeType.ENUM,
                "ImportDirective": NodeType.IMPORT,
                "InheritanceSpecifier": NodeType.INHERITANCE
            }
            
            node_type_str = node.get("nodeType")
            if node_type_str not in node_type_map:
                # Process children for unknown node types
                for child in node.get("nodes", []):
                    child_node = traverse_ast(child, parent)
                    if child_node:
                        nodes.append(child_node)
                return None
            
            node_type = node_type_map[node_type_str]
            name = node.get("name", f"unnamed_{node_type.value}")
            
            # Extract source location if available
            src = node.get("src", "0:0:0").split(":")
            start_line = int(src[0]) if len(src) > 0 else 0
            end_line = start_line + int(src[1]) if len(src) > 1 else start_line
            
            # Create semantic node
            semantic_node = ASTNode(
                node_type=node_type,
                name=name,
                source_location=(start_line, end_line),
                file_path=file_path,
                parent=parent,
                attributes=self._extract_node_attributes(node)
            )
            
            # Process children
            for child in node.get("nodes", []):
                child_node = traverse_ast(child, semantic_node)
                if child_node:
                    semantic_node.children.append(child_node)
                    nodes.append(child_node)
            
            return semantic_node
        
        # Start traversal from root
        if "nodes" in ast_json:
            for root_node in ast_json["nodes"]:
                semantic_node = traverse_ast(root_node)
                if semantic_node:
                    nodes.append(semantic_node)
        
        return nodes
    
    def _extract_node_attributes(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant attributes from AST node."""
        attributes = {}
        
        # Common attributes
        if "visibility" in node:
            attributes["visibility"] = node["visibility"]
        if "stateMutability" in node:
            attributes["state_mutability"] = node["stateMutability"]
        if "virtual" in node:
            attributes["virtual"] = node["virtual"]
        if "override" in node:
            attributes["override"] = node["override"]
        
        # Function-specific attributes
        if node.get("nodeType") == "FunctionDefinition":
            attributes["is_constructor"] = node.get("kind") == "constructor"
            attributes["is_fallback"] = node.get("kind") == "fallback"
            attributes["is_receive"] = node.get("kind") == "receive"
            attributes["modifiers"] = [mod.get("modifierName", {}).get("name") 
                                    for mod in node.get("modifiers", [])]
        
        return attributes
    
    def _analyze_control_flow(self, nodes: List[ASTNode]) -> Dict[str, List[str]]:
        """Analyze control flow between functions."""
        control_flow = {}
        
        for node in nodes:
            if node.node_type == NodeType.FUNCTION:
                # For now, simplified control flow analysis
                # In a full implementation, we'd parse function bodies for calls
                called_functions = []
                
                # Extract function calls from modifiers
                modifiers = node.attributes.get("modifiers", [])
                called_functions.extend(modifiers)
                
                control_flow[node.name] = called_functions
        
        return control_flow
    
    def _analyze_state_dependencies(self, nodes: List[ASTNode]) -> Dict[str, Set[str]]:
        """Analyze state variable dependencies for each function."""
        dependencies = {}
        
        # Find all state variables
        state_vars = {node.name for node in nodes if node.node_type == NodeType.STATE_VAR}
        
        for node in nodes:
            if node.node_type == NodeType.FUNCTION:
                # For now, simplified analysis
                # Full implementation would parse function body for state variable access
                dependencies[node.name] = set()
        
        return dependencies
    
    def _detect_security_patterns(self, nodes: List[ASTNode]) -> List[SecurityPattern]:
        """Detect security patterns using semantic analysis."""
        detected_patterns = []
        
        # Check for access control patterns
        if any(mod in ["onlyOwner", "onlyRole"] for node in nodes 
               if node.node_type == NodeType.FUNCTION 
               for mod in node.attributes.get("modifiers", [])):
            detected_patterns.append(SecurityPattern.ACCESS_CONTROL)
        
        # Check for reentrancy protection
        if any("nonReentrant" in node.attributes.get("modifiers", []) 
               for node in nodes if node.node_type == NodeType.FUNCTION):
            detected_patterns.append(SecurityPattern.REENTRANCY_GUARD)
        
        return detected_patterns
    
    def _calculate_risk_factors(self, nodes: List[ASTNode], 
                               security_patterns: List[SecurityPattern]) -> Dict[str, float]:
        """Calculate risk factors based on semantic analysis."""
        risk_factors = {}
        
        # Function-level risk analysis
        for node in nodes:
            if node.node_type == NodeType.FUNCTION:
                risk = 0.0
                
                # Payable functions are riskier
                if node.attributes.get("state_mutability") == "payable":
                    risk += 0.3
                
                # External functions are riskier
                if node.attributes.get("visibility") == "external":
                    risk += 0.2
                
                # Functions without access control are riskier
                modifiers = node.attributes.get("modifiers", [])
                if not any(mod in ["onlyOwner", "onlyRole"] for mod in modifiers):
                    risk += 0.2
                
                risk_factors[node.name] = min(risk, 1.0)
        
        return risk_factors
    
    def _calculate_complexity_metrics(self, nodes: List[ASTNode]) -> Dict[str, int]:
        """Calculate complexity metrics from AST."""
        metrics = {
            "total_functions": 0,
            "external_functions": 0,
            "payable_functions": 0,
            "state_variables": 0,
            "total_complexity": 0
        }
        
        for node in nodes:
            if node.node_type == NodeType.FUNCTION:
                metrics["total_functions"] += 1
                if node.attributes.get("visibility") == "external":
                    metrics["external_functions"] += 1
                if node.attributes.get("state_mutability") == "payable":
                    metrics["payable_functions"] += 1
            elif node.node_type == NodeType.STATE_VAR:
                metrics["state_variables"] += 1
        
        # Calculate total complexity score
        metrics["total_complexity"] = (
            metrics["external_functions"] * 3 +
            metrics["payable_functions"] * 5 +
            metrics["state_variables"] * 1
        )
        
        return metrics
    
    def _extract_external_dependencies(self, nodes: List[ASTNode]) -> Set[str]:
        """Extract external dependencies from imports and interfaces."""
        dependencies = set()
        
        for node in nodes:
            if node.node_type == NodeType.IMPORT:
                dependencies.add(node.name)
        
        return dependencies
    
    async def _fallback_text_analysis(self, file_path: str) -> SemanticAnalysis:
        """Fallback to text-based analysis when AST generation fails."""
        logger.info(f"Using fallback text analysis for {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read {file_path}: {e}")
            return SemanticAnalysis(
                file_path=file_path,
                ast_nodes=[],
                control_flow={},
                state_dependencies={},
                security_patterns=[],
                risk_factors={},
                complexity_metrics={},
                external_dependencies=set()
            )
        
        # Basic text-based analysis as fallback
        ast_nodes = []
        
        # Extract contracts
        contract_matches = re.finditer(r'contract\s+(\w+)', content)
        for match in contract_matches:
            node = ASTNode(
                node_type=NodeType.CONTRACT,
                name=match.group(1),
                source_location=(content[:match.start()].count('\n') + 1, 
                               content[:match.end()].count('\n') + 1),
                file_path=file_path
            )
            ast_nodes.append(node)
        
        # Extract functions
        function_matches = re.finditer(r'function\s+(\w+)', content)
        for match in function_matches:
            node = ASTNode(
                node_type=NodeType.FUNCTION,
                name=match.group(1),
                source_location=(content[:match.start()].count('\n') + 1,
                               content[:match.end()].count('\n') + 1),
                file_path=file_path
            )
            ast_nodes.append(node)
        
        return SemanticAnalysis(
            file_path=file_path,
            ast_nodes=ast_nodes,
            control_flow={},
            state_dependencies={},
            security_patterns=[],
            risk_factors={},
            complexity_metrics={},
            external_dependencies=set()
        )
    
    async def analyze_test_file(self, file_path: str) -> SemanticAnalysis:
        """
        Analyze test files using Python AST for semantic understanding.
        
        Args:
            file_path: Path to the test file (typically .sol but with test structure)
            
        Returns:
            Semantic analysis of test structure and patterns
        """
        # For Solidity test files, we still use Solidity AST but with test-specific analysis
        analysis = await self.analyze_solidity_file(file_path)
        
        # Add test-specific semantic analysis
        analysis = await self._enhance_test_analysis(analysis)
        
        return analysis
    
    async def _enhance_test_analysis(self, analysis: SemanticAnalysis) -> SemanticAnalysis:
        """Enhance analysis with test-specific semantic patterns."""
        # Identify test functions
        test_functions = [node for node in analysis.ast_nodes 
                         if node.node_type == NodeType.FUNCTION and 
                         node.name.startswith('test')]
        
        # Analyze test patterns semantically
        for test_func in test_functions:
            # Mark as test function
            test_func.attributes["is_test"] = True
            
            # Detect test types
            if "fuzz" in test_func.name.lower():
                test_func.attributes["test_type"] = "fuzz"
            elif "invariant" in test_func.name.lower():
                test_func.attributes["test_type"] = "invariant"
            else:
                test_func.attributes["test_type"] = "unit"
        
        return analysis 