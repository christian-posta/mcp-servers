#!/usr/bin/env python3
"""
Example script demonstrating the MCP Echo Server and Client
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

import httpx
from mcp_echo_client import MCPEchoClient


async def example_basic_usage():
    """Example of basic client usage."""
    print("📖 Example: Basic Client Usage")
    print("-" * 40)
    
    async with MCPEchoClient() as client:
        # Initialize the connection
        init_result = await client.initialize()
        server_name = init_result.get('serverInfo', {}).get('name', 'Unknown')
        print(f"Connected to: {server_name}")
        
        # Simple echo
        result = await client.echo("Hello, MCP!")
        print(f"Echo result: {result}")
        
        # Echo with repetition
        result = await client.echo("Repeat me! ", 3)
        print(f"Repeated echo: {result}")


async def example_tool_calls():
    """Example of direct tool calls."""
    print("\n📖 Example: Direct Tool Calls")
    print("-" * 40)
    
    async with MCPEchoClient() as client:
        await client.initialize()
        
        # Call the echo tool directly
        result = await client.call_tool("echo", {
            "message": "Direct tool call",
            "repeat_count": 2
        })
        
        content = result.get("content", [])
        if content:
            print(f"Tool call result: {content[0].get('text', '')}")


async def example_prompts():
    """Example of using prompts."""
    print("\n📖 Example: Using Prompts")
    print("-" * 40)
    
    async with MCPEchoClient() as client:
        await client.initialize()
        
        # List available prompts
        prompts = await client.list_prompts()
        print(f"Available prompts: {len(prompts)}")
        
        # Get a prompt with arguments
        prompt_result = await client.get_prompt("echo_prompt", {
            "message": "Custom message from prompt"
        })
        
        messages = prompt_result.get("messages", [])
        if messages:
            content = messages[0].get("content", [])
            if content:
                print(f"Prompt result: {content[0].get('text', '')}")


async def example_raw_http():
    """Example of raw HTTP requests."""
    print("\n📖 Example: Raw HTTP Requests")
    print("-" * 40)
    
    async with httpx.AsyncClient() as client:
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": "example-1",
            "method": "initialize"
        }
        
        response = await client.post("http://localhost:8000/mcp", json=init_request)
        init_result = response.json()
        print(f"Initialize response: {init_result.get('result', {}).get('serverInfo', {})}")
        
        # Echo tool call
        echo_request = {
            "jsonrpc": "2.0",
            "id": "example-2",
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Raw HTTP example",
                    "repeat_count": 1
                }
            }
        }
        
        response = await client.post("http://localhost:8000/mcp", json=echo_request)
        echo_result = response.json()
        content = echo_result.get('result', {}).get('content', [])
        if content:
            print(f"Raw HTTP echo result: {content[0].get('text', '')}")


async def example_error_handling():
    """Example of error handling."""
    print("\n📖 Example: Error Handling")
    print("-" * 40)
    
    async with MCPEchoClient() as client:
        await client.initialize()
        
        # Try to call a non-existent tool
        try:
            await client.call_tool("non_existent_tool", {})
        except Exception as e:
            print(f"Expected error for non-existent tool: {e}")
        
        # Try to echo with invalid parameters
        try:
            await client.echo("", -1)  # Invalid repeat_count
        except Exception as e:
            print(f"Expected error for invalid parameters: {e}")


async def main():
    """Run all examples."""
    print("🚀 MCP Echo Server Examples")
    print("=" * 50)
    print("Make sure the server is running with: python -m mcp_server_echo")
    print()
    
    try:
        await example_basic_usage()
        await example_tool_calls()
        await example_prompts()
        await example_raw_http()
        await example_error_handling()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Make sure the server is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main()) 