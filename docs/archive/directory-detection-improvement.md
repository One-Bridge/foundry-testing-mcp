# Directory Detection Improvements - Seamless Project Usage

## The Goal: Seamless Developer Experience

**What users want**: Open their Solidity project, call MCP tools, and have them automatically work on that project.

**Previous behavior**: Tools would detect directory issues and refuse to work.

**New behavior**: Tools automatically work on whatever directory you're calling them from, with helpful guidance when needed.

## How It Works Now

### Priority-Based Directory Resolution

The MCP tools now use a smart priority system to find your project:

1. **Explicit Path**: If you specify a project path, that's used
2. **MCP_CLIENT_CWD**: Your editor/client's working directory (automatic)
3. **MCP_PROJECT_PATH**: Manual override if needed  
4. **Current Directory**: Whatever directory the server is running from

### Seamless Workflow

```
User Workflow:
├── cd /path/to/my-defi-project     # Navigate to your project
├── Open project in Cursor/editor   # MCP client sets working directory
├── Call: initialize_protocol_testing_agent()  # Tools work on your project
└── ✅ Analysis begins automatically
```

### Helpful Guidance Instead of Errors

**Before**:
```json
{
  "status": "validation_failed",
  "error": "No smart contract framework detected"
}
```

**Now**:
```json
{
  "status": "project_setup_needed",
  "guidance": {
    "message": "No Foundry project detected - let's help you set one up!",
    "quick_setup": {
      "option_1": {
        "title": "Initialize Foundry in current directory", 
        "command": "forge init --force"
      }
    }
  }
}
```

## Configuration Examples

### Automatic (Recommended)

Most MCP clients automatically set the working directory:

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/path/to/python",
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"]
    }
  }
}
```

The client automatically sets `MCP_CLIENT_CWD` to your current working directory.

### Manual Override (If Needed)

```json
{
  "mcpServers": {
    "foundry-testing": {
      "command": "/path/to/python", 
      "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "MCP_CLIENT_CWD": "/path/to/your/project"
      }
    }
  }
}
```

## Common Scenarios

### Scenario 1: Working on Existing Foundry Project

```bash
cd /path/to/my-defi-protocol     # Your project with foundry.toml
# Call MCP tools - they automatically work here
```

**Result**: Tools immediately analyze your contracts and provide testing guidance.

### Scenario 2: Starting New Project

```bash
cd /path/to/new-project-folder   # Empty or basic directory  
# Call MCP tools
```

**Result**: Tools detect no Foundry project and offer to help set one up with `forge init`.

### Scenario 3: Wrong Directory Detection

If directory detection isn't working:

1. **Use the debug tool**: `debug_directory_detection()`
2. **Get specific guidance** for your MCP client configuration
3. **Manual override** with environment variables if needed

## Key Benefits

### ✅ Seamless Usage
- Open project → Call tools → They work automatically
- No manual configuration for standard setups
- Tools adapt to whatever directory you're working in

### ✅ Helpful, Not Blocking
- Instead of refusing to work, tools offer to help set up projects
- Clear guidance for getting from "no project" to "working project"
- Smart detection of different project types (Hardhat, Truffle, etc.)

### ✅ Clear Troubleshooting
- Debug tools show exactly what directory is being used
- Specific configuration examples for different MCP clients
- Step-by-step guidance when things aren't working

## Developer Experience

**The goal**: You should never have to think about directory detection. The tools should just work on whatever project you're currently working on.

**User workflow**:
1. `cd my-project` (or open in editor)
2. Call MCP tools
3. Tools automatically work on your project
4. If no Foundry project exists, tools help you set one up

This creates a smooth, frustration-free experience where the testing tools integrate naturally into your development workflow. 