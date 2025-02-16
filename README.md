# P2P Network Implementation

## Overview
This project demonstrates a P2P network with two main use cases:
1. Normal peer-to-peer interaction
2. Power law distribution testing

## Core Components

### Seed Node (`seed.py`)
- Acts as a central registry for peer discovery
- Maintains a list of active peers
- Handles peer registration and peer list distribution
- Manages dead node removal

### Peer Node (`peer.py`)
- Connects to seed nodes for network discovery
- Maintains connections with other peers
- Implements gossip protocol for message propagation
- Performs liveness tests to detect disconnected peers
- Auto-adjusts connections based on node capacity

## NOTE: Should be in p2p_protocol file directory

```bash
cd p2p_protocol
```

## Use Case 1: Normal P2P Operation

### Setup and Running
```bash
python runner.py  # Start seed nodes
python peer.py  # Start individual peers (enter port when prompted)
```

### What Happens
- Seed nodes start listening on configured ports.
- Each peer:
  - Connects to available seeds
  - Registers itself
  - Gets a list of other peers
  - Establishes connections with other peers
  - Starts sending gossip messages
  - Monitors peer liveness

### Testing Peer Behavior
- Start 3-4 peers in different terminals.
- Observe connection messages.
- Watch message propagation between peers.
- Close a peer and observe how others detect and handle disconnection.

## Use Case 2: Power Law Distribution Testing

### Setup and Running
```bash
python runner.py  # Start seeds
python PeerRunner.py  # Start multiple peers
# Wait ~2 minutes for network stabilization
python visualizer.py  # View distribution
```

## Detailed System Architecture

### Peer Class Structure (`peer.py`)
#### Key Components
- **Socket Management**: Peer socket for listening, seed connections, peer connections
- **Data Structures**:
  - `available_peers`: List of known peers
  - `message_list`: Hash table for message deduplication
  - `alive_peers`: Active peer tracking
  - `peer_timestamps`: Liveness monitoring
- **Connection Limits**: 
```python
def calculate_max_peers(self):
    base = 1.5
    return int(40 * math.pow(base, -self.node_id / 10))
```

### Peer Network Operations
#### Registration Protocol
- Sends: `register:IP:PORT`
- Receives: `registered successfully`
- Requests: Peer list
- Receives: `peer list:IP1#PORT1:IP2#PORT2...`

#### Peer-to-Peer Communication
```python
def handle_peer(self, new_socket):
    # Verify peer capacity
    # Exchange connection messages
    # Start message handling threads
    # Initialize liveness monitoring
```
- **Message Types**:
  - Connection messages
  - Liveness requests/replies
  - Gossip messages
  - Dead node notifications

#### Gossip Protocol Implementation
```python
def generate_messages(self, new_socket):
    # Generates 10 messages with 5-second intervals
    # Uses secure hash for message deduplication
```

### Seed Node Architecture (`seed.py`)

#### Peer Management
```python
def handle_peer(self, peer, addr):
    # Handles:
    # - Registration
    # - Peer list requests
    # - Dead node notifications
```

#### Dead Node Handling
```python
def dead_node(self, peer, message):
    # Removes dead peer from list
    # Logs removal
    # Notifies other peers
```

![image](https://github.com/user-attachments/assets/1f89fa2e-f3cb-4486-9319-67cb5feed3f9)


## Network Security Features

### Message Security
```python
def secure_hash(message):
    salt = b"ASSIGNMENT_1"
    iterations = 100000
    # SHA-512 hashing implementation
```

### Connection Validation
- Peer capacity checks
- Node ID verification
- Duplicate connection prevention

## Liveness Detection System

### Periodic Checks
```python
def liveness_test(self, new_socket):
    # Sends request every 13 seconds
    # Tracks failed attempts
    # Handles peer removal after 3 failures
```

### Timestamp Management
- Records last response time
- Calculates response delays
- Updates peer status

## Logging and Monitoring

### File Logging
- `outputfile.log`: Network events
- `freqtrack.log`: Peer degree tracking

### Log Format
```
timestamp:event_description
peer_id=>degree
```

## Power Law Implementation

### Degree Calculation
- Based on node ID
- Exponential decay function
- Maximum of 60 connections

### Visualization
```python
def analyze_degrees_plot():
    # Reads freqtrack.log
    # Calculates distribution
    # Generates matplotlib visualization
```
![image](https://github.com/user-attachments/assets/357cbc74-b5cb-4f17-a277-b3517bf7f306)

## Advanced Usage

### Custom Network Configurations
Modify `config.txt`:
```
127.0.0.1:8080
127.0.0.1:8081
...
```

## Testing Scenarios

### Network Partition Testing
- Start multiple peers
- Disconnect seed nodes
- Observe reconnection behavior

### Message Propagation Testing
- Monitor gossip message flow
- Verify message deduplication
- Check propagation delays

## Troubleshooting Guide

### Common Issues
- **Port Conflicts**: Use different ports or kill existing processes
- **Connection Timeouts**: Check seed node availability
- **Message Propagation Issues**: Verify peer connections

cal connection

### Software
- **Python 3.x**
- Required packages:
```bash
pip install matplotlib socket threading logging hashlib
```

## References
- P2P Network Protocols
- Distributed Systems Architecture
- Network Security Best Practices
- Power Law in Network Topology
