# Markdown Editor User Manual

A full-featured terminal-based markdown editor built with Textual, featuring file management, live preview, vim keybindings, and comprehensive formatting tools.

## Installation & Setup

### Option 1: Direct Installation with uvx (Recommended)
```bash
# Install and run directly without cloning
uvx --from git+https://github.com/friscorose/claudedit.git claudedit
```

### Option 2: Development Setup with uv
```bash
# Clone repository and set up development environment
git clone https://github.com/friscorose/claudedit.git
cd claudedit
uv sync
uv run claudedit
```

### Option 3: Global Installation
```bash
# Install globally for system-wide access
git clone https://github.com/friscorose/claudedit.git
cd claudedit
uv tool install .
claudedit  # Now available as a command
```

### Dependencies
The project uses `uv` for dependency management. Required packages are automatically installed:
- `textual` - Terminal UI framework
- `rich` - Rich text rendering

## Interface Overview

The editor consists of four main areas:
- **Header**: Application title and current file name (shows `*` for unsaved changes)
- **File Tree**: Directory navigation with custom tree widget (left panel)
- **Editor/Preview**: Main editing area with toggle between edit and preview modes
- **Status Bar**: Current status, vim mode indicator, and context messages
- **Footer**: Available keyboard shortcuts

## File Operations

### Basic File Management
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New File | Create a new markdown document with default content |
| `Ctrl+S` | Save | Save current file (prompts Save As if no filename) |
| `Ctrl+Shift+S` | Save As | Save with new filename via modal dialog |
| `Ctrl+O` | Open | Shows instruction to use file tree (no file dialog) |
| `Ctrl+Q` | Quit | Exit application (warns about unsaved changes) |

### File Tree Navigation
- **Click files**: Open `.md`, `.markdown`, `.txt`, `.text` files directly
- **Click directories**: Navigate into folders
- **Click ".."**: Navigate to parent directory (when not at filesystem root)
- **Icons**: 📁 directories, 📝 markdown files, 📄 text files
- **Toggle**: Press `F1` to show/hide entire file tree panel
- **Auto-refresh**: Tree updates automatically after save operations

## Editing Features

### Preview Mode Toggle
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+P` | Toggle Preview | Switch between edit and preview modes |

**Edit Mode**: 
- Syntax-highlighted markdown editing with line numbers
- Full text editing capabilities
- File modification tracking

**Preview Mode**: 
- Rendered markdown view in the same space as editor
- Rich markdown rendering with proper formatting
- Replaces editor view completely (not side-by-side)

### Text Formatting Menu
Press `Ctrl+F` to open the formatting menu with these options:

#### Headings
- **Heading 1-6**: Converts text to `# ## ### #### ##### ######` format

#### Text Styling  
- **Bold**: Wraps text in `**text**`
- **Italic**: Wraps text in `*text*`
- **Bold Italic**: Wraps text in `***text***`
- **Strikethrough**: Wraps text in `~~text~~`

#### Code Formatting
- **Inline Code**: Wraps text in `` `code` ``
- **Code Block**: Creates fenced code block:
  ```
  ```
  code block
  ```
  ```

#### Lists and Structure
- **Unordered List**: Converts lines to `- item` format
- **Ordered List**: Converts lines to `1. item` format (auto-numbered)
- **Blockquote**: Prefixes lines with `> quoted text`

#### Links and Media
- **Link**: Creates `[text](url)` format
- **Image**: Creates `![alt text](image_url)` format
- **Horizontal Rule**: Inserts `---`

#### Tables
- **Table**: Creates basic table structure with headers and sample data

### Formatting Behavior
- **Selected text**: Applies formatting to selection
- **No selection**: Uses current word under cursor or placeholder text
- **Multi-line selections**: Processes each line individually for list/quote formats

## Vim Keybindings

### Toggle Vim Mode
| Shortcut | Action |
|----------|--------|
| `Ctrl+V` | Enable/disable vim keybindings |

### Vim Modes
- **INSERT**: Normal text editing (default when vim enabled)
- **NORMAL**: Command mode for navigation and operations
- **Status Display**: Current mode shown in status bar as `[INSERT]` or `[NORMAL]`

### Mode Switching
| Key | Action | Mode Change |
|-----|--------|-------------|
| `Esc` | Switch to NORMAL mode | Any → NORMAL |
| `i` | Enter INSERT mode at cursor | NORMAL → INSERT |
| `a` | Enter INSERT mode after cursor | NORMAL → INSERT |
| `o` | New line below + INSERT mode | NORMAL → INSERT |
| `O` | New line above + INSERT mode | NORMAL → INSERT |

### Navigation (NORMAL Mode Only)
| Key | Action |
|-----|--------|
| `h` | Move cursor left |
| `l` | Move cursor right |
| `j` | Move cursor down |
| `k` | Move cursor up |
| `w` | Move to next word |
| `b` | Move to previous word |
| `0` | Move to beginning of line |
| `$` | Move to end of line |
| `g` | Go to beginning of file |
| `G` | Go to end of file |

### Editing (NORMAL Mode Only)
| Key | Action |
|-----|--------|
| `x` | Delete character under cursor |
| `d` | Delete current line |
| `u` | Undo last change |
| `Ctrl+R` | Redo last undone change |

## Complete Keyboard Reference

### Global Shortcuts (Always Available)
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file instruction |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+P` | Toggle preview mode |
| `Ctrl+F` | Format menu |
| `Ctrl+V` | Toggle vim mode |
| `Ctrl+Q` | Quit application |
| `F1` | Toggle file tree visibility |

### Status Bar Information
The status bar displays:
- **Operation status**: Current action or instruction
- **Vim mode**: `[INSERT]` or `[NORMAL]` when vim mode is enabled
- **File status**: Navigation, save confirmations, error messages
- **Context help**: Helpful tips and current mode information

### Supported File Types
**Readable formats**:
- `.md` - Markdown files (primary)
- `.markdown` - Markdown files  
- `.txt` - Plain text files
- `.text` - Text files

**File tree behavior**: Only supported file types can be opened; others show error message.

## Workflow Guide

### Getting Started

#### Quick Start (uvx)
```bash
# Run directly without installation
uvx --from git+https://github.com/friscorose/claudedit.git claudedit
```

#### Development Workflow (uv)
```bash
# Set up development environment
git clone https://github.com/friscorose/claudedit.git
cd claudedit
uv sync                    # Install dependencies
uv run claudedit          # Run the application
```

#### Regular Usage
1. **Launch**: Run `claudedit` (if globally installed) or `uvx claudedit`
2. **Navigate**: Use file tree to browse to your project directory
3. **Open/Create**: Click files to open or use `Ctrl+N` for new documents
4. **Edit**: Type markdown with syntax highlighting
5. **Format**: Use `Ctrl+F` for quick formatting of selected text
6. **Preview**: Press `Ctrl+P` to see rendered markdown
7. **Save**: Use `Ctrl+S` to save regularly

### Vim Users
- **Enable**: Press `Ctrl+V` to toggle vim keybindings
- **Start mode**: Begins in INSERT mode for immediate typing
- **Switch modes**: Use `Esc` for NORMAL mode, `i/a/o/O` for INSERT
- **Navigation**: All basic vim movement keys work in NORMAL mode
- **Status**: Current vim mode always shown in status bar

### File Management Tips
- **Directory navigation**: Click folders or ".." to navigate
- **Tree visibility**: Use `F1` to hide/show tree for more editor space
- **Auto-refresh**: File tree updates after save operations
- **Unsaved changes**: Title shows `*` prefix for modified files

## Development & Customization

### Project Structure
```
claudedit/
├── pyproject.toml         # uv project configuration
├── uv.lock               # Locked dependencies
├── src/
│   └── claudedit/
│       ├── __init__.py
│       └── main.py       # Main application code
└── README.md
```

### Development Commands
```bash
# Install development dependencies
uv sync --dev

# Run tests (if available)
uv run pytest

# Run linting
uv run ruff check

# Format code
uv run ruff format

# Run the application in development
uv run claudedit

# Build for distribution
uv build
```

### Environment Management
```bash
# Show current environment
uv python list

# Use specific Python version
uv python install 3.12
uv sync --python 3.12

# Show dependency tree
uv tree

# Update dependencies
uv sync --upgrade
```

## Technical Details

### Preview Rendering
- **Engine**: Rich markdown renderer with full formatting support
- **Update**: Preview refreshes when switching from edit mode
- **Content**: Stored separately to preserve editor state
- **Mode switching**: Seamless toggle between edit and preview

### File Handling
- **Encoding**: UTF-8 for all file operations
- **Auto-detection**: Supported file types identified by extension
- **Error handling**: Graceful handling of permission/access errors
- **Path resolution**: Full path support with proper directory navigation

### Vim Implementation
- **Scope**: Core navigation and editing commands
- **Modes**: Proper INSERT/NORMAL mode separation
- **Key handling**: Event-based key processing with mode awareness
- **Status tracking**: Real-time mode display in status bar

## Troubleshooting

### Installation Issues
- **uv not found**: Install uv first: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git access**: Ensure you have git installed and repository access
- **Python version**: Requires Python 3.8+ (automatically managed by uv)

### Runtime Issues
- **Files not opening**: Ensure file has supported extension (.md, .txt, etc.)
- **Vim mode confusion**: Check status bar for current mode `[INSERT]` or `[NORMAL]`
- **Preview not updating**: Switch to edit mode and back to refresh
- **File tree missing**: Press `F1` to toggle visibility
- **Formatting not applied**: Ensure text is selected or cursor is on word

### Performance Notes
- **Large files**: May take time to load in preview mode
- **Real-time updates**: Preview renders only when switching modes
- **Memory usage**: Editor content stored separately during preview
- **Tree refresh**: Automatic after file operations

### Error Messages
- **"Cannot open X files"**: File type not supported
- **"Error opening file"**: Permission or file access issue  
- **"Error saving file"**: Write permission or disk space issue
- **"Warning: Unsaved changes"**: Displayed when quitting with modifications

## Project Configuration

### pyproject.toml Example
```toml
[project]
name = "claudedit"
version = "0.1.0"
description = "A full-featured terminal markdown editor"
dependencies = [
    "textual>=0.41.0",
    "rich>=13.0.0",
]

[project.scripts]
claudedit = "claudedit.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```

---

*Built with Textual framework for modern terminal user interfaces*  
*Managed with uv for fast, reliable Python project management*
