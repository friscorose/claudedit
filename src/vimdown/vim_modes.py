"""
Vim mode handling and markdown formatting for the TextArea widget.
"""

from textual import events
from textual.widgets import TextArea


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

    def _handle_normal_mode_commands(self, event: events.Key) -> bool:
        """Handle normal mode vim commands."""
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

        return handled

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
            if self._handle_normal_mode_commands(event):
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
