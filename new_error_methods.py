    
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
        location_match = re.search(r'--> ([^:]+):(\d+):(\d+)', stderr)
        if location_match:
            file_path, line_num, col_num = location_match.groups()
            return f"{file_path}:{line_num}:{col_num}"
        
        # Look for Error in contract pattern  
        contract_match = re.search(r'Error.*?([A-Z][a-zA-Z0-9]+\.sol)', stderr)
        if contract_match:
            return contract_match.group(1)
            
        return "Unknown location"
    
    def _get_stack_too_deep_solutions(self, location: str = "") -> Dict[str, Any]:
        """Get specific solutions for stack too deep errors."""
        base_location = location.split(':')[0] if location else "affected contract"
        
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
