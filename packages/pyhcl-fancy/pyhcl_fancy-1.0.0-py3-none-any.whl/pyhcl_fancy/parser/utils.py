import pathlib
import hcl2


def _open_all_tf_files(directory_path: str) -> dict:
    """
    Recursively opens all Terraform (.tf) files in the given directory and
    loads their content into a dictionary.

    Args:
        directory_path (str): The path to the directory containing Terraform files.

    Returns:
        dict: A dictionary mapping each Terraform file path to its parsed content.
    """
    tf_dir = pathlib.Path(directory_path)
    tf_file_content = {}

    for tf_file in tf_dir.rglob("./*.tf"):
        with open(tf_file, "r") as f:
            tf_file_content[str(tf_file)] = hcl2.load(f)

    return tf_file_content
