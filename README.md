# WhisperNet
Implementation of a Gossip protocol over a peer-to-peer network to broadcast messages and check the liveness of connected peers. Peers register with seed nodes, retrieve peer lists, and establish TCP connections. Messages are broadcasted using a gossip mechanism with a Message List (ML) to prevent redundant forwarding. 
