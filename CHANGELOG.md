# Changelog

All notable changes to the Foundry Testing MCP will be documented in this file.

## [1.1.0] - 2024-01-XX

### Added
- **New `run_clean.py` Script**: Clean MCP server runner specifically designed for MCP client integration
  - Silent operation with no stdout/stderr interference
  - Errors logged to `/tmp/mcp_server_error.log` instead of console
  - Optimized for MCP protocol communication
  - Graceful shutdown handling
- **Dual Operation Modes**: Clear separation between production and development server startup
- **Enhanced Documentation**: Updated all documentation to reflect new deployment approach
- **Improved Installation Script**: Updated `install.sh` with guidance for both modes

### Changed
- **MCP Client Integration**: Now uses `run_clean.py` instead of `run.py` for Cursor, Claude Desktop, and other MCP clients
- **Error Handling**: Production mode logs errors to files rather than console to avoid protocol interference
- **Logging Strategy**: Silent logging in production mode, verbose logging in development mode
- **Documentation Updates**: All docs now reflect the new dual-mode approach

### Fixed
- **MCP Protocol Interference**: Resolved "red dot" issues in MCP clients caused by stdout/stderr conflicts
- **FastMCP 2.10.1 Compatibility**: Fixed compatibility issues with latest FastMCP version
- **Resource URI Validation**: Fixed resource URI formatting for FastMCP 2.10.1 requirements
- **Async Event Loop Conflicts**: Resolved "Already running asyncio in this thread" errors
- **Dependencies**: Removed non-existent `asyncio-extensions` package from requirements

### Migration Guide

**For MCP Client Users:**
1. Update your MCP client configuration to use `run_clean.py`:
   ```json
   {
     "mcpServers": {
       "foundry-testing": {
         "command": "/path/to/foundry-testing-mcp/venv/bin/python",
         "args": ["/path/to/foundry-testing-mcp/run_clean.py"],
         "env": {
           "MCP_TRANSPORT_MODE": "stdio"
         }
       }
     }
   }
   ```

**For Developers:**
- Continue using `run.py` for development and debugging
- Use `run_clean.py` only for MCP client integration
- Check updated documentation for new deployment patterns

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Foundry Testing MCP
- Complete testing workflow automation
- AI-guided testing strategy development
- Comprehensive test template system
- Deep Foundry CLI integration
- Real-time coverage analysis
- Security testing patterns
- Interactive session management
- Professional documentation suite

### Features
- **TestingMCPServer**: Main FastMCP server with component orchestration
- **FoundryAdapter**: Deep Foundry CLI integration with async command execution
- **TestingTools**: Interactive workflow management with 4-phase testing execution
- **TestingResources**: MCP resource management for templates and documentation
- **TestingPrompts**: AI-guided analysis and strategy development
- **Template System**: Professional test templates for all testing scenarios
- **Coverage Analysis**: Real-time coverage tracking with gap identification
- **Security Testing**: Built-in security testing patterns and vulnerability detection

### Documentation
- Executive Summary with business case and ROI analysis
- Technical Architecture Guide with detailed implementation specs
- User Implementation Walkthrough with complete usage examples
- Comprehensive README with quick start guide 