"""Taken from official Textual official widget,
modified to allow directory selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from rich.style import Style
from rich.text import Text, TextType
from textual.widgets import Tree
from textual.widgets._tree import TOGGLE_STYLE
from textual.widgets.tree import TreeNode

@dataclass
class DirEntry:
    """Attaches directory information ot a node."""

    path: str
    is_dir: bool
    loaded: bool = False


class DirectoryTree(Tree[DirEntry]):
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "tree--label",
        "tree--guides",
        "tree--guides-hover",
        "tree--guides-selected",
        "tree--cursor",
        "tree--highlight",
        "tree--highlight-line",
        "directory-tree--folder",
        "directory-tree--file",
        "directory-tree--extension",
        "directory-tree--hidden",
    }

    DEFAULT_CSS = """
    DirectoryTree > .directory-tree--folder {
        text-style: bold;
    }

    DirectoryTree > .directory-tree--file {

    }

    DirectoryTree > .directory-tree--extension {
        text-style: italic;
    }

    DirectoryTree > .directory-tree--hidden {
        color: $text 50%;
    }
    """

    def __init__(
        self,
        path: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.path = path
        self.selected_dir = path
        super().__init__(
            path,
            data=DirEntry(path, True),
            name=name,
            id=id,
            classes=classes,
        )

    def process_label(self, label: TextType) -> Text:
        """Process a str or Text in to a label.
        Maybe overridden in a subclass to change modify how labels are rendered.

        Args:
            label (TextType): Label.

        Returns:
            Text: A Rich Text object.
        """
        if isinstance(label, str):
            text_label = Text(label)
        else:
            text_label = label
        first_line = text_label.split()[0]
        return first_line

    def render_label(
        self, node: TreeNode[DirEntry], base_style: Style, style: Style
    ) -> Text:
        node_label = node._label.copy()
        node_label.stylize(style)

        prefix = ("📂 " if node.is_expanded else "📁 ", base_style + TOGGLE_STYLE)
        node_label.stylize_before(
            self.get_component_rich_style("directory-tree--folder", partial=True)
        )

        if node_label.plain.startswith("."):
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--hidden")
            )

        text = Text.assemble(prefix, node_label)
        return text

    def load_directory(self, node: TreeNode[DirEntry]) -> None:
        assert node.data is not None
        dir_path = Path(node.data.path)
        node.data.loaded = True
        directory = sorted(
            list(dir_path.iterdir()),
            key=lambda path: (not path.is_dir(), path.name.lower()),
        )
        for path in directory:
            if not path.is_dir():
                continue
            node.add(
                path.name,
                data=DirEntry(str(path), path.is_dir()),
                allow_expand=path.is_dir(),
            )
        node.expand()

    def on_mount(self) -> None:
        self.load_directory(self.root)

    def on_tree_node_expanded(self, event: Tree.NodeSelected[Any]) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if dir_entry.is_dir:
            if not dir_entry.loaded:
                self.load_directory(event.node)

    def on_tree_node_selected(self, event: Tree.NodeSelected[Any]) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if dir_entry.is_dir:
            self.selected_dir = dir_entry.path
            print("Selected dir:", self.selected_dir)
