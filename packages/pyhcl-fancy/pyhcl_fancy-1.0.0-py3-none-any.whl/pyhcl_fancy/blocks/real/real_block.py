from pyhcl_fancy.blocks.terraform_block import TerraformBlock


class RealBlock(TerraformBlock):
    def __init__(self):
        """
        Initializes a new instance of the RealBlock class.

        Attributes:
            state_path (str): The state path of the block.
            count (int): The count of the block.
            for_each (list | dict): The for_each of the block.
            content (dict): The content of the block.

        Inherited Attributes:
            file_path (str): The path of the file where the block is defined
        """
        super().__init__()
        self.state_path: str = ""
        self.count: int = None
        self.for_each: list | dict = None
        self.content: dict = {}
