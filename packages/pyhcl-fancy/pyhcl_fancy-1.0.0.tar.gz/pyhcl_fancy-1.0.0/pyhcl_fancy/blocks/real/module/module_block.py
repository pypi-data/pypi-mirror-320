from pyhcl_fancy.blocks.real.real_block import RealBlock
from pyhcl_fancy.collection_tree.node import Node


class ModuleBlock(RealBlock):
    def __init__(self):
        """
        Initializes a new instance of the ModuleBlock class.

        Attributes:
            module_name (str): The name of the module.
            module_source (str): The source of the module.
            module_version (str): The version of the module.

        Inherited Attributes:
            state_path (str): The state path of the block.
            count (int): The count of the block.
            for_each (list | dict): The for_each of the block.
            content (dict): The content of the block.
            file_path (str): The path of the file where the block is defined
        """
        super().__init__()
        self.module_name: str = ""
        self.module_source: str = ""
        self.module_version: str = ""

    def parse(
        self, raw_module_dict: dict, module_file_path: str, parent_file_node: Node
    ) -> None:
        """
        Parses the raw_module_dict to set the ModuleBlock's fields.

        Args:
            raw_module_dict (dict): The raw dictionary from the terraform file for the module block.
            module_file_path (str): The path of the file where the module block is defined.
            parent_file_node (Node): The parent node in the collection tree.

        Returns:
            None
        """
        self.module_name = list(raw_module_dict.keys())[0]
        self.file_path = module_file_path
        if parent_file_node.submodule_state_path is None:
            self.state_path = f"module.{self.module_name}"
        else:
            self.state_path = (
                f"{parent_file_node.submodule_state_path}.module.{self.module_name}"
            )
        for attribute in raw_module_dict[self.module_name]:
            match attribute:
                case "source":
                    self.module_source = raw_module_dict[self.module_name][attribute]
                case "version":
                    self.module_version = raw_module_dict[self.module_name][attribute]
                case _:
                    self.content[attribute] = raw_module_dict[self.module_name][
                        attribute
                    ]
