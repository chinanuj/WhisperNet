import socket
import threading
import time
import logging

class SeedNode:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.peer_list = set()  # Stores (IP, Port) of registered peers
        self.lock = threading.Lock()  # Ensures thread-safe access to peer_list

        # Configure logging
        logging.basicConfig(
            filename="seed_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )
        logging.info(f"Seed node started at {self.ip}:{self.port}")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        print(f"Seed node started at {self.ip}:{self.port}")
        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        try:
            request = client.recv(1024).decode()
            if request.startswith("REGISTER"):
                _, ip, port = request.split(":")
                with self.lock:
                    self.peer_list.add((ip, int(port)))
                client.send(b"OK")
                print(f"Registered peer: {ip}:{port}")
                logging.info(f"Registered peer: {ip}:{port}")
            elif request.startswith("GET_PEERS"):
                with self.lock:
                    client.send(str(list(self.peer_list)).encode())
                print(f"Sent peer list to {client.getpeername()}")
                logging.info(f"Sent peer list to {client.getpeername()}")
            elif request.startswith("Dead Node"):
                _, dead_ip, dead_port, timestamp, reporter_ip = request.split(":")
                with self.lock:
                    self.peer_list.discard((dead_ip, int(dead_port)))
                print(f"Removed dead node: {dead_ip}:{dead_port} (reported by {reporter_ip})")
                logging.info(f"Removed dead node: {dead_ip}:{dead_port} (reported by {reporter_ip})")
                client.send(b"OK")
            else:
                # Handle received messages
                print(f"Received message: {request}")
                logging.info(f"Received message: {request}")
        except Exception as e:
            print(f"Error handling client: {e}")
            logging.error(f"Error handling client: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    seed = SeedNode("172.31.98.231", 8000)  # Your laptop's IP and port
    seed.start()