Lab 1

#Advait Gaur (B22CS004)
#Anuj Chincolikar (B22ES018)

This project is a distributed peer-to-peer messaging system implemented in Python using socket programming. It consists of seed nodes and peer nodes that communicate with each other to exchange messages. The system is designed to create a network where peers forward messages to each other, simulating a decentralised communication environment.

Project Structure : 

1. config.csv : Configuration file containing seed nodes' information. [ seed number , seed address and seed port ]
2. hmm.txt , hmm2.txt , hmm3.txt : Python scripts implementing the peer node and seed node functionalities. 
3. peer.py : Python script defining behaviour of peer nodes.It establishes connections with other peers and seeds, listens for incoming messages, and forwards messages to other connected peers.
4. seed.py : Python script defining behaviour of seed nodes.It establishes connections with other peers and seeds, listens for incoming messages, and forwards messages to other connected peers.
5. test.bat : A batch file used for testing. It starts multiple instances of seed and peer nodes.
6. outputfile.txt : Output file to log the messages exchanged.

Requirements :

1.Python
2.Pandas Library

Instructions :

1.Make sure that all the files are present in the same directory.
2.Open your terminal and run the test.bat file

Finally you will be able to view the messages exchanged between nodes that will be logged in "output.txt".

Additional Points:

1.Modify the "config.csv" file to adjust the seed nodes' addresses and ports
2.Ensure that Python and required dependencies are installed.
3.Adjust firewall settings if necessary to allow communication between nodes.

