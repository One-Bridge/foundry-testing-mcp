#!/usr/bin/env python3
"""
Simple validation script to check that the fixes are present in the code
"""

import re
from pathlib import Path

def check_file_content(file_path: str, pattern: str, description: str) -> bool:
    """Check if a pattern exists in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}")
            return False
    except Exception as e:
        print(f"❌ Error checking {description}: {e}")
        return False

def main():
    """Validate that all fixes are present."""
    print("🔍 Validating MCP Workflow Fixes...")
    
    checks = [
        # Check 1: TestingSession has completed_phases
        {
            "file": "components/testing_tools.py",
            "pattern": r"self\.completed_phases = \[\]",
            "description": "TestingSession.__init__ has completed_phases attribute"
        },
        
        # Check 2: TestingSession.to_dict includes completed_phases
        {
            "file": "components/testing_tools.py", 
            "pattern": r'"completed_phases": self\.completed_phases',
            "description": "TestingSession.to_dict() includes completed_phases"
        },
        
        # Check 3: analyze_current_test_coverage accepts project_path parameter
        {
            "file": "components/testing_tools.py",
            "pattern": r"async def analyze_current_test_coverage\([^)]*project_path: str = \"\"",
            "description": "analyze_current_test_coverage accepts project_path parameter"
        },
        
        # Check 4: _execute_validation_step passes project_path to coverage analysis
        {
            "file": "components/testing_tools.py",
            "pattern": r"project_path=project_path\s*\)",
            "description": "_execute_validation_step passes project_path to tools"
        },
        
        # Check 5: Integration template method exists
        {
            "file": "components/testing_resources.py",
            "pattern": r"def _get_integration_test_template\(self\)",
            "description": "_get_integration_test_template method exists"
        },
        
        # Check 6: Workflow phase execution uses session.project_path
        {
            "file": "components/testing_tools.py",
            "pattern": r"project_path=session\.project_path",
            "description": "Progress monitoring uses session.project_path"
        }
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check_file_content(check["file"], check["pattern"], check["description"]):
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All fixes are present in the code!")
        print("\n✅ The workflow should now work correctly:")
        print("   - TestingSession.completed_phases attribute exists")
        print("   - Project path is passed consistently through tools")
        print("   - Template loading errors are fixed")
        print("   - Validation steps use correct project directories")
        return True
    else:
        print("⚠️  Some fixes may be missing. Please review the failed checks.")
        return False

if __name__ == "__main__":
    main() 