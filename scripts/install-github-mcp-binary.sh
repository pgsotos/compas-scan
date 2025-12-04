#!/bin/bash
# Script to install GitHub MCP binary as alternative to Docker

set -e

ARCH=$(uname -m)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

# Map architecture
case $ARCH in
    x86_64)
        ARCH="amd64"
        ;;
    arm64|aarch64)
        ARCH="arm64"
        ;;
    *)
        echo "❌ Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Map OS
case $OS in
    darwin)
        OS="darwin"
        ;;
    linux)
        OS="linux"
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

VERSION="v0.24.0"
BINARY_NAME="github-mcp-server"
INSTALL_DIR="$HOME/.local/bin"
BINARY_PATH="$INSTALL_DIR/$BINARY_NAME"
TEMP_DIR=$(mktemp -d)

# Map OS name for download URL
case $OS in
    darwin)
        OS_NAME="Darwin"
        ;;
    linux)
        OS_NAME="Linux"
        ;;
esac

# Map architecture name for download URL
case $ARCH in
    amd64)
        ARCH_NAME="x86_64"
        ;;
    arm64)
        ARCH_NAME="arm64"
        ;;
esac

DOWNLOAD_URL="https://github.com/github/github-mcp-server/releases/download/${VERSION}/github-mcp-server_${OS_NAME}_${ARCH_NAME}.tar.gz"
TARBALL_PATH="$TEMP_DIR/github-mcp-server.tar.gz"

echo "🔧 Installing GitHub MCP Server binary..."
echo "   Version: $VERSION"
echo "   OS: $OS_NAME"
echo "   Arch: $ARCH_NAME"
echo "   Install path: $BINARY_PATH"
echo ""

# Create install directory
mkdir -p "$INSTALL_DIR"

# Download tarball
echo "📥 Downloading binary..."
if curl -L -f -o "$TARBALL_PATH" "$DOWNLOAD_URL"; then
    echo "✅ Download successful"
else
    echo "❌ Download failed"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Extract binary
echo "📦 Extracting binary..."
cd "$TEMP_DIR"
tar -xzf "$TARBALL_PATH" || {
    echo "❌ Extraction failed"
    rm -rf "$TEMP_DIR"
    exit 1
}

# Move binary to install directory
if [ -f "$TEMP_DIR/$BINARY_NAME" ]; then
    mv "$TEMP_DIR/$BINARY_NAME" "$BINARY_PATH"
    echo "✅ Binary extracted and moved"
else
    echo "❌ Binary not found in tarball"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Cleanup
rm -rf "$TEMP_DIR"

# Make executable
chmod +x "$BINARY_PATH"
echo "✅ Binary is now executable"

# Verify installation
if [ -f "$BINARY_PATH" ] && [ -x "$BINARY_PATH" ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "📋 Binary location: $BINARY_PATH"
    echo ""
    
    # Check if in PATH
    if echo "$PATH" | grep -q "$HOME/.local/bin"; then
        echo "✅ $HOME/.local/bin is in PATH"
    else
        echo "⚠️  $HOME/.local/bin is NOT in PATH"
        echo "   Add to your shell profile (~/.zshrc or ~/.bashrc):"
        echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    echo ""
    echo "🔄 Next steps:"
    echo "1. Run: ./scripts/setup-github-mcp.sh"
    echo "2. The script will detect the binary and use it instead of Docker"
    echo ""
else
    echo "❌ Installation verification failed"
    exit 1
fi

