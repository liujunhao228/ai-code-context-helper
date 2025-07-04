"""
GUI组件模块

该模块负责创建和管理应用程序的图形用户界面元素，包括窗口、菜单、
按钮、标签、树视图等。提供了用户界面的初始化、更新和事件处理。
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from ai_code_context_helper.tooltip import create_tooltip
from ai_code_context_helper.config import (
    TREE_COLUMN_WIDTH,
    TREE_COLUMN_MIN_WIDTH,
    TREE_COLUMN_ID,
    CHECK_COLUMN_WIDTH,
    CHECK_COLUMN_MIN_WIDTH,
    CHECK_COLUMN_ID,
    LINES_COLUMN_ID,
    LINES_COLUMN_WIDTH,
    LINES_COLUMN_MIN_WIDTH,
    SIZE_COLUMN_ID,
    SIZE_COLUMN_WIDTH,
    SIZE_COLUMN_MIN_WIDTH,
)
from ai_code_context_helper.markdown_exporter import generate_markdown
from ai_code_context_helper.tree_operations import TreeOperations



class GUIComponents:
    """
    负责创建和管理GUI组件的类

    管理应用程序的所有GUI元素，包括窗口、控件和布局。
    处理UI元素的创建、配置和更新，以及用户界面的多语言支持。

    Attributes:
        parent (CodeContextGenerator): 父对象，提供对主应用程序的访问

    Methods:
        create_widgets(): 创建并布局所有GUI控件
        center_window(window): 将窗口居中显示在屏幕上
        update_ui_texts(): 更新界面上的所有文本
        update_tooltips(): 更新所有工具提示
    """

    def __init__(self, parent):
        """
        初始化GUI组件管理器

        Args:
            parent (CodeContextGenerator): 父对象，提供对主应用程序的访问
        """
        self.parent = parent
        self._last_clicked_item = None
        self._last_click_time = 0
        self._is_dragging = False  # 跟踪是否在拖动
        self._current_selections = set()  # 跟踪当前选择项
        self._last_item_toggle_state = {}  # 存储项目在拖动开始时的状态

    def create_widgets(self):
        """
        创建并布局所有GUI控件

        初始化应用程序的所有GUI元素，包括状态栏、工具栏、设置面板、
        文件树视图和各种按钮。并设置事件绑定和初始状态。
        """

        # 状态栏 - 显示程序状态和操作结果
        self.parent.status_var = tk.StringVar()
        self.parent.status_bar = ttk.Label(
            self.parent.root,
            textvariable=self.parent.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        self.parent.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        self.parent.status_var.set(self.parent.texts["ready"])
        create_tooltip(self.parent.status_bar, self.parent.texts["tooltip_status_bar"])

        # 主框架 - 包含所有其他控件
        main_frame = ttk.Frame(self.parent.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 工具栏框架 - 包含帮助和关于按钮
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # 左侧为空白占位
        ttk.Label(toolbar_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.X)
        # 添加置顶按钮
        self.parent.topmost_btn_style = ttk.Style()
        self.parent.topmost_btn_style.configure("Normal.TButton", background=None)
        self.parent.topmost_btn_style.configure("Active.TButton", background="#d1e7dd")

        # 根据当前置顶状态决定显示的文本和样式
        button_text = (
            self.parent.texts.get("topmost_active_text", "取消置顶")
            if self.parent.is_topmost.get()
            else self.parent.texts.get("topmost_text", "置顶窗口")
        )
        button_style = (
            "Active.TButton" if self.parent.is_topmost.get() else "Normal.TButton"
        )

        self.parent.topmost_btn = ttk.Button(
            toolbar_frame,
            text=button_text,
            command=self.toggle_topmost_state,
            style=button_style,
        )
        self.parent.topmost_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(
            self.parent.topmost_btn,
            self.parent.texts.get("topmost_tooltip", "使窗口保持在最前方"),
        )
        # 更新日志按钮 - 打开GitHub上的更新日志
        self.parent.changelog_btn = ttk.Button(
            toolbar_frame,
            text=self.parent.texts["changelog_text"],
            command=self.parent.open_changelog,
        )
        self.parent.changelog_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(
            self.parent.changelog_btn, self.parent.texts["changelog_tooltip"]
        )

        # 关于作者按钮 - 显示作者公众号二维码
        self.parent.qrcode_btn = ttk.Button(
            toolbar_frame,
            text=self.parent.texts["about_author_text"],
            command=self.parent.show_qrcode,
        )
        self.parent.qrcode_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(
            self.parent.qrcode_btn, self.parent.texts["about_author_tooltip"]
        )

        # 设置面板 - 包含目录路径和各种设置选项
        self.parent.control_frame = ttk.LabelFrame(
            main_frame, text=self.parent.texts["settings"], padding="10"
        )
        self.parent.control_frame.pack(fill=tk.X, pady=5)

        # 顶部控制区 - 包含语言选择和高级选项切换按钮
        top_controls = ttk.Frame(self.parent.control_frame)
        top_controls.pack(fill=tk.X, pady=5)

        # 语言选择标签和下拉框 - 用于切换界面语言
        self.parent.lang_label = ttk.Label(
            top_controls, text=self.parent.texts["language"]
        )
        self.parent.lang_label.pack(side=tk.LEFT, padx=5)

        # 构建语言显示名称列表
        self.parent.language_names = {}  # 用于存储显示名称到代码的映射
        language_display_names = []

        for lang_code in self.parent.languages.keys():
            name = self.parent.languages[lang_code]["language_name"]
            self.parent.language_names[name] = lang_code
            language_display_names.append(name)

        # 获取当前语言的显示名称
        current_display_name = self.parent.languages[self.parent.current_language][
            "language_name"
        ]

        # 语言选择下拉框
        self.parent.language_var = tk.StringVar(value=current_display_name)
        self.parent.language_combo = ttk.Combobox(
            top_controls,
            textvariable=self.parent.language_var,
            values=language_display_names,
            width=15,
            state="readonly",
        )
        self.parent.language_combo.pack(side=tk.LEFT, padx=5)
        self.parent.language_combo.bind(
            "<<ComboboxSelected>>", self.parent.change_language
        )

        # 高级选项切换按钮 - 显示或隐藏高级设置项
        self.parent.toggle_btn = ttk.Button(
            top_controls,
            text=(
                self.parent.texts["hide_options"]
                if self.parent.show_advanced_options
                else self.parent.texts["show_options"]
            ),
            command=self.parent.toggle_advanced_options,
            width=12,
        )
        self.parent.toggle_btn.pack(side=tk.RIGHT, padx=5)
        create_tooltip(
            self.parent.toggle_btn, self.parent.texts["tooltip_toggle_options"]
        )

        # 目录路径选择区域 - 包含路径输入框和浏览按钮
        dir_frame = ttk.Frame(self.parent.control_frame)
        dir_frame.pack(fill=tk.X, pady=5)

        # 目录路径标签
        self.parent.dir_label = ttk.Label(dir_frame, text=self.parent.texts["dir_path"])
        self.parent.dir_label.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.parent.dir_label, self.parent.texts["tooltip_dir_path"])
        self.parent.dir_path = tk.StringVar()

        # 目录路径输入/选择框 - 可以输入路径或从历史记录中选择
        entry_frame = ttk.Frame(dir_frame)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.parent.dir_entry = ttk.Combobox(
            entry_frame, textvariable=self.parent.dir_path
        )
        self.parent.dir_entry.pack(fill=tk.X, expand=True)
        if self.parent.dir_history:
            self.parent.dir_entry["values"] = self.parent.dir_history

        self.parent.dir_entry.bind(
            "<<ComboboxSelected>>", self.parent.on_combobox_select
        )
        self.parent.dir_entry.bind("<Button-3>", self.parent.show_dir_history_menu)

        # 浏览按钮 - 打开文件夹选择对话框
        self.parent.browse_btn = ttk.Button(
            dir_frame,
            text=self.parent.texts["browse"],
            command=self.parent.browse_directory,
        )
        self.parent.browse_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.parent.browse_btn, self.parent.texts["tooltip_browse"])

        # 高级选项框架 - 可折叠，包含各种高级设置选项
        self.parent.advanced_options_frame = ttk.Frame(self.parent.control_frame)
        if self.parent.show_advanced_options:
            self.parent.advanced_options_frame.pack(fill=tk.X, pady=5)

        # 高级选项内容区
        options_frame = ttk.Frame(self.parent.advanced_options_frame)
        options_frame.pack(fill=tk.X, pady=5)

        # 左侧选项区 - 包含复选框等选项
        left_options = ttk.Frame(options_frame)
        left_options.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 显示隐藏文件选项 - 显示以点(.)开头的文件和设置了隐藏属性的文件
        self.parent.show_hidden = tk.BooleanVar(
            value=self.parent.settings.show_hidden_value
        )
        self.parent.show_hidden_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["show_hidden"],
            variable=self.parent.show_hidden,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.show_hidden_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.show_hidden_cb,
            self.parent.texts["tooltip_show_hidden"],
        )

        # 使用.gitignore规则过滤选项
        self.parent.use_gitignore = tk.BooleanVar(
            value=self.parent.settings.use_gitignore_value
        )
        self.parent.use_gitignore_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["use_gitignore"],
            variable=self.parent.use_gitignore,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.use_gitignore_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.use_gitignore_cb,
            self.parent.texts["tooltip_use_gitignore"],
        )

        # 显示文件选项 - 在目录树中显示文件
        self.parent.show_files = tk.BooleanVar(
            value=self.parent.settings.show_files_value
        )
        self.parent.show_files_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["show_files"],
            variable=self.parent.show_files,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.show_files_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.show_files_cb, self.parent.texts["tooltip_show_files"]
        )

        # 显示文件夹选项 - 在目录树中显示文件夹
        self.parent.show_folders = tk.BooleanVar(
            value=self.parent.settings.show_folders_value
        )
        self.parent.show_folders_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["show_folders"],
            variable=self.parent.show_folders,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.show_folders_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.show_folders_cb, self.parent.texts["tooltip_show_folders"]
        )

        # 使用相对路径选项 - 复制时使用相对根目录的路径而非绝对路径
        self.parent.use_relative_path = tk.BooleanVar(
            value=self.parent.settings.use_relative_path_value
        )
        self.parent.relative_path_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["use_relative_path"],
            variable=self.parent.use_relative_path,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.relative_path_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.relative_path_cb, self.parent.texts["tooltip_use_relative"]
        )

        # 启用鼠标框选模式选项 - 允许通过鼠标拖动批量选择文件
        self.parent.enable_easy_multiselect = tk.BooleanVar(
            value=self.parent.settings.enable_easy_multiselect_value
        )
        self.parent.easy_multiselect_cb = ttk.Checkbutton(
            left_options,
            text=self.parent.texts["enable_easy_multiselect"],
            variable=self.parent.enable_easy_multiselect,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.easy_multiselect_cb.pack(anchor=tk.W)
        create_tooltip(
            self.parent.easy_multiselect_cb,
            self.parent.texts["tooltip_easy_multiselect"],
        )

        # 文本格式设置按钮 - 打开文本格式设置对话框
        self.parent.format_btn = ttk.Button(
            left_options,
            text=self.parent.texts["format_settings"],
            command=self.parent.show_format_settings,
        )
        self.parent.format_btn.pack(anchor=tk.W, pady=5)
        create_tooltip(
            self.parent.format_btn, self.parent.texts["tooltip_format_settings"]
        )

        # Markdown格式设置按钮
        self.parent.markdown_format_btn = ttk.Button(
            left_options,
            text=self.parent.texts["markdown_format_settings"],
            command=self.parent.show_markdown_settings,
        )
        self.parent.markdown_format_btn.pack(anchor=tk.W, pady=5)
        create_tooltip(
            self.parent.markdown_format_btn,
            self.parent.texts["tooltip_markdown_format_settings"]
        )


        # 右侧选项区 - 包含数值和文本输入
        right_options = ttk.Frame(options_frame)
        right_options.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 最大深度设置 - 控制目录树显示的最大层级
        depth_frame = ttk.Frame(right_options)
        depth_frame.pack(anchor=tk.W)
        self.parent.depth_label = ttk.Label(
            depth_frame, text=self.parent.texts["max_depth"]
        )
        self.parent.depth_label.pack(side=tk.LEFT)
        create_tooltip(self.parent.depth_label, self.parent.texts["tooltip_max_depth"])

        self.parent.max_depth = tk.IntVar(value=self.parent.settings.max_depth_value)
        self.parent.depth_spinbox = ttk.Spinbox(
            depth_frame,
            from_=0,
            to=100,
            width=5,
            textvariable=self.parent.max_depth,
            command=self.parent.on_setting_option_changed,
        )
        self.parent.depth_spinbox.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.parent.depth_spinbox, self.parent.texts["tooltip_spinbox"])

        # 文件过滤器设置 - 使用正则表达式过滤显示的文件
        filter_frame = ttk.Frame(right_options)
        filter_frame.pack(anchor=tk.W, pady=5)
        self.parent.filter_label = ttk.Label(
            filter_frame, text=self.parent.texts["file_filter"]
        )
        self.parent.filter_label.pack(side=tk.LEFT)
        create_tooltip(
            self.parent.filter_label,
            self.parent.texts["tooltip_file_filter"],
        )

        self.parent.file_filter = tk.StringVar(
            value=self.parent.settings.file_filter_value
        )
        filter_entry = ttk.Entry(
            filter_frame, textvariable=self.parent.file_filter, width=20
        )
        filter_entry.pack(side=tk.LEFT, padx=5)

        # 按钮区域 - 包含主要操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        # 重置目录树按钮 - 清除所有展开状态，只保留根节点展开
        self.parent.reset_btn = ttk.Button(
            btn_frame,
            text=self.parent.texts["reset_tree"],
            command=self.parent.reset_tree,
        )
        self.parent.reset_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(
            self.parent.reset_btn,
            self.parent.texts["tooltip_reset_tree"],
        )

        # 更新目录树按钮 - 保持当前展开状态更新目录树内容
        self.parent.update_btn = ttk.Button(
            btn_frame,
            text=self.parent.texts["update_tree"],
            command=self.parent.update_tree,
        )
        self.parent.update_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(
            self.parent.update_btn,
            self.parent.texts["tooltip_update_tree"],
        )

        # 复制目录树按钮 - 将目录树文本表示复制到剪贴板
        self.parent.copy_btn = ttk.Button(
            btn_frame,
            text=self.parent.texts["copy_tree"],
            command=self.parent.copy_to_clipboard,
        )
        self.parent.copy_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(
            self.parent.copy_btn, self.parent.texts["tooltip_copy_tree"] + " (Ctrl+C)"
        )

        # 保存到文件按钮 - 将目录树保存到文本文件
        self.parent.save_btn = ttk.Button(
            btn_frame,
            text=self.parent.texts["save_to_file"],
            command=self.parent.save_to_file,
        )
        self.parent.save_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.parent.save_btn, self.parent.texts["tooltip_save_file"])

        # 导出为Markdown按钮
        self.parent.export_btn = ttk.Button(
            btn_frame,
            text=self.parent.texts["export_markdown"],
            command=self.export_markdown
        )
        self.parent.export_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.parent.export_btn, self.parent.texts["tooltip_export_markdown"])

        # 目录树视图区域 - 显示文件和文件夹的树形结构
        self.parent.result_frame = ttk.LabelFrame(
            main_frame, text=self.parent.texts["dir_tree"], padding="10"
        )
        self.parent.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 树形视图控件 - 显示目录结构
        self.parent.tree = ttk.Treeview(
            self.parent.result_frame, selectmode="extended", show="tree headings"
        )

        # 设置列
        self.parent.tree["columns"] = (CHECK_COLUMN_ID, LINES_COLUMN_ID, SIZE_COLUMN_ID)

        # 配置树的主列（文件名列）
        self.parent.tree.column(
            TREE_COLUMN_ID, width=TREE_COLUMN_WIDTH, minwidth=TREE_COLUMN_MIN_WIDTH
        )
        # 添加主列标题
        self.parent.tree.heading(
            TREE_COLUMN_ID, text=self.parent.texts.get("tree_column_name", "Name")
        )
        # 配置复选框列
        self.parent.tree.column(
            CHECK_COLUMN_ID,
            width=CHECK_COLUMN_WIDTH,
            minwidth=CHECK_COLUMN_MIN_WIDTH,
            anchor="center",
        )
        self.parent.tree.heading(
            CHECK_COLUMN_ID, text=self.parent.texts.get("tree_column_select", "Select")
        )

        # 配置行数列
        self.parent.tree.column(
            LINES_COLUMN_ID,
            width=LINES_COLUMN_WIDTH,
            minwidth=LINES_COLUMN_MIN_WIDTH,
            anchor="e",
        )
        self.parent.tree.heading(
            LINES_COLUMN_ID, text=self.parent.texts.get("tree_column_lines", "Lines")
        )

        # 配置大小列
        self.parent.tree.column(
            SIZE_COLUMN_ID,
            width=SIZE_COLUMN_WIDTH,
            minwidth=SIZE_COLUMN_MIN_WIDTH,
            anchor="e",
        )
        self.parent.tree.heading(
            SIZE_COLUMN_ID, text=self.parent.texts.get("tree_column_size", "Size")
        )

        # 树形视图滚动条 - 垂直和水平
        tree_scroll_y = ttk.Scrollbar(
            self.parent.result_frame, orient="vertical", command=self.parent.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            self.parent.result_frame,
            orient="horizontal",
            command=self.parent.tree.xview,
        )
        self.parent.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.parent.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 设置树形视图标签样式
        self.parent.tree.tag_configure("gray", foreground="gray")

        # 绑定树形视图事件处理函数
        self.parent.tree.bind("<Button-1>", self.parent.tree_ops.on_tree_button_down)
        self.parent.tree.bind(
            "<ButtonRelease-1>", self.parent.tree_ops.on_tree_button_up
        )
        self.parent.tree.bind(
            "<<TreeviewOpen>>", self.parent.tree_ops.on_tree_open, add="+"
        )
        self.parent.tree.bind(
            "<<TreeviewClose>>", self.parent.tree_ops.on_tree_close, add="+"
        )
        self.parent.tree.bind("<Button-3>", self.parent.show_context_menu)

        # 绑定目录路径变更和文件过滤器变更事件
        self.parent.dir_path.trace_add("write", self.parent.on_dir_changed)
        self.parent.file_filter.trace_add(
            "write", self.parent.on_setting_option_changed
        )

        # 根据设置控制高级选项的显示
        if not self.parent.show_advanced_options:
            self.parent.advanced_options_frame.pack_forget()
            self.parent.toggle_btn.configure(text=self.parent.texts["show_options"])

    def toggle_topmost_state(self):
        """切换窗口置顶状态并更新按钮样式"""
        # 调用父类的toggle_topmost方法
        self.parent.toggle_topmost()

        # 更新按钮样式
        if self.parent.is_topmost.get():
            # 激活状态样式
            self.parent.topmost_btn.configure(
                style="Active.TButton",
                text=self.parent.texts.get("topmost_active_text"),
            )
        else:
            # 非激活状态样式
            self.parent.topmost_btn.configure(
                style="Normal.TButton",
                text=self.parent.texts.get("topmost_text"),
            )

    def center_window(self, window):
        """
        将窗口居中显示在屏幕上

        计算屏幕中心点和窗口尺寸，然后将窗口放置在中心位置。

        Args:
            window (tk.Toplevel): 需要居中的窗口
        """
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry("{}x{}+{}+{}".format(width, height, x, y))

    def update_ui_texts(self):
        """
        更新界面上的所有文本
        """
        # 更新标签、按钮等控件文本
        self.parent.status_var.set(self.parent.texts["ready"])

        # 更新主窗口标题（包含版本号）
        self.parent.app_title_text = self.parent.texts["app_title"]
        self.parent.root.title(
            f"{self.parent.texts['app_title']} v{self.parent.version}"
        )

        # 更新设置框标题
        self.parent.control_frame.configure(text=self.parent.texts["settings"])

        # 更新语言标签
        self.parent.lang_label.configure(text=self.parent.texts["language"])

        # 更新路径标签
        self.parent.dir_label.configure(text=self.parent.texts["dir_path"])

        # 更新切换按钮文本
        self.parent.toggle_btn.configure(
            text=(
                self.parent.texts["hide_options"]
                if self.parent.show_advanced_options
                else self.parent.texts["show_options"]
            )
        )

        # 更新按钮文本
        self.parent.browse_btn.configure(text=self.parent.texts["browse"])
        self.parent.reset_btn.configure(text=self.parent.texts["reset_tree"])
        self.parent.update_btn.configure(text=self.parent.texts["update_tree"])
        self.parent.copy_btn.configure(text=self.parent.texts["copy_tree"])
        self.parent.save_btn.configure(text=self.parent.texts["save_to_file"])
        self.parent.format_btn.configure(text=self.parent.texts["format_settings"])
        self.parent.markdown_format_btn.configure(text=self.parent.texts["markdown_format_settings"])
        self.parent.export_btn.configure(text=self.parent.texts["export_markdown"])

        # 更新置顶按钮文本
        if hasattr(self.parent, "topmost_btn"):
            if self.parent.is_topmost.get():
                self.parent.topmost_btn.configure(
                    text=self.parent.texts.get("topmost_active_text")
                )
            else:
                self.parent.topmost_btn.configure(
                    text=self.parent.texts.get("topmost_text")
                )

        # 更新工具栏按钮文本
        self.parent.changelog_btn.configure(text=self.parent.texts["changelog_text"])
        self.parent.qrcode_btn.configure(text=self.parent.texts["about_author_text"])

        # 更新复选框文本
        self.parent.easy_multiselect_cb.configure(
            text=self.parent.texts["enable_easy_multiselect"]
        )
        self.parent.show_hidden_cb.configure(text=self.parent.texts["show_hidden"])
        self.parent.show_files_cb.configure(text=self.parent.texts["show_files"])
        self.parent.show_folders_cb.configure(text=self.parent.texts["show_folders"])
        self.parent.relative_path_cb.configure(
            text=self.parent.texts["use_relative_path"]
        )
        # 更新use_gitignore复选框文本
        if hasattr(self.parent, "use_gitignore_cb"):
            self.parent.use_gitignore_cb.configure(
                text=self.parent.texts["use_gitignore"]
            )

        # 更新深度和过滤器标签
        self.parent.depth_label.configure(text=self.parent.texts["max_depth"])
        self.parent.filter_label.configure(text=self.parent.texts["file_filter"])

        # 更新目录树框标题
        self.parent.result_frame.configure(text=self.parent.texts["dir_tree"])

        # 更新工具提示
        self.update_tooltips()
        
        # 更新树标题
        self.parent.tree.heading(TREE_COLUMN_ID, text=self.parent.texts.get("tree_column_name", "Name"))
        self.parent.tree.heading(CHECK_COLUMN_ID, text=self.parent.texts.get("tree_column_select", "Select"))
        self.parent.tree.heading(LINES_COLUMN_ID, text=self.parent.texts.get("tree_column_lines", "Lines"))
        self.parent.tree.heading(SIZE_COLUMN_ID, text=self.parent.texts.get("tree_column_size", "Size"))

    def update_tooltips(self):
        """
        更新所有工具提示
        """
        create_tooltip(self.parent.status_bar, self.parent.texts["tooltip_status_bar"])
        create_tooltip(self.parent.dir_label, self.parent.texts["tooltip_dir_path"])
        create_tooltip(self.parent.browse_btn, self.parent.texts["tooltip_browse"])
        create_tooltip(
            self.parent.show_hidden_cb, self.parent.texts["tooltip_show_hidden"]
        )
        create_tooltip(
            self.parent.show_files_cb, self.parent.texts["tooltip_show_files"]
        )
        create_tooltip(
            self.parent.show_folders_cb, self.parent.texts["tooltip_show_folders"]
        )
        create_tooltip(
            self.parent.relative_path_cb, self.parent.texts["tooltip_use_relative"]
        )
        create_tooltip(
            self.parent.format_btn, self.parent.texts["tooltip_format_settings"]
        )
        create_tooltip(self.parent.depth_label, self.parent.texts["tooltip_max_depth"])
        create_tooltip(self.parent.depth_spinbox, self.parent.texts["tooltip_spinbox"])
        create_tooltip(
            self.parent.filter_label, self.parent.texts["tooltip_file_filter"]
        )
        create_tooltip(self.parent.reset_btn, self.parent.texts["tooltip_reset_tree"])
        create_tooltip(self.parent.update_btn, self.parent.texts["tooltip_update_tree"])
        create_tooltip(self.parent.copy_btn, self.parent.texts["tooltip_copy_tree"])
        create_tooltip(self.parent.save_btn, self.parent.texts["tooltip_save_file"])
        create_tooltip(self.parent.export_btn, self.parent.texts["tooltip_export_markdown"])
        create_tooltip(
            self.parent.easy_multiselect_cb,
            self.parent.texts["tooltip_easy_multiselect"],
        )
        create_tooltip(
            self.parent.markdown_format_btn,
            self.parent.texts["tooltip_markdown_format_settings"]
        )

        create_tooltip(
            self.parent.toggle_btn,
            self.parent.texts["tooltip_toggle_options"],
        )

        # 置顶按钮工具
        if hasattr(self.parent, "topmost_btn"):
            create_tooltip(
                self.parent.topmost_btn,
                self.parent.texts.get("topmost_tooltip", "使窗口保持在最前方"),
            )

        # 工具栏按钮工具
        create_tooltip(
            self.parent.changelog_btn, self.parent.texts["changelog_tooltip"]
        )
        create_tooltip(
            self.parent.qrcode_btn, self.parent.texts["about_author_tooltip"]
        )

        # 添加对gitignore复选框工具提示的更新（如果存在）
        if hasattr(self.parent, "use_gitignore_cb"):
            create_tooltip(
                self.parent.use_gitignore_cb,
                self.parent.texts["tooltip_use_gitignore"],
            )

    def export_markdown(self):
        """
        导出选中节点及其子节点的所有文件到Markdown
        只负责界面交互和调用收集逻辑。
        """
        selected_items = self.parent.tree.selection()
        if not selected_items:
            self.parent.status_var.set(self.parent.texts.get("status_no_selection", "未选中任何项"))
            return

        # 新重构：收集所有需要导出的文件（只收集文件绝对路径）
        files = self.collect_export_files(selected_items)
        if not files:
            self.parent.status_var.set(self.parent.texts.get("status_no_text_files", "未找到可导出的文本文件"))
            return

        # 设置默认文件名为项目根目录名
        base_dir = self.parent.dir_path.get().strip()
        if base_dir:
            dir_name = os.path.basename(base_dir)
            if not dir_name:
                dir_name = os.path.basename(os.path.dirname(base_dir))
            default_filename = f"{dir_name}.md"
        else:
            default_filename = "export.md"

        output_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md")],
            initialfile=default_filename
        )
        if not output_path:
            return

        include_markers = self.parent.settings.include_markers
        show_encoding = self.parent.settings.show_encoding

        success, errors = generate_markdown(
            output_path=output_path,
            files=files,  # 只传递文件绝对路径
            project_root=base_dir,  # 新增参数，传递项目根目录
            include_markers=include_markers,
            show_encoding=show_encoding
        )

        if success > 0:
            self.parent.status_var.set(
                self.parent.texts.get("status_export_success", "成功导出{0}个文件").format(success)
            )
        if errors:
            messagebox.showerror("导出错误", "\n".join(errors))

    def collect_export_files(self, selected_items):
        """
        支持三种情况：
        1. 只选文件夹节点时递归导出所有文件夹下的文件；
        2. 只选文件节点时只导出这些文件；
        3. 混合选择时递归导出文件夹下所有文件并导出选中文件，避免重复。
        返回 [file_path, ...]
        """
        tree = self.parent.tree
        tree_items = self.parent.tree_items
        tree_ops = self.parent.tree_ops
        supported_exts = set(self.parent.settings.supported_extensions.keys())
        id_to_path = {v: k for k, v in tree_items.items()}
        file_nodes = []
        folder_nodes = []
        for item in selected_items:
            if item not in id_to_path:
                continue
            path = id_to_path[item]
            if os.path.isfile(path):
                file_nodes.append(item)
            elif os.path.isdir(path):
                folder_nodes.append(item)
        result = set()
        # 只选文件夹
        if folder_nodes and not file_nodes:
            for folder_item in folder_nodes:
                file_paths = tree_ops.get_all_files_under_node(folder_item)
                for file_path in file_paths:
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() in supported_exts:
                        result.add(file_path)
        # 只选文件
        elif file_nodes and not folder_nodes:
            for file_item in file_nodes:
                path = id_to_path[file_item]
                _, ext = os.path.splitext(path)
                if ext.lower() in supported_exts:
                    result.add(path)
        # 混合选择
        else:
            for folder_item in folder_nodes:
                file_paths = tree_ops.get_all_files_under_node(folder_item)
                for file_path in file_paths:
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() in supported_exts:
                        result.add(file_path)
            for file_item in file_nodes:
                path = id_to_path[file_item]
                _, ext = os.path.splitext(path)
                if ext.lower() in supported_exts:
                    result.add(path)
        return list(result)