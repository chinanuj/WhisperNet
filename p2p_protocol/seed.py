import socket 
import threading
import logging

class Seed:
    def __init__(self,port,ip='localhost'):
        self.ip=ip
        self.port=port
        self.seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.seed_socket.bind((self.ip,self.port))
        self.peerlist = []
        logging.info(f'Seed Started with Address {self.ip}:{self.port}')
    
    def listen(self):
        print(f'Seed Listening on {self.ip}:{self.port}')
        self.seed_socket.listen(15)
        while True:
            try:
                peer, addr = self.seed_socket.accept()
                thread_for_peer = threading.Thread(target=self.handle_peer,args=(peer,addr))
                thread_for_peer.start()
            except Exception as e:
                print(f"Error Occured(listen Module of Seed.py) : {e}")

    def dead_node(self, peer, message):
        if (message[1], int(message[2])) in self.peerlist:
            self.peerlist.remove((message[1], int(message[2])))
            peer.close()
            print(f"Dead Node:{message[1]}:{message[2]}:{message[3]}:{message[4]}:{message[5]}")
            logging.info(f'Dead node {message[1]}:{message[2]} removed from peer list of seed and this is reported by {message[4]}:{message[5]}')
        else:
            print(f"Dead node {message[1]}:{message[2]} already removed")
            logging.info(f'Dead node {message[1]}:{message[2]} already removed from peer list of seed and this is reported by {message[4]}:{message[5]}')

    def register(self, peer, message):
        self.peerlist.append((message[1], int(message[2])))
        peer.send('registered successfully'.encode())
        print(f"Peer registered successfully with seed with address {self.ip}:{self.port}")
        logging.info(f'{message[1]}:{message[2]} registered to seed with address {self.ip}:{self.port}')

    def sendpeerlist(self, peer, message):
        lst = str()
        for i in self.peerlist:
            lst += f":{i[0]}#{str(i[1])}"
        peer.send(f"peer list:{lst}".encode())

    def handle_peer(self, peer, addr):
        try:
            while True:
                message = peer.recv(1024).decode()
                message = message.split(':')
                print(f"Message from {addr} : {message}")
                if message[0] == 'peer list':
                    self.sendpeerlist(peer,message)
                if message[0] == 'register':
                    self.register(peer, message)
                if message[0] == 'Dead Node':
                    self.dead_node(peer, message)

        except Exception as e:
            if isinstance(e, OSError) and e.winerror == 10038:  
                pass
            else:
                print(f"Error Occurred (Handling Peer module): {e}")
                logging.info(f'Error Occurred (Handling Peer module): {e}')

            
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,filename='outputfile.log',format='%(asctime)s:%(message)s')
    port=int(input('Enter port to connect to: '))
    seed = Seed(port=port)
    seed.listen()

'''
Because 5051 is the peer's listening port (where other peers can connect to it), but when it makes outgoing connections, it uses random ephemeral ports assigned by the OS.
Think of it like this:

Port 5051 is like your peer's "home address" where others can find it
The random ports (54376, 54377, etc.) are like temporary "return addresses" used when your peer visits different seeds
'''