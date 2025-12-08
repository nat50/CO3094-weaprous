# WeApRous - P2P Chat Application Testing Guide (Task 2)

This document provides comprehensive testing commands for the P2P chat application, which builds upon Task 1's authentication system and adds peer-to-peer messaging capabilities.

## Architecture Overview

The P2P chat system consists of:
- **Tracker Server**: Manages peer registration and discovery (port 9000)
- **Peer Nodes**: Individual chat clients that communicate directly (ports 9001, 9002, 9003, etc.)
- **RESTful APIs**: HTTP-based communication between components

---

## Prerequisites

### Option 1: Direct P2P Communication

**Step 1:** Start the Tracker Server
```bash
python3 start_tracker.py --ip 127.0.0.1 --port 9000
```

**Step 2:** Start Multiple Peer Nodes

**Terminal 1 - Peer 1:**
```bash
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 9000
```

**Terminal 2 - Peer 2:**
```bash
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9002 --tracker-ip 127.0.0.1 --tracker-port 9000
```

**Terminal 3 - Peer 3:**
```bash
python3 start_peer.py --peer-ip 127.0.0.1 --peer-port 9003 --tracker-ip 127.0.0.1 --tracker-port 9000
```

### Option 2: Through Proxy with Load Balancing (Task 3)

**Step 1:** Start the Tracker Server
```bash
python3 start_tracker.py --ip 0.0.0.0 --port 9000
```

**Step 2:** Start Multiple Peer Nodes (same as above but with 0.0.0.0)
```bash
python3 start_peer.py --peer-ip 0.0.0.0 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 9000
python3 start_peer.py --peer-ip 0.0.0.0 --peer-port 9002 --tracker-ip 127.0.0.1 --tracker-port 9000
python3 start_peer.py --peer-ip 0.0.0.0 --peer-port 9003 --tracker-ip 127.0.0.1 --tracker-port 9000
```

**Step 3:** Update `config/proxy.conf` to configure load balancing across peers:
```
host "app2.local" {
    proxy_pass http://127.0.0.1:9001;
    proxy_pass http://127.0.0.1:9002;
    proxy_pass http://127.0.0.1:9003;
    dist_policy round-robin
}
```

**Step 4:** Start the proxy server
```bash
python3 start_proxy.py --server-ip 0.0.0.0 --server-port 8080
```

**Step 5:** Add host entry (for testing with domain name):
```bash
# Edit /etc/hosts (requires sudo)
echo "127.0.0.1 app2.local" | sudo tee -a /etc/hosts
```

**Step 6:** Test through proxy with load balancing:
```bash
# Each request will be distributed to different peer (round-robin)
curl -H "Host: app2.local" http://127.0.0.1:8080/api/me \
  -H "Cookie: auth=true"
```

**Note:** The proxy will automatically distribute requests across all three peers using round-robin load balancing.

---

## Task 2: Peer-to-Peer Communication Testing

### Feature 1: Tracker Server Registration

#### Test 1: Peer Registration
**Requirement:** Peers should register with tracker and receive unique peer_id

```bash
# Register a new peer
curl -i -X POST http://127.0.0.1:9000/submit-info \
  -H "Content-Type: application/json" \
  -d '{"ip": "127.0.0.1", "port": 9004}'
```

**Expected Response:**
```json
{
  "status": "success",
  "peer_id": 4
}
```

---

#### Test 2: Get Peer List
**Requirement:** Retrieve list of all registered peers

```bash
curl -i -X GET http://127.0.0.1:9000/get-list \
  -H "Cookie: auth=true"
```

**Expected Response:**
```json
{
  "status": "success",
  "peers": [
    {"peer_id": 1, "ip": "127.0.0.1", "port": 9001, "timestamp": "2025-12-08T..."},
    {"peer_id": 2, "ip": "127.0.0.1", "port": 9002, "timestamp": "2025-12-08T..."},
    {"peer_id": 3, "ip": "127.0.0.1", "port": 9003, "timestamp": "2025-12-08T..."}
  ]
}
```

---

### Feature 2: RESTful API Endpoints

#### Test 3: Get Current Peer ID
**Requirement:** Each peer should know its own peer_id

```bash
# For Peer 1 (port 9001)
curl -i -X GET http://127.0.0.1:9001/api/me
```

**Expected Response:**
```json
{
  "status": "success",
  "peer_id": 1
}
```

---

#### Test 4: Get Available Peers
**Requirement:** Peer should retrieve list of other peers (excluding itself)

```bash
# From Peer 1, get list of other peers
curl -i -X GET http://127.0.0.1:9001/api/peers
```

**Expected Response:**
```json
{
  "status": "success",
  "peers": [
    {"peer_id": 2, "ip": "127.0.0.1", "port": 9002, "timestamp": "...", "unread": false},
    {"peer_id": 3, "ip": "127.0.0.1", "port": 9003, "timestamp": "...", "unread": false}
  ]
}
```

---

### Feature 3: Direct Peer-to-Peer Messaging

#### Test 5: Send Direct Message
**Requirement:** Send message from Peer 1 to Peer 2

```bash
# Peer 1 sends message to Peer 2
curl -i -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from Peer 1!",
    "target_peer_id": 2
  }'
```

**Expected Response:**
```json
{
  "status": "success"
}
```

---

#### Test 6: Retrieve Chat History
**Requirement:** Retrieve conversation between two peers

```bash
# Peer 2 retrieves chat with Peer 1
curl -i -X POST http://127.0.0.1:9002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"peer_id": 1}'
```

**Expected Response:**
```json
{
  "status": "success",
  "messages": [
    {
      "from": 1,
      "data": "Hello from Peer 1!",
      "timestamp": "2025-12-08T10:30:00.000000"
    }
  ]
}
```

---

#### Test 7: Bidirectional Communication
**Requirement:** Both peers can send and receive messages

```bash
# Peer 2 replies to Peer 1
curl -X POST http://127.0.0.1:9002/api/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi Peer 1! This is Peer 2",
    "target_peer_id": 1
  }'

# Peer 1 retrieves updated chat
curl -X POST http://127.0.0.1:9001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"peer_id": 2}'
```

**Expected Response:**
```json
{
  "status": "success",
  "messages": [
    {
      "from": 1,
      "data": "Hello from Peer 1!",
      "timestamp": "2025-12-08T10:30:00.000000"
    },
    {
      "from": 2,
      "data": "Hi Peer 1! This is Peer 2",
      "timestamp": "2025-12-08T10:30:15.000000"
    }
  ]
}
```

---

### Feature 4: Broadcast Messaging

#### Test 8: Broadcast to All Peers
**Requirement:** Send message to all peers simultaneously

```bash
# Peer 1 broadcasts to everyone
curl -i -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Broadcast: Hello everyone!"
  }'
```

**Expected Behavior:**
- Message stored in chat history with Peer 2 and Peer 3
- All other peers receive the message

**Verify on Peer 2:**
```bash
curl -X POST http://127.0.0.1:9002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"peer_id": 1}'
```

**Verify on Peer 3:**
```bash
curl -X POST http://127.0.0.1:9003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"peer_id": 1}'
```

---

### Feature 5: Channel Messaging

#### Test 9: Send Message to Channel
**Requirement:** Multiple peers can communicate in a shared channel

```bash
# Peer 1 sends to Channel 1
curl -i -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Channel 1!",
    "channel_id": "1"
  }'
```

**Expected Response:**
```json
{
  "status": "success"
}
```

---

#### Test 10: Retrieve Channel Messages
**Requirement:** All peers can see channel messages

```bash
# Peer 2 retrieves Channel 1 messages
curl -i -X POST http://127.0.0.1:9002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "1"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "messages": [
    {
      "from": 1,
      "data": "Hello Channel 1!",
      "timestamp": "2025-12-08T10:35:00.000000"
    }
  ]
}
```

---

#### Test 11: Multiple Peers in Channel
**Requirement:** Multiple peers can participate in same channel

```bash
# Peer 2 joins Channel 1
curl -X POST http://127.0.0.1:9002/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Peer 2 here!", "channel_id": "1"}'

# Peer 3 joins Channel 1
curl -X POST http://127.0.0.1:9003/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Peer 3 joining!", "channel_id": "1"}'

# Verify all messages visible to Peer 1
curl -X POST http://127.0.0.1:9001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "1"}'
```

---

### Feature 6: Unread Message Notifications

#### Test 12: Unread Message Detection
**Requirement:** Peers should mark chats with unread messages

```bash
# Peer 3 sends to Peer 1
curl -X POST http://127.0.0.1:9003/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hey Peer 1!", "target_peer_id": 1}'

# Peer 1 checks peer list (should show Peer 3 has unread)
curl -X GET http://127.0.0.1:9001/api/peers
```

**Expected Response:**
```json
{
  "status": "success",
  "peers": [
    {"peer_id": 2, "unread": false, ...},
    {"peer_id": 3, "unread": true, ...}
  ]
}
```

---

#### Test 13: Clear Unread on Chat Open
**Requirement:** Opening a chat should clear unread status

```bash
# Peer 1 opens chat with Peer 3
curl -X POST http://127.0.0.1:9001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"peer_id": 3}'

# Check peer list again
curl -X GET http://127.0.0.1:9001/api/peers
```

**Expected:** `unread` for Peer 3 should now be `false`

---

### Feature 7: Web Interface Access

#### Test 14: Access Chat UI Without Authentication
**Requirement:** Accessing chat app without auth cookie should fail

```bash
curl -i -X GET http://127.0.0.1:9001/
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized` (if Task 1 auth is integrated)
- OR Status: `HTTP/1.1 200 OK` with chat interface (if using wwwapp routes)

---

#### Test 15: Access Chat UI With Routes
**Requirement:** RESTful routes should serve chat interface from wwwapp folder

```bash
# Access via peer with registered routes
curl -i -X GET http://127.0.0.1:9001/index.html
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Content-Type: `text/html`
- Body: P2P Chat HTML interface

---

## Complete Test Scenarios

### Scenario 1: Three-Way Conversation

```bash
# Peer 1 -> Peer 2
curl -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Peer 2", "target_peer_id": 2}'

# Peer 2 -> Peer 3
curl -X POST http://127.0.0.1:9002/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi Peer 3", "target_peer_id": 3}'

# Peer 3 -> Peer 1
curl -X POST http://127.0.0.1:9003/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hey Peer 1", "target_peer_id": 1}'

# Verify all chats exist
curl -X POST http://127.0.0.1:9001/api/chat -H "Content-Type: application/json" -d '{"peer_id": 2}'
curl -X POST http://127.0.0.1:9002/api/chat -H "Content-Type: application/json" -d '{"peer_id": 3}'
curl -X POST http://127.0.0.1:9003/api/chat -H "Content-Type: application/json" -d '{"peer_id": 1}'
```

---

### Scenario 2: Group Discussion in Channel

```bash
# All peers join Channel 2
curl -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Peer 1: Starting discussion", "channel_id": "2"}'

curl -X POST http://127.0.0.1:9002/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Peer 2: I agree!", "channel_id": "2"}'

curl -X POST http://127.0.0.1:9003/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Peer 3: Me too!", "channel_id": "2"}'

# Anyone can view full conversation
curl -X POST http://127.0.0.1:9001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "2"}'
```

---

### Scenario 3: Broadcast Announcement

```bash
# Peer 1 announces to everyone
curl -X POST http://127.0.0.1:9001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "IMPORTANT: System maintenance at 10 PM"}'

# Verify message appears in all peer chats
curl -X POST http://127.0.0.1:9002/api/chat -H "Content-Type: application/json" -d '{"peer_id": 1}'
curl -X POST http://127.0.0.1:9003/api/chat -H "Content-Type: application/json" -d '{"peer_id": 1}'
```

---
