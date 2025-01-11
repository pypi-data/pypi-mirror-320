from pyhcl_fancy.blocks.terraform_block import TerraformBlock


class ProviderBlock(TerraformBlock):
    def __init__(self):
        """
        Initializes a new instance of the ProviderBlock class.

        Attributes:
            type (str): The type of the provider.
            region (str): The region for the provider.
            alias (str): The alias of the provider.
            assume_role (str): The assume role for the provider.
            default_tags (dict): The default tags for the provider.
            options (dict): The options for the provider.

        Inherited Attributes:
            file_path (str): The path of the file where the provider is defined.
        """
        super().__init__()
        self.type: str = ""
        self.region: str = ""
        self.alias: str = ""
        self.assume_role: dict = {}
        self.default_tags: dict = {}
        self.options: dict = {}

    def parse(self, raw_provider_dict: dict, provider_file_path: str) -> None:
        """
        Parses the raw_provider_dict to set the ProviderBlock's fields.

        Args:
            raw_provider_dict (dict): The raw dictionary from the terraform file for the provider block.
            provider_file_path (str): The path of the file where the provider block is defined.

        Returns:
            None
        """
        self.type = list(raw_provider_dict.keys())[0]
        self.file_path = provider_file_path
        for attribute in raw_provider_dict[self.type]:
            match attribute:
                case "region":
                    self.region = raw_provider_dict[self.type][attribute]
                case "alias":
                    self.alias = raw_provider_dict[self.type][attribute]
                case "assume_role":
                    if len(raw_provider_dict[self.type][attribute]) > 1:
                        raise ValueError(
                            f"Invalid assume role configuration: multiple assume roles found in {provider_file_path}"
                        )
                    self.assume_role = raw_provider_dict[self.type][attribute][0]
                case "default_tags":
                    self.default_tags = raw_provider_dict[self.type][attribute][0][
                        "tags"
                    ]
                case _:
                    self.options[attribute] = raw_provider_dict[self.type][attribute]
