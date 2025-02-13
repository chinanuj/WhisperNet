import socket
import time
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
import sys
from copy import deepcopy

MAX_threads = 100
peer_list = []
terminate_flag = False
def read_config():
    seeds_list = pd.read_csv('config.csv')

    seeds_dict = {}
    for i in range(len(seeds_list)):
        seeds_dict[seeds_list.iloc[i,0]] = [seeds_list.iloc[i,1], seeds_list.iloc[i,2]]

    return seeds_dict


def get_time():
    timestamp = time.time()
    formatted_timestamp = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(timestamp))

    return formatted_timestamp
    
def listen_peers(server_socket,seed_num):
    global MAX_threads,peer_list,terminate_flag
    with ThreadPoolExecutor(max_workers=MAX_threads) as executor:
        try:
            while not terminate_flag:
                peer_socket, peer_address = server_socket.accept()
                tie = get_time()
                peer_port = peer_socket.recv(1024).decode()
                log_connection(peer_address,tie,seed_num)
                print(f"Accepted connection from {peer_address}")
                executor.submit(handle_peers, peer_socket)
                lst = [peer_address[0],int(peer_port)]
                peer_list.append(lst)
        finally:
            terminate_flag = True
            server_socket.close()
            print("close")

def handle_peers(peer_socket):
    global peer_list
    try:
        data = deepcopy(peer_list)
        json_data = json.dumps(data)
        peer_socket.sendall(json_data.encode())
        print(data)
    finally:
        peer_socket.close()


def log_connection(det,tim,num):

    with open('outputfile.txt', 'a') as file:
        file.write("For Seed Num: "+str(num)+" Peer Registration:- \n")
        file.write(str(tim)+"                  ")
        file.write(str(det)+ "\n")

def remove_dead():
    print("Lorem Ipsum!")

def log_removal(det,tim,num):
    with open('outputfile.txt', 'a') as file:
        file.write("For Seed Num: "+str(num)+" Peer Registration:- \n")
        file.write(str(tim)+"                  ")
        file.write(str(det)+ "\n")
    print("Lorem Ipsum!")


def main(seed_num):
    seeds = read_config()
    seed = seeds[seed_num]
    print(seed_num)
    seed_host = seed[0]
    seed_port = seed[1]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((seed_host, seed_port))
    server_socket.listen(100)
    listen_peers(server_socket,seed_num)
    print("Lorem Ipsum!")


if __name__ == '__main__':
    SEED_NUM = int(sys.argv[1])
    main(SEED_NUM)