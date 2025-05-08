#!/bin/bash

echo "Checking system distribution."

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Error: Unable to determine the system distribution."
    exit 1
fi


install_dependencies() {
    echo "Installing dependencies for $DISTRO..."
    case $DISTRO in
        ubuntu|debian)
            sudo apt-get update
            sudo apt install -y jq cifs-utils
            ;;
        arch|manjaro)
            sudo pacman -Syu --noconfirm
            sudo pacman -Sy --noconfirm jq cifs-utils
            ;;
        *)
            echo "Error: Unsupported distribution: $DISTRO"
            exit 1
            ;;
    esac
}

install_dependencies
