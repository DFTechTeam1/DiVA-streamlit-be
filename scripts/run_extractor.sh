#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_extractor.sh [ --<IP_ADDRESS> | --help ]"
    echo ""
    echo "Available IP Addresses:"
    for ip in 192.168.100.101 192.168.100.102 192.168.100.103 192.168.100.104 192.168.100.105; do
        echo "  --$ip   Extract all shared folders on $ip"
    done
    echo "--help                Show this help message"
}

if [ -z "$1" ]; then
    echo "Error: No IP address specified. Please provide one of the listed IPs."
    show_help
    exit 1
fi

case "$1" in
    --192.168.100.101|--192.168.100.102|--192.168.100.103|--192.168.100.104|--192.168.100.105)
        echo "Checking OS Environment..."

        # Detecting OS Type
        if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
            echo "WSL detected"
            VENV_PATH=".venv/bin/activate"
        else
            case "$OSTYPE" in
                linux*)
                    echo "Linux-based OS detected"
                    VENV_PATH=".venv/bin/activate"
                    ;;
                darwin*)
                    echo "macOS detected"
                    VENV_PATH=".venv/bin/activate"
                    ;;
                cygwin* | msys* | mingw*)
                    echo "Windows-based OS detected"
                    VENV_PATH=".venv/Scripts/activate"
                    ;;
                *)
                    echo "Unsupported OS."
                    exit 1
                    ;;
            esac
        fi

        # Check if virtual environment exists before activation
        if [ -f "$VENV_PATH" ]; then
            source "$VENV_PATH"
        else
            echo "Error: Virtual environment not found at $VENV_PATH"
            exit 1
        fi

        # Extracting IP Address
        IP_ADDRESS="${1#--}"
        echo "Targeting $IP_ADDRESS for extracting shared folders..."
        python3 utils/executor.py "$IP_ADDRESS"
        ;;
    --help)
        show_help
        ;;
    *)
        echo "Error: Invalid IP address option."
        show_help
        exit 1
        ;;
esac
