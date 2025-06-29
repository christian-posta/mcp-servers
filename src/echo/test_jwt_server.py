import asyncio
import json
from typing import Optional

import httpx

MCP_SERVER_URL = "http://localhost:9000"

class SimpleMCPClient:
    """Simple MCP client for testing JWT authentication."""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
    
    async def get_demo_tokens(self):
        """Get demo tokens from the server."""
        print("🎫 Fetching demo tokens...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/auth/demo-tokens")
            
            if response.status_code == 200:
                tokens = response.json()["demo_tokens"]
                print("\n📋 Available Demo Tokens:")
                print("=" * 50)
                
                for i, token_info in enumerate(tokens, 1):
                    print(f"{i}. User: {token_info['user']}")
                    print(f"   Scopes: {', '.join(token_info['scopes'])}")
                    print(f"   Token: {token_info['token'][:50]}...")
                    print()
                
                return tokens
            else:
                print(f"❌ Failed to get demo tokens: {response.status_code}")
                return []
    
    async def generate_custom_token(self, username: str, scopes: list = None):
        """Generate a custom token for a specific user."""
        if scopes is None:
            scopes = ["mcp:read", "mcp:tools", "mcp:prompts"]
        
        print(f"🔑 Generating token for user: {username}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/auth/token",
                json={
                    "username": username,
                    "scopes": scopes
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                
                print(f"✅ Token generated successfully!")
                print(f"User: {token_data['user']}")
                print(f"Expires in: {token_data['expires_in']} seconds")
                print(f"Scopes: {token_data['scope']}")
                print(f"Token: {self.access_token[:50]}...")
                
                return token_data
            else:
                print(f"❌ Failed to generate token: {response.status_code}")
                print(f"Error: {response.text}")
                return None
    
    async def test_mcp_requests(self):
        """Test various MCP requests."""
        if not self.access_token:
            print("❌ No access token set. Generate one first.")
            return
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Test initialize
            print("\n🚀 Testing MCP initialize...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "jwt-test-client", "version": "1.0.0"}
                    }
                }
            )
            await self.print_response("Initialize", response)
            
            # Test tools/list
            print("\n🔧 Testing tools/list...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
            )
            await self.print_response("Tools List", response)
            
            # Test whoami tool
            print("\n👤 Testing whoami tool...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "whoami",
                        "arguments": {}
                    }
                }
            )
            await self.print_response("Whoami Tool", response)
            
            # Test echo tool
            print("\n📢 Testing echo tool...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "echo",
                        "arguments": {"message": "Hello from JWT client!"}
                    }
                }
            )
            await self.print_response("Echo Tool", response)
            
            # Test admin tool (will fail for non-admin users)
            print("\n🔐 Testing admin tool...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "admin_tool",
                        "arguments": {"action": "test_admin_action"}
                    }
                }
            )
            await self.print_response("Admin Tool", response)
            
            # Test prompts/list
            print("\n📝 Testing prompts/list...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "prompts/list"
                }
            )
            await self.print_response("Prompts List", response)
            
            # Test ping
            print("\n🏓 Testing ping...")
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "ping"
                }
            )
            await self.print_response("Ping", response)
    
    async def test_without_token(self):
        """Test MCP request without token (should get 401)."""
        print("\n🚫 Testing request without token (should fail)...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "ping"
                }
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 401:
                print("✅ Correctly returned 401 Unauthorized")
                print(f"WWW-Authenticate: {response.headers.get('WWW-Authenticate', 'Not set')}")
            else:
                print(f"❌ Expected 401, got {response.status_code}")
            print(f"Response: {response.text}")
    
    async def debug_token(self):
        """Debug the current token."""
        if not self.access_token:
            print("❌ No access token set.")
            return
        
        print("🔍 Debugging current token...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/auth/debug-token",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                debug_info = response.json()
                if debug_info.get("status") == "valid":
                    print("✅ Token is valid!")
                    print(f"User: {debug_info.get('user')}")
                    if 'debug' in debug_info:
                        debug = debug_info['debug']
                        print(f"Current time: {debug.get('current_time')}")
                        print(f"Token issued: {debug.get('token_iat_human')}")
                        print(f"Token expires: {debug.get('token_exp_human')}")
                else:
                    print("❌ Token validation failed!")
                    print(f"Error: {debug_info.get('error')}")
                    if 'debug' in debug_info:
                        debug = debug_info['debug']
                        print(f"\n🕐 Time Debug Info:")
                        print(f"Current time: {debug.get('current_time')} (timestamp: {debug.get('current_timestamp')})")
                        print(f"Token iat: {debug.get('token_iat_human')} (timestamp: {debug.get('token_iat')})")
                        print(f"Token exp: {debug.get('token_exp_human')} (timestamp: {debug.get('token_exp')})")
                        print(f"Is future token: {debug.get('is_future_token')}")
                        print(f"Is expired: {debug.get('is_expired')}")
                        if debug.get('time_until_valid', 0) > 0:
                            print(f"⏰ Token will be valid in {debug.get('time_until_valid')} seconds")
            else:
                print(f"❌ Debug request failed: {response.status_code}")
                print(f"Response: {response.text}")
        
        # Also check server time
        print("\n🕐 Checking server time...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/auth/time-check")
            if response.status_code == 200:
                time_info = response.json()
                print(f"Server time: {time_info.get('server_time_utc')} UTC")
                print(f"Server timestamp: {time_info.get('server_timestamp')}")
            else:
                print(f"❌ Could not get server time: {response.status_code}")
        """Pretty print HTTP response."""
    async def print_response(self, test_name: str, response: httpx.Response):
        """Pretty print HTTP response."""
        print(f"{test_name} - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "result" in data:
                    print(f"✅ Success: {json.dumps(data['result'], indent=2)}")
                else:
                    print(f"✅ Response: {json.dumps(data, indent=2)}")
            except:
                print(f"✅ Response: {response.text}")
        else:
            print(f"❌ Error: {response.text}")

async def main():
    """Main function to test JWT authentication."""
    client = SimpleMCPClient()
    
    print("🔑 Simple JWT MCP Test Client")
    print("=" * 50)
    
    # Test without token first
    await client.test_without_token()
    
    print("\n" + "=" * 50)
    print("Choose an option:")
    print("1. Use demo tokens")
    print("2. Generate custom token")
    print("3. Use existing token")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Get demo tokens and let user choose
        tokens = await client.get_demo_tokens()
        if tokens:
            token_choice = input("\nEnter token number (1-3): ").strip()
            try:
                token_index = int(token_choice) - 1
                if 0 <= token_index < len(tokens):
                    client.access_token = tokens[token_index]["token"]
                    print(f"✅ Using token for user: {tokens[token_index]['user']}")
                    
                    # Debug the token
                    await client.debug_token()
                else:
                    print("❌ Invalid token number")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
    
    elif choice == "2":
        # Generate custom token
        username = input("Enter username: ").strip()
        
        print("\nAvailable scopes:")
        print("1. mcp:read")
        print("2. mcp:tools") 
        print("3. mcp:prompts")
        print("4. All scopes")
        
        scope_choice = input("Enter scope choice (1-4): ").strip()
        
        scope_map = {
            "1": ["mcp:read"],
            "2": ["mcp:tools"],
            "3": ["mcp:prompts"],
            "4": ["mcp:read", "mcp:tools", "mcp:prompts"]
        }
        
        scopes = scope_map.get(scope_choice, ["mcp:read", "mcp:tools", "mcp:prompts"])
        
        await client.generate_custom_token(username, scopes)
        if client.access_token:
            await client.debug_token()
    
    elif choice == "3":
        # Use existing token
        token = input("Enter JWT token: ").strip()
        client.access_token = token
        print("✅ Token set successfully")
        await client.debug_token()
    
    else:
        print("❌ Invalid choice")
        return
    
    if client.access_token:
        print("\n" + "=" * 50)
        print("🧪 Running MCP Tests...")
        await client.test_mcp_requests()

if __name__ == "__main__":
    asyncio.run(main())