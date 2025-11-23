import argparse
from apps.peer_app import app, register_with_tracker

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--peer-ip', default='127.0.0.1')
    parser.add_argument('--peer-port', type=int, required=True)
    parser.add_argument('--tracker-ip', default='127.0.0.1')
    parser.add_argument('--tracker-port', type=int, default=9000)
    
    args = parser.parse_args()
    
    app.config = {
        'peer_ip': args.peer_ip,
        'peer_port': args.peer_port,
        'tracker_ip': args.tracker_ip,
        'tracker_port': args.tracker_port
    }
    
    app.prepare_address(args.peer_ip, args.peer_port)
    app.run()

