import subprocess
import time

def start_seed(ip, port):
    return subprocess.Popen(["python3", "seed.py", ip, str(port)])

def start_peer(ip, port, seeds):
    return subprocess.Popen(["python3", "peer.py", ip, str(port)] + seeds)

if __name__ == "__main__":
    # Start seed nodes
    seed1 = start_seed("127.0.0.1", 5000)
    seed2 = start_seed("127.0.0.1", 5001)
    time.sleep(2)  # Wait for seeds to start

    # Start peer nodes
    peer1 = start_peer("127.0.0.1", 6000, ["127.0.0.1:5000", "127.0.0.1:5001"])
    peer2 = start_peer("127.0.0.1", 6001, ["127.0.0.1:5000", "127.0.0.1:5001"])
    time.sleep(2)  # Wait for peers to register

    # Let the system run for a while
    time.sleep(30)

    # Kill a peer to simulate a dead node
    peer1.terminate()
    print("Killed peer1 to simulate a dead node")
    time.sleep(20)  # Wait for dead node detection

    # Cleanup
    seed1.terminate()
    seed2.terminate()
    peer2.terminate()