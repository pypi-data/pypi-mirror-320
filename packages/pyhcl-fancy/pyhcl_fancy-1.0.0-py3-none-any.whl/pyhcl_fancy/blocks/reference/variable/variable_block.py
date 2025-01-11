from pyhcl_fancy.blocks.terraform_block import TerraformBlock
from typing import Any


class VariableBlock(TerraformBlock):
    def __init__(self):
        """
        Initializes a new instance of the VariableBlock class.

        Attributes:
            variable_name (str): The name of the variable.
            description (str): The description of the variable.
            type (str): The type of the variable.
            default (Any): The default value of the variable.
            validation (dict): The validation rules for the variable.

        Inherited Attributes:
            file_path (str): The path of the file where the variable is defined.
        """
        super().__init__()
        self.variable_name: str = ""
        self.description: str = ""
        self.type: str = ""
        self.default: Any = None
        self.validation: dict = {}

    def parse(self, raw_variable_dict: dict, variable_file_path: str) -> None:
        """
        Parses the raw_variable_dict dictionary and sets the VariableBlock's fields.

        Args:
            raw_variable_dict (dict): The raw dictionary from the terraform file for the variable block.
            variable_file_path (str): The path of the file where the variable block is defined.

        Returns:
            None
        """
        self.variable_name = list(raw_variable_dict.keys())[0]
        self.file_path = variable_file_path
        for attribute in raw_variable_dict[self.variable_name]:
            match attribute:
                case "description":
                    self.description = raw_variable_dict[self.variable_name][attribute]
                case "type":
                    self.type = raw_variable_dict[self.variable_name][attribute]
                case "default":
                    self.default = raw_variable_dict[self.variable_name][attribute]
                case "validation":
                    self.validation = raw_variable_dict[self.variable_name][attribute]
