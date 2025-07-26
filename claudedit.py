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

import os
from pathlib import Path
from typing import Optional

from rich.markdown import Markdown
from rich.syntax import Syntax
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Static,
    TextArea,
    Label,
)
from textual.screen import ModalScreen


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
                id="filename-input"
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
        width: 30;
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
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("f1", "toggle_file_tree", "Toggle Tree", priority=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file: Optional[Path] = None
        self.is_modified = False
        self.show_preview = False
        self.show_file_tree = True
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="container"):
            yield DirectoryTree(str(Path.cwd()), id="file-tree")
            with Vertical(id="editor-container"):
                yield TextArea(
                    text="# Welcome to Markdown Editor\n\nStart typing your markdown content here...",
                    language="markdown",
                    id="text-editor",
                    show_line_numbers=True,
                )
                yield Container(
                    Static("", id="preview-content"),
                    id="preview-container",
                    classes="hidden"
                )
        yield Static("Ready", id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the editor."""
        self.title = "Markdown Editor"
        self.sub_title = "Untitled"
        self.update_status("Ready - Press F1 to toggle file tree, Ctrl+P for preview")
        
    def update_status(self, message: str) -> None:
        """Update the status bar."""
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(message)
        
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
        self.is_modified = True
        self.update_title()
        
        if self.show_preview:
            self.update_preview()
    
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
    
    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from the directory tree."""
        file_path = Path(event.path)
        
        # Only open markdown files and text files
        if file_path.suffix.lower() in ['.md', '.markdown', '.txt', '.text']:
            self.open_file_path(file_path)
        else:
            self.update_status(f"Cannot open {file_path.suffix} files")
    
    def open_file_path(self, file_path: Path) -> None:
        """Open a file in the editor."""
        try:
            content = file_path.read_text(encoding='utf-8')
            text_editor = self.query_one("#text-editor", TextArea)
            text_editor.text = content
            
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.update_status(f"Opened: {file_path}")
            
            if self.show_preview:
                self.update_preview()
                
        except Exception as e:
            self.update_status(f"Error opening file: {e}")
    
    def save_current_file(self) -> bool:
        """Save the current file. Returns True if saved successfully."""
        if not self.current_file:
            return False
            
        try:
            text_editor = self.query_one("#text-editor", TextArea)
            self.current_file.write_text(text_editor.text, encoding='utf-8')
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
            text_editor = self.query_one("#text-editor", TextArea)
            file_path.write_text(text_editor.text, encoding='utf-8')
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.update_status(f"Saved as: {file_path}")
            
            # Refresh the directory tree
            file_tree = self.query_one("#file-tree", DirectoryTree)
            file_tree.reload()
            
            return True
        except Exception as e:
            self.update_status(f"Error saving file: {e}")
            return False
    
    def action_new_file(self) -> None:
        """Create a new file."""
        text_editor = self.query_one("#text-editor", TextArea)
        text_editor.text = "# New Document\n\n"
        self.current_file = None
        self.is_modified = True
        self.update_title()
        self.update_status("New file created")
        
        if self.show_preview:
            self.update_preview()
    
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
        """Toggle the markdown preview pane."""
        self.show_preview = not self.show_preview
        
        text_editor = self.query_one("#text-editor", TextArea)
        preview_container = self.query_one("#preview-container", Container)
        
        if self.show_preview:
            preview_container.remove_class("hidden")
            text_editor.styles.height = "50%"
            self.update_preview()
            self.update_status("Preview enabled")
        else:
            preview_container.add_class("hidden")
            text_editor.styles.height = "100%"
            self.update_status("Preview disabled")
    
    def action_toggle_file_tree(self) -> None:
        """Toggle the file tree visibility."""
        self.show_file_tree = not self.show_file_tree
        file_tree = self.query_one("#file-tree", DirectoryTree)
        
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
