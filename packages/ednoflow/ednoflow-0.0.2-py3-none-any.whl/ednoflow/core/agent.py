class Agent:
    """
    Represents an agent that moves through the graph.
    Agents are located on edges and interact with nodes as decision points.

    Attributes:
        agent_id (str): A unique identifier for the agent.
        current_edge (Edge): The edge where the agent is currently located.
        position (float): The agent's position along the edge (0.0 to 1.0, representing progress).
        metadata (dict): Additional information about the agent.
    """

    def __init__(self, agent_id, current_edge, position=0.0, metadata=None):
        """
        Initialize an Agent instance.

        Args:
            agent_id (str): A unique identifier for the agent.
            current_edge (Edge): The edge where the agent starts.
            position (float, optional): The agent's position along the edge (default is 0.0, at the start of the edge).
            metadata (dict, optional): Additional information about the agent.
        """
        if not (0.0 <= position <= 1.0):
            raise ValueError("Position must be a value between 0.0 and 1.0")
        
        self.agent_id = agent_id
        self.current_edge = current_edge
        self.position = position
        self.metadata = metadata or {}

    def __repr__(self):
        """
        Return a string representation of the Agent instance.

        Returns:
            str: A string showing the agent's ID, current edge, and position.
        """
        return (f"Agent(agent_id='{self.agent_id}', current_edge=({self.current_edge.start_node.node_id} -> "
                f"{self.current_edge.end_node.node_id}), position={self.position:.2f})")

    def move_along_edge(self, distance):
        """
        Move the agent along the current edge by a specified distance.

        Args:
            distance (float): The distance to move the agent along the edge (normalized between 0.0 and 1.0).

        Raises:
            ValueError: If the movement causes the position to go out of bounds (below 0.0 or above 1.0).
        """
        new_position = self.position + distance
        if not (0.0 <= new_position <= 1.0):
            raise ValueError("Movement out of edge bounds. Position must stay between 0.0 and 1.0.")
        
        self.position = new_position

    def transfer_to_edge(self, new_edge):
        """
        Transfer the agent to a new edge.

        Args:
            new_edge (Edge): The edge where the agent will be transferred.
        """
        self.current_edge = new_edge
        self.position = 0.0  # Reset position to the start of the new edge

    def add_metadata(self, key, value):
        """
        Add or update metadata for the agent.

        Args:
            key (str): The key for the metadata.
            value (Any): The value associated with the key.
        """
        self.metadata[key] = value
