# The vimdown Markdown Editor User Manual

A full-featured terminal-based markdown editor built with Textual, featuring file management, live preview, comprehensive vim keybindings, and visual mode markdown formatting.

## Installation & Setup

### Option 1: Direct Installation with uvx (Recommended)
```bash
# Install and run directly without cloning
uvx --from git+https://github.com/friscorose/vimdown.git vimdown
```

### Option 2: Development Setup with uv
```bash
# Clone repository and set up development environment
git clone https://github.com/friscorose/vimdown.git
cd vimdown
uv sync
uv run vimdown
```

### Option 3: Global Installation
```bash
# Install globally for system-wide access
git clone https://github.com/friscorose/vimdown.git
cd vimdown
uv tool install .
vimdown  # Now available as a command
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
- **Status Bar**: Current vim mode indicator with color coding in editor border
- **Footer**: Available keyboard shortcuts

## File Operations

### Basic File Management
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New File | Create a new markdown document and enter INSERT mode |
| `Ctrl+S` | Save | Save current file (prompts Save As if no filename) |
| `Ctrl+Shift+S` | Save As | Save with new filename via modal dialog |
| `Ctrl+O` | Open | Shows instruction to use file tree (no file dialog) |
| `Ctrl+Q` | Quit | Exit application |

### File Tree Navigation
- **Click files**: Open `.md`, `.markdown`, `.txt`, `.text` files directly
- **Click directories**: Navigate into folders
- **Click ".."**: Navigate to parent directory (when not at filesystem root)
- **Icons**: 📁 directories, 📝 markdown files, 📄 text files
- **Toggle**: Press `Ctrl+T` to show/hide entire file tree panel
- **Auto-refresh**: Tree updates automatically after save operations

## Vim Mode System

### Vim Modes (Always Active)
The editor operates in one of three vim modes at all times:

- **INSERT**: Normal text editing (green indicator) - Default startup mode
- **NORMAL**: Command mode for navigation and operations (blue indicator)
- **VISUAL**: Text selection with markdown formatting (yellow indicator)

### Mode Display
Current mode is shown in the editor's border subtitle with color coding:
- `[INSERT]` in green
- `[NORMAL]` in blue  
- `[VISUAL]` in yellow

### Mode Switching
| Key | Action | Mode Change |
|-----|--------|-------------|
| `Esc` | Switch to NORMAL mode | Any → NORMAL |
| `i` | Enter INSERT mode at cursor | NORMAL → INSERT |
| `a` | Enter INSERT mode after cursor | NORMAL → INSERT |
| `A` | Enter INSERT mode at end of line | NORMAL → INSERT |
| `I` | Enter INSERT mode at beginning of line | NORMAL → INSERT |
| `o` | New line below + INSERT mode | NORMAL → INSERT |
| `O` | New line above + INSERT mode | NORMAL → INSERT |
| `v` | Enter VISUAL mode with selection | NORMAL → VISUAL |
| **Text Selection** | Auto-enter VISUAL mode | Any → VISUAL |

### Navigation (NORMAL Mode)
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
| `g` | Go to beginning of file (simplified gg) |
| `G` | Go to end of file |

### Editing (NORMAL Mode)
| Key | Action |
|-----|--------|
| `x` | Delete character under cursor |
| `d` | Delete current line (simplified dd) |
| `u` | Undo last change |
| `Ctrl+R` | Redo last undone change |

## Visual Mode Markdown Formatting

### Automatic Visual Mode
- **Mouse Selection**: Selecting text automatically enters VISUAL mode
- **Keyboard Selection**: Use `v` in NORMAL mode then move cursor to select
- **Selection Extension**: Movement keys extend selection in VISUAL mode

### Visual Mode Formatting Keys
When text is selected in VISUAL mode, use these intuitive keys for instant markdown formatting:

#### Text Styling
| Key | Result | Markdown |
|-----|--------|----------|
| `b` | **Bold text** | `**text**` |
| `i` | *Italic text* | `*text*` |
| `s` | ~~Strikethrough~~ | `~~text~~` |

#### Code Formatting
| Key | Result | Markdown |
|-----|--------|----------|
| `c` | `Inline code` | `` `text` `` |
| `C` | Code block | ``` fenced block ``` |

#### Headers
| Key | Result | Markdown |
|-----|--------|----------|
| `1` | # Header 1 | `# text` |
| `2` | ## Header 2 | `## text` |
| `3` | ### Header 3 | `### text` |
| `4` | #### Header 4 | `#### text` |
| `5` | ##### Header 5 | `##### text` |
| `6` | ###### Header 6 | `###### text` |

#### Lists and Structure
| Key | Result | Markdown |
|-----|--------|----------|
| `l` | - List item | `- text` |
| `L` | 1. Ordered list | `1. text` |
| `q` | > Blockquote | `> text` |

#### Links and Special
| Key | Result | Markdown |
|-----|--------|----------|
| `u` | [Link](url) | `[text](url)` |
| `r` | [Reference][ref] | `[text][ref]` |
| `t` | \| Table cell \| | `| text |` |

### Visual Mode Behavior
- **Instant formatting**: Key press immediately applies formatting and returns to NORMAL mode
- **Selection preservation**: Original text is replaced with formatted version
- **Error handling**: Invalid keys exit VISUAL mode without changes
- **Movement keys**: `h`, `j`, `k`, `l`, `w`, `b`, `0`, `$` extend selection

## Preview Mode

### Preview Toggle
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+P` | Toggle Preview | Switch between edit and preview modes |

**Edit Mode**: 
- Syntax-highlighted markdown editing with vim modes
- Line numbers and full text editing capabilities
- File modification tracking

**Preview Mode**: 
- Rendered markdown view in the same space as editor
- Rich markdown rendering with proper formatting
- Replaces editor view completely (not side-by-side)

## Legacy Format Menu

### Text Formatting Menu (Alternative to Visual Mode)
Press `Ctrl+F` to open the formatting menu with these options:

#### Available Options
- **Heading 1-6**: Converts text to `# ## ### #### ##### ######` format
- **Bold/Italic/Strikethrough**: Text styling options
- **Code/Code Block**: Inline and block code formatting
- **Lists**: Unordered and ordered list creation
- **Blockquote**: Quote formatting
- **Links/Images**: Link and image insertion
- **Table**: Basic table structure creation
- **Horizontal Rule**: Inserts `---`

**Note**: Visual mode formatting (select text + key) is faster and more intuitive than the format menu.

## Complete Keyboard Reference

### Global Shortcuts (Always Available)
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file instruction |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+P` | Toggle preview mode |
| `Ctrl+F` | Format menu (legacy) |
| `Ctrl+Q` | Quit application |
| `Ctrl+T` | Toggle file tree visibility |

### Vim Mode Indicators
The editor border displays current mode with color coding:
- **INSERT mode**: `[INSERT]` in green - ready for text input
- **NORMAL mode**: `[NORMAL]` in blue - ready for navigation/commands  
- **VISUAL mode**: `[VISUAL]` in yellow - text selected for formatting

### Supported File Types
**Readable formats**:
- `.md` - Markdown files (primary)
- `.markdown` - Markdown files  
- `.txt` - Plain text files
- `.text` - Text files

**File tree behavior**: Only supported file types can be opened.

## Workflow Guide

### Getting Started

#### Quick Start (uvx)
```bash
# Run directly without installation
uvx --from git+https://github.com/friscorose/vimdown.git vimdown
```

#### Typical Editing Session
1. **Launch**: Application starts in INSERT mode
2. **Navigate**: Use file tree to browse and open files
3. **Edit**: Start typing immediately (INSERT mode active)
4. **Format**: Select text and press format keys (`b`, `i`, `s`, etc.)
5. **Navigate**: Press `Esc` for NORMAL mode, use vim keys
6. **Preview**: Press `Ctrl+P` to see rendered markdown
7. **Save**: Use `Ctrl+S` regularly

### Visual Mode Formatting Workflow
1. **Select text**: Mouse selection or `v` + movement in NORMAL mode
2. **Format instantly**: Press `b` for bold, `i` for italic, `1-6` for headers, etc.
3. **Automatic return**: Formatting applied and returns to NORMAL mode
4. **Continue editing**: Press `i` to return to INSERT mode

### Vim Navigation Workflow
1. **Switch to NORMAL**: Press `Esc` from INSERT mode
2. **Navigate**: Use `hjkl`, `w`, `b`, `0`, `$`, `g`, `G`
3. **Edit text**: Use `x`, `d`, `u`, `Ctrl+R`
4. **Return to INSERT**: Use `i`, `a`, `o`, `O`, `A`, `I`

### File Management Tips
- **Directory navigation**: Click folders or ".." to navigate
- **Tree visibility**: Use `Ctrl+T` to hide/show tree for more editor space
- **Auto-refresh**: File tree updates after save operations
- **New files**: `Ctrl+N` creates new document and enters INSERT mode

## Technical Details

### Vim Mode Implementation
- **Always active**: No toggle - vim modes are always operational
- **Mode awareness**: All key handling respects current mode
- **Visual mode trigger**: Text selection automatically activates VISUAL mode
- **Formatting integration**: Visual mode provides direct markdown formatting
- **Status display**: Real-time mode indication in editor border

### Key Binding Conflicts
The visual mode formatting keys are carefully chosen to avoid conflicts:
- **Preserves navigation**: `hjkl`, `w`, `0`, `$` work normally in VISUAL mode
- **Preserves editing**: `y`, `d`, `p` operations not overridden
- **Intuitive mnemonics**: `b`=bold, `i`=italic, `s`=strikethrough, `c`=code
- **Shift variations**: `l`=list, `L`=ordered list, `c`=code, `C`=code block

### Preview Rendering
- **Engine**: Rich markdown renderer with full formatting support
- **Mode switching**: Seamless toggle preserves editor state
- **Content storage**: Editor content maintained separately during preview

### File Handling
- **Encoding**: UTF-8 for all file operations
- **Auto-detection**: Supported file types identified by extension
- **Error handling**: Graceful handling of permission/access errors

## Troubleshooting

### Mode Confusion
- **Check border**: Current mode always shown with color coding
- **ESC to reset**: Press `Esc` to return to NORMAL mode from any state
- **INSERT for typing**: Press `i` from NORMAL mode to start typing
- **Visual auto-trigger**: Selecting text automatically enters VISUAL mode

### Formatting Issues
- **No selection**: Ensure text is selected before using format keys
- **Wrong mode**: Format keys only work in VISUAL mode (yellow indicator)
- **Key not working**: Verify you're using the correct format key (see reference)
- **Auto-exit**: Formatting keys automatically return to NORMAL mode

### Navigation Issues
- **Keys not working**: Ensure you're in NORMAL mode (blue indicator)
- **Text appearing**: You're in INSERT mode - press `Esc` first
- **Selection extending**: You're in VISUAL mode - press `Esc` to exit

### File Operations
- **Files not opening**: Ensure file has supported extension (.md, .txt, etc.)
- **Tree missing**: Press `Ctrl+T` to toggle file tree visibility
- **Save not working**: Check file permissions and disk space

## Comparison: Visual Mode vs Format Menu

### Visual Mode Formatting (Recommended)
- **Speed**: Instant formatting with single key press
- **Workflow**: Select text → press key → continue editing
- **Intuitive**: Mnemonic keys (b=bold, i=italic, etc.)
- **Vim-like**: Integrates perfectly with vim workflow

### Format Menu (Legacy)
- **Comprehensive**: Shows all available options
- **Discovery**: Good for learning available formats
- **Workflow**: Select text → Ctrl+F → choose option → apply
- **Slower**: Requires menu navigation

**Recommendation**: Use visual mode formatting for speed and efficiency. Use format menu for discovering new formatting options.

---

*Built with Textual framework for modern terminal user interfaces*  
*Featuring comprehensive vim keybindings with visual mode markdown formatting*  
*Managed with uv for fast, reliable Python project management*
