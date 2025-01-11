from pyhcl_fancy.blocks.real.real_block import RealBlock
from pyhcl_fancy.collection_tree.node import Node


class DataBlock(RealBlock):
    def __init__(self):
        """
        Initializes a new instance of the DataBlock class.

        Attributes:
            data_type (str): The type of the data block.
            data_name (str): The name of the data block.

        Inherited Attributes:
            state_path (str): The state path of the block.
            count (int): The count of the block.
            for_each (list | dict): The for_each of the block.
            content (dict): The content of the block.
            file_path (str): The path of the file where the block is defined
        """
        super().__init__()
        self.data_type: str = ""
        self.data_name: str = ""

    def parse(
        self, raw_data_dict: dict, data_file_path: str, parent_file_node: Node
    ) -> None:
        """
        Parses the raw_data_dict dictionary and sets the DataBlock's fields.

        Args:
            raw_data_dict (dict): The raw dictionary from the terraform file for the data block.
            data_file_path (str): The path of the file where the data block is defined.
            parent_file_node (Node): The parent node in the collection tree.

        Returns:
            None
        """
        self.data_type = list(raw_data_dict.keys())[0]
        self.data_name = list(raw_data_dict[self.data_type].keys())[0]
        self.file_path = data_file_path
        if parent_file_node.submodule_state_path is None:
            self.state_path = f"data.{self.data_type}.{self.data_name}"
        else:
            self.state_path = f"{parent_file_node.submodule_state_path}.data.{self.data_type}.{self.data_name}"
        for attribute in raw_data_dict[self.data_type][self.data_name]:
            self.content[attribute] = raw_data_dict[self.data_type][self.data_name][
                attribute
            ]
