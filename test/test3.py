import random
import math
import networkx as nx
from collections import defaultdict

class P2PNode:
    def init(self, node_id):
        self.node_id = node_id
        self.peers = set()
        self.message_cache = set()
        self.max_peers = self._calculate_max_peers()

    def calculatemax_peers(self):
        base = 1.5
        return int(100 * math.pow(base, -self.node_id / 10))

    def can_accept_peers(self):
        return len(self.peers) < self.max_peers

    def add_peer(self, peer_id):
        if peer_id != self.node_id and self.can_accept_peers():
            self.peers.add(peer_id)
            return True
        return False

class PowerLawP2PNetwork:
    def init(self, num_nodes):
        self.nodes = {}
        self.initialize_network(num_nodes)

    def initialize_network(self, num_nodes):
        for i in range(num_nodes):
            self.nodes[i] = P2PNode(i)
        for i in range(1, num_nodes):
            potential_peers = list(range(i))
            weights = [len(self.nodes[j].peers) + 1 for j in potential_peers]
            num_connections = min(
                len(potential_peers)
            )
            selected_peers = random.choices(
                potential_peers,
                weights=weights,
                k=num_connections
            )
            for peer in selected_peers:
                self._connect_nodes(i, peer)

    def connectnodes(self, node1_id, node2_id):
        if node1_id != node2_id:
            self.nodes[node1_id].add_peer(node2_id)
            self.nodes[node2_id].add_peer(node1_id)

    def gossip_message(self, source_id, message):
        if source_id not in self.nodes:
            return
        visited = set([source_id])
        queue = [source_id]
        propagation_path = defaultdict(list)
        while queue:
            current_id = queue.pop(0)
            current_node = self.nodes[current_id]
            forwarding_peers = random.sample(
                list(current_node.peers),
                k=min(3, len(current_node.peers))
            )
            for peer_id in forwarding_peers:
                if peer_id not in visited:
                    visited.add(peer_id)
                    queue.append(peer_id)
                    propagation_path[current_id].append(peer_id)
        return propagation_path
    def get_network_stats(self):
        """Calculate network statistics"""
        degrees = [len(node.peers) for node in self.nodes.values()]
        return {
            'max_degree': max(degrees),
            'min_degree': min(degrees),
            'avg_degree': sum(degrees) / len(degrees),
            'degree_distribution': sorted(degrees, reverse=True)
        }
network = PowerLawP2PNetwork(1000)
stats = network.get_network_stats()
print(f"Network degree distribution: {stats['degree_distribution'][:10]}")
propagation = network.gossip_message(0, "test message")