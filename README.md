# CO3094 WeApRous - HTTP Server and P2P Chat

This project is a course assignment for HCMUT Computer Networks (CO3094). It implements a basic HTTP server, a reverse proxy, and a hybrid client-server + peer-to-peer (P2P) chat application using raw TCP sockets. The server includes cookie-based authentication and a lightweight RESTful routing framework (WeApRous).

## Features
- HTTP server with static file serving (`www/`, `static/`)
- Cookie-based login and protected pages (`admin` / `password`)
- Reverse proxy with simple load balancing (round-robin)
- WeApRous RESTful app router (decorator-based routes)
- Tracker + peer nodes for P2P chat with broadcast and channels
- Web UI for chat (`wwwapp/`)

## Project Structure
- `daemon/`: core HTTP server, proxy, routing, request/response parsing
- `start_backend.py`: start a backend HTTP server
- `start_proxy.py`: start a reverse proxy (reads `config/proxy.conf`)
- `start_sampleapp.py`: start a sample WeApRous app
- `apps/tracker_server.py`: tracker for peer registration
- `apps/peer_app.py`: peer chat logic and REST APIs
- `start_tracker.py`: start tracker server
- `start_peer.py`: start a peer node (chat UI + APIs)
- `www/`: Task 1 static pages (login + index)
- `wwwapp/`: Task 2 chat UI pages
- `test_task1/`, `test_task2/`: testing guides and scripts

## Requirements
- Python 3.x
- No external frameworks (socket-based implementation)

## Setup: Use IP
The assignment requires binding and testing with machines in the same subnet:

1) Open PowerShell and run:
```powershell
ipconfig
```

2) Find active adapter IPv4 (e.g., `192.168.1.23`).

3) Use that IP in all commands and in `config/proxy.conf`.

With this setup, any device on the same subnet can access the services using
`http://<IP>:<PORT>` (assuming firewall rules allow it).

You can also distribute components across devices in the same subnet:
run multiple backends on different machines, place the proxy on another machine,
and access everything from a browser on a third device.

## Run: Task 1 (HTTP + Cookies)

### Option A: Direct backend
```powershell
python start_backend.py --server-ip <IP> --server-port 9000
```
Open:
- `http://<IP>:9000/login`
- Login with `admin / password`
- After login, visit `http://<IP>:9000/`

### Option B: Through proxy
1) Edit `config/proxy.conf` (replace IPs with `<IP>`):
```conf
host "<IP>:8080" {
    proxy_pass http://<IP>:9000;
}
```

2) Start backend and proxy:
```powershell
python start_backend.py --server-ip <IP> --server-port 9000
python start_proxy.py --server-ip <IP> --server-port 8080
```
Open:
- `http://<IP>:8080/login`

## Run: Task 2 (P2P Chat)

### 1) Start tracker
```powershell
python start_tracker.py --ip <IP> --port 9000
```

### 2) Start multiple peers (each in a new terminal). For example with 3 peers:
```powershell
python start_peer.py --peer-ip <IP> --peer-port 9001 --tracker-ip <IP> --tracker-port 9000
python start_peer.py --peer-ip <IP> --peer-port 9002 --tracker-ip <IP> --tracker-port 9000
python start_peer.py --peer-ip <IP> --peer-port 9003 --tracker-ip <IP> --tracker-port 9000
```

### 3) Open chat UI
For each peer:
- `http://<IP>:9001/login`
- `http://<IP>:9002/login`
- `http://<IP>:9003/login`

Login with `admin / password`.

## Run: Sample WeApRous App (Optional)
```powershell
python start_sampleapp.py --server-ip <IP> --server-port 8000
```
Endpoints:
- `POST /login`
- `PUT /hello`

## Notes
- If you want to use virtual hosts like `app1.local`, add them to your OS hosts file and update `config/proxy.conf`.
- The server serves HTML from `www/` (Task 1) and from `wwwapp/` (Task 2 with routes enabled).
