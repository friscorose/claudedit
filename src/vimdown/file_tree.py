"""
Custom file tree widget with directory navigation.
"""

from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.widgets import Static, Tree
from textual.message import Message


class DirectoryChanged(Message):
    """Message sent when directory changes."""

    def __init__(self, path: Path):
        super().__init__()
        self.path = path


class FileSelected(Message):
    """Message sent when a file is selected."""

    def __init__(self, path: Path):
        super().__init__()
        self.path = path


class CustomDirectoryTree(Static):
    """Custom directory tree widget with parent directory navigation."""

    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)
        self.current_path = Path(path)

    def compose(self) -> ComposeResult:
        yield Tree("Files", id="file-tree-widget")

    def on_mount(self) -> None:
        """Initialize the tree with current directory contents."""
        self.refresh_tree()

    def refresh_tree(self) -> None:
        """Refresh the tree with current directory contents."""
        tree = self.query_one("#file-tree-widget", Tree)
        tree.clear()

        root = tree.root
        root.set_label(f"📁 {self.current_path.name or str(self.current_path)}")

        # Add parent directory option if not at root
        if self.current_path.parent != self.current_path:
            parent_node = root.add(
                "📁 ..", data={"type": "parent", "path": self.current_path.parent}
            )
            parent_node.allow_expand = False

        # Add directories first
        try:
            directories = sorted([p for p in self.current_path.iterdir() if p.is_dir()])
            for dir_path in directories:
                dir_node = root.add(
                    f"📁 {dir_path.name}", data={"type": "directory", "path": dir_path}
                )
                dir_node.allow_expand = False
        except PermissionError:
            pass

        # Add files
        try:
            files = sorted([p for p in self.current_path.iterdir() if p.is_file()])
            for file_path in files:
                icon = "📄"
                if file_path.suffix.lower() in [".md", ".markdown"]:
                    icon = "📝"
                elif file_path.suffix.lower() in [".txt", ".text"]:
                    icon = "📄"
                file_node = root.add(
                    f"{icon} {file_path.name}", data={"type": "file", "path": file_path}
                )
                file_node.allow_expand = False
        except PermissionError:
            pass

        root.expand()

    def navigate_to(self, path: Path) -> None:
        """Navigate to a different directory."""
        if path.is_dir():
            self.current_path = path
            self.refresh_tree()

    @on(Tree.NodeSelected)
    def on_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection in the tree."""
        if event.node.data:
            node_data = event.node.data
            if node_data["type"] == "parent":
                self.navigate_to(node_data["path"])
                self.post_message(DirectoryChanged(node_data["path"]))
            elif node_data["type"] == "directory":
                self.navigate_to(node_data["path"])
                self.post_message(DirectoryChanged(node_data["path"]))
            elif node_data["type"] == "file":
                self.post_message(FileSelected(node_data["path"]))
