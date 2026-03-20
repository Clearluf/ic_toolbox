"""
侧边栏导航 - Sidebar
工具列表和导航
"""

import tkinter as tk
from tkinter import ttk
from . import config


class Sidebar(tk.Frame):
    TOOLS = [
        ("⇄", "进制转换",   "Base Converter"),
        ("⊡", "数据切片",   "Data Slicer"),
        ("≠", "数据比对",   "Data Diff"),
        ("⊟", "寄存器映射", "Reg Map  (即将推出)"),
        ("✎", "断言模板",   "SVA Template  (即将推出)"),
    ]

    def __init__(self, parent, on_select, *args, **kwargs):
        super().__init__(parent, bg=config.BG_SIDEBAR, width=180, *args, **kwargs)
        self.pack_propagate(False)
        self.on_select = on_select
        self._selected = 0
        self._btns = []
        self._build()

    def _build(self):
        # Logo 区域
        logo_frame = tk.Frame(self, bg=config.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(20, 0), padx=16)

        tk.Label(logo_frame, text="⬡ IC Toolbox",
                font=("Consolas", 13, "bold"),
                bg=config.BG_SIDEBAR, fg=config.ACCENT).pack(anchor=tk.W)
        tk.Label(logo_frame, text="IC验证工具箱 v1.0",
                font=("Consolas", 8),
                bg=config.BG_SIDEBAR, fg=config.FG_MUTED).pack(anchor=tk.W)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=(12, 8), padx=10)

        tk.Label(self, text="TOOLS", font=("Consolas", 8, "bold"),
                bg=config.BG_SIDEBAR, fg=config.FG_MUTED).pack(anchor=tk.W, padx=16)

        for i, (icon, name, sub) in enumerate(self.TOOLS):
            available = (i in (0, 1, 2))
            btn_frame = tk.Frame(self, bg=config.BG_SIDEBAR, cursor="hand2" if available else "arrow")
            btn_frame.pack(fill=tk.X, pady=2)

            # 选中指示条
            indicator = tk.Frame(btn_frame, width=3,
                                 bg=config.ACCENT if i == 0 else config.BG_SIDEBAR)
            indicator.pack(side=tk.LEFT, fill=tk.Y)

            inner = tk.Frame(btn_frame,
                             bg=config.BG_HOVER if i == 0 else config.BG_SIDEBAR,
                             padx=12, pady=8)
            inner.pack(side=tk.LEFT, fill=tk.X, expand=True)

            icon_lbl = tk.Label(inner, text=icon,
                                font=("Consolas", 12),
                                bg=inner.cget("bg"),
                                fg=config.ACCENT if i == 0 else (config.FG_MUTED if not available else config.FG_SECONDARY))
            icon_lbl.pack(side=tk.LEFT)

            text_frame = tk.Frame(inner, bg=inner.cget("bg"))
            text_frame.pack(side=tk.LEFT, padx=(8, 0))

            name_lbl = tk.Label(text_frame, text=name,
                                font=("Consolas", 9, "bold"),
                                bg=inner.cget("bg"),
                                fg=config.ACCENT if i == 0 else (config.FG_MUTED if not available else config.FG_SECONDARY))
            name_lbl.pack(anchor=tk.W)

            sub_lbl = tk.Label(text_frame, text=sub,
                              font=("Consolas", 7),
                              bg=inner.cget("bg"),
                              fg=config.FG_MUTED)
            sub_lbl.pack(anchor=tk.W)

            self._btns.append({
                "frame": btn_frame, "inner": inner,
                "indicator": indicator,
                "icon": icon_lbl, "name": name_lbl, "sub": sub_lbl,
                "available": available
            })

            if available:
                for w in [btn_frame, inner, icon_lbl, text_frame, name_lbl, sub_lbl]:
                    w.bind("<Button-1>", lambda e, idx=i: self._select(idx))
                    w.bind("<Enter>", lambda e, idx=i: self._hover(idx, True))
                    w.bind("<Leave>", lambda e, idx=i: self._hover(idx, False))

        # 底部版本信息
        tk.Label(self, text="Made for IC Verification\n© 2026",
                font=("Consolas", 7),
                bg=config.BG_SIDEBAR, fg=config.FG_MUTED,
                justify=tk.CENTER).pack(side=tk.BOTTOM, pady=16)

    def _select(self, idx):
        if not self._btns[idx]["available"]:
            return
        old = self._selected
        self._selected = idx

        # 更新旧按钮样式
        ob = self._btns[old]
        ob["indicator"].config(bg=config.BG_SIDEBAR)
        ob["inner"].config(bg=config.BG_SIDEBAR)
        for w in [ob["inner"], ob["icon"], ob["name"], ob["sub"]]:
            w.config(bg=config.BG_SIDEBAR)
        ob["name"].config(fg=config.FG_SECONDARY)
        ob["icon"].config(fg=config.FG_SECONDARY)

        # 更新新按钮样式
        nb = self._btns[idx]
        nb["indicator"].config(bg=config.ACCENT)
        nb["inner"].config(bg=config.BG_HOVER)
        for w in [nb["inner"], nb["icon"], nb["name"], nb["sub"]]:
            w.config(bg=config.BG_HOVER)
        nb["name"].config(fg=config.ACCENT)
        nb["icon"].config(fg=config.ACCENT)

        self.on_select(idx)

    def _hover(self, idx, entering):
        if idx == self._selected:
            return
        b = self._btns[idx]
        if not b["available"]:
            return
        color = config.BG_HOVER if entering else config.BG_SIDEBAR
        b["inner"].config(bg=color)
        for w in [b["icon"], b["name"], b["sub"]]:
            w.config(bg=color)
