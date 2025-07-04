<p align="center">English | <a href="README_zh.md">中文</a><p>

# AI Code Context Helper

**A local tool for exporting code structure and content, designed for efficient AI collaboration.**

## Quick Start

1. **Download**: [Releases](https://github.com/liujunhao228/ai-code-context-helper/releases)
2. **Extract** and run `AI Code Context Helper.exe`
3. **Select your project directory** to begin

## Main Features

- **One-click code context export**: Select files, folders, or both, and quickly copy paths, code, or structure—perfect for AI assistants.
- **Automatic .gitignore filtering**: Excludes unnecessary files and folders during export, no manual cleanup needed.
- **Tree view & multi-selection**: Visualize your project, batch-select with mouse, ideal for large codebases.
- **Markdown & multi-format export**: Instantly generate Markdown for docs, review, or AI prompts.
- **Local & private**: Runs fully offline, nothing leaves your machine.
- **Workflow integration**: Global hotkey, system tray, status bar stats, regex/depth filtering—streamline your daily dev tasks.

## Export Modes & Examples

### 1. File Nodes Only

- **How**: Select one or more files
- **Export**: Full path + code content for each file

### 2. Folder Nodes Only

- **How**: Select one or more folders only
- **Export**: Directory tree structure (no code content)

### 3. Mixed Files and Folders

- **How**: Select both files and folders
- **Export**:
  - Folders: directory tree structure
  - Files: path + code content

### 4. Markdown Export

- Right-click and choose "Export as Markdown"
- Suitable for documentation, code review, or AI prompt preparation

## Common Shortcuts

- **Ctrl+C**: Copy path and code/structure of selected files/folders
- **Ctrl+B**: Copy file names
- **Ctrl+F**: Open folder in file explorer
- **Ctrl+T**: Open terminal in selected folder
- **Ctrl+2**: Global hotkey to show/hide the window

## Advanced Usage

- **Regex/depth filtering**: Supports regex filtering and directory depth limit
- **.gitignore auto-filtering**: Automatically applies your project's .gitignore rules to exclude ignored files and folders from export
- **Status bar stats**: Shows selected file count and total lines
- **System tray**: Minimize to tray, always available
- **Multi-language**: Switch between English and Chinese

## Build & Development

- Requirements: Python 3.9+, Poetry
- Install dependencies:

  ```bash
  git clone https://github.com/liujunhao228/ai-code-context-helper.git
  cd ai-code-context-helper
  poetry install
  ```

- Build executable:

  ```bash
  poetry run python -m cx_Freeze build
  ```

## License

GPL-3.0, see [LICENSE](LICENSE)
