@echo off
echo Starting Tracker...
start "Tracker" cmd /k python start_tracker.py --port 9000

timeout /t 2

echo Starting Peer 1...
start "Peer 1" cmd /k python start_peer.py --peer-port 9001 --tracker-port 9000

echo Starting Peer 2...
start "Peer 2" cmd /k python start_peer.py --peer-port 9002 --tracker-port 9000

echo Starting Peer 3...
start "Peer 3" cmd /k python start_peer.py --peer-port 9003 --tracker-port 9000

echo All services started.
