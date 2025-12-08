#!/bin/bash

# WeApRous Task 2 - Start All Servers
# This script starts the tracker and 3 peer nodes in the background

echo "=========================================="
echo "Starting WeApRous P2P Chat System"
echo "=========================================="
echo ""

# # Check if servers are already running
# if lsof -Pi :9000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
#     echo "⚠️  Port 9000 (Tracker) is already in use"
#     echo "   Run './test_task2/stop_all.sh' to stop existing servers"
#     exit 1
# fi

# # Start Tracker Server
# echo "[1/4] Starting Tracker Server on port 9000..."
# python3 start_tracker.py --ip 127.0.0.1 --port 9000 > /tmp/tracker.log 2>&1 &
# TRACKER_PID=$!
# echo "      PID: $TRACKER_PID"

# # Wait for tracker to be ready
# echo "      Waiting for tracker to initialize..."
# for i in {1..10}; do
#     if curl -s http://127.0.0.1:9000/get-list >/dev/null 2>&1; then
#         echo "      ✓ Tracker ready"
#         break
#     fi
#     sleep 1
# done

# # Start proxy
# echo "[1/4] Starting proxy on 8080..."
# python3 start_proxy.py > /tmp/peer1.log 2>&1 &
# PROXY_PID=$!
# echo "      PID: $PROXY"
# sleep 2

# Start Peer 1
echo "[2/4] Starting Peer 1 on port 9001..."
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 9000 > /tmp/peer1.log 2>&1 &
PEER1_PID=$!
echo "      PID: $PEER1_PID"
sleep 2

# Start Peer 2
echo "[3/4] Starting Peer 2 on port 9002..."
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9002 --tracker-ip 127.0.0.1 --tracker-port 9000 > /tmp/peer2.log 2>&1 &
PEER2_PID=$!
echo "      PID: $PEER2_PID"
sleep 2

# Start Peer 3
echo "[4/4] Starting Peer 3 on port 9003..."
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9003 --tracker-ip 127.0.0.1 --tracker-port 9000 > /tmp/peer3.log 2>&1 &
PEER3_PID=$!
echo "      PID: $PEER3_PID"
sleep 2

echo ""
echo "=========================================="
echo "All servers started successfully!"
echo "=========================================="
echo ""
# echo "Tracker:  http://127.0.0.1:9000 (PID: $TRACKER_PID)"
echo "Peer 1:   http://127.0.0.1:9001 (PID: $PEER1_PID)"
echo "Peer 2:   http://127.0.0.1:9002 (PID: $PEER2_PID)"
echo "Peer 3:   http://127.0.0.1:9003 (PID: $PEER3_PID)"
echo ""
echo "Logs:"
echo "  Tracker: /tmp/tracker.log"
echo "  Peer 1:  /tmp/peer1.log"
echo "  Peer 2:  /tmp/peer2.log"
echo "  Peer 3:  /tmp/peer3.log"
echo ""

# Save PIDs to file for easy cleanup
echo "$TRACKER_PID" > /tmp/weaprous_pids.txt
echo "$PEER1_PID" >> /tmp/weaprous_pids.txt
echo "$PEER2_PID" >> /tmp/weaprous_pids.txt
echo "$PEER3_PID" >> /tmp/weaprous_pids.txt

# # Verify servers are responding
# echo "Verifying servers..."
# sleep 1

# # Check tracker
# if curl -s http://127.0.0.1:9000/get-list | grep -q '"status":"success"'; then
#     echo "✓ Tracker is responding"
# else
#     echo "✗ Tracker is not responding"
# fi

# Check peers
PEER_COUNT=$(curl -s http://127.0.0.1:9000/get-list | grep -o '"peer_id"' | wc -l)
echo "✓ $PEER_COUNT peers registered with tracker"

echo ""
echo "Ready to run tests!"
echo "  Run: ./test_task2/run_test_task2.sh"
echo ""
echo "To stop all servers:"
echo "  Run: ./test_task2/stop_all.sh"
echo ""
echo "To view logs:"
echo "  tail -f /tmp/tracker.log"
echo "  tail -f /tmp/peer1.log"
echo ""
