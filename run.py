#!/usr/bin/env python3
"""
Smart Contract Testing MCP Server - Runner Script

Simple script to start the MCP server with proper configuration and error handling.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("testing_mcp_server.log", mode="a")
        ]
    )

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import fastmcp
        print("✅ FastMCP dependency found")
    except ImportError:
        print("❌ FastMCP not found. Please install with: pip install fastmcp")
        return False
    
    # Check for Foundry
    import shutil
    if not shutil.which("forge"):
        print("⚠️  Foundry not found. Please install from https://getfoundry.sh/")
        print("   The server will start but Foundry features will be limited.")
    else:
        print("✅ Foundry found")
    
    return True

def load_environment():
    """Load environment variables from .env file if it exists."""
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Environment loaded from {env_file}")
        except ImportError:
            print("⚠️  python-dotenv not installed. Environment file ignored.")
    
    # Set default values
    os.environ.setdefault("MCP_TRANSPORT_MODE", "stdio")
    os.environ.setdefault("MCP_SERVER_HOST", "127.0.0.1")
    os.environ.setdefault("MCP_SERVER_PORT", "8002")

def print_banner():
    """Print startup banner."""
    print("""
🔒⚡ Smart Contract Testing MCP Server
=====================================
Interactive AI-Powered Testing Workflows
    """)
    
    print(f"📁 Project Root: {project_root}")
    print(f"🚀 Transport Mode: {os.getenv('MCP_TRANSPORT_MODE', 'stdio')}")
    
    if os.getenv('MCP_TRANSPORT_MODE') == 'http':
        host = os.getenv('MCP_SERVER_HOST', '127.0.0.1')
        port = os.getenv('MCP_SERVER_PORT', '8002')
        print(f"🌐 Server Address: http://{host}:{port}")
    
    print("=====================================\n")

def main():
    """Main entry point."""
    print_banner()
    setup_logging()
    
    if not check_dependencies():
        sys.exit(1)
    
    load_environment()
    
    try:
        # Import and start the server using its built-in main function
        from components.testing_server import main as server_main
        
        print("🔄 Initializing Smart Contract Testing MCP Server...")
        print("📡 Starting server...")
        
        # Let the server handle everything including event loop management
        asyncio.run(server_main())
        
    except KeyboardInterrupt:
        # Handle graceful shutdown without printing if I/O is closed
        try:
            print("\n👋 Server shutdown requested by user")
        except (ValueError, OSError):
            pass
    except Exception as e:
        try:
            logging.error(f"Server error: {e}")
            print(f"❌ Server error: {e}")
        except (ValueError, OSError):
            pass
        sys.exit(1)
    finally:
        try:
            print("🛑 Server stopped")
        except (ValueError, OSError):
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            print("\n👋 Goodbye!")
        except (ValueError, OSError):
            pass
    except Exception as e:
        try:
            print(f"❌ Fatal error: {e}")
        except (ValueError, OSError):
            pass
        sys.exit(1) 