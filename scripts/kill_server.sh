#!/bin/bash

show_help() {
    echo "Usage: sh scripts/kill_server.sh [ --port <port> ] | [ --help ]"
    echo ""
    echo "--port    Port of running server."
    echo "--help    Show this help message."
    echo "Example: sh scripts/kill_server.sh --port 24000"
}

extract_pid() {
    local port=$1
    lsof -i :$port | awk 'NR==2 {print $2}'
}

kill_pid() {
    local pid=$1
    if [ -n "$pid" ]; then
        echo "Killing process with PID: $pid"
        kill -9 "$pid"
        if [ $? -eq 0 ]; then
            echo "Process $pid terminated successfully."
        else
            echo "Failed to terminate process $pid."
        fi
    else
        echo "No PID provided to kill."
    fi
}

if [ "$1" = "--help" ]; then
    show_help
    exit 0
elif [ "$1" = "--port" ] && [ -n "$2" ]; then
    PORT="$2"
    PID=$(extract_pid "$PORT")
    if [ -z "$PID" ]; then
        echo "No process found running on port $PORT. Skipping kill."
        exit 0
    fi
    kill_pid "$PID"
else
    echo "Error: Invalid arguments."
    show_help
    exit 1
fi
