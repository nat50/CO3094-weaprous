#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.proxy
~~~~~~~~~~~~~~~~~

This module implements a simple proxy server using Python's socket and threading libraries.
It routes incoming HTTP requests to backend services based on hostname mappings and returns
the corresponding responses to clients.

Requirement:
-----------------
- socket: provides socket networking interface.
- threading: enables concurrent client handling via threads.
- response: customized :class: `Response <Response>` utilities.
- httpadapter: :class: `HttpAdapter <HttpAdapter >` adapter for HTTP request processing.
- dictionary: :class: `CaseInsensitiveDict <CaseInsensitiveDict>` for managing headers and cookies.

"""
import socket
import threading
from .response import *
from .httpadapter import HttpAdapter
from .dictionary import CaseInsensitiveDict

#: Counter for round-robin load balancing
#: Maps hostname to current backend index
ROUND_ROBIN_COUNTER = {}

def forward_request(host, port, request):
    """
    Forwards an HTTP request to a backend server and retrieves the response.

    :params host (str): IP address of the backend server.
    :params port (int): port number of the backend server.
    :params request (str): incoming HTTP request.

    :rtype bytes: Raw HTTP response from the backend server. If the connection
                  fails, returns a 404 Not Found response.
    """

    backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        backend.connect((host, port))
        backend.sendall(request.encode())
        response = b""
        while True:
            chunk = backend.recv(4096)
            if not chunk:
                break
            response += chunk
        return response
    except socket.error as e:
      print("Socket error: {}".format(e))
      return (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "Connection: close\r\n"
            "\r\n"
            "404 Not Found"
        ).encode('utf-8')


def resolve_routing_policy(hostname, routes):
    """
    Handles an routing policy to return the matching proxy_pass.
    It determines the target backend to forward the request to.

    :params host (str): IP address of the request target server.
    :params port (int): port number of the request target server.
    :params routes (dict): dictionary mapping hostnames and location.
    """

    print(f"[Host name] {hostname}")
    proxy_map, policy = routes.get(hostname,('127.0.0.1:9000','round-robin'))
    print (f"[Map] {proxy_map}")
    print (f"[Policy] {policy}")

    proxy_host = ''
    proxy_port = '9000'
    if isinstance(proxy_map, list):
        if len(proxy_map) == 0:
            print("[Proxy] Emtpy resolved routing of hostname {}".format(hostname))
            print ("Empty proxy_map result")
            proxy_host = '127.0.0.1'
            proxy_port = '9000'
        elif len(proxy_map) == 1:
            proxy_host, proxy_port = proxy_map[0].split(":", 2)
        else:
            # Multiple backends - apply distribution policy
            if policy == 'round-robin':
                # Round-robin: rotate through backends sequentially
                if hostname not in ROUND_ROBIN_COUNTER:
                    ROUND_ROBIN_COUNTER[hostname] = 0
                
                index = ROUND_ROBIN_COUNTER[hostname] % len(proxy_map)
                proxy_host, proxy_port = proxy_map[index].split(":", 2)
                
                # Increment for next request
                ROUND_ROBIN_COUNTER[hostname] += 1
                print("[Proxy] Round-robin: select backend {}/{} -> {}:{} from host {}".format(
                    index + 1, len(proxy_map), proxy_host, proxy_port, hostname))
            else:
                # Unknown policy - use first backend as fallback
                print("[Proxy] Unknown policy '{}', using first backend".format(policy))
                proxy_host, proxy_port = proxy_map[0].split(":", 2)
    else:
        print("[Proxy] resolve route of hostname {} is a singulair to".format(hostname))
        proxy_host, proxy_port = proxy_map.split(":", 2)

    return proxy_host, proxy_port

def handle_client(ip, port, conn, addr, routes):
    """
    Handles an individual client connection by parsing the request,
    determining the target backend, and forwarding the request.

    The handler extracts the Host header from the request to
    matches the hostname against known routes. In the matching
    condition,it forwards the request to the appropriate backend.

    The handler sends the backend response back to the client or
    returns 404 if the hostname is unreachable or is not recognized.

    :params ip (str): IP address of the proxy server.
    :params port (int): port number of the proxy server.
    :params conn (socket.socket): client connection socket.
    :params addr (tuple): client address (IP, port).
    :params routes (dict): dictionary mapping hostnames and location.
    """

    request = conn.recv(1024).decode()

    # Extract hostname
    for line in request.splitlines():
        if line.lower().startswith('host:'):
            hostname = line.split(':', 1)[1].strip()

    print("[Proxy] {} at Host: {}".format(addr, hostname))

    # Get backend configuration
    proxy_map, policy = routes.get(hostname, ('127.0.0.1:9000', 'round-robin'))
    backends = proxy_map if isinstance(proxy_map, list) else [proxy_map]
    
    response = None
    
    # Try backends until one succeeds
    for backend in range(len(backends)):
        resolved_host, resolved_port = resolve_routing_policy(hostname, routes)
        try:
            resolved_port = int(resolved_port)
        except ValueError:
            print("Not a valid integer")
            continue
        
        print("[Proxy] Host name {} is forwarded to {}:{}".format(hostname, resolved_host, resolved_port))
        response = forward_request(resolved_host, resolved_port, request)
        
        # If backend is up (not 404), use this response
        if response and not response.startswith(b"HTTP/1.1 404"):
            print("[Proxy] Success: {}:{}".format(resolved_host, resolved_port))
            break
        else:
            print("[Proxy] Backend {}:{} is down, trying next...".format(resolved_host, resolved_port))
    
    # If all backends failed, return 502
    if response is None or response.startswith(b"HTTP/1.1 404"):
        response = (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 15\r\n"
            "Connection: close\r\n"
            "\r\n"
            "502 Bad Gateway"
        ).encode('utf-8')

    conn.sendall(response)
    conn.close()

def run_proxy(ip, port, routes):
    """
    Starts the proxy server and listens for incoming connections. 

    The process dinds the proxy server to the specified IP and port.
    In each incomping connection, it accepts the connections and
    spawns a new thread for each client using `handle_client`.
 

    :params ip (str): IP address to bind the proxy server.
    :params port (int): port number to listen on.
    :params routes (dict): dictionary mapping hostnames and location.

    """

    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows the socket to reuse the address immediately

    try:
        proxy.bind((ip, port))
        proxy.listen(50)
        print("[Proxy] Listening on IP {} port {}".format(ip,port))
        while True:
            conn, addr = proxy.accept()
            client_thread = threading.Thread(target=handle_client, args=(ip, port, conn, addr, routes))
            client_thread.start()
    except socket.error as e:
        print("Socket error: {}".format(e))
    except KeyboardInterrupt:
        print ("\n| SHUTTING DOWN... |")

def create_proxy(ip, port, routes):
    """
    Entry point for launching the proxy server.

    :params ip (str): IP address to bind the proxy server.
    :params port (int): port number to listen on.
    :params routes (dict): dictionary mapping hostnames and location.
    """

    run_proxy(ip, port, routes)
