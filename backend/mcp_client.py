"""
Enhanced MCP Client Wrapper for Shopping Assistant.
Uses HTTP/SSE transport for better compatibility with external APIs.
"""
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, create_model
from typing import Optional, Any, Dict
import asyncio
import json
import sys
import os
import subprocess
import time
import requests


class HTTPMCPClient:
    """MCP client using HTTP/SSE transport."""
    
    def __init__(self, server_host: str = "localhost", server_port: int = 8001):
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"http://{server_host}:{server_port}/sse"
        self.tools = []
        self.server_process = None
    
    def start_server(self, server_script_path: str):
        """Start the MCP server as a subprocess."""
        python_exec = sys.executable
        
        print(f"🚀 Starting MCP Server...", file=sys.stderr)
        print(f"   Server: {server_script_path}", file=sys.stderr)
        print(f"   Python: {python_exec}", file=sys.stderr)
        print(f"   URL: {self.server_url}", file=sys.stderr)
        sys.stderr.flush()
        
        # Start server process
        self.server_process = subprocess.Popen(
            [python_exec, server_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to be ready
        print("⏳ Waiting for server to start...", file=sys.stderr)
        sys.stderr.flush()
        
        # Give it a few seconds to start up
        time.sleep(3)
        
        # Check if process is still running
        if self.server_process.poll() is not None:
            # Process died
            stdout = self.server_process.stdout.read()
            stderr = self.server_process.stderr.read()
            print(f"❌ Server process died!", file=sys.stderr)
            print(f"STDOUT: {stdout}", file=sys.stderr)
            print(f"STDERR: {stderr}", file=sys.stderr)
            return False
        
        print(f"✅ Server process running (PID: {self.server_process.pid})", file=sys.stderr)
        sys.stderr.flush()
        return True
    
    async def connect_and_get_tools(self):
        """Connect to MCP server via SSE and retrieve tools."""
        print(f"🔌 Connecting to MCP Server at {self.server_url}...", file=sys.stderr)
        sys.stderr.flush()
        
        try:
            # Connect using SSE client
            async with sse_client(self.server_url) as (read_stream, write_stream):
                print("✅ SSE streams connected", file=sys.stderr)
                sys.stderr.flush()
                
                async with ClientSession(read_stream, write_stream) as session:
                    print("✅ Client session created", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # Initialize the connection
                    init_result = await session.initialize()
                    print(f"✅ Connected to MCP server", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    print(f"✅ Found {len(tools_result.tools)} tools:", file=sys.stderr)
                    
                    # Convert MCP tools to LangChain tools
                    langchain_tools = []
                    for mcp_tool in tools_result.tools:
                        print(f"   📦 {mcp_tool.name}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        # Create LangChain tool with HTTP client
                        lc_tool = self._create_langchain_tool(mcp_tool)
                        langchain_tools.append(lc_tool)
                    
                    self.tools = langchain_tools
                    return langchain_tools
        
        except Exception as e:
            print(f"❌ Connection failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            raise
    
    def _create_args_schema(self, mcp_tool) -> type[BaseModel]:
        """Create a Pydantic model for tool arguments based on MCP tool schema."""
        
        # Get input schema from MCP tool
        if not hasattr(mcp_tool, 'inputSchema') or not mcp_tool.inputSchema:
            # No schema - create empty model
            return create_model(f"{mcp_tool.name}Args")
        
        schema = mcp_tool.inputSchema
        
        # Extract properties and required fields
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # Build field definitions for Pydantic model
        field_definitions = {}
        for prop_name, prop_schema in properties.items():
            # Determine type
            prop_type = prop_schema.get('type', 'string')
            description = prop_schema.get('description', '')
            
            # Map JSON schema types to Python types
            if prop_type == 'string':
                py_type = str
            elif prop_type == 'number':
                py_type = float
            elif prop_type == 'integer':
                py_type = int
            elif prop_type == 'boolean':
                py_type = bool
            elif prop_type == 'array':
                py_type = list
            elif prop_type == 'object':
                py_type = dict
            else:
                py_type = Any
            
            # Make optional if not required
            if prop_name not in required:
                py_type = Optional[py_type]
                field_definitions[prop_name] = (py_type, Field(default=None, description=description))
            else:
                field_definitions[prop_name] = (py_type, Field(description=description))
        
        # Create dynamic Pydantic model
        return create_model(f"{mcp_tool.name}Args", **field_definitions)
    
    def _create_langchain_tool(self, mcp_tool):
        """Convert MCP tool to LangChain StructuredTool with HTTP calls."""
        
        # Create args schema
        args_schema = self._create_args_schema(mcp_tool)
        
        # Create wrapper function that accepts the schema
        def sync_tool_wrapper(**kwargs) -> str:
            """Synchronous wrapper that calls tool via HTTP."""
            print(f"🔧 Tool wrapper called: {mcp_tool.name}", file=sys.stderr)
            print(f"   Kwargs received: {kwargs}", file=sys.stderr)
            sys.stderr.flush()
            
            # Create new event loop for async call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._call_tool_http(mcp_tool.name, kwargs))
                return result
            finally:
                loop.close()
        
        return StructuredTool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"MCP tool: {mcp_tool.name}",
            func=sync_tool_wrapper,
            args_schema=args_schema,
            return_direct=False
        )
    
    async def _call_tool_http(self, tool_name: str, arguments: dict) -> str:
        """Call tool via HTTP/SSE and format response properly."""
        print(f"🌐 Calling MCP tool: {tool_name}", file=sys.stderr)
        print(f"   Arguments: {arguments}", file=sys.stderr)
        sys.stderr.flush()
        
        try:
            # Connect and make the call
            async with sse_client(self.server_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, arguments=arguments)
                    
                    print(f"✅ Tool call completed", file=sys.stderr)
                    print(f"   Content items: {len(result.content) if result.content else 0}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # Extract and format content from result
                    if result.content:
                        # FastMCP returns multiple TextContent items for list results
                        # We need to combine them into a proper JSON structure
                        
                        if len(result.content) == 1:
                            # Single item - return as is
                            item = result.content[0]
                            if hasattr(item, 'text'):
                                return item.text
                        else:
                            # Multiple items - this is a list of products
                            # Parse each item as JSON and combine into array
                            items = []
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    try:
                                        parsed = json.loads(content_item.text)
                                        items.append(parsed)
                                    except json.JSONDecodeError:
                                        # If not JSON, just add the text
                                        items.append({"text": content_item.text})
                            
                            # Return as JSON array string
                            result_json = json.dumps(items)
                            print(f"📤 Returning {len(items)} items", file=sys.stderr)
                            sys.stderr.flush()
                            return result_json
                    
                    return json.dumps({"error": "Empty response"})
        
        except Exception as e:
            error_result = json.dumps({"error": str(e)})
            print(f"❌ Tool call error: {error_result}", file=sys.stderr)
            sys.stderr.flush()
            return error_result
    
    def shutdown(self):
        """Shutdown the server process."""
        if self.server_process:
            print("🛑 Shutting down MCP server...", file=sys.stderr)
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Server stopped", file=sys.stderr)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️ Server killed (didn't stop gracefully)", file=sys.stderr)


# Global client instance
_mcp_client = None


def get_mcp_tools(host: str = "localhost", port: int = 8001, auto_start_server: bool = True):
    """Get MCP tools using HTTP/SSE transport."""
    global _mcp_client
    
    if _mcp_client is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "mcp_server.py")
        
        # Create client
        _mcp_client = HTTPMCPClient(server_host=host, server_port=port)
        
        # Only start server if requested and check if it's not already running
        if auto_start_server:
            # Check if server is already running
            try:
                test_url = f"http://{host}:{port}/sse"
                response = requests.get(test_url, timeout=1)
                print(f"✅ MCP Server already running at {test_url}", file=sys.stderr)
                sys.stderr.flush()
            except requests.exceptions.RequestException:
                # Server not running, start it
                if not _mcp_client.start_server(server_path):
                    print("❌ Failed to start MCP server", file=sys.stderr)
                    return []
        else:
            print(f"⚠️ Auto-start disabled. Make sure MCP server is running at http://{host}:{port}", file=sys.stderr)
            sys.stderr.flush()
        
        # Connect and get tools
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tools = loop.run_until_complete(_mcp_client.connect_and_get_tools())
            loop.close()
            return tools
        except Exception as e:
            print(f"❌ Failed to get tools: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            loop.close()
            return []
    
    return _mcp_client.tools


def shutdown_mcp_client():
    """Shutdown the MCP client and server."""
    global _mcp_client
    if _mcp_client:
        _mcp_client.shutdown()
        _mcp_client = None