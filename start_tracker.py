import argparse
from apps.tracker_server import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--ip', default='0.0.0.0')
    
    args = parser.parse_args()
    
    print(f"[Tracker] Starting on {args.ip}:{args.port}")
    app.prepare_address(args.ip, args.port)
    app.run()