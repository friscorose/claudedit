"""
Markdown formatting utilities.
"""


class MarkdownFormatter:
    """Utility class for applying markdown formatting to text."""

    @staticmethod
    def format_text(format_type: str, selected_text: str) -> str:
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

    @staticmethod
    def get_current_word(text: str, cursor_pos: int) -> tuple[str, int, int]:
        """Extract the current word at cursor position."""
        start = cursor_pos
        end = cursor_pos
        
        # Find word boundaries
        while start > 0 and text[start - 1].isalnum():
            start -= 1
        while end < len(text) and text[end].isalnum():
            end += 1
            
        word = text[start:end] if start < end else ""
        return word, start, end
