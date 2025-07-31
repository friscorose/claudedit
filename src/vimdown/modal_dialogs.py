"""
Modal dialog screens for the markdown editor.
"""

from pathlib import Path
from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, OptionList, Static
from textual.widgets.option_list import Option
from textual.screen import ModalScreen


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
