"""
配置模块 - 集中管理应用程序配置和常量

该模块包含应用程序的默认设置、路径配置、UI配置等常量，
使配置更加集中、易于管理和修改。
"""

# 文件和代码格式设置
DEFAULT_PATH_PREFIX = "文件路径: "
DEFAULT_PATH_SUFFIX = "\n"
DEFAULT_CODE_PREFIX = "```\n"
DEFAULT_CODE_SUFFIX = "\n```\n"

# UI相关配置
UI_FONT_FAMILY = "微软雅黑"
UI_BUTTON_FONT_SIZE = 10
UI_LABEL_FONT_SIZE = 10
UI_TREEVIEW_FONT_SIZE = 10
UI_HEADING_FONT_STYLE = "bold"
UI_HEADING_FONT_SIZE = 10
UI_TOOLTIP_FONT = (UI_FONT_FAMILY, 9, "normal")
UI_TOOLTIP_BG_COLOR = "#ffffe0"
UI_TOOLTIP_DELAY = 200  # 毫秒

# 窗口相关配置
DEFAULT_WINDOW_SIZE = "700x750"
DEFAULT_WINDOW_MIN_SIZE = (600, 400)
QRCODE_WINDOW_SIZE = "500x260"
FORMAT_WINDOW_SIZE = "500x350"
FORMAT_WINDOW_MIN_SIZE = (500, 350)

# 文件处理相关配置
MAX_TEXT_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CHINESE_ENCODINGS = ["utf-8", "gb18030", "gbk", "gb2312", "big5"]
PREVIEW_CHARS_LENGTH = 1000  # 检查乱码的字符数

# 历史记录设置
MAX_HISTORY_ITEMS = 50

# 资源路径配置
RESOURCES_DIR = "resources"
ICON_FILENAME = "icon.ico"
QRCODE_FILENAME = "weixin.png"
SETTINGS_FILENAME = "default_settings.json"

# 树形视图设置
TREE_COLUMN_WIDTH = 400
TREE_COLUMN_MIN_WIDTH = 200
CHECK_COLUMN_WIDTH = 50
CHECK_COLUMN_MIN_WIDTH = 50
LINES_COLUMN_WIDTH = 70
LINES_COLUMN_MIN_WIDTH = 50
SIZE_COLUMN_WIDTH = 80
SIZE_COLUMN_MIN_WIDTH = 60
CHECK_MARK = "✓"
TREE_COLUMN_ID = "#0"
CHECK_COLUMN_ID = "checked"
LINES_COLUMN_ID = "lines"
SIZE_COLUMN_ID = "size"

# 链接
CHANGELOG_URL = (
    "https://github.com/sansan0/ai-code-context-helper/blob/master/CHANGELOG.md"
)

# 预设文本
QRCODE_WINDOW_TITLE = "关注公众号"
QRCODE_TEXT = "扫码关注公众号，支持作者更新~"

# 默认拓展名匹配规则（如需自定义，JSON配置文件中修改也可（其优先级更高））
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.css': 'css',
    '.html': 'html',
    '.htm': 'html',
    '.xml': 'xml',
    '.json': 'json',
    '.sh': 'shell',
    '.bat': 'batch',
    '.ps1': 'powershell',
    '.md': 'markdown',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.txt': 'text',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.dart': 'dart',
    '.lua': 'lua',
    '.pl': 'perl',
    '.r': 'r',
    '.sql': 'sql',
    '.cs': 'csharp',
    '.vb': 'vbnet',
    '.fs': 'fsharp'
}