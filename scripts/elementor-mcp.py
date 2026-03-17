#!/usr/bin/env python3
"""Elementor MCP CLI wrapper - reads connection from .mcp.json in the project."""

import sys
import json
import subprocess
import argparse
import re
import os


def find_mcp_config():
    """Find .mcp.json by checking --project-dir flag, then walking up from cwd."""
    search_dirs = []

    # 1. Explicit --project-dir from argv (parsed before argparse runs)
    for i, arg in enumerate(sys.argv):
        if arg == "--project-dir" and i + 1 < len(sys.argv):
            search_dirs.append(sys.argv[i + 1])
        elif arg.startswith("--project-dir="):
            search_dirs.append(arg.split("=", 1)[1])

    # 2. Current working directory and parents
    cwd = os.getcwd()
    d = cwd
    while True:
        search_dirs.append(d)
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent

    for d in search_dirs:
        mcp_path = os.path.join(d, ".mcp.json")
        if os.path.isfile(mcp_path):
            return mcp_path

    return None


def load_mcp_config(config_path, server_name=None):
    """Load MCP server URL and auth headers from .mcp.json."""
    with open(config_path, "r") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    if not servers:
        print("Error: No MCP servers found in .mcp.json", file=sys.stderr)
        sys.exit(1)

    # If server_name specified, use that; otherwise find first elementor server
    if server_name:
        if server_name not in servers:
            print(f"Error: Server '{server_name}' not found in .mcp.json", file=sys.stderr)
            print(f"Available: {', '.join(servers.keys())}", file=sys.stderr)
            sys.exit(1)
        server = servers[server_name]
    else:
        # Auto-detect: prefer server with "elementor" in name, else first http server
        for name, srv in servers.items():
            if "elementor" in name.lower() and srv.get("type") == "http":
                server = srv
                server_name = name
                break
        else:
            # Fallback to first http server
            for name, srv in servers.items():
                if srv.get("type") == "http":
                    server = srv
                    server_name = name
                    break
            else:
                print("Error: No HTTP MCP server found in .mcp.json", file=sys.stderr)
                sys.exit(1)

    url = server.get("url")
    headers = server.get("headers", {})

    if not url:
        print(f"Error: No URL for server '{server_name}'", file=sys.stderr)
        sys.exit(1)

    return url, headers, server_name


def curl_post(url, headers, data, timeout=30):
    """Make a POST request using curl and return (response_headers, body)."""
    cmd = [
        "curl", "-s", "-k", "-D", "-",
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
    ]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["-d", json.dumps(data)])
    cmd.extend(["--max-time", str(timeout)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: curl failed with code {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    output = result.stdout
    # Split headers from body - handle both \r\n and \n line endings
    parts = re.split(r'\r?\n\r?\n', output, maxsplit=1)
    if len(parts) == 2:
        raw_headers, body = parts
    else:
        raw_headers, body = "", output

    # Parse headers
    resp_headers = {}
    for line in re.split(r'\r?\n', raw_headers):
        if ":" in line and not line.startswith("HTTP"):
            k, v = line.split(":", 1)
            resp_headers[k.strip().lower()] = v.strip()

    return resp_headers, body


def initialize_session(url, headers):
    """Initialize MCP session and return session ID."""
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "elementor-mcp-skill", "version": "1.0"}
        }
    }
    resp_headers, body = curl_post(url, headers, data)
    session_id = resp_headers.get("mcp-session-id")
    if not session_id:
        print("Error: No session ID in response", file=sys.stderr)
        print(f"Headers found: {resp_headers}", file=sys.stderr)
        sys.exit(1)
    return session_id


def call_tool(url, headers, session_id, tool_name, arguments=None):
    """Call an MCP tool and return the result."""
    req_headers = {**headers, "Mcp-Session-Id": session_id}
    data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    _, body = curl_post(url, req_headers, data, timeout=60)
    return body


def list_tools(url, headers, session_id):
    """List all available tools."""
    req_headers = {**headers, "Mcp-Session-Id": session_id}
    data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    _, body = curl_post(url, req_headers, data)
    try:
        result = json.loads(body)
        tools = result.get("result", {}).get("tools", [])
        for t in tools:
            print(f"  {t['name']}: {t.get('description', '')[:100]}")
    except json.JSONDecodeError:
        print(body)


def main():
    parser = argparse.ArgumentParser(description="Elementor MCP CLI - reads config from .mcp.json")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--tool", type=str, help="Tool name to call")
    parser.add_argument("--params", type=str, default="{}", help="JSON string of parameters")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--project-dir", type=str, help="Project directory containing .mcp.json")
    parser.add_argument("--server", type=str, help="MCP server name from .mcp.json (auto-detects if omitted)")

    args = parser.parse_args()

    # Find and load config
    config_path = find_mcp_config()
    if not config_path:
        print("Error: No .mcp.json found in project directory or parents.", file=sys.stderr)
        print("Create a .mcp.json with your Elementor MCP server config.", file=sys.stderr)
        print('Example: {"mcpServers": {"elementor-mcp": {"type": "http", "url": "https://yoursite.com/wp-json/mcp/elementor-mcp-server", "headers": {"Authorization": "Basic ..."}}}}', file=sys.stderr)
        sys.exit(1)

    url, headers, server_name = load_mcp_config(config_path, args.server)
    print(f"[Connected: {server_name} @ {url}]", file=sys.stderr)

    session_id = initialize_session(url, headers)

    if args.list:
        list_tools(url, headers, session_id)
        return

    if not args.tool:
        parser.print_help()
        return

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON params: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_tool(url, headers, session_id, args.tool, params)

    if args.pretty:
        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(result)
    else:
        print(result)


if __name__ == "__main__":
    main()
