import socket 
import threading
import logging
from datetime import datetime
from time import sleep
import time
import hashlib
import random
import math

def add_padding(raw_data):
    return raw_data + ' '*(1024-len(raw_data))

def secure_hash(message):
    salt = b"ASSIGNMENT_1"
    iterations = 100000  
    if isinstance(message, str):
        message = message.encode('utf-8')
    salted_message = salt + message
    hash_obj = hashlib.sha512()
    result = salted_message
    for _ in range(iterations):
        hash_obj.update(result)
        result = hash_obj.digest()
    
    return hash_obj.hexdigest()

def log_degree(peer_id, degree):
    with open('freqtrack.log', 'a') as f:
        f.write(f"{peer_id}=>{degree}\n")

class Peer:
    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.peer_socker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_socker.bind((ip, port))
        
        self.node_id = port % 100 
        self.max_peers = self.calculate_max_peers()
        
        self.available_peers = []
        
        self.seed_list = []
        with open('config.txt', 'r') as f:
            all_ip = f.readlines()
            for ip in all_ip:
                self.seed_list.append(ip.strip())
        f.close()

        self.sockets_to_seed = []
        self.sockets_to_peers = []
        self.message_list = {}
        self.alive_peers = {} 
        self.addr_socket_map = {}
        self.socket_addr_map = {}
        self.peer_timestamps = {}
    
    def calculate_max_peers(self):
        base = 1.5
        return int(40 * math.pow(base, -self.node_id / 10))
    
    def can_accept_peers(self):
        return len(self.addr_socket_map) < self.max_peers
    
    def add_peer(self, peer_addr):
        if peer_addr[1] % 100 != self.node_id and self.can_accept_peers():
            return True
        return False
    
    def start(self):
        Connect_with_Seed_Thread = threading.Thread(target=self.connection_with_seeds)
        Connect_with_Seed_Thread.start()
        Listen_to_peers = threading.Thread(target=self.listen)
        Listen_to_peers.start()
        Connect_with_Seed_Thread.join()
        Listen_to_peers.join()
        
    def connection_with_seeds(self):
        indices = list(range(len(self.seed_list)))
        random.shuffle(indices)
        selected_seeds = [self.seed_list[i] for i in indices[:(len(self.seed_list) // 2) + 1]]

        for seed in selected_seeds:
            seed = seed.split(':')
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((seed[0], int(seed[1])))
                self.sockets_to_seed.append(new_socket)

                handlingSeedThread = threading.Thread(target=self.seed_handling, args=(new_socket,))
                handlingSeedThread.start()
                handlingSeedThread.join()

            except Exception as e:
                print(f"Error Occurred while connecting to seed {seed} :", e)
                logging.info(f'Error Occurred while connecting to seed {e}')
                
        logging.info(f'PEER ({self.ip}:{self.port}) gets the peer list: {self.available_peers}')
        threading.Thread(target=self.peerConnection).start() 

    def listen(self):
        print(f'Peer Listening on {self.ip}:{self.port}')
        self.peer_socker.listen(15)
        while True:
            try:
                peer, _ = self.peer_socker.accept()
                # Check if we can accept new peers before adding to sockets
                if not self.can_accept_peers():
                    print(f"Maximum peer limit ({self.max_peers}) reached. Rejecting new connection.")
                    peer.close()
                    continue
                    
                self.sockets_to_peers.append(peer)
                peer_thread = threading.Thread(target=self.handle_peer,args=(peer,))
                peer_thread.start()
                print(f"Peer with address {peer.getpeername()} connected (The port here is created by OS during Thread Creation)")
                logging.info(f"Peer with address {peer.getpeername()} connected")
            except Exception as e:
                print("An error occurred while listening/handling a peer: ", e)

    def response_finder(self, socket):
        res = socket.recv(1024)
        res.strip()
        return res

    def get_peer_list(self, message):
        for peer_info in message[2:]:
            peer_details = peer_info.split('#')
            peer_ip = peer_details[0]
            peer_port = int(peer_details[1])
            new_peer = (peer_ip, peer_port)
            if new_peer not in self.available_peers:
                self.available_peers.append(new_peer)
         
    def peerConnection(self):
        for peer in self.available_peers:
            if peer[0] == self.ip and peer[1] == self.port:
                continue
            if not self.can_accept_peers():
                print(f"Maximum peer limit ({self.max_peers}) reached. Cannot connect to more peers.")
                break
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((peer[0], peer[1]))
                self.sockets_to_peers.append(new_socket)
                threading.Thread(target=self.handle_peer, args=(new_socket,)).start()
            except Exception as e:
                print(f"An error occurred while connecting to peer {peer}: ", e)
                continue

    def seed_handling(self, new_socket):
        try:
            message = f"register:{self.ip}:{self.port}"
            new_socket.send(message.encode())
            print("Established connection with seed with address", new_socket.getpeername())
            logging.info(f"Estd connection with seed with address {new_socket.getpeername()}")
            response = self.response_finder(new_socket)
            if response == "registered successfully":
                logging.info(f'Peer registered successfully with seed with address {new_socket.getpeername()}')
            
            sleep(2)
            new_socket.send("peer list".encode())

            while True:
                data = self.response_finder(new_socket)
                decoded_data = data.decode()
                message = decoded_data.split(':')
                if message[0] == 'peer list':
                    self.get_peer_list(message)
                    break
            print(f"Peer list received from seed: {self.available_peers}")
        except Exception as e:
            print(f"An error occurred while handling the seed: {e}")
    
    def handle_peer(self, new_socket):
        try:
            peer_addr = new_socket.getpeername()
            if not self.add_peer(peer_addr):
                print(f"Cannot accept new peer {peer_addr}. Maximum peers reached or invalid peer.")
                new_socket.close()
                return

            new_socket.send(add_padding("Connection with Peer:{0}:{1}").format(self.ip,self.port).encode())
            message=""
            while(message==""):
                data = self.response_finder(new_socket)
                message = data.decode().split(':')
                if message[0]=="Connection with Peer":
                    self.addr_socket_map[(message[1],int(message[2]))]=new_socket
                    self.socket_addr_map[new_socket]=(message[1],int(message[2]))
                    break
                new_socket.send(add_padding("Connection with Peer:{0}:{1}").format(self.ip,self.port).encode())
            
            logging.info(f"Peer {self.ip}:{self.port} - Current peers: {len(self.addr_socket_map)}, Max peers: {self.max_peers}")
            
            sleep(1)
            threading.Thread(target=self.handle_messages, args=(new_socket,)).start()
            threading.Thread(target=self.liveness_test, args=(new_socket,)).start()
            threading.Thread(target=self.generate_messages, args=(new_socket,)).start()
            
            print(f"New peer connection established with {self.socket_addr_map[new_socket]}")
            logging.info(f"New peer connection established with {self.socket_addr_map[new_socket]}")
            
            current_degree = len(self.addr_socket_map)
            log_degree(f"{self.ip}:{self.port}", current_degree)
            
        except Exception as e:
            print(f"Error in handle_peer: {e}")
            logging.info(f"Error in handle_peer: {e}")

    def handle_messages(self, new_socket):       
        while True:
            try:
                data = self.response_finder(new_socket)
                if not data:
                    print(f"Peer {self.socket_addr_map[new_socket]} disconnected")
                    break

                message = data.decode().split(':')
                if message[0]=="Connection with Peer":
                    self.addr_socket_map[(message[1],int(message[2]))]=new_socket
                    self.socket_addr_map[new_socket]=(message[1],int(message[2]))

                elif message[0]=="Liveness Request":
                    timestamp_of_sender = float(message[1])
                    new_socket.send(add_padding(f"Liveness Reply:{timestamp_of_sender}:{self.socket_addr_map[new_socket][0]}:{self.socket_addr_map[new_socket][1]}:{self.ip}:{self.port}").encode())
                
                elif message[0]=="Liveness Reply":
                    self.peer_timestamps[self.socket_addr_map[new_socket]] = float(message[1])

                elif message[0]=="gmessage":
                    new_socket.send(add_padding('forwarding').encode())
                    message_hash = secure_hash(message[4])
                    
                    if message_hash not in self.message_list:
                        self.message_list[message_hash] = True
                        print(f"{message[1]}:{message[2]}:{message[3]}:{message[4].rstrip()}")                        
                        for socket in self.socket_addr_map.keys():
                            if socket != new_socket:
                                try:
                                    socket.send(add_padding(f"gmessage:{datetime.now().timestamp()}:{self.ip}:{self.port}:{message[4]}").encode())
                                    socket.recv(1024)
                                except ConnectionResetError:
                                    continue
                                except Exception as e:
                                    print(f"Failed to forward message to {self.socket_addr_map[socket]}: {e}")
                                    continue

                elif message[0] == "Dead Node":
                    print(f"Dead Node:{message[1]}:{message[2]}:{message[3]}:{message[4]}:{message[5]}")
                    print("Peer removed from available peers: ", self.socket_addr_map[new_socket])
                    break
                sleep(1)
            except Exception as e:
                print(f"Connection lost with peer {self.socket_addr_map.get(new_socket, 'unknown')}: {e}")
                break

    def liveness_test(self, new_socket):
        fail_count = 0
        while True:
            sleep(13)
            timestamp = datetime.now().timestamp()
            addr = self.socket_addr_map[new_socket]
            if addr in self.peer_timestamps:
                if timestamp - self.peer_timestamps[addr] == 0:
                    fail_count = 0

            try:
                request = "Liveness Request:{0}:{1}:{2}".format(timestamp, self.ip, self.port)
                new_socket.send(add_padding(request).encode())
                
            except Exception as e:
                print(f"Maybe Disconnected, Liveliness test request {fail_count+1}")
                fail_count += 1
                if fail_count >= 3:
                    dead_node_message = f"Dead Node:{addr[0]}:{addr[1]}:{timestamp}:{self.ip}:{self.port}"
                    for seed_socket in self.sockets_to_seed:
                        try:
                            seed_socket.send(add_padding(dead_node_message).encode())
                        except:
                            continue
                    self.remove_dead_peer(new_socket)
                    return
            
            addr = self.socket_addr_map[new_socket]
            if addr in self.peer_timestamps:
                if timestamp - self.peer_timestamps[addr] == 0:
                    fail_count = 0

    def generate_messages(self, new_socket):   
        for i in range(10):
            try:
                message = f"gmessage:{datetime.now().timestamp()}:{self.ip}:{self.port}:message {1+i}"
                new_socket.send(add_padding(message).encode())
            except Exception as e:
                print(f"Failed to send gossip message: {e}")
                break
            sleep(5)

    def remove_dead_peer(self, socket):
        try:
            addr = self.socket_addr_map[socket]
            if addr in self.available_peers:
                self.available_peers.remove(addr)
            if addr in self.peer_timestamps:
                del self.peer_timestamps[addr]
            if addr in self.addr_socket_map:
                del self.addr_socket_map[addr]
            if socket in self.socket_addr_map:
                del self.socket_addr_map[socket]
            if socket in self.sockets_to_peers:
                self.sockets_to_peers.remove(socket)
            socket.close()
            print(f"Peer {addr} removed from {self.ip}:{self.port}")
            logging.info(f'Peer {addr} removed from all data structures')
            
            current_degree = len(self.addr_socket_map)
            log_degree(f"{self.ip}:{self.port}", current_degree)
            return
            
        except Exception as e:
            print(f"Error removing dead peer: {e}")
   
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='outputfile.log', format='%(asctime)s:%(message)s')
    port = int(input('Enter port to connect to: '))
    peer = Peer(port=port, ip='localhost')
    peer.start()


