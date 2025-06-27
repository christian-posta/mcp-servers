#!/usr/bin/env python3
"""
Install and test script for the MCP Echo Server
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Errors: {e.stderr}")
        return e


def install_dependencies():
    """Install dependencies for both server and client."""
    print("🔧 Installing dependencies...")
    
    # Install server dependencies
    server_dir = Path(__file__).parent
    print(f"\nInstalling server dependencies in {server_dir}")
    result = run_command("pip install -e .", cwd=server_dir)
    if result.returncode != 0:
        print("❌ Failed to install server dependencies")
        return False
    
    # Install client dependencies
    client_dir = server_dir.parent / "echo-client"
    print(f"\nInstalling client dependencies in {client_dir}")
    result = run_command("pip install -e .", cwd=client_dir)
    if result.returncode != 0:
        print("❌ Failed to install client dependencies")
        return False
    
    print("✅ All dependencies installed successfully!")
    return True


def test_imports():
    """Test that all modules can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        import mcp_server_echo
        print("✅ mcp_server_echo imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import mcp_server_echo: {e}")
        return False
    
    try:
        import mcp_echo_client
        print("✅ mcp_echo_client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import mcp_echo_client: {e}")
        return False
    
    return True


def main():
    """Main installation and test function."""
    print("🚀 MCP Echo Server Installation and Test")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed!")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    print("\n✅ Installation and basic tests completed successfully!")
    print("\nNext steps:")
    print("1. Start the server: python -m mcp_server_echo")
    print("2. In another terminal, run the client: python -m mcp_echo_client")
    print("3. Or run the examples: python example.py")
    print("4. Or run the tests: python test_server.py")


if __name__ == "__main__":
    main() 