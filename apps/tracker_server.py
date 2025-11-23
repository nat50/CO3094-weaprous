import json
from datetime import datetime
from daemon import *

active_peers = {}
app = WeApRous()

@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    data = json.loads(body)
    if not all([data.get('ip'), data.get('port')]):
        return json.dumps({'status': 'error'})
    
    # Auto-assign peer_id as index
    peer_id = len(active_peers)
    
    active_peers[peer_id] = {
        'ip': data['ip'],
        'port': int(data['port']),
        'timestamp': datetime.now().isoformat()
    }
    return json.dumps({'status': 'success', 'peer_id': peer_id})

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    peers = [{'peer_id': pid, 'ip': info['ip'], 'port': info['port'], 'timestamp': info['timestamp']} 
             for pid, info in active_peers.items()]
    return json.dumps({'status': 'success', 'peers': peers})
