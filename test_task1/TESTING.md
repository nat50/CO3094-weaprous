# WeApRous - Authentication Testing Guide

This document provides comprehensive curl commands to test the authentication and cookie-based access control implementation for the CO3094 network assignment.

## Prerequisites

### Option 1: Direct Backend Access

Start the backend server:
```bash
python3 start_backend.py --server-ip 127.0.0.1 --server-port 9000
```

The server will listen on `http://127.0.0.1:9000`

### Option 2: Through Proxy (Recommended for Task 3)

**Step 1:** Start the backend server:
```bash
python3 start_backend.py --server-ip 0.0.0.0 --server-port 9000
```

**Step 2:** Update `config/proxy.conf` with your IP address, then start the proxy:
```bash
python3 start_proxy.py --server-ip 0.0.0.0 --server-port 8080
```

**Step 3:** Access through proxy at `http://127.0.0.1:8080`

**Note:** For proxy testing, replace `127.0.0.1:9000` with `127.0.0.1:8080` in all curl commands below.

---

## Task 1A: Authentication Handling

### Test 1: Valid Login (Correct Credentials)
**Requirement:** POST to `/login` with valid credentials should return 302 Found with `Set-Cookie: auth=true`

```bash
curl -i -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

**Expected Response:**
- Status: `HTTP/1.1 302 Found`
- Header: `Set-Cookie: auth=true; Path=/; HttpOnly`
- Header: `Location: /`
- Body: Empty (Content-Length: 0)

---

### Test 2: Invalid Login - Wrong Password
**Requirement:** POST to `/login` with invalid credentials should return 401 Unauthorized

```bash
curl -i -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrongpassword"
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`
- Header: `Content-Type: text/html`
- Header: `Cache-Control: no-store`
- Body: `401 Unauthorized`

---

### Test 3: Invalid Login - Wrong Username
**Requirement:** POST to `/login` with invalid username should return 401 Unauthorized

```bash
curl -i -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hacker&password=password"
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`
- Body: `401 Unauthorized`

---

### Test 4: Invalid Login - Empty Credentials
**Requirement:** POST to `/login` with empty credentials should return 401 Unauthorized

```bash
curl -i -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d ""
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`

---

### Test 5: GET Request to /login
**Requirement:** GET to `/login` should serve the login form page

```bash
curl -i -X GET http://127.0.0.1:9000/login
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Header: `Content-Type: text/html`
- Body: HTML login form with username and password fields

---

## Task 1B: Cookie-Based Access Control

### Test 6: Access Root Without Cookie
**Requirement:** GET to `/` without auth cookie should return 401 Unauthorized

```bash
curl -i -X GET http://127.0.0.1:9000/
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`
- Body: `401 Unauthorized`

---

### Test 7: Access Root With Valid Cookie
**Requirement:** GET to `/` with auth=true cookie should serve the index page

```bash
curl -i -X GET http://127.0.0.1:9000/ \
  -H "Cookie: auth=true"
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Header: `Content-Type: text/html`
- Body: HTML content of index.html (bksysnet@hcmut Domain page)

---

### Test 8: Access Root With Invalid Cookie Value
**Requirement:** GET to `/` with wrong cookie value should return 401 Unauthorized

```bash
curl -i -X GET http://127.0.0.1:9000/ \
  -H "Cookie: auth=false"
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`

---

### Test 9: Access Root With Wrong Cookie Name
**Requirement:** GET to `/` with different cookie name should return 401 Unauthorized

```bash
curl -i -X GET http://127.0.0.1:9000/ \
  -H "Cookie: session=true"
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized`

---

### Test 10: Complete Login Flow
**Requirement:** Simulate complete authentication flow - login and then access protected resource

```bash
# Step 1: Login and save cookie
curl -i -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password" \
  -c cookies.txt

# Step 2: Access protected resource with saved cookie
curl -i -X GET http://127.0.0.1:9000/ \
  -b cookies.txt
```

**Expected Response:**
- First request: 302 Found with Set-Cookie
- Second request: 200 OK with index.html content

---

## Additional Tests: Header Parsing

### Test 11: Multiple Cookies
**Requirement:** Server should parse multiple cookies correctly

```bash
curl -i -X GET http://127.0.0.1:9000/ \
  -H "Cookie: session=abc123; auth=true; user=admin"
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Server should extract `auth=true` from multiple cookies

---

### Test 12: Access Static Resources With Cookie
**Requirement:** CSS and images should be accessible with auth cookie

```bash
# Access CSS file
curl -i -X GET http://127.0.0.1:9000/css/styles.css \
  -H "Cookie: auth=true"

# Access image file
curl -i -X GET http://127.0.0.1:9000/images/welcome.png \
  -H "Cookie: auth=true"
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Appropriate Content-Type headers (text/css, image/png)

---

## Concurrency Testing

### Test 13: Multiple Simultaneous Requests
**Requirement:** Server should handle concurrent connections using threading

```bash
# Run 3 concurrent requests
for i in {1..3}; do
  curl -X POST http://127.0.0.1:9000/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=password" &
done
wait
```

**Expected Behavior:**
- All requests should be handled successfully
- Server should create separate threads for each connection
- No connection refused or timeout errors

---

### Test 14: Rapid Sequential Requests
**Requirement:** Server should handle rapid sequential requests without errors

```bash
# Send 10 rapid requests
for i in {1..10}; do
  curl -s -X GET http://127.0.0.1:9000/ \
    -H "Cookie: auth=true" \
    -o /dev/null -w "Request $i: %{http_code}\n"
done
```

**Expected Behavior:**
- All requests return 200 OK
- No connection errors or timeouts

---

## Error Handling Tests

### Test 15: Malformed POST Request
**Requirement:** Server should handle malformed requests gracefully

```bash
curl -i -X POST http://127.0.0.1:9000/login \
  -d "username=admin"
```

**Expected Response:**
- Status: `HTTP/1.1 401 Unauthorized` (missing password field)

---

### Test 16: Invalid HTTP Method
**Requirement:** Server should handle unexpected HTTP methods

```bash
curl -i -X PUT http://127.0.0.1:9000/login \
  -d "username=admin&password=password"
```

**Expected Response:**
- Should not crash the server
- May return 404 Not Found or similar error

---

### Test 17: Access Non-Existent Path
**Requirement:** Server should return 404 for non-existent resources

```bash
curl -i -X GET http://127.0.0.1:9000/nonexistent.html \
  -H "Cookie: auth=true"
```

**Expected Response:**
- Status: `HTTP/1.1 404 Not Found`
- Body: `404 Not Found`

---

## Session Management Tests

### Test 18: Cookie Persistence Across Requests
**Requirement:** Cookie should persist across multiple requests in same session

```bash
# Save cookies after login
curl -c cookies.txt -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"

# Use saved cookies for multiple requests
curl -b cookies.txt http://127.0.0.1:9000/
curl -b cookies.txt http://127.0.0.1:9000/css/styles.css
curl -b cookies.txt http://127.0.0.1:9000/images/welcome.png
```

**Expected Behavior:**
- All requests should succeed with 200 OK
- Cookie file should contain `auth=true`

---

### Test 19: Case Insensitivity of Headers
**Requirement:** Server should handle case-insensitive headers (CaseInsensitiveDict)

```bash
curl -i -X GET http://127.0.0.1:9000/ \
  -H "cookie: auth=true"
```

**Expected Response:**
- Status: `HTTP/1.1 200 OK`
- Server should recognize lowercase "cookie" header

---

## Load Balancing Tests (Task 3)

### Test 20: Round-Robin with Multiple Backend Servers

**Setup:** Start 3 backend servers and 1 proxy

**Terminal 1 - Backend 1:**
```bash
python3 start_backend.py --server-ip 0.0.0.0 --server-port 9001
```

**Terminal 2 - Backend 2:**
```bash
python3 start_backend.py --server-ip 0.0.0.0 --server-port 9002
```

**Terminal 3 - Backend 3:**
```bash
python3 start_backend.py --server-ip 0.0.0.0 --server-port 9003
```

**Terminal 4 - Proxy:**

Update `config/proxy.conf`:
```conf
host "localhost" {
    proxy_pass http://127.0.0.1:9001;
    proxy_pass http://127.0.0.1:9002;
    proxy_pass http://127.0.0.1:9003;
    dist_policy round-robin
}
```

Then start proxy:
```bash
python3 start_proxy.py --server-ip 0.0.0.0 --server-port 8080
```

### Test 21: Verify Round-Robin Distribution

**Test:** Send multiple login requests through proxy

```bash
# Login 9 times to see full 3-cycle round-robin
# app1.local
for i in {1..9}; do   echo "=== Login Request $i ===";   curl -i -X POST http://127.0.0.1:8080/login     -H "Host: app1.local"     -H "Content-Type: application/x-www-form-urlencoded"     -d "username=admin&password=password" 2>&1 | grep -E "HTTP|Set-Cookie";   echo "";   sleep 0.3; done
```

```bash
# Login 9 times to see full 3-cycle round-robin
# app2.local
for i in {1..9}; do   
  echo "=== Login Request $i ===";   
  curl -i -X POST http://127.0.0.1:8080/login     
    -H "Host: app2.local"
    -H "Content-Type: application/x-www-form-urlencoded"     
    -d "username=admin&password=password" 2>&1 | grep -E "HTTP|Set-Cookie";   
  echo "";   
  sleep 0.3;
done
```

**Expected:**
- All 9 requests return `HTTP/1.1 302 Found` with `Set-Cookie: auth=true`
- Check proxy logs to verify round-robin:
  ```
  [Proxy] Round-robin: select backend 1/3 -> 127.0.0.1:9001
  [Proxy] Round-robin: select backend 2/3 -> 127.0.0.1:9002
  [Proxy] Round-robin: select backend 3/3 -> 127.0.0.1:9003
  [Proxy] Round-robin: select backend 1/3 -> 127.0.0.1:9001  (cycles back)
  ```

### Test 22: Authenticated Requests Through Load Balancer

**Test:** Login once, then access protected pages multiple times

```bash
# Step 1: Login and save cookie
curl -i -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password" \
  -c cookies.txt

# Step 2: Access homepage 6 times (round-robin distribution)
for i in {1..6}; do
  echo "=== Request $i ==="
  curl -s -b cookies.txt http://127.0.0.1:8080/ | head -n 5
  sleep 0.3
done
```

**Expected:**
- All requests return 200 OK with homepage content
- Proxy logs show requests distributed across 3 backends

### Test 23: Mixed Login and Protected Resource Requests

**Test:** Alternate between login and protected page access

```bash
# Cycle 1: Login -> Homepage
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password" \
  -c cookies.txt > /dev/null 2>&1

curl -s -b cookies.txt http://127.0.0.1:8080/ | head -n 3

# Cycle 2: Login -> Homepage
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password" \
  -c cookies.txt > /dev/null 2>&1

curl -s -b cookies.txt http://127.0.0.1:8080/ | head -n 3

# Cycle 3: Login -> Homepage
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password" \
  -c cookies.txt > /dev/null 2>&1

curl -s -b cookies.txt http://127.0.0.1:8080/ | head -n 3
```

**Expected:**
- 6 total requests (3 login + 3 homepage)
- Proxy distributes across all 3 backends in sequence
- All authenticated requests succeed

### Test 24: Check Load Distribution

**Test:** Verify requests are evenly distributed

```bash
# Send 30 requests
for i in {1..30}; do
  curl -s http://127.0.0.1:8080/login > /dev/null 2>&1
done

# Check proxy logs
# Each backend should have received ~10 requests (30 ÷ 3 = 10)
```

**Expected:** Proxy logs show approximately equal distribution:
- Backend 1 (9001): ~10 requests
- Backend 2 (9002): ~10 requests
- Backend 3 (9003): ~10 requests

### Test 25: Backend Failover

**Test:** Stop one backend and verify proxy handles it gracefully

```bash
# Stop Backend 2 (Ctrl+C in Terminal 2)

# Send 6 requests
for i in {1..6}; do
  echo "Request $i:"
  curl -i -X POST http://127.0.0.1:8080/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=password" 2>&1 | grep "HTTP"
done
```

**Expected:**
- Requests continue to work
- Proxy detects Backend 2 is down
- Requests are handled by Backend 1 and 3
- Proxy logs show: `[Proxy] Backend 127.0.0.1:9002 is down, trying next...`

---