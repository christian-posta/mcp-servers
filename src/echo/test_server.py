#!/usr/bin/env python3
"""
Test script for the MCP Echo Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

import httpx
from mcp_echo_client import MCPEchoClient


async def test_server():
    """Test the echo server functionality."""
    print("🧪 Testing MCP Echo Server")
    print("=" * 50)
    
    # Test server health
    print("\n1. Testing server health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Server is healthy: {health}")
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python -m mcp_server_echo")
        return False
    
    # Test MCP client
    print("\n2. Testing MCP client...")
    try:
        async with MCPEchoClient() as client:
            # Initialize
            print("   Initializing...")
            init_result = await client.initialize()
            print(f"   ✅ Initialized: {init_result.get('serverInfo', {}).get('name', 'Unknown')}")
            
            # List tools
            print("   Listing tools...")
            tools = await client.list_tools()
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool['name']}: {tool['description']}")
            
            # List prompts
            print("   Listing prompts...")
            prompts = await client.list_prompts()
            print(f"   ✅ Found {len(prompts)} prompts:")
            for prompt in prompts:
                print(f"      - {prompt['name']}: {prompt['description']}")
            
            # Test echo tool
            print("   Testing echo tool...")
            echo_result = await client.echo("Test message", 2)
            expected = "Test messageTest message"
            if echo_result == expected:
                print(f"   ✅ Echo works: {echo_result}")
            else:
                print(f"   ❌ Echo failed: expected '{expected}', got '{echo_result}'")
                return False
            
            # Test ping
            print("   Testing ping...")
            ping_result = await client.ping()
            print(f"   ✅ Ping successful: {ping_result}")
            
    except Exception as e:
        print(f"   ❌ Client test failed: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True


async def test_raw_http():
    """Test raw HTTP requests to the MCP endpoint."""
    print("\n3. Testing raw HTTP requests...")
    
    async with httpx.AsyncClient() as client:
        # Test initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize"
        }
        
        response = await client.post("http://localhost:8000/mcp", json=init_request)
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "error" not in result:
                print("   ✅ Raw initialize request successful")
            else:
                print(f"   ❌ Raw initialize failed: {result}")
                return False
        else:
            print(f"   ❌ Raw initialize failed: {response.status_code}")
            return False
        
        # Test echo tool call
        echo_request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Raw HTTP test",
                    "repeat_count": 1
                }
            }
        }
        
        response = await client.post("http://localhost:8000/mcp", json=echo_request)
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "error" not in result:
                content = result["result"].get("content", [])
                if content and content[0].get("text") == "Raw HTTP test":
                    print("   ✅ Raw echo request successful")
                else:
                    print(f"   ❌ Raw echo content mismatch: {content}")
                    return False
            else:
                print(f"   ❌ Raw echo failed: {result}")
                return False
        else:
            print(f"   ❌ Raw echo failed: {response.status_code}")
            return False
    
    print("   ✅ All raw HTTP tests passed!")
    return True


async def main():
    """Run all tests."""
    print("Starting MCP Echo Server tests...")
    
    # Test 1: Server health and client functionality
    if not await test_server():
        print("\n❌ Server tests failed!")
        sys.exit(1)
    
    # Test 2: Raw HTTP requests
    if not await test_raw_http():
        print("\n❌ Raw HTTP tests failed!")
        sys.exit(1)
    
    print("\n🎉 All tests completed successfully!")
    print("\nTo run the server:")
    print("  cd src/echo")
    print("  python -m mcp_server_echo")
    print("\nTo run the client demo:")
    print("  cd src/echo-client")
    print("  python -m mcp_echo_client")


if __name__ == "__main__":
    asyncio.run(main()) 