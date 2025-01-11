from pyhcl_fancy.collection_tree.node import Node
from pyhcl_fancy.blocks.real.module.module_block import ModuleBlock
from pyhcl_fancy.collection_tree.exceptions import (
    FileNodeNotFoundError,
    DirectoryNodeNotFoundError,
    InvalidMoveLocationError,
)


class CollectionTree:
    def __init__(self):
        """
        Initializes a new instance of the CollectionTree class.

        Attributes:
            root (Node): The root node of the collection tree.
        """
        self.root: Node = None

    def add_root(self, node: Node) -> Node:
        """
        Adds a root node to the collection tree if one does not already exist.

        Args:
            node: The root node to add to the collection tree.

        Returns:
            The root node of the collection tree.
        """
        if self.root is None:
            self.root = node
        return self.root

    def find_directory_node(self, target_directory: str) -> Node:
        """
        Wrapper function to find a directory node in the collection tree.

        Args:
            target_directory (str): The path of the directory to search for.

        Returns:
            Node: The directory node if found, otherwise raises a DirectoryNodeNotFoundError.
        """
        found_node = self._find_directory_node(self.root, target_directory)
        if found_node is None:
            raise DirectoryNodeNotFoundError(
                f"Directory node for {target_directory} not found in the collection tree."
            )

        return found_node

    def _find_directory_node(self, node: Node, target_directory: str) -> Node:
        """
        Recursively searches for a directory node within the collection tree
        given a directory path.

        Args:
            node (Node): The current node to search in the collection tree.
            target_directory (str): The path of the directory to search for.

        Returns:
            Node: The directory node if found, otherwise None.
        """
        if node.is_directory and node.relative_file_path == target_directory:
            return node

        for child in node.children:
            found_node = self._find_directory_node(child, target_directory)
            if found_node is not None:
                return found_node

        return None

    def find_file_node(self, target_file: str) -> Node:
        """
        Wrapper function to find a file node in the collection tree.

        Args:
            target_file (str): The path of the file to search for.

        Returns:
            Node: The file node if found, otherwise raises a FileNodeNotFoundError.
        """
        found_node = self._find_file_node(self.root, target_file)
        if found_node is None:
            raise FileNodeNotFoundError(
                f"File node for {target_file} not found in the collection tree."
            )

        return found_node

    def _find_file_node(self, node: Node, target_file: str) -> Node:
        """
        Recursively searches for a file node within the collection tree
        given a file path.

        Args:
            node (Node): The current node to search in the collection tree.
            target_file (str): The path of the file to search for.

        Returns:
            Node: The file node if found, otherwise None.
        """
        if not node.is_directory and node.relative_file_path == target_file:
            return node

        for child in node.children:
            found_node = self._find_file_node(child, target_file)
            if found_node is not None:
                return found_node

        return None

    def move_node(self, source: Node, destination: Node, caller: ModuleBlock) -> Node:
        """
        Moves a node from one location to another in the collection tree.

        Args:
            source (Node): The node to be moved.
            destination (Node): The node to which the source node is to be moved.
            caller (ModuleBlock): The caller of the move operation.

        Returns:
            Node: A reference to the moved node.

        Raises:
            InvalidMoveLocationError: If the source and destination nodes have the same directory status or if the destination node is already the parent of the source node.
        """
        if source == destination:
            raise InvalidMoveLocationError("Cannot move a node to itself.")
        elif source.parent == destination:
            raise InvalidMoveLocationError(
                "The destination node is already the parent of the source node."
            )
        elif not source.is_directory ^ destination.is_directory:
            raise InvalidMoveLocationError(
                f"The source and destination nodes must not have the same directory status. Both nodes have directory status {source.is_directory}."
            )

        curr_parent = source.parent
        for child in curr_parent.children:
            if child == source:
                node_to_move = child

        # remove node from current parent and add to new parent
        curr_parent.children.remove(node_to_move)
        destination.add_child(node_to_move)

        # update the submodule state path
        if destination.submodule_state_path == "":
            source.submodule_state_path = f"module.{caller.module_name}"
        else:
            source.submodule_state_path = (
                f"{destination.submodule_state_path}.module.{caller.module_name}"
            )

        return source

    def visualize(self) -> None:
        """
        Prints a visual representation of the collection tree to the console.

        This representation is a tree structure with the root node at the top and
        each node's children indented below it. The relative file path of each node
        is printed on the same line as the node.
        """
        self._visualize(self.root, "")

    def _visualize(self, node: Node, prefix: str) -> None:
        """
        Recursively prints the visual representation of the collection tree.

        Args:
            node (Node): The current node being visualized in the collection tree.
            prefix (str): The prefix string used to format the visual representation,
                        indicating the depth of the node in the tree structure.
        """
        print(prefix + node.relative_file_path)

        for child in node.children:
            self._visualize(child, prefix + "|  ")
