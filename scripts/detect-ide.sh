#!/bin/bash
# Utility script to detect MCP configuration path for IDE
# Works with Cursor, Claude Code, and other MCP-compatible IDEs

get_mcp_config_path() {
    # Try common IDE MCP config locations
    if [ -d "$HOME/.cursor" ]; then
        echo "$HOME/.cursor/mcp.json"
    elif [ -d "$HOME/.claude-code" ]; then
        echo "$HOME/.claude-code/mcp.json"
    else
        # Default to Cursor path (most common)
        echo "$HOME/.cursor/mcp.json"
    fi
}

get_mcp_config_dir() {
    local config_file=$(get_mcp_config_path)
    echo "$(dirname "$config_file")"
}

# If script is executed directly, output config path
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    get_mcp_config_path
fi

