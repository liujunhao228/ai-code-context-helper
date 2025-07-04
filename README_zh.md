<p align="center"><a href="README.md">English</a> | 中文<p>

# AI Code Context Helper


## 快速开始

1. **下载**：[Releases](https://github.com/liujunhao228/ai-code-context-helper/releases)
2. **解压**，运行 `AI Code Context Helper.exe`
3. **选择项目目录**，即可操作

## 主要功能

- **一键导出代码上下文**：支持文件、文件夹、混合选择，快速复制路径、代码或结构，适配 AI 助手需求。
- **自动应用 .gitignore 过滤**：导出时自动排除不需要的文件和目录，无需手动筛选。
- **目录树可视化与多选**：清晰展示项目结构，支持批量选择、鼠标框选，适合大项目。
- **Markdown/多格式导出**：一键生成适合文档、审查、AI 提示词的 Markdown 文件。
- **本地运行，隐私安全**：无需联网，所有操作本地完成，代码不外泄。
- **高效集成开发流程**：全局热键、系统托盘、状态栏统计、正则/深度筛选，提升日常效率。

## 导出功能详解与示例

### 1. 只选文件节点

- **操作**：勾选一个或多个文件
- **导出内容**：每个文件的完整路径 + 代码内容

### 2. 只选文件夹节点

- **操作**：只勾选一个或多个文件夹
- **导出内容**：导出所选文件夹的目录树结构（不含具体代码）

### 3. 混合选择文件和文件夹

- **操作**：同时勾选文件和文件夹
- **导出内容**：
  - 文件夹：导出其目录树结构
  - 文件：导出路径和代码内容

### 4. Markdown 导出

- 右键菜单选择"导出为 Markdown"
- 适合整理文档、代码审查、AI 提示词

## 常用操作

- **Ctrl+C**：复制选中文件/文件夹的路径和代码/结构
- **Ctrl+B**：复制文件名
- **Ctrl+F**：资源管理器中打开文件夹
- **Ctrl+T**：命令行终端定位到文件夹
- **Ctrl+2**：全局热键，显示/隐藏窗口

## 进阶用法

- **正则/深度筛选**：支持正则过滤、目录深度限制
- **.gitignore 自动过滤**：自动识别并应用项目中的 .gitignore 规则，导出时自动排除被忽略的文件和目录
- **状态栏统计**：显示选中文件数、总行数
- **系统托盘**：最小化驻留，随时可用
- **多语言**：中英文切换

## 构建与开发

- 依赖：Python 3.9+，Poetry
- 安装依赖：

  ```bash
  git clone https://github.com/liujunhao228/ai-code-context-helper.git
  cd ai-code-context-helper
  poetry install
  ```

- 构建可执行文件：

  ```bash
  poetry run python -m cx_Freeze build
  ```

## 许可

GPL-3.0，详见 [LICENSE](LICENSE)
