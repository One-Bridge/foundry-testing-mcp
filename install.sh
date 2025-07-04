#!/bin/bash
# Smart Contract Testing MCP Server - Installation Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🔒⚡ Smart Contract Testing MCP Server Installation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3.8+ is available
check_python() {
    print_step "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        major=$(echo $python_version | cut -d'.' -f1)
        minor=$(echo $python_version | cut -d'.' -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            print_success "Python $python_version found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ required. Found: $python_version"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    print_step "Checking pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install pip"
        exit 1
    fi
}

# Check if Foundry is installed
check_foundry() {
    print_step "Checking Foundry installation..."
    
    if command -v forge &> /dev/null; then
        forge_version=$(forge --version | head -n1)
        print_success "Foundry found: $forge_version"
    else
        print_warning "Foundry not found"
        echo "To install Foundry, run: curl -L https://foundry.paradigm.xyz | bash"
        echo "Then restart your terminal and run: foundryup"
        echo ""
        read -p "Continue without Foundry? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create virtual environment
setup_venv() {
    print_step "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Upgrade pip first
    $PIP_CMD install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies
    read -p "Install development dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $PIP_CMD install -e ".[dev]"
        print_success "Development dependencies installed"
    fi
}

# Setup environment configuration
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success "Environment file created from template"
        else
            print_warning "No environment template found"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Make scripts executable
setup_scripts() {
    print_step "Setting up scripts..."
    
    chmod +x run.py
    chmod +x run_clean.py
    chmod +x install.sh
    
    print_success "Scripts made executable"
}

# Run basic tests
run_tests() {
    print_step "Running basic tests..."
    
    if command -v pytest &> /dev/null; then
        # Run a simple import test
        $PYTHON_CMD -c "
try:
    from components.testing_server import TestingMCPServer
    print('✅ Import test passed')
except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
"
        print_success "Basic tests passed"
    else
        print_warning "pytest not available, skipping tests"
    fi
}

# Test server startup
test_server_startup() {
    print_step "Testing server startup..."
    
    # Test the clean runner
    timeout 3 $PYTHON_CMD run_clean.py &
    clean_pid=$!
    sleep 1
    
    if kill -0 $clean_pid 2>/dev/null; then
        kill $clean_pid 2>/dev/null
        print_success "Clean server startup test passed"
    else
        print_warning "Clean server startup test failed"
    fi
}

# Main installation flow
main() {
    echo "Starting installation process..."
    echo ""
    
    check_python
    check_pip
    check_foundry
    setup_venv
    install_dependencies
    setup_environment
    setup_scripts
    run_tests
    test_server_startup
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo ""
    echo "For MCP Client Integration (Cursor, Claude Desktop):"
    echo "1. Configure your MCP client with:"
    echo "   Command: $(pwd)/venv/bin/python"
    echo "   Args: $(pwd)/run_clean.py"
    echo "   Environment: MCP_TRANSPORT_MODE=stdio"
    echo ""
    echo "For Development and Debugging:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Configure .env file if needed"
    echo "3. Start the development server: python run.py"
    echo ""
    echo "📝 Script Usage:"
    echo "• run_clean.py - For MCP client integration (silent mode)"
    echo "• run.py       - For development and debugging (verbose mode)"
    echo ""
    echo "🔧 Available tools after connection:"
    echo "• initialize_protocol_testing_agent"
    echo "• execute_testing_workflow"
    echo "• analyze_current_test_coverage"
    echo "• validate_current_project"
    echo "• get_server_info"
    echo ""
    echo "📖 Documentation:"
    echo "• README.md - Quick start guide"
    echo "• docs/user-implementation-walkthrough.md - Detailed usage guide"
    echo "• docs/technical-architecture-guide.md - Technical details"
    echo ""
}

# Run main installation
main "$@" 