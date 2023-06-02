from rich.text import Text
from textual.widgets.tree import TreeNode


class MyContracts:
    def __init__(self):
        self.id = None


def create_contract_tree(node: TreeNode, json_data: object) -> None:
    """Adds JSON data to a node.

    Args:
        node (TreeNode): A Tree node.
        json_data (object): An object decoded from JSON.
    """

    from rich.highlighter import ReprHighlighter

    highlighter = ReprHighlighter()

    def add_node(name: str, node: TreeNode, data: object) -> None:
        """Adds a node to the tree.

        Args:
            name (str): Name of the node.
            node (TreeNode): Parent node.
            data (object): Data associated with the node.
        """
        if isinstance(data, dict):
            node.set_label(Text(f"{{}} {name}"))
            for key, value in data.items():
                new_node = node.add("")
                add_node(key, new_node, value)
        elif isinstance(data, list):
            node.set_label(Text(f"[] {name}"))
            for index, value in enumerate(data):
                new_node = node.add("")
                if "name" in value:
                    add_node(str(value["name"]), new_node, value)
                elif "symbol" in value:
                    add_node(str(value["symbol"]), new_node, value)
                else:
                    add_node(str(index), new_node, value)
        else:
            node.allow_expand = False
            if name:
                label = Text.assemble(
                    Text.from_markup(f"[b]{name}[/b]="), highlighter(repr(data))
                )
            else:
                label = Text(repr(data))
            node.set_label(label)

    add_node("Contracts", node, json_data)
