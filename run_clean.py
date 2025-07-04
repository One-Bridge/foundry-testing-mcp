#!/usr/bin/env python3
"""
Clean MCP Server Runner for Cursor Integration
==============================================

This runner is specifically designed for MCP clients like Cursor.
It removes all stdout/stderr interference to ensure clean MCP protocol communication.

For development and debugging, use run.py instead.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_silent_logging():
    """Setup logging that doesn't interfere with MCP protocol."""
    # Create a null handler that discards all log messages
    null_handler = logging.NullHandler()
    
    # Configure root logger to use null handler
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(null_handler)
    root_logger.setLevel(logging.CRITICAL)
    
    # Silence all MCP-related loggers
    for logger_name in ['fastmcp', 'mcp', 'components', 'testing_server']:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(null_handler)
        logger.setLevel(logging.CRITICAL)
        logger.propagate = False

def load_environment_silent():
    """Load environment variables without any output."""
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass  # dotenv not available, continue silently

async def main():
    """Clean main entry point for MCP protocol."""
    # Setup silent logging first
    setup_silent_logging()
    
    # Load environment silently
    load_environment_silent()
    
    # Set MCP transport mode to stdio
    os.environ["MCP_TRANSPORT_MODE"] = "stdio"
    
    try:
        # Import and run server
        from components.testing_server import TestingMCPServer
        
        # Create and run server
        server = TestingMCPServer()
        await server.run_server()
        
    except Exception as e:
        # Log to stderr only if absolutely necessary
        # Most MCP protocol errors should be handled by FastMCP
        import traceback
        error_msg = f"Server error: {e}\n{traceback.format_exc()}"
        # Write to a log file instead of stderr to avoid protocol interference
        try:
            with open("/tmp/mcp_server_error.log", "w") as f:
                f.write(error_msg)
        except:
            pass  # If we can't write to log, fail silently
        
        # Exit with error code
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully without output
        sys.exit(0)
    except Exception:
        # Exit silently on any other error
        sys.exit(1) 