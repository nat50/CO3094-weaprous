import json
import socket
from datetime import datetime
from daemon import *

messages = {}
app = WeApRous()
app.config = {}

def get_chat_key(peer_id1, peer_id2):
    id1 = int(peer_id1)
    id2 = int(peer_id2)
    return f"{min(id1, id2)}_{max(id1, id2)}"

def save_message(chat_key, from_peer_id, message, timestamp):
    if chat_key not in messages:
        messages[chat_key] = []
    messages[chat_key].append({
        'from': from_peer_id,
        'data': message,
        'timestamp': timestamp
    })

def register_with_tracker(peer_ip, peer_port):
    config = app.config
    sock = socket.socket()
    sock.connect((config['tracker_ip'], config['tracker_port']))
    
    data = json.dumps({'ip': peer_ip, 'port': peer_port})
    request = (f"POST /submit-info HTTP/1.1\r\n"
              f"Host: {config['tracker_ip']}:{config['tracker_port']}\r\n"
              f"Content-Type: application/json\r\n"
              f"Content-Length: {len(data)}\r\n\r\n"
              f"{data}")
    
    sock.sendall(request.encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    sock.close()
    
    return response

def get_peer_list():
    config = app.config
    sock = socket.socket()
    sock.connect((config['tracker_ip'], config['tracker_port']))
    
    request = (f"GET /get-list HTTP/1.1\r\n"
              f"Host: {config['tracker_ip']}:{config['tracker_port']}\r\n\r\n")
    sock.sendall(request.encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    sock.close()
    
    _, body = response.split('\r\n\r\n', 1)
    data = json.loads(body)
    return data['peers']

def send_to_peer(peer_ip, peer_port, message_data):
    try:
        sock = socket.socket()
        sock.connect((peer_ip, peer_port))
        
        data = json.dumps(message_data)
        request = (f"POST /send-peer HTTP/1.1\r\n"
                  f"Host: {peer_ip}:{peer_port}\r\n"
                  f"Content-Type: application/json\r\n"
                  f"Content-Length: {len(data)}\r\n\r\n"
                  f"{data}")
        
        sock.sendall(request.encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sock.close()
        return 'success' in response.lower()
    except:
        return False

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_index(headers, body):
    return None

@app.route('/api/me', methods=['GET'])
def api_me(headers, body):
    peer_id = app.config.get('peer_id')
    if peer_id is not None:
        peer_id = int(peer_id)
    return json.dumps({'status': 'success', 'peer_id': peer_id})

@app.route('/api/peers', methods=['GET'])
def api_peers(headers, body):
    peer_id = app.config.get('peer_id')
    if peer_id is not None:
        peer_id = int(peer_id)
    all_peers = get_peer_list()
    filtered_peers = [p for p in all_peers if p.get('peer_id') != peer_id]
    return json.dumps({'status': 'success', 'peers': filtered_peers})

@app.route('/api/chat', methods=['POST'])
def api_chat_messages(headers, body):
    peer_id = app.config.get('peer_id')
    if peer_id is None:
        return json.dumps({'status': 'error', 'message': 'Peer not registered'})
    
    peer_id = int(peer_id)
    data = json.loads(body) if body else {}
    target_peer_id = data.get('peer_id')
    
    if target_peer_id is None:
        return json.dumps({'status': 'error', 'message': 'peer_id required'})
    
    target_peer_id = int(target_peer_id)
    chat_key = get_chat_key(peer_id, target_peer_id)
    return json.dumps({'status': 'success', 'messages': messages.get(chat_key, [])})

@app.route('/api/send', methods=['POST'])
def api_send(headers, body):
    data = json.loads(body)
    message = data.get('message', '')
    target_peer_id = data.get('target_peer_id')
    peer_id = app.config.get('peer_id')
    
    peer_id = int(peer_id)
    if target_peer_id is not None:
        target_peer_id = int(target_peer_id)
    
    msg_data = {
        'from': peer_id,
        'data': message,
        'timestamp': datetime.now().isoformat()
    }
    
    timestamp = msg_data['timestamp']
    
    if target_peer_id is not None:
        # Direct Message
        chat_key = get_chat_key(peer_id, target_peer_id)
        save_message(chat_key, peer_id, message, timestamp)

        peers = get_peer_list()
        if target_peer_id != peer_id:
            for peer in peers:
                if peer.get('peer_id') == target_peer_id:
                    send_to_peer(peer['ip'], peer['port'], msg_data)
                    break
    else:
        # Broadcast
        peers = get_peer_list()
        for peer in peers:
            if peer.get('peer_id') != peer_id:
                chat_key = get_chat_key(peer_id, peer['peer_id'])
                save_message(chat_key, peer_id, message, timestamp)
                send_to_peer(peer['ip'], peer['port'], msg_data)
    
    return json.dumps({'status': 'success'})

@app.route('/send-peer', methods=['POST'])
def receive_message(headers, body):
    data = json.loads(body)
    peer_id = app.config.get('peer_id')
    
    peer_id = int(peer_id)
    from_peer_id = int(data['from'])
    chat_key = get_chat_key(peer_id, from_peer_id)
    save_message(chat_key, from_peer_id, data['data'], data.get('timestamp', datetime.now().isoformat()))
    return json.dumps({'status': 'success'})