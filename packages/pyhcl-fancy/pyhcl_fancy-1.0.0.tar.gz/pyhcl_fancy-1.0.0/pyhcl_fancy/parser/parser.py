from pathlib import Path

from pyhcl_fancy.collection_tree.node import Node
from pyhcl_fancy.collection_tree.tree import CollectionTree
from pyhcl_fancy.collection_tree.exceptions import DirectoryNodeNotFoundError


from pyhcl_fancy.blocks.real.data.data_block import DataBlock
from pyhcl_fancy.blocks.real.module.module_block import ModuleBlock
from pyhcl_fancy.blocks.real.resource.resource_block import ResourceBlock
from pyhcl_fancy.blocks.reference.meta.meta_block import TerraformMetaBlock
from pyhcl_fancy.blocks.reference.output.output_block import OutputBlock
from pyhcl_fancy.blocks.reference.provider.provider_block import ProviderBlock
from pyhcl_fancy.blocks.reference.local.local_block import LocalBlock
from pyhcl_fancy.blocks.reference.variable.variable_block import VariableBlock

from pyhcl_fancy.parser.utils import _open_all_tf_files
from pyhcl_fancy.parser.exceptions import UnexpectedTerraformBlockError


class FancyParser:
    def __init__(self, terraform_directory: str):
        """
        Initializes a new instance of the FancyParser class.

        Args:
            terraform_directory (str): The path to the directory containing Terraform files.

        Attributes:
            terraform_directory (str): The path to the directory containing Terraform files.
            terraform_content (dict): A dictionary mapping file paths to their parsed content.
            collection_tree (CollectionTree): The collection tree containing the directory and file nodes.
        """
        self.terraform_directory = terraform_directory
        self.terraform_content: dict = {}
        self.collection_tree: CollectionTree = CollectionTree()

    def construct_empty_tree(self) -> None:
        """
        Constructs an empty collection tree from the Terraform files.

        Iterates through the Terraform content, setting up the directory
        and file nodes in the collection tree. It initializes the root node
        and adds directory and file nodes based on the file paths in the
        Terraform content. If a directory node is not found, it creates a new
        one and adds it to the collection tree.
        """
        root = self._set_tree_root()

        for file in self.terraform_content:
            directory_path = str(Path(file).parent)
            # if file path minus file name is the given directory, file is root level
            if directory_path == self.terraform_directory:
                directory_node = root
            else:
                try:
                    # directory path is everything but the last element
                    directory_node = self.collection_tree.find_directory_node(
                        directory_path
                    )
                # if directory node isn't found, create it
                except DirectoryNodeNotFoundError:
                    directory_node = Node()
                    directory_node.is_directory = True
                    directory_node.relative_file_path = directory_path
                    directory_node.parent = root
                    root.add_child(directory_node)

            # add the file node to the directory node
            file_node = Node()
            file_node.relative_file_path = file
            directory_node.add_child(file_node)

    def parse(self) -> None:
        """
        Parses the Terraform content and constructs the collection tree.

        This function iterates over all files in the Terraform content and
        parses the blocks in each file. It uses a switch case to apply a ruleset
        based on the type of block. The ruleset is as follows:

        * For each module block, it initializes a new ModuleBlock and parses
          the raw module dictionary. It then checks if the module source points
          to a submodule, and if so, moves the submodule's directory node to the
          calling module's file node.
        * For each resource block, it initializes a new ResourceBlock and parses
          the raw resource dictionary.
        * For each data block, it initializes a new DataBlock and parses the raw
          data dictionary.
        * For each output block, it initializes a new OutputBlock and parses the
          raw output dictionary.
        * For each variable block, it initializes a new VariableBlock and parses
          the raw variable dictionary.
        * For each local block, it initializes a new LocalBlock and parses the
          raw locals dictionary.
        * For each provider block, it initializes a new ProviderBlock and parses
          the raw provider dictionary.
        * For each terraform block, it initializes a new TerraformMetaBlock and
          parses the raw meta dictionary.
        * If an unexpected block type is found, it raises an UnexpectedTerraformBlockError.

        Returns:
            None

        Notes:
            This function represents the primary API for this library and will
            be the main entrypoint that calling applications will use.
        """
        self._read_tf_files()
        self.construct_empty_tree()

        for file in self.terraform_content:
            file_node = self.collection_tree.find_file_node(file)

            for block_type in self.terraform_content[file]:
                # switch case to apply a ruleset based on the type of block
                match block_type:
                    case "module":
                        for module in self.terraform_content[file][block_type]:
                            module_block = ModuleBlock()
                            module_block.parse(
                                raw_module_dict=module,
                                module_file_path=file,
                                parent_file_node=file_node,
                            )
                            file_node.blocks.append(module_block)

                            # logical block to get valid parent of local submodules
                            true_parent = file_node.parent
                            absolute_module_source = (
                                true_parent.relative_file_path
                                + "/"
                                + module_block.module_source.lstrip("./")
                            )
                            if module_block.module_source.startswith("../"):
                                file_count_walk_back = 0
                                i = 0
                                separated_module_source = (
                                    module_block.module_source.split("/")
                                )
                                while separated_module_source[i] == "..":
                                    file_count_walk_back += 1
                                    i += 1

                                true_parent_directory = "/".join(
                                    true_parent.relative_file_path.split("/")[
                                        :-file_count_walk_back
                                    ]
                                )
                                absolute_module_source = (
                                    true_parent_directory
                                    + "/"
                                    + module_block.module_source.lstrip("../")
                                )
                                true_parent = self.collection_tree.find_directory_node(
                                    absolute_module_source
                                )

                            # module source points to a submodule, move that submodules directory node to the calling module's file node
                            if Path(absolute_module_source).is_dir():
                                submodule_directory_node = (
                                    self.collection_tree.find_directory_node(
                                        absolute_module_source,
                                    )
                                )
                                # print(f"moving {submodule_directory_node.relative_file_path} to {file_node.relative_file_path}")
                                self.collection_tree.move_node(
                                    submodule_directory_node, file_node, module_block
                                )
                    case "resource":
                        for resource in self.terraform_content[file][block_type]:
                            resource_block = ResourceBlock()
                            resource_block.parse(
                                raw_resource_dict=resource,
                                resource_file_path=file,
                                parent_file_node=file_node,
                            )
                            file_node.blocks.append(resource_block)
                    case "data":
                        for data in self.terraform_content[file][block_type]:
                            data_block = DataBlock()
                            data_block.parse(
                                raw_data_dict=data,
                                data_file_path=file,
                                parent_file_node=file_node,
                            )
                            file_node.blocks.append(data_block)
                    case "output":
                        for output in self.terraform_content[file][block_type]:
                            output_block = OutputBlock()
                            output_block.parse(
                                raw_output_dict=output, output_file_path=file
                            )
                            file_node.blocks.append(output_block)
                    case "variable":
                        for variable in self.terraform_content[file][block_type]:
                            variable_block = VariableBlock()
                            variable_block.parse(
                                raw_variable_dict=variable, variable_file_path=file
                            )
                            file_node.blocks.append(variable_block)
                    case "locals":
                        local_block = LocalBlock()
                        local_block.parse(
                            raw_locals_dict=self.terraform_content[file][block_type],
                            locals_file_path=file,
                        )
                        file_node.blocks.append(local_block)
                    case "provider":
                        for provider in self.terraform_content[file][block_type]:
                            provider_block = ProviderBlock()
                            provider_block.parse(
                                raw_provider_dict=provider, provider_file_path=file
                            )
                            file_node.blocks.append(provider_block)
                    case "terraform":
                        for meta in self.terraform_content[file][block_type]:
                            meta_block = TerraformMetaBlock()
                            meta_block.parse(raw_meta_dict=meta, meta_file_path=file)
                            file_node.blocks.append(meta_block)
                    case _:
                        raise UnexpectedTerraformBlockError(
                            f"Found unexpected Terraform block type {block_type} in file {file}"
                        )

    def _read_tf_files(self) -> None:
        """
        Reads and loads all Terraform files from the specified directory.

        This function utilizes the `_open_all_tf_files` utility to open
        and parse all Terraform files in the provided directory. The parsed
        content is then stored in the `terraform_content` attribute as a
        dictionary mapping file paths to their content.

        Returns:
            None
        """
        self.terraform_content = _open_all_tf_files(self.terraform_directory)

    def _set_tree_root(self) -> Node:
        """
        Initializes the root node of the collection tree.

        This function creates a Node object that is marked as the root of the
        collection tree. The root node is a directory node with its file path
        set to the provided Terraform directory.

        Returns:
            Node: The root node of the collection tree.
        """
        root = Node()
        root.is_root = True
        root.is_directory = True
        root.submodule_state_path = ""
        root.relative_file_path = self.terraform_directory
        return self.collection_tree.add_root(root)
