from typing import List, Dict, Union, Optional

from kivy.uix.treeview import TreeView, TreeViewLabel

Tree = Dict[str, Union[str, List['Tree']]]


def populate_tree_view(tree_view: TreeView,
                       parent: Union[TreeView, TreeViewLabel, None],
                       node: Tree) -> None:
    """
    Populates a TreeView recursively from node data.

    :param tree_view:
    :param parent:
    :param node:
    :return:
    """
    if parent is None:
        tree_node = tree_view.add_node(
            TreeViewLabel(
                text=node['node_id'],
                is_open=True
            ))
    else:
        tree_node = tree_view.add_node(
            TreeViewLabel(
                text=node['node_id'],
                is_open=False
            ),
            parent
        )

    for child_node in node['children']:
        populate_tree_view(
            tree_view, tree_node, child_node
        )

