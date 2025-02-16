import threading
from peer import Peer
import time
import random

def run_peer(port):
    try:
        peer = Peer(port=port, ip='localhost')
        peer.start()
    except Exception as e:
        print(f"Error starting peer on port {port}: {e}")

def main():
    open('outputfile.log', 'w').close()
    open('freqtrack.log', 'w').close()
    
    threads = []
    base_port = 5000
    
    print("Starting 40 peers...")
    
    for i in range(40):
        port = base_port + i
        thread = threading.Thread(target=run_peer, args=(port,))
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(0.1, 0.3))
        print(f"Started peer {i+1}/40 on port {port}")

    print("\nAll peers started. Press Ctrl+C to stop.")
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping all peers...")
        exit(0)
