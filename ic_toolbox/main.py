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

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ic_toolbox import config
from ic_toolbox.sidebar import Sidebar
from ic_toolbox.tools import BaseConverterFrame, DataSlicerFrame, DataDiffFrame, BitExtractorFrame


class ICToolbox(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("IC Verification Toolbox  |  IC验证工具箱")
        self.geometry("1000x720")
        self.minsize(860, 600)
        _ = self.configure(bg=config.BG_DARK)

        # 初始化实例变量（解决未初始化警告）
        self.sidebar: Sidebar
        self.content: tk.Frame
        self.current_tool: tk.Frame | None = None
        self._base_converter: tk.Frame | None = None
        self._data_slicer: tk.Frame | None = None
        self._data_diff: tk.Frame | None = None
        self._bit_extractor: tk.Frame | None = None

        # 设置 DPI 感知（Windows）
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self._setup_style()
        self._build_layout()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        _ = style.configure("TCombobox",  # type: ignore
                        fieldbackground=config.BG_INPUT,
                        background=config.BG_INPUT,
                        foreground=config.FG_PRIMARY,
                        selectbackground=config.ACCENT,
                        selectforeground=config.BG_DARK,
                        bordercolor=config.BORDER,
                        arrowcolor=config.FG_SECONDARY)
        _ = style.configure("TSeparator", background=config.BORDER)  # type: ignore
        _ = style.map("TCombobox",  # type: ignore
                  fieldbackground=[("readonly", config.BG_INPUT)],
                  foreground=[("readonly", config.FG_PRIMARY)])

    def _build_layout(self) -> None:
        # 侧边栏
        self.sidebar = Sidebar(self, on_select=self._switch_tool)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # 分隔线
        tk.Frame(self, bg=config.BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # 主内容区
        self.content = tk.Frame(self, bg=config.BG_DARK)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 当前工具页
        self._show_base_converter()

    def _switch_tool(self, idx: int) -> None:
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

    def _show_base_converter(self) -> None:
        if self._base_converter is None:
            self._base_converter = BaseConverterFrame(self.content)
        self._base_converter.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._base_converter

    def _show_data_slicer(self) -> None:
        if self._data_slicer is None:
            self._data_slicer = DataSlicerFrame(self.content)
        self._data_slicer.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._data_slicer

    def _show_data_diff(self) -> None:
        if self._data_diff is None:
            self._data_diff = DataDiffFrame(self.content)
        self._data_diff.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._data_diff

    def _show_bit_extractor(self) -> None:
        if self._bit_extractor is None:
            self._bit_extractor = BitExtractorFrame(self.content)
        self._bit_extractor.pack(fill=tk.BOTH, expand=True)
        self.current_tool = self._bit_extractor


if __name__ == "__main__":
    app = ICToolbox()
    app.mainloop()
