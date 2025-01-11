class Edge:
    class NodeConnection:
        def __init__(self, node: str, index: int):
            self.node = node
            self.index = index

    def __init__(self, from_node: str, from_index: int, to_node: str, to_index: int):
        self.from_connection = self.NodeConnection(from_node, from_index)
        self.to_connection = self.NodeConnection(to_node, to_index)

    def __repr__(self):
        return f"Edge(from={self.from_connection.node}, from_index={self.from_connection.index}, to={self.to_connection.node}, to_index={self.to_connection.index})"
