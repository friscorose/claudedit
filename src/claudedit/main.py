#!/usr/bin/env python3
"""
A full-featured markdown editor built with Textual.
Features:
- File tree navigation
- Syntax-highlighted markdown editing
- Live markdown preview
- File operations (new, open, save, save as)
- Keyboard shortcuts
"""

from pathlib import Path
from typing import Optional

from rich.markdown import Markdown
from textual import on, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Static,
    TextArea,
    Label,
    OptionList,
    Tree,
)
from textual.widgets.option_list import Option
from textual.screen import ModalScreen
from textual.message import Message


class VimTextArea(TextArea):
    """TextArea with vim keybindings support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vim_mode = False
        self.vim_command_mode = False  # Normal mode vs Insert mode
        self.vim_status = "INSERT"

    def enable_vim_mode(self, enabled: bool = True):
        """Enable or disable vim mode."""
        self.vim_mode = enabled
        if enabled:
            self.vim_command_mode = False  # Start in insert mode
            self.vim_status = "INSERT"
        else:
            self.vim_status = ""

    async def _on_key(self, event: events.Key) -> None:
        """Handle vim keybindings."""
        if not self.vim_mode:
            await super()._on_key(event)
            return

        # Handle Escape key to toggle between modes
        if event.key == "escape":
            if self.vim_command_mode:
                # Already in command mode, stay in command mode
                pass
            else:
                # Switch to command mode
                self.vim_command_mode = True
                self.vim_status = "NORMAL"
            event.prevent_default()
            return

        # Command mode (Normal mode) keybindings
        if self.vim_command_mode:
            if event.key == "i":
                # Enter insert mode
                self.vim_command_mode = False
                self.vim_status = "INSERT"
                event.prevent_default()
                return
            elif event.key == "a":
                # Enter insert mode after cursor
                self.vim_command_mode = False
                self.vim_status = "INSERT"
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
                event.prevent_default()
                return
            elif event.key == "o":
                # Open new line below and enter insert mode
                cursor_line, _ = self.cursor_position
                self.cursor_position = (cursor_line, len(self.get_line(cursor_line)))
                self.insert("\n")
                self.vim_command_mode = False
                self.vim_status = "INSERT"
                event.prevent_default()
                return
            elif event.key == "shift+o":
                # Open new line above and enter insert mode
                cursor_line, _ = self.cursor_position
                self.cursor_position = (cursor_line, 0)
                self.insert("\n")
                self.cursor_position = (cursor_line, 0)
                self.vim_command_mode = False
                self.vim_status = "INSERT"
                event.prevent_default()
                return
            elif event.key == "h":
                # Move left
                if self.cursor_position > 0:
                    self.cursor_position -= 1
                event.prevent_default()
                return
            elif event.key == "l":
                # Move right
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
                event.prevent_default()
                return
            elif event.key == "j":
                # Move down
                self.action_cursor_down()
                event.prevent_default()
                return
            elif event.key == "k":
                # Move up
                self.action_cursor_up()
                event.prevent_default()
                return
            elif event.key == "w":
                # Move to next word
                self.action_cursor_word_right()
                event.prevent_default()
                return
            elif event.key == "b":
                # Move to previous word
                self.action_cursor_word_left()
                event.prevent_default()
                return
            elif event.key == "x":
                # Delete character under cursor
                if self.cursor_position < len(self.text):
                    self.delete(1)
                event.prevent_default()
                return
            elif event.key == "d":
                # Start delete command (simplified - just delete current line)
                self.action_delete_line()
                event.prevent_default()
                return
            elif event.key == "u":
                # Undo
                self.action_undo()
                event.prevent_default()
                return
            elif event.key == "ctrl+r":
                # Redo
                self.action_redo()
                event.prevent_default()
                return
            elif event.key == "shift+g":
                # Go to end of file
                self.cursor_position = len(self.text)
                event.prevent_default()
                return
            elif event.key == "g":
                # Go to beginning of file (simplified gg)
                self.cursor_position = 0
                event.prevent_default()
                return
            elif event.key == "0":
                # Go to beginning of line
                self.action_cursor_line_start()
                event.prevent_default()
                return
            elif event.key == "shift+4":  # $
                # Go to end of line
                self.action_cursor_line_end()
                event.prevent_default()
                return
            else:
                # In command mode, don't allow regular text input
                event.prevent_default()
                return

        # Insert mode - allow normal editing
        await super()._on_key(event)


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


class FormatMenuScreen(ModalScreen):
    """Modal screen for markdown formatting options."""

    def compose(self) -> ComposeResult:
        with Container(id="format-menu-dialog"):
            yield Label("Format Selected Text", id="format-menu-title")
            yield OptionList(
                Option("Heading 1", id="h1"),
                Option("Heading 2", id="h2"),
                Option("Heading 3", id="h3"),
                Option("Heading 4", id="h4"),
                Option("Heading 5", id="h5"),
                Option("Heading 6", id="h6"),
                Option("Bold", id="bold"),
                Option("Italic", id="italic"),
                Option("Bold Italic", id="bold_italic"),
                Option("Strikethrough", id="strikethrough"),
                Option("Inline Code", id="code"),
                Option("Code Block", id="code_block"),
                Option("Blockquote", id="blockquote"),
                Option("Unordered List", id="ul"),
                Option("Ordered List", id="ol"),
                Option("Link", id="link"),
                Option("Image", id="image"),
                Option("Table", id="table"),
                Option("Horizontal Rule", id="hr"),
                id="format-options",
            )
            with Horizontal(id="format-menu-buttons"):
                yield Button("Apply", variant="primary", id="apply-format-button")
                yield Button("Cancel", variant="default", id="cancel-format-button")

    @on(Button.Pressed, "#apply-format-button")
    def apply_format(self) -> None:
        format_options = self.query_one("#format-options", OptionList)
        if format_options.highlighted is not None:
            selected_option = format_options.get_option_at_index(
                format_options.highlighted
            )
            self.dismiss(selected_option.id)
        else:
            self.dismiss(None)

    @on(Button.Pressed, "#cancel-format-button")
    def cancel_format(self) -> None:
        self.dismiss(None)

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)


class SaveAsScreen(ModalScreen):
    """Modal screen for Save As dialog."""

    def __init__(self, current_path: Optional[Path] = None):
        super().__init__()
        self.current_path = current_path

    def compose(self) -> ComposeResult:
        with Container(id="save-as-dialog"):
            yield Label("Save As", id="save-as-title")
            yield Input(
                placeholder="Enter filename...",
                value=str(self.current_path) if self.current_path else "",
                id="filename-input",
            )
            with Horizontal(id="save-as-buttons"):
                yield Button("Save", variant="primary", id="save-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    @on(Button.Pressed, "#save-button")
    def save_file(self) -> None:
        filename_input = self.query_one("#filename-input", Input)
        filename = filename_input.value.strip()
        if filename:
            self.dismiss(Path(filename))
        else:
            filename_input.focus()

    @on(Button.Pressed, "#cancel-button")
    def cancel_save(self) -> None:
        self.dismiss(None)

    @on(Input.Submitted, "#filename-input")
    def on_filename_submitted(self) -> None:
        self.save_file()


class MarkdownEditor(App):
    """A markdown editor with file tree and live preview."""

    CSS = """
    #format-menu-dialog {
        width: 50;
        height: 25;
        background: $surface;
        border: thick $primary;
        padding: 1;
        margin: 2 4;
        offset: 50% 50%;
        content-align: center middle;
    }
    
    #format-menu-title {
        dock: top;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #format-options {
        dock: top;
        height: 18;
        margin-bottom: 1;
    }
    
    #format-menu-buttons {
        dock: bottom;
        height: 3;
        align: center middle;
    }
    
    #format-menu-buttons Button {
        margin: 0 1;
    }
    
    #save-as-dialog {
        width: 60;
        height: 9;
        background: $surface;
        border: thick $primary;
        padding: 1;
        margin: 2 4;
        offset: 50% 50%;
        content-align: center middle;
    }
    
    #save-as-title {
        dock: top;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #filename-input {
        dock: top;
        margin-bottom: 1;
    }
    
    #save-as-buttons {
        dock: bottom;
        height: 3;
        align: center middle;
    }
    
    #save-as-buttons Button {
        margin: 0 1;
    }
    
    .container {
        height: 100%;
    }
    
    #file-tree {
        dock: left;
        width: 35;
        border-right: solid $primary;
    }
    
    #editor-container {
        height: 100%;
    }
    
    #text-editor {
        height: 100%;
        border: solid $primary;
        margin: 0 1;
    }
    
    #preview-container {
        height: 100%;
        border: solid $accent;
        margin: 0 1;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "new_file", "New", priority=True),
        Binding("ctrl+o", "open_file", "Open", priority=True),
        Binding("ctrl+s", "save_file", "Save", priority=True),
        Binding("ctrl+shift+s", "save_as", "Save As", priority=True),
        Binding("ctrl+p", "toggle_preview", "Toggle Preview", priority=True),
        Binding("ctrl+f", "format_text", "Format", priority=True),
        Binding("ctrl+v", "toggle_vim", "Toggle Vim", priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("f1", "toggle_file_tree", "Toggle Tree", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.current_file: Optional[Path] = None
        self.is_modified = False
        self.preview_mode = False  # Changed from show_preview
        self.show_file_tree = True
        self.current_directory = Path.cwd()
        self.editor_content = ""  # Store content when in preview mode
        self.vim_mode = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="container"):
            yield CustomDirectoryTree(str(self.current_directory), id="file-tree")
            with Vertical(id="editor-container"):
                yield VimTextArea(
                    text="# Welcome to Markdown Editor\n\nStart typing your markdown content here...",
                    language="markdown",
                    id="text-editor",
                    show_line_numbers=True,
                )
                yield ScrollableContainer(
                    Static("", id="preview-content"),
                    id="preview-container",
                    classes="hidden",
                )
        yield Static("Ready", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the editor."""
        self.title = "Markdown Editor"
        self.sub_title = "Untitled"
        self.update_status(
            "Ready - Press F1 to toggle file tree, Ctrl+P to toggle preview, Ctrl+V for vim mode"
        )

    @on(DirectoryChanged)
    def on_directory_changed(self, event: DirectoryChanged) -> None:
        """Handle directory navigation."""
        self.current_directory = event.path
        self.update_status(f"Navigated to: {self.current_directory}")

    @on(FileSelected)
    def on_file_selected(self, event: FileSelected) -> None:
        """Handle file selection from the custom directory tree."""
        file_path = event.path

        # Only open markdown files and text files
        if file_path.suffix.lower() in [".md", ".markdown", ".txt", ".text"]:
            self.open_file_path(file_path)
        else:
            self.update_status(f"Cannot open {file_path.suffix} files")

    def update_status(self, message: str) -> None:
        """Update the status bar."""
        status_bar = self.query_one("#status-bar", Static)
        vim_status = ""
        if self.vim_mode:
            text_editor = self.query_one("#text-editor", VimTextArea)
            vim_status = (
                f" [{text_editor.vim_status}]" if text_editor.vim_status else " [VIM]"
            )
        status_bar.update(f"{message}{vim_status}")

    def update_title(self) -> None:
        """Update the window title based on current file."""
        if self.current_file:
            filename = self.current_file.name
            self.sub_title = f"{'*' if self.is_modified else ''}{filename}"
        else:
            self.sub_title = f"{'*' if self.is_modified else ''}Untitled"

    @on(TextArea.Changed, "#text-editor")
    def on_text_changed(self, event: TextArea.Changed) -> None:
        """Handle text changes in the editor."""
        if not self.preview_mode:  # Only mark as modified if in edit mode
            self.is_modified = True
            self.update_title()

        # Update vim mode status display
        if self.vim_mode:
            text_editor = self.query_one("#text-editor", VimTextArea)
            self.update_status("Text changed")

    def update_preview(self) -> None:
        """Update the markdown preview."""
        text_editor = self.query_one("#text-editor", TextArea)
        preview_content = self.query_one("#preview-content", Static)

        markdown_text = text_editor.text
        if markdown_text.strip():
            rendered = Markdown(markdown_text)
            preview_content.update(rendered)
        else:
            preview_content.update("Preview will appear here...")

    def toggle_preview_mode(self) -> None:
        """Toggle between edit and preview modes."""
        text_editor = self.query_one("#text-editor", VimTextArea)
        preview_container = self.query_one("#preview-container", ScrollableContainer)

        if self.preview_mode:
            # Switch to edit mode
            text_editor.remove_class("hidden")
            preview_container.add_class("hidden")
            # Restore the editor content
            text_editor.text = self.editor_content
            text_editor.focus()
            self.preview_mode = False
            self.update_status("Edit mode - Press Ctrl+P to preview")
        else:
            # Switch to preview mode
            self.editor_content = text_editor.text  # Store current content
            text_editor.add_class("hidden")
            preview_container.remove_class("hidden")
            self.update_preview()
            self.preview_mode = True
            self.update_status("Preview mode - Press Ctrl+P to edit")

    @on(DirectoryTree.FileSelected)
    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection from the standard directory tree (fallback)."""
        # This is kept for compatibility but won't be used with CustomDirectoryTree
        pass

    def open_file_path(self, file_path: Path) -> None:
        """Open a file in the editor."""
        try:
            content = file_path.read_text(encoding="utf-8")
            text_editor = self.query_one("#text-editor", VimTextArea)
            text_editor.text = content

            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.update_status(f"Opened: {file_path}")

        except Exception as e:
            self.update_status(f"Error opening file: {e}")

    def save_current_file(self) -> bool:
        """Save the current file. Returns True if saved successfully."""
        if not self.current_file:
            return False

        try:
            text_editor = self.query_one("#text-editor", VimTextArea)
            self.current_file.write_text(text_editor.text, encoding="utf-8")
            self.is_modified = False
            self.update_title()
            self.update_status(f"Saved: {self.current_file}")
            return True
        except Exception as e:
            self.update_status(f"Error saving file: {e}")
            return False

    def save_file_as(self, file_path: Path) -> bool:
        """Save the current content to a new file."""
        try:
            text_editor = self.query_one("#text-editor", VimTextArea)
            file_path.write_text(text_editor.text, encoding="utf-8")
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.update_status(f"Saved as: {file_path}")

            # Refresh the directory tree
            file_tree = self.query_one("#file-tree", CustomDirectoryTree)
            file_tree.refresh_tree()

            return True
        except Exception as e:
            self.update_status(f"Error saving file: {e}")
            return False

    def action_new_file(self) -> None:
        """Create a new file."""
        text_editor = self.query_one("#text-editor", VimTextArea)
        text_editor.text = "# New Document\n\n"
        self.current_file = None
        self.is_modified = True
        self.update_title()
        self.update_status("New file created")

    def action_open_file(self) -> None:
        """Open file dialog (simplified - uses file tree selection)."""
        self.update_status("Select a file from the file tree to open")

    def action_save_file(self) -> None:
        """Save the current file."""
        if self.current_file:
            self.save_current_file()
        else:
            self.action_save_as()

    def action_save_as(self) -> None:
        """Show save as dialog."""

        def handle_save_as(result: Optional[Path]) -> None:
            if result:
                self.save_file_as(result)

        self.push_screen(SaveAsScreen(self.current_file), handle_save_as)

    def action_toggle_preview(self) -> None:
        """Toggle between edit and preview modes."""
        self.toggle_preview_mode()

    def format_text(self, format_type: str, selected_text: str) -> str:
        """Apply markdown formatting to selected text."""
        if not selected_text:
            selected_text = "text"

        if format_type == "h1":
            return f"# {selected_text}"
        elif format_type == "h2":
            return f"## {selected_text}"
        elif format_type == "h3":
            return f"### {selected_text}"
        elif format_type == "h4":
            return f"#### {selected_text}"
        elif format_type == "h5":
            return f"##### {selected_text}"
        elif format_type == "h6":
            return f"###### {selected_text}"
        elif format_type == "bold":
            return f"**{selected_text}**"
        elif format_type == "italic":
            return f"*{selected_text}*"
        elif format_type == "bold_italic":
            return f"***{selected_text}***"
        elif format_type == "strikethrough":
            return f"~~{selected_text}~~"
        elif format_type == "code":
            return f"`{selected_text}`"
        elif format_type == "code_block":
            return f"```\n{selected_text}\n```"
        elif format_type == "blockquote":
            lines = selected_text.split("\n")
            return "\n".join(f"> {line}" for line in lines)
        elif format_type == "ul":
            lines = selected_text.split("\n")
            return "\n".join(f"- {line}" for line in lines)
        elif format_type == "ol":
            lines = selected_text.split("\n")
            return "\n".join(f"{i + 1}. {line}" for i, line in enumerate(lines))
        elif format_type == "link":
            return f"[{selected_text}](url)"
        elif format_type == "image":
            return f"![{selected_text}](image_url)"
        elif format_type == "table":
            return f"| {selected_text} | Column 2 |\n|----------|----------|\n| Row 1    | Data     |\n| Row 2    | Data     |"
        elif format_type == "hr":
            return "---"
        else:
            return selected_text

    def action_format_text(self) -> None:
        """Show the format menu."""

        def handle_format(format_type: Optional[str]) -> None:
            if format_type:
                text_editor = self.query_one("#text-editor", VimTextArea)

                # Get selected text or current word
                selection = text_editor.selected_text
                if not selection:
                    # If no selection, get current word or use placeholder
                    cursor_pos = text_editor.cursor_position
                    text = text_editor.text
                    # Simple word extraction (could be improved)
                    start = cursor_pos
                    end = cursor_pos
                    while start > 0 and text[start - 1].isalnum():
                        start -= 1
                    while end < len(text) and text[end].isalnum():
                        end += 1
                    selection = text[start:end] if start < end else ""

                formatted_text = self.format_text(format_type, selection)

                if text_editor.selected_text:
                    # Replace selected text
                    text_editor.replace(
                        formatted_text,
                        text_editor.selection.start,
                        text_editor.selection.end,
                    )
                else:
                    # Insert at cursor position
                    text_editor.insert(formatted_text)

                self.is_modified = True
                self.update_title()
                self.update_status(f"Applied {format_type} formatting")

        self.push_screen(FormatMenuScreen(), handle_format)

    def action_go_up_directory(self) -> None:
        """Navigate to parent directory."""
        parent = self.current_directory.parent
        if parent != self.current_directory:  # Prevent going above root
            self.current_directory = parent
            file_tree = self.query_one("#file-tree", DirectoryTree)
            file_tree.path = str(self.current_directory)
            file_tree.reload()
            self.update_status(f"Navigated to: {self.current_directory}")
        else:
            self.update_status("Already at root directory")

    def action_toggle_file_tree(self) -> None:
        """Toggle the file tree visibility."""
        self.show_file_tree = not self.show_file_tree
        file_tree = self.query_one("#file-tree", CustomDirectoryTree)

        if self.show_file_tree:
            file_tree.remove_class("hidden")
            self.update_status("File tree shown")
        else:
            file_tree.add_class("hidden")
            self.update_status("File tree hidden")

    def action_quit(self) -> None:
        """Quit the application."""
        if self.is_modified:
            # In a real app, you'd want to show a confirmation dialog
            self.update_status("Warning: Unsaved changes will be lost!")
        self.exit()


def main():
    """Run the markdown editor."""
    app = MarkdownEditor()
    app.run()


if __name__ == "__main__":
    main()
