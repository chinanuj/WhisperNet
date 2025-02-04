import socket
import threading
import time
import logging

class PeerNode:
    def __init__(self, ip, port, seeds):
        self.ip = ip
        self.port = port
        self.seeds = seeds
        self.connected_peers = set()  # Stores (IP, Port) of connected peers
        self.message_list = {}  # Tracks message propagation
        self.lock = threading.Lock()  # Ensures thread-safe access to shared data
        self.ping_failures = {}  # Tracks ping failures for each peer

        # Configure logging
        logging.basicConfig(
            filename="peer_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )
        logging.info(f"Peer node started at {self.ip}:{self.port}")

    def register_with_seeds(self):
        for seed in self.seeds:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((seed["ip"], seed["port"]))
                sock.send(f"REGISTER:{self.ip}:{self.port}".encode())
                response = sock.recv(1024)
                if response == b"OK":
                    print(f"Registered with seed {seed['ip']}:{seed['port']}")
                    logging.info(f"Registered with seed {seed['ip']}:{seed['port']}")
                sock.close()
            except Exception as e:
                print(f"Failed to register with seed {seed['ip']}:{seed['port']}: {e}")
                logging.error(f"Failed to register with seed {seed['ip']}:{seed['port']}: {e}")

    def connect_to_peers(self):
        for seed in self.seeds:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((seed["ip"], seed["port"]))
                sock.send(b"GET_PEERS")
                peer_list = eval(sock.recv(1024).decode())
                for peer in peer_list:
                    if peer != (self.ip, self.port):  # Avoid connecting to self
                        with self.lock:
                            self.connected_peers.add(peer)
                sock.close()
            except Exception as e:
                print(f"Failed to get peers from seed {seed['ip']}:{seed['port']}: {e}")
                logging.error(f"Failed to get peers from seed {seed['ip']}:{seed['port']}: {e}")

    def start(self):
        self.register_with_seeds()
        self.connect_to_peers()
        threading.Thread(target=self.check_liveness).start()
        threading.Thread(target=self.user_input).start()  # Start user input thread

    def broadcast_message(self, message):
        message = f"{time.time()}:{self.ip}:{message}"
        message_hash = hash(message)
        with self.lock:
            self.message_list[message_hash] = {"sent_to": set(), "received_from": set()}

        #Implementation 1 : Msg from peer to peer
        for peer in list(self.connected_peers):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((peer[0], peer[1]))
                sock.send(message.encode())
                with self.lock:
                    self.message_list[message_hash]["sent_to"].add(peer)
                sock.close()
                print(f"Sent message to {peer[0]}:{peer[1]}: {message}")
                logging.info(f"Sent message to {peer[0]}:{peer[1]}: {message}")
            except Exception as e:
                print(f"Failed to send message to peer {peer[0]}:{peer[1]}: {e}")
                logging.error(f"Failed to send message to peer {peer[0]}:{peer[1]}: {e}")
            
        #Implementation 2 : Msg from peer to seed
        try:
            for seed in self.seeds:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((seed["ip"], seed["port"]))
                sock.send(message.encode())
                with self.lock:
                    self.message_list[message_hash]["sent_to"].add((seed["ip"], seed["port"]))
                sock.close()
                print(f"Sent message to {seed['ip']}:{seed['port']}: {message}")
                logging.info(f"Sent message to {seed['ip']}:{seed['port']}: {message}")
        except Exception:
            print(f"Failed to send message to seed {seed['ip']}:{seed['port']}")
            logging.error(f"Failed to send message to seed {seed['ip']}:{seed['port']}")
        
    def check_liveness(self):
        while True:
            for peer in list(self.connected_peers):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((peer[0], peer[1]))
                    sock.send(b"PING")
                    response = sock.recv(1024)
                    if response != b"PONG":
                        self.handle_ping_failure(peer)
                    else:
                        with self.lock:
                            self.ping_failures[peer] = 0
                    sock.close()
                except Exception as e:
                    self.handle_ping_failure(peer)
            time.sleep(13)

    def handle_ping_failure(self, peer):
        with self.lock:
            self.ping_failures[peer] = self.ping_failures.get(peer, 0) + 1
            if self.ping_failures[peer] >= 3:
                self.report_dead_node(peer)
                self.connected_peers.discard(peer)
                del self.ping_failures[peer]

    def report_dead_node(self, peer):
        for seed in self.seeds:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((seed["ip"], seed["port"]))
                sock.send(f"Dead Node:{peer[0]}:{peer[1]}:{time.time()}:{self.ip}".encode())
                sock.close()
                print(f"Reported dead node: {peer[0]}:{peer[1]}")
                logging.info(f"Reported dead node: {peer[0]}:{peer[1]}")
            except Exception as e:
                print(f"Failed to report dead node to seed {seed['ip']}:{seed['port']}: {e}")
                logging.error(f"Failed to report dead node to seed {seed['ip']}:{seed['port']}: {e}")

    def user_input(self):
        while True:
            message = input("Enter a message to broadcast (or 'exit' to quit): ")
            if message.lower() == "exit":
                break
            self.broadcast_message(message)

if __name__ == "__main__":
    seeds = [{"ip": "172.31.98.231", "port": 9000},{"ip": "172.31.98.231", "port": 9001}]  
    peer = PeerNode("172.31.92.206", 6000, seeds)  
    peer.start()