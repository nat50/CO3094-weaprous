#!/bin/bash

# WeApRous Task 2 - Stop All Servers
# This script stops all tracker and peer servers

echo "=========================================="
echo "Stopping WeApRous P2P Chat System"
echo "=========================================="
echo ""

STOPPED=0

# Stop using saved PIDs
if [ -f /tmp/weaprous_pids.txt ]; then
    echo "Stopping servers using saved PIDs..."
    while IFS= read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "  Stopped process $pid"
            STOPPED=$((STOPPED + 1))
        fi
    done < /tmp/weaprous_pids.txt
    rm -f /tmp/weaprous_pids.txt
fi

# Fallback: kill by port
echo ""
echo "Checking for any remaining processes..."

for PORT in 8080 9000 9001 9002 9003; do
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null
        echo "  Stopped process on port $PORT (PID: $PID)"
        STOPPED=$((STOPPED + 1))
    fi
done

# Clean up log files (optional)
if [ "$1" == "--clean-logs" ]; then
    echo ""
    echo "Cleaning up log files..."
    rm -f /tmp/tracker.log /tmp/peer1.log /tmp/peer2.log /tmp/peer3.log
    echo "  Log files deleted"
fi

echo ""
if [ $STOPPED -eq 0 ]; then
    echo "No running servers found."
else
    echo "✓ Stopped $STOPPED process(es)"
fi
echo "=========================================="
echo ""
