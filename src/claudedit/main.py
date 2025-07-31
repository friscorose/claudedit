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
    """TextArea with comprehensive vim keybindings support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vim_mode = "INSERT"  # INSERT, NORMAL, VISUAL
        self._update_vim_status()

    def _update_vim_status(self):
        """Update vim status and notify parent."""
        self.vim_status = self.vim_mode
        # Update border subtitle to show current mode
        mode_colors = {
            "INSERT": "green",
            "NORMAL": "blue", 
            "VISUAL": "yellow"
        }
        self.border_subtitle = f"[{mode_colors.get(self.vim_mode, 'white')}]{self.vim_mode}[/]"

    def _enter_insert_mode(self):
        """Enter INSERT mode."""
        self.vim_mode = "INSERT"
        self._update_vim_status()

    def _enter_normal_mode(self):
        """Enter NORMAL mode."""
        self.vim_mode = "NORMAL"
        # Clear any selection when entering normal mode
        if self.selection.start != self.selection.end:
            self.selection = self.selection.start
        self._update_vim_status()

    def _enter_visual_mode(self):
        """Enter VISUAL mode."""
        self.vim_mode = "VISUAL"
        self._update_vim_status()

    def _get_selected_text(self) -> str:
        """Get currently selected text."""
        if self.selection.start != self.selection.end:
            return self.selected_text
        return ""

    def _replace_selection(self, new_text: str):
        """Replace selected text with new text."""
        if self.selection.start != self.selection.end:
            self.replace(new_text, self.selection.start, self.selection.end)

    def _format_markdown(self, format_type: str, text: str) -> str:
        """Apply markdown formatting to text."""
        if not text:
            text = "text"

        formatters = {
            "b": lambda t: f"**{t}**",  # Bold
            "i": lambda t: f"*{t}*",   # Italic  
            "s": lambda t: f"~~{t}~~", # Strikethrough
            "c": lambda t: f"`{t}`",   # Code
            "C": lambda t: f"```\n{t}\n```", # Code block
            "1": lambda t: f"# {t}",   # Header 1
            "2": lambda t: f"## {t}",  # Header 2
            "3": lambda t: f"### {t}", # Header 3  
            "4": lambda t: f"#### {t}", # Header 4
            "5": lambda t: f"##### {t}", # Header 5
            "6": lambda t: f"###### {t}", # Header 6
            "l": lambda t: f"- {t}",   # Unordered list
            "L": lambda t: f"1. {t}",  # Ordered list  
            "q": lambda t: f"> {t}",   # Blockquote
            "u": lambda t: f"[{t}](url)", # URL/Link
            "r": lambda t: f"[{t}][ref]", # Reference link
            "t": lambda t: f"| {t} |", # Table cell
        }
        
        formatter = formatters.get(format_type)
        return formatter(text) if formatter else text

    def _handle_visual_mode_formatting(self, key: str) -> bool:
        """Handle markdown formatting in visual mode."""
        selected_text = self._get_selected_text()
        if not selected_text:
            return False
            
        # Check if key is a formatting key
        format_keys = ["b", "i", "s", "c", "C", "1", "2", "3", "4", "5", "6", "l", "L", "q", "u", "r", "t"]
        
        if key in format_keys:
            formatted_text = self._format_markdown(key, selected_text)
            self._replace_selection(formatted_text)
            self._enter_normal_mode()
            return True
            
        return False

    def on_key(self, event: events.Key) -> None:
        """Handle vim keybindings."""
        
        # Check if we have a selection and should enter VISUAL mode
        if (self.selection.start != self.selection.end and 
            self.vim_mode != "VISUAL" and 
            event.key not in ["escape"]):
            self._enter_visual_mode()

        # Handle Escape key - always goes to NORMAL mode
        if event.key == "escape":
            self._enter_normal_mode()
            event.prevent_default()
            return

        # VISUAL mode handling
        if self.vim_mode == "VISUAL":
            # Try markdown formatting first
            if self._handle_visual_mode_formatting(event.key):
                event.prevent_default()
                return
                
            # Handle visual mode navigation (extends selection)
            if event.key in ["h", "j", "k", "l", "w", "b", "0", "shift+4"]:
                # Let normal cursor movement handle selection extension
                return
            
            # Other keys exit visual mode
            if event.key not in ["shift", "ctrl", "alt"]:
                self._enter_normal_mode()
                # Don't prevent default, let the key be processed

        # NORMAL mode handling  
        elif self.vim_mode == "NORMAL":
            handled = True
            
            if event.key == "i":
                # Enter insert mode at cursor
                self._enter_insert_mode()
                
            elif event.key == "a":
                # Enter insert mode after cursor
                row, col = self.cursor_location
                line = self.get_line(row)
                if col < len(line.plain):
                    self.cursor_location = (row, col + 1)
                self._enter_insert_mode()
                
            elif event.key == "o":
                # Open new line below and enter insert mode
                row, col = self.cursor_location
                line = self.get_line(row)
                self.cursor_location = (row, len(line.plain))
                self.insert("\n")
                self._enter_insert_mode()
                
            elif event.key == "shift+o":
                # Open new line above and enter insert mode
                row, col = self.cursor_location
                self.cursor_location = (row, 0)
                self.insert("\n")
                self.cursor_location = (row, 0)
                self._enter_insert_mode()
                
            elif event.key == "shift+a":
                # Enter insert mode at end of line
                self.action_cursor_line_end()
                self._enter_insert_mode()
                
            elif event.key == "shift+i":
                # Enter insert mode at beginning of line
                self.action_cursor_line_start()
                self._enter_insert_mode()
                
            elif event.key == "v":
                # Enter visual mode and start selection
                self._enter_visual_mode()
                # Start selection at current cursor position
                self.selection = self.cursor_location
                
            elif event.key == "h":
                # Move left
                row, col = self.cursor_location
                if col > 0:
                    self.cursor_location = (row, col - 1)
                elif row > 0:
                    prev_line = self.get_line(row - 1)
                    self.cursor_location = (row - 1, len(prev_line.plain))
                    
            elif event.key == "l":
                # Move right  
                row, col = self.cursor_location
                line = self.get_line(row)
                if col < len(line.plain):
                    self.cursor_location = (row, col + 1)
                elif row < self.document.line_count - 1:
                    self.cursor_location = (row + 1, 0)
                    
            elif event.key == "j":
                # Move down
                self.action_cursor_down()
                
            elif event.key == "k":
                # Move up
                self.action_cursor_up()
                
            elif event.key == "w":
                # Move to next word
                self.action_cursor_word_right()
                
            elif event.key == "b":
                # Move to previous word (in normal mode)
                self.action_cursor_word_left()
                
            elif event.key == "x":
                # Delete character under cursor
                row, col = self.cursor_location
                line = self.get_line(row)
                if col < len(line.plain):
                    end_pos = (row, col + 1)
                    self.delete((row, col), end_pos)
                    
            elif event.key == "d":
                # Delete current line (simplified dd)
                self.action_delete_line()
                
            elif event.key == "u":
                # Undo
                self.action_undo()
                
            elif event.key == "ctrl+r":
                # Redo
                self.action_redo()
                
            elif event.key == "shift+g":
                # Go to end of file
                last_line = self.document.line_count - 1
                if last_line >= 0:
                    last_line_text = self.get_line(last_line)
                    self.cursor_location = (last_line, len(last_line_text.plain))
                    
            elif event.key == "g":
                # Go to beginning of file (simplified gg)
                self.cursor_location = (0, 0)
                
            elif event.key == "0":
                # Go to beginning of line
                self.action_cursor_line_start()
                
            elif event.key == "shift+4":  # $
                # Go to end of line
                self.action_cursor_line_end()
                
            else:
                handled = False

            if handled:
                event.prevent_default()
                return

        # INSERT mode - let normal text input happen, but handle special keys
        elif self.vim_mode == "INSERT":
            # In insert mode, most keys should work normally
            # Only handle special vim keys
            if event.key in ["ctrl+c"]:  # Alternative escape
                self._enter_normal_mode()
                event.prevent_default()
                return

        # If we reach here and we're in NORMAL mode, prevent default to avoid text input
        if self.vim_mode == "NORMAL":
            event.prevent_default()


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
        """Open a file in the editor."""
        try:
            content = file_path.read_text(encoding="utf-8")
            text_editor = self.query_one("#text-editor", VimTextArea)
            text_editor.text = content

            self.current_file = file_path
            self.is_modified = False
            self.update_title()

        except Exception as e:
            pass  # Could add error handling here

    def save_current_file(self) -> bool:
        """Save the current file. Returns True if saved successfully."""
        if not self.current_file:
            return False

        try:
            text_editor = self.query_one("#text-editor", VimTextArea)
            self.current_file.write_text(text_editor.text, encoding="utf-8")
            self.is_modified = False
            self.update_title()
            return True
        except Exception as e:
            return False

    def save_file_as(self, file_path: Path) -> bool:
        """Save the current content to a new file."""
        try:
            text_editor = self.query_one("#text-editor", VimTextArea)
            file_path.write_text(text_editor.text, encoding="utf-8")
            self.current_file = file_path
            self.is_modified = False
            self.update_title()

            # Refresh the directory tree
            file_tree = self.query_one("#file-tree", CustomDirectoryTree)
            file_tree.refresh_tree()

            return True
        except Exception as e:
            return False

    def action_new_file(self) -> None:
        """Create a new file."""
        text_editor = self.query_one("#text-editor", VimTextArea)
        text_editor.text = "# New Document\n\n"
        text_editor._enter_insert_mode()  # Start in insert mode
        self.current_file = None
        self.is_modified = True
        self.update_title()

    def action_open_file(self) -> None:
        """Open file dialog (uses file tree selection)."""
        pass

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

        formatters = {
            "h1": lambda t: f"# {t}",
            "h2": lambda t: f"## {t}",
            "h3": lambda t: f"### {t}",
            "h4": lambda t: f"#### {t}",
            "h5": lambda t: f"##### {t}",
            "h6": lambda t: f"###### {t}",
            "bold": lambda t: f"**{t}**",
            "italic": lambda t: f"*{t}*",
            "bold_italic": lambda t: f"***{t}***",
            "strikethrough": lambda t: f"~~{t}~~",
            "code": lambda t: f"`{t}`",
            "code_block": lambda t: f"```\n{t}\n```",
            "blockquote": lambda t: "\n".join(f"> {line}" for line in t.split("\n")),
            "ul": lambda t: "\n".join(f"- {line}" for line in t.split("\n")),
            "ol": lambda t: "\n".join(f"{i + 1}. {line}" for i, line in enumerate(t.split("\n"))),
            "link": lambda t: f"[{t}](url)",
            "image": lambda t: f"![{t}](image_url)",
            "table": lambda t: f"| {t} | Column 2 |\n|----------|----------|\n| Row 1    | Data     |\n| Row 2    | Data     |",
            "hr": lambda t: "---"
        }
        
        formatter = formatters.get(format_type)
        return formatter(selected_text) if formatter else selected_text

    def action_format_text(self) -> None:
        """Show the format menu."""
        def handle_format(format_type: Optional[str]) -> None:
            if format_type:
                text_editor = self.query_one("#text-editor", VimTextArea)
                selection = text_editor.selected_text
                
                if not selection:
                    # Get current word if no selection
                    cursor_pos = text_editor.cursor_location
                    text = text_editor.text
                    # Simple word extraction
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

        self.push_screen(FormatMenuScreen(), handle_format)

    def action_toggle_file_tree(self) -> None:
        """Toggle the file tree visibility."""
        self.show_file_tree = not self.show_file_tree
        file_tree = self.query_one("#file-tree", CustomDirectoryTree)

        if self.show_file_tree:
            file_tree.remove_class("hidden")
        else:
            file_tree.add_class("hidden")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def main():
    """Run the markdown editor."""
    app = MarkdownEditor()
    app.run()


if __name__ == "__main__":
    main()
