import random
import socket
import time
import pandas as pd
from threading import Thread
import json
import sys

GENERATE_FLAG = False
MESSAGE_COUNT = 0
MESSAGE_LOG = {}
connect_peers_total = []
COUNT = {}

def generate_message(peer_ip,peer_port):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    timestamp = get_time()
    message = f"{timestamp}:{peer_ip}:{peer_port}:{MESSAGE_COUNT}"
    return message

def get_time():
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    timestamp = time.time()
    formatted_timestamp = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(timestamp))
    return formatted_timestamp


def read_config():
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    seeds_list = pd.read_csv('config.csv')
    seeds_dict = {}
    for i in range(len(seeds_list)):
        seeds_dict[seeds_list.iloc[i,0]] = [seeds_list.iloc[i,1], seeds_list.iloc[i,2]]
    return seeds_dict

def select_seeds(seeds_dict):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    n = (len(seeds_dict)//2) +1
    random_numbers = random.sample(range(1, len(seeds_dict)+1), n)
    return random_numbers

def connect_seeds(seeds_dict, rand_nums, PEER_NUM, PEER_IP):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    peer_set = []
    peer_lists = {}
    for rand_num in rand_nums:
        seed_host, seed_port = seeds_dict[rand_num]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_for_seeds:
            try:
                socket_for_seeds.connect((str(seed_host), int(seed_port)))
                peer_port = 20000 + PEER_NUM
                socket_for_seeds.send(str(peer_port).encode())
                peer_list = socket_for_seeds.recv(1024)
                if peer_list:
                    peer_list = json.loads(peer_list.decode())
                    peer_lists[rand_num] = peer_list
                    for peer in peer_list:
                        if (peer not in peer_set) and (peer != [str(PEER_IP), int(20000 + PEER_NUM)]):
                            peer_set.append(peer)
            except Exception as e:
                print(f"Error connecting to seed {rand_num}: {e}")
            finally: 
                socket_for_seeds.close()
    return peer_set, peer_lists

def select_peers(peer_set):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    if len(peer_set) < 5:
        for peer in peer_set:
            connect_peers_total.append(peer)
        return peer_set
    else:
        sel_peer = []
        random_numbers = random.sample(range(0, len(peer_set)), 4)
        for idx in random_numbers:
            sel_peer.append(peer_set[idx])
            connect_peers_total.append(peer_set[idx])
        return sel_peer



def connect_peers(sel_peers, PEER_IP,PEER_NUM):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    if len(sel_peers)>0:
        for peer in sel_peers:
            peer_ip,peer_port = peer
            peer_connection_thread = Thread(target=handle_peers_out, args=(peer_ip, peer_port, PEER_IP,PEER_NUM))
            peer_connection_thread.start()



def handle_peers_out(peer_ip, peer_port, PEER_IP,PEER_NUM):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    peer_send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_send_socket.connect((peer_ip, peer_port))
    GENERATE_FLAG = True
    tim = get_time()
    data = f"First :{tim}:{PEER_IP}:{PEER_NUM}"
    peer_send_socket.send(data.encode())

def handle_gen(peer_ip,peer_port,message):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    peer_send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_send_socket.connect((peer_ip, peer_port))
    peer_send_socket.send(message.encode())


def gen(PEER_IP,PEER_NUM):
    global GENERATE_FLAG,connect_peers_total,MESSAGE_COUNT,MESSAGE_LOG
    complete = True
    while not GENERATE_FLAG:
        a = 1   
    while GENERATE_FLAG :
        while MESSAGE_COUNT <10 and complete:
            complete = False
            message = generate_message(PEER_IP,int(PEER_NUM+20000))
            MESSAGE_COUNT+= 1
            for peer in connect_peers_total:
                peer_ip,peer_port = peer
                gen_thread = Thread(target = handle_gen, args = (peer_ip,peer_port,message))
                gen_thread.start()
                gen_thread.join()
                message_hash = hash(message[20:])
                MESSAGE_LOG[message_hash] = True
                print(f"Sent message to {peer_ip}:{peer_port}: {message}")
            time.sleep(5)
            complete = True
        if MESSAGE_COUNT == 10:
            print(MESSAGE_LOG)
            break
            


def start_listen_peer(PEER_IP, PEER_NUM, peerset):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    peer_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_recv_socket.bind((PEER_IP,int(20000+PEER_NUM)))
    peer_recv_socket.listen(100)
    while True:
        peer_socket, peer_address = peer_recv_socket.accept()
        peer_recv_thread = Thread(target=handle_peer_recv, args=(peer_socket, peer_address, peerset,PEER_NUM))
        peer_recv_thread.start()

def handle_peer_recv(peer_socket, peer_address, peerset,PEER_NUM):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total,COUNT
    try:
        message = peer_socket.recv(1024).decode()
        if message:
            message1 = message.split(':')
            if message1[0] != "First ":
                message_hash = hash(message[20:])
                if message_hash not in MESSAGE_LOG:
                    for peer in peerset:
                        peer_ip, peer_port = peer
                        if peer_ip != peer_address[0] or peer_port != int(message[-7:-2]):
                            peer_socket.sendall(message.encode())
                            print(f"Forwarded message to {peer_ip}:{peer_port}: {message}")
                    MESSAGE_LOG[message_hash] = True
            else:
                GENERATE_FLAG = True
                message1[5] = int(message1[5]) + 20000
                peer = [message1[4],message1[5]]
                connect_peers_total.append(peer)
    except ConnectionAbortedError as c:
        a = 1
    except Exception as e:
        print(f"Error receiving message from {peer_address}: {e}")
    

def generate_liveness_request(peer_ip,peer_port):
    timestamp = get_time()
    message = f"Liveness Request:{timestamp}:{peer_ip}:{peer_port}"
    return message


def generate_liveness_reply(sender_timestamp, sender_ip,sender_port):
    message = f"Liveness Reply:{sender_timestamp}:{sender_ip}:{sender_port}:{socket.gethostbyname(socket.gethostname())}"
    return message


def send_liveness_messages(peer_ip, peer_port):
    global COUNT,connect_peers_total
    for peer in connect_peers_total:
        _,a = peer
        COUNT[a] = 0
    peer_port = 20000 + int(peer_port)
    while True:
        time.sleep(13)
        liveness_request = generate_liveness_request(peer_ip,peer_port)
        for peer in connect_peers_total:
            peer_ip ,peer_port = peer
            COUNT[peer_port] += 1
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as liveness_socket:
                liveness_socket.connect((peer_ip, peer_port))
                liveness_socket.sendall(liveness_request.encode())
        for key,values in COUNT.items():
            if values >= 3:
                dead_node = key
                report(dead_node)

def report(node):
    print("The node:" + node +"is dead")



def main(PEER_NUM, PEER_IP):
    global MESSAGE_COUNT, GENERATE_FLAG,MESSAGE_LOG,connect_peers_total
    seeds = read_config()
    rands = select_seeds(seeds) 
    peerset, peer_list = connect_seeds(seeds, rands, PEER_NUM, PEER_IP)
    print(peer_list)
    print("\n")
    print(PEER_NUM)
    print("\n")
    print(peerset)
    PEER_IP = str(PEER_IP)
    listen_thread = Thread(target=start_listen_peer, args=(PEER_IP, PEER_NUM, peerset))
    listen_thread.start()
    peers_sel = select_peers(peerset)
    connect_peers(peers_sel, PEER_IP,PEER_NUM)
    gen_thread = Thread(target = gen, args=(PEER_IP,PEER_NUM))
    gen_thread.start()
    # liveliness_thread = Thread(target = send_liveness_messages, args=(PEER_IP,PEER_NUM))
    # liveliness_thread.start()
if __name__ == '__main__':
    PEER_NUM = int(sys.argv[1])
    PEER_IP = sys.argv[2]
    main(PEER_NUM, PEER_IP)
