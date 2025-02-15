import threading
from seed import Seed 
import logging

logging.basicConfig(level=logging.INFO,filename='outputfile.log',format='%(asctime)s:%(message)s')

open('outputfile.log', 'w').close()
open('freqtrack.log', 'w').close()

seed_list = []
with open('config.txt','r') as f:
    all_ip = f.readlines()
    for ip in all_ip:
        seed_list.append(ip.strip())

print("seed list is ", seed_list)

threads = []
for ip in seed_list:
    seed = Seed(port = int(ip[-4:]))
    seedThread = threading.Thread(target=seed.listen)
    seedThread.start()
    threads.append(seedThread)

for thread in threads:
    thread.join()

    '''
    The program will wait at this point until each thread finishes its work
    '''