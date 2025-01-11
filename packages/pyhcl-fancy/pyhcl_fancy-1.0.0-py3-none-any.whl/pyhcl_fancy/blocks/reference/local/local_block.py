from pyhcl_fancy.blocks.terraform_block import TerraformBlock


class LocalBlock(TerraformBlock):
    def __init__(self):
        """
        Initializes a new instance of the LocalBlock class.

        Attributes:
            content (dict): The content of the locals block.

        Inherited Attributes:
            file_path (str): The path of the file where the block is defined
        """
        super().__init__()
        self.content: dict = {}

    def parse(self, raw_locals_dict: dict, locals_file_path: str) -> str:
        """
        Parses the raw locals dictionary and sets the content of the LocalBlock.

        Args:
            raw_locals_dict (dict): The raw locals dictionary to parse.
            locals_file_path (str): The path of the file containing the locals block.

        Returns:
            str: The parsed content of the locals block.
        """
        self.file_path = locals_file_path
        for local_dict in raw_locals_dict:
            self.content.update(local_dict)
