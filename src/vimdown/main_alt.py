#!/usr/bin/env python3
"""
A full-featured markdown editor built with Textual.
Features:
- File tree navigation
- Syntax-highlighted markdown editing with vim modes
- Live markdown preview
- File operations (new, open, save, save as)
- Keyboard shortcuts
- Enhanced Vim mode with INSERT/NORMAL/VISUAL modes
- Visual mode markdown formatting with intuitive key bindings
"""

from pathlib import Path
from typing import Optional

from rich.markdown import Markdown
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Footer, Header, Static, TextArea

from vim_modes import VimTextArea
from file_tree import CustomDirectoryTree, DirectoryChanged, FileSelected
from modal_dialogs import FormatMenuScreen, SaveAsScreen
from markdown_formatter import MarkdownFormatter


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
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+t", "toggle_file_tree", "Toggle Tree", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.current_file: Optional[Path] = None
        self.is_modified = False
        self.preview_mode = False
        self.show_file_tree = True
        self.current_directory = Path.cwd()
        self.editor_content = ""
        self.formatter = MarkdownFormatter()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="container"):
            yield CustomDirectoryTree(str(self.current_directory), id="file-tree")
            with Vertical(id="editor-container"):
                yield VimTextArea(
                    text="# Welcome to Vim Markdown Editor\n\nPress 'i' to enter INSERT mode and start typing.\nPress ESC to enter NORMAL mode.\nSelect text to enter VISUAL mode, then:\n- 'b' for **bold**\n- 'i' for *italic*\n- 's' for ~~strikethrough~~\n- 'c' for `code`\n- '1-6' for headers\n- 'l' for lists\n- And many more!\n\nStart typing your markdown content here...",
                    language="markdown",
                    id="text-editor",
                    show_line_numbers=True,
                )
                yield ScrollableContainer(
                    Static("", id="preview-content"),
                    id="preview-container",
                    classes="hidden",
                )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the editor."""
        self.title = "Vim Markdown Editor"
        self.sub_title = "Untitled"
        # Start with editor focused in INSERT mode
        text_editor = self.query_one("#text-editor", VimTextArea)
        text_editor.focus()

    @on(DirectoryChanged)
    def on_directory_changed(self, event: DirectoryChanged) -> None:
        """Handle directory navigation."""
        self.current_directory = event.path

    @on(FileSelected)
    def on_file_selected(self, event: FileSelected) -> None:
        """Handle file selection from the custom directory tree."""
        file_path = event.path

        # Only open markdown files and text files
        if file_path.suffix.lower() in [".md", ".markdown", ".txt", ".text"]:
            self.open_file_path(file_path)

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
        if not self.preview_mode:
            self.is_modified = True
            self.update_title()

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
            text_editor.text = self.editor_content
            text_editor.focus()
            self.preview_mode = False
        else:
            # Switch to preview mode
            self.editor_content = text_editor.text
            text_editor.add_class("hidden")
            preview_container.remove_class("hidden")
            self.update_preview()
            self.preview_mode = True

    def open_file_path(self, file_path: Path) -> None:
        """Open a file in the editor"""
