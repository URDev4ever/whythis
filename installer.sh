#!/bin/bash
# whythis installer - Created by URDev

set -e

INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
SCRIPT_NAME="whythis"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/whythis.py"

print_usage() {
    echo "Usage: $0 [install|uninstall|reinstall]"
    echo "  install    - Install whythis globally"
    echo "  uninstall  - Remove whythis from system"
    echo "  reinstall  - Reinstall whythis"
    echo ""
    echo "Options:"
    echo "  INSTALL_DIR=/custom/path $0 install"
}

check_permissions() {
    if [[ ! -w "$INSTALL_DIR" ]]; then
        echo "✗ Permission denied: Cannot write to $INSTALL_DIR"
        echo "  Try: sudo $0 $1"
        exit 1
    fi
}

install_whythis() {
    echo "🔧 Installing whythis..."
    
    # Check if Python3 is available
    if ! command -v python3 &> /dev/null; then
        echo "✗ Python3 is required but not installed"
        exit 1
    fi
    
    # Check if script exists
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        echo "✗ Script not found: $SCRIPT_PATH"
        echo "  Make sure whythis.py is in the same directory"
        exit 1
    fi
    
    check_permissions "install"
    
    # Make the Python script executable
    chmod +x "$SCRIPT_PATH"
    
    # Copy the Python script directly to install directory
    cp "$SCRIPT_PATH" "${INSTALL_DIR}/${SCRIPT_NAME}"
    chmod +x "${INSTALL_DIR}/${SCRIPT_NAME}"
    
    echo "✓ Installed: ${INSTALL_DIR}/${SCRIPT_NAME}"
    echo "✓ Source: $SCRIPT_PATH"
    
    # Verify installation
    if command -v "$SCRIPT_NAME" &> /dev/null; then
        echo "✅ Installation successful!"
        echo "   Run: whythis --help"
    else
        echo "⚠ Note: Add $INSTALL_DIR to your PATH if not already"
        echo "  For bash/zsh:"
        echo "    echo 'export PATH=\"\$PATH:$INSTALL_DIR\"' >> ~/.bashrc"
        echo "    source ~/.bashrc"
    fi
}

uninstall_whythis() {
    echo "🗑 Uninstalling whythis..."
    
    check_permissions "uninstall"
    
    if [[ -f "${INSTALL_DIR}/${SCRIPT_NAME}" ]]; then
        rm -f "${INSTALL_DIR}/${SCRIPT_NAME}"
        echo "✓ Removed: ${INSTALL_DIR}/${SCRIPT_NAME}"
    else
        echo "⚠ whythis not found in ${INSTALL_DIR}"
    fi
    
    # Note: Database in ~/.whythis/ is preserved
    echo "ℹ Database preserved at: ~/.whythis/"
    echo "  Remove manually if desired: rm -rf ~/.whythis/"
}

main() {
    case "${1:-}" in
        install)
            install_whythis
            ;;
        uninstall)
            uninstall_whythis
            ;;
        reinstall)
            uninstall_whythis
            install_whythis
            ;;
        *)
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
