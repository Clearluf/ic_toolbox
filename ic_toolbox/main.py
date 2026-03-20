"""
IC Verification Engineer Toolbox
IC验证工程师辅助工具箱 - 主入口

目录结构:
    ic_toolbox/
    ├── main.py           # 主入口
    ├── config.py         # 共享配置（颜色主题等）
    ├── sidebar.py        # 侧边栏导航
    └── tools/
        ├── __init__.py
        ├── base_converter.py   # 进制转换器
        ├── data_slicer.py     # 数据切片器
        └── data_diff.py       # 数据比对器
"""

import tkinter as tk
from tkinter import ttk

from . import config
from .sidebar import Sidebar
from .tools import BaseConverterFrame, DataSlicerFrame, DataDiffFrame, BitExtractorFrame


class ICToolbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IC Verification Toolbox  |  IC验证工具箱")
        self.geometry("1000x720")
        self.minsize(860, 600)
        self.configure(bg=config.BG_DARK)

        # 设置 DPI 感知（Windows）
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self._setup_style()
        self._build_layout()

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=config.BG_INPUT,
                        background=config.BG_INPUT,
                        foreground=config.FG_PRIMARY,
                        selectbackground=config.ACCENT,
                        selectforeground=config.BG_DARK,
                        bordercolor=config.BORDER,
                        arrowcolor=config.FG_SECONDARY)
        style.configure("TSeparator", background=config.BORDER)
        style.map("TCombobox",
                  fieldbackground=[("readonly", config.BG_INPUT)],
                  foreground=[("readonly", config.FG_PRIMARY)])

    def _build_layout(self):
        # 侧边栏
        self.sidebar = Sidebar(self, on_select=self._switch_tool)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # 分隔线
        tk.Frame(self, bg=config.BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # 主内容区
        self.content = tk.Frame(self, bg=config.BG_DARK)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 当前工具页
        self.current_tool = None
        self._show_base_converter()

    def _switch_tool(self, idx):
        if self.current_tool:
            self.current_tool.pack_forget()
        if idx == 0:
            self._show_base_converter()
        elif idx == 1:
            self._show_data_slicer()
        elif idx == 2:
            self._show_data_diff()
        elif idx == 3:
            self._show_bit_extractor()

    def _show_base_converter(self):
        if not hasattr(self, "_base_converter"):
            self._base_converter = BaseConverterFrame(self.content)
        self._base_converter.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._base_converter

    def _show_data_slicer(self):
        if not hasattr(self, "_data_slicer"):
            self._data_slicer = DataSlicerFrame(self.content)
        self._data_slicer.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._data_slicer

    def _show_data_diff(self):
        if not hasattr(self, "_data_diff"):
            self._data_diff = DataDiffFrame(self.content)
        self._data_diff.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._data_diff

    def _show_bit_extractor(self):
        if not hasattr(self, "_bit_extractor"):
            self._bit_extractor = BitExtractorFrame(self.content)
        self._bit_extractor.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._bit_extractor


if __name__ == "__main__":
    app = ICToolbox()
    app.mainloop()
