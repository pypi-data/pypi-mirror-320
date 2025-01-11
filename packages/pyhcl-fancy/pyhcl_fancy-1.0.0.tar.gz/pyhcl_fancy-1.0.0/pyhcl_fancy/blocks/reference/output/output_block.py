from pyhcl_fancy.blocks.terraform_block import TerraformBlock
from typing import Any


class OutputBlock(TerraformBlock):
    def __init__(self):
        """
        Initializes a new instance of the OutputBlock class.

        Attributes:
            name (str): The name of the output variable.
            value (Any): The value of the output variable.
            description (str): The description of the output variable.
            options (dict): The options for the output variable.

        Inherited Attributes:
            file_path (str): The path of the file where the output variable is defined.
        """
        super().__init__()
        self.name: str = ""
        self.value: Any = None
        self.description: str = ""
        self.options: dict = {}

    def parse(self, raw_output_dict: dict, output_file_path: str) -> None:
        """
        Parses the raw_output_dict dictionary and sets the OutputBlock's fields.

        Args:
            raw_output_dict (dict): The raw dictionary from the terraform file for the output block.
            output_file_path (str): The path of the file where the output block is defined.

        Returns:
            None
        """
        self.name = list(raw_output_dict.keys())[0]
        self.file_path = output_file_path
        for attribute in raw_output_dict[self.name]:
            match attribute:
                case "value":
                    self.value = raw_output_dict[self.name][attribute]
                case "description":
                    self.description = raw_output_dict[self.name][attribute]
                case _:
                    self.options[attribute] = raw_output_dict[self.name][attribute]
