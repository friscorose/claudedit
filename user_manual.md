# Markdown Editor User Manual

A full-featured terminal-based markdown editor built with Textual, featuring file management, live preview, vim keybindings, and comprehensive formatting tools.

## Installation & Setup

```bash
pip install textual rich
python markdown_editor.py
```

## Interface Overview

The editor consists of four main areas:
- **Header**: Application title and current file name
- **File Tree**: Directory navigation (left panel)
- **Editor/Preview**: Main editing area with in-place preview toggle
- **Status Bar**: Current status, vim mode, and helpful messages
- **Footer**: Available keyboard shortcuts

## File Operations

### Basic File Management
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New File | Create a new markdown document |
| `Ctrl+S` | Save | Save current file |
| `Ctrl+Shift+S` | Save As | Save with new filename |
| `Ctrl+Q` | Quit | Exit the application |

### File Tree Navigation
- **Click files**: Open `.md`, `.markdown`, `.txt` files directly
- **Click directories**: Navigate into folders
- **Click ".."**: Go to parent directory (when available)
- **Icons**: 📁 directories, 📝 markdown files, 📄 text files
- **Toggle**: Press `F1` to show/hide file tree

## Editing Features

### Preview Mode
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+P` | Toggle Preview | Switch between edit and preview modes |

**Edit Mode**: Syntax-highlighted markdown editing with line numbers
**Preview Mode**: Rendered markdown view in the same space

### Text Formatting
Press `Ctrl+F` to open the formatting menu with these options:

#### Headings
- **Heading 1-6**: `# ## ### #### ##### ######`

#### Text Styling
- **Bold**: `**text**`
- **Italic**: `*text*`
- **Bold Italic**: `***text***`
- **Strikethrough**: `~~text~~`

#### Code
- **Inline Code**: `` `code` ``
- **Code Block**: 
  ```
  ```
  code block
  ```
  ```

#### Lists
- **Unordered List**: `- item`
- **Ordered List**: `1. item`

#### Special Elements
- **Blockquote**: `> quoted text`
- **Link**: `[text](url)`
- **Image**: `![alt text](image_url)`
- **Horizontal Rule**: `---`
- **Table**: Basic table structure with headers

## Vim Keybindings

### Toggle Vim Mode
| Shortcut | Action |
|----------|--------|
| `Ctrl+V` | Enable/disable vim keybindings |

### Vim Modes
- **INSERT**: Normal text editing (default when vim enabled)
- **NORMAL**: Command mode for navigation and operations
- **Status**: Current mode shown in status bar `[INSERT]` or `[NORMAL]`

### Mode Switching
| Key | Action |
|-----|--------|
| `Esc` | Switch to NORMAL mode |
| `i` | Enter INSERT mode at cursor |
| `a` | Enter INSERT mode after cursor |
| `o` | New line below + INSERT mode |
| `O` | New line above + INSERT mode |

### Navigation (NORMAL Mode)
| Key | Action |
|-----|--------|
| `h` | Move left |
| `l` | Move right |
| `j` | Move down |
| `k` | Move up |
| `w` | Next word |
| `b` | Previous word |
| `0` | Beginning of line |
| `$` | End of line |
| `g` | Go to file start |
| `G` | Go to file end |

### Editing (NORMAL Mode)
| Key | Action |
|-----|--------|
| `x` | Delete character under cursor |
| `d` | Delete current line |
| `u` | Undo |
| `Ctrl+R` | Redo |

## Quick Reference

### All Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+P` | Toggle preview |
| `Ctrl+F` | Format menu |
| `Ctrl+V` | Toggle vim mode |
| `Ctrl+Q` | Quit |
| `F1` | Toggle file tree |

### Status Bar Information
The status bar displays:
- Current operation status
- Vim mode indicator `[INSERT]` or `[NORMAL]` (when vim enabled)
- Helpful context messages

### File Support
**Supported formats**:
- `.md` - Markdown files
- `.markdown` - Markdown files  
- `.txt` - Plain text files
- `.text` - Text files

## Tips & Best Practices

### Workflow Suggestions
1. **Start**: Use file tree to navigate to your project directory
2. **Create**: Press `Ctrl+N` for new files or click existing files
3. **Edit**: Type markdown with syntax highlighting assistance
4. **Format**: Use `Ctrl+F` for quick formatting of selected text
5. **Preview**: Press `Ctrl+P` to see rendered output
6. **Save**: Use `Ctrl+S` regularly to save your work

### Vim Users
- Toggle vim mode with `Ctrl+V` for familiar editing experience
- Start in INSERT mode for immediate typing
- Use `Esc` to access NORMAL mode for navigation
- Most common vim operations are supported

### File Management
- Use ".." nodes in file tree for easy parent directory navigation
- File tree automatically refreshes when files are saved
- Click any supported file type to open directly

## Troubleshooting

### Common Issues
- **Files not opening**: Ensure file has supported extension (.md, .txt, etc.)
- **Vim mode confusion**: Check status bar for current mode indicator
- **Preview not updating**: Switch to edit mode and back to refresh preview
- **File tree not showing**: Press `F1` to toggle visibility

### Performance Notes
- Preview renders in real-time when toggling modes
- Large files may take a moment to load in preview mode
- File tree refreshes automatically after save operations

---

*Built with Textual framework for modern terminal user interfaces*


