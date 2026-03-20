"""
数据切片器 - Data Slicer
将二进制/十六进制数据按固定位宽切片
"""

import tkinter as tk
from tkinter import ttk
import re
from .. import config


class DataSlicerFrame(tk.Frame):
    """数据切片器：将一段二进制/十六进制数据按固定位宽切片"""

    COLOR  = config.COLOR_SLICER   # 青色主题
    COLOR2 = config.COLOR_SHIFT    # 紫色辅助

    SLICE_WIDTHS = ["4", "8", "16", "32", "64", "自定义"]

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=config.BG_DARK, *args, **kwargs)
        self._slice_widgets = []   # 存放切片卡片，用于动态刷新
        self._build_ui()

    # ──────────────────── UI ─────────────────

    def _build_ui(self):
        # ── 标题 ──────────────────────────────
        title_frame = tk.Frame(self, bg=config.BG_DARK)
        title_frame.pack(fill=tk.X, padx=32, pady=(28, 0))

        tk.Label(title_frame, text="⊡  数据切片器",
                font=("Consolas", 20, "bold"),
                bg=config.BG_DARK, fg=self.COLOR).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Data Slicer",
                font=("Consolas", 11),
                bg=config.BG_DARK, fg=config.FG_MUTED).pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=32, pady=(12, 0))

        # ── 输入区 ────────────────────────────
        input_card = tk.Frame(self, bg=config.BG_CARD)
        input_card.pack(fill=tk.X, padx=32, pady=(18, 0))

        tk.Frame(input_card, bg=self.COLOR, width=4).pack(side=tk.LEFT, fill=tk.Y)

        ic = tk.Frame(input_card, bg=config.BG_CARD)
        ic.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=14)

        # 第一行：输入格式 + 总位宽
        row1 = tk.Frame(ic, bg=config.BG_CARD)
        row1.pack(fill=tk.X)

        # 输入格式
        tk.Label(row1, text="输入格式:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.fmt_var = tk.StringVar(value="HEX")
        for fmt in ["HEX", "BIN"]:
            tk.Radiobutton(
                row1, text=fmt, variable=self.fmt_var, value=fmt,
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_PRIMARY,
                selectcolor=config.BG_INPUT,
                activebackground=config.BG_CARD,
                command=self._on_fmt_change
            ).pack(side=tk.LEFT, padx=(8, 0))

        # 分隔
        tk.Label(row1, text="  |  ", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 总位宽
        tk.Label(row1, text="总位宽:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.total_width_var = tk.StringVar(value="自动")
        tw_opts = ["自动", "8", "16", "32", "64", "128", "256", "512", "1024", "自定义"]
        self.tw_combo = ttk.Combobox(
            row1, textvariable=self.total_width_var,
            values=tw_opts, width=8, state="readonly",
            font=("Consolas", 9)
        )
        self.tw_combo.pack(side=tk.LEFT, padx=(6, 0))
        self.tw_combo.bind("<<ComboboxSelected>>", self._on_tw_change)

        self.tw_custom_entry = tk.Entry(
            row1, width=6, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 9), insertbackground=self.COLOR,
            relief=tk.FLAT, bd=4
        )

        # 字节序
        tk.Label(row1, text="  字节序:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.endian_var = tk.StringVar(value="Big-Endian")
        for e in ["Big-Endian", "Little-Endian"]:
            tk.Radiobutton(
                row1, text=e, variable=self.endian_var, value=e,
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_PRIMARY,
                selectcolor=config.BG_INPUT,
                activebackground=config.BG_CARD,
                command=self._do_slice
            ).pack(side=tk.LEFT, padx=(8, 0))

        # 第二行：数据输入框
        row2 = tk.Frame(ic, bg=config.BG_CARD)
        row2.pack(fill=tk.X, pady=(10, 0))

        tk.Label(row2, text="数据:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        self.data_var = tk.StringVar()
        self.data_entry = tk.Entry(
            row2, textvariable=self.data_var,
            font=("Consolas", 13),
            bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            insertbackground=self.COLOR,
            relief=tk.FLAT, bd=6,
            selectbackground=config.ACCENT,
            selectforeground=config.BG_DARK
        )
        self.data_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        self.data_var.trace_add("write", lambda *a: self._do_slice())

        # 示例按钮
        for label, val, fmt in [
            ("示例 HEX", "DEADBEEF_CAFEBABE", "HEX"),
            ("示例 BIN", "1100_1010_1111_0000", "BIN"),
        ]:
            tk.Button(
                row2, text=label,
                command=lambda v=val, f=fmt: self._load_example(v, f),
                bg=config.BG_INPUT, fg=config.FG_MUTED,
                font=("Consolas", 8), relief=tk.FLAT,
                padx=8, pady=2, cursor="hand2",
                activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
            ).pack(side=tk.LEFT, padx=(6, 0))

        # 第三行：切片宽度
        row3 = tk.Frame(ic, bg=config.BG_CARD)
        row3.pack(fill=tk.X, pady=(10, 0))

        tk.Label(row3, text="切片宽度:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        self.slice_width_var = tk.StringVar(value="8")
        self.sw_combo = ttk.Combobox(
            row3, textvariable=self.slice_width_var,
            values=self.SLICE_WIDTHS, width=8, state="readonly",
            font=("Consolas", 9)
        )
        self.sw_combo.pack(side=tk.LEFT, padx=(6, 0))
        self.sw_combo.bind("<<ComboboxSelected>>", self._on_sw_change)

        self.sw_custom_entry = tk.Entry(
            row3, width=6, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 9), insertbackground=self.COLOR,
            relief=tk.FLAT, bd=4
        )

        # 快捷宽度按钮
        tk.Label(row3, text="  快捷:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)
        for w in [4, 8, 16, 32, 64]:
            tk.Button(
                row3, text=f"{w}b",
                command=lambda v=w: self._set_slice_width(v),
                bg=config.BG_INPUT, fg=config.FG_SECONDARY,
                font=("Consolas", 9), relief=tk.FLAT,
                padx=6, pady=2, cursor="hand2",
                activebackground=config.BG_HOVER, activeforeground=self.COLOR
            ).pack(side=tk.LEFT, padx=(4, 0))

        # 显示选项
        tk.Label(row3, text="  显示:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)
        self.show_bin_var = tk.BooleanVar(value=True)
        self.show_dec_var = tk.BooleanVar(value=True)
        for text, var in [("BIN", self.show_bin_var), ("DEC", self.show_dec_var)]:
            tk.Checkbutton(
                row3, text=text, variable=var,
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY,
                selectcolor=config.BG_INPUT,
                activebackground=config.BG_CARD,
                command=self._do_slice
            ).pack(side=tk.LEFT, padx=(6, 0))

        # ── 状态行 ────────────────────────────
        self.status_var = tk.StringVar(value="就绪 · 输入数据后自动切片")
        tk.Label(self, textvariable=self.status_var,
                font=("Consolas", 9), bg=config.BG_DARK, fg=config.FG_MUTED
                ).pack(fill=tk.X, padx=32, pady=(10, 4), anchor=tk.W)

        # ── 结果区（可滚动） ──────────────────
        result_outer = tk.Frame(self, bg=config.BG_DARK)
        result_outer.pack(fill=tk.BOTH, expand=True, padx=32, pady=(0, 16))

        # Canvas + Scrollbar
        self._canvas = tk.Canvas(result_outer, bg=config.BG_DARK,
                                 highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(result_outer, orient=tk.VERTICAL,
                                  command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._result_frame = tk.Frame(self._canvas, bg=config.BG_DARK)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._result_frame, anchor=tk.NW)

        self._result_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        # 鼠标滚轮
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # ──────────────────── Events ──────────────

    def _on_frame_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_fmt_change(self):
        self.data_var.set("")
        self._do_slice()

    def _on_tw_change(self, event=None):
        if self.total_width_var.get() == "自定义":
            self.tw_custom_entry.pack(side=tk.LEFT, padx=(6, 0))
        else:
            self.tw_custom_entry.pack_forget()
        self._do_slice()

    def _on_sw_change(self, event=None):
        if self.slice_width_var.get() == "自定义":
            self.sw_custom_entry.pack(side=tk.LEFT, padx=(6, 0))
            self.sw_custom_entry.bind("<Return>", lambda e: self._do_slice())
        else:
            self.sw_custom_entry.pack_forget()
        self._do_slice()

    def _set_slice_width(self, w):
        self.slice_width_var.set(str(w))
        self.sw_custom_entry.pack_forget()
        self._do_slice()

    def _load_example(self, val, fmt):
        self.fmt_var.set(fmt)
        self.data_var.set(val)

    # ──────────────────── Core Logic ──────────

    def _get_slice_width(self):
        v = self.slice_width_var.get()
        if v == "自定义":
            try:
                return int(self.sw_custom_entry.get())
            except ValueError:
                return 8
        return int(v)

    def _get_total_width(self, bit_len):
        """返回有效总位宽。'自动'时用实际数据位数，'自定义'读输入框"""
        tv = self.total_width_var.get()
        if tv == "自动":
            return bit_len
        if tv == "自定义":
            try:
                return int(self.tw_custom_entry.get())
            except ValueError:
                return bit_len
        return int(tv)

    def _parse_data(self, raw):
        """返回 (bit_string, err_msg)"""
        raw = raw.strip().replace("_", "").replace(" ", "")
        if not raw:
            return None, None
        fmt = self.fmt_var.get()
        try:
            if fmt == "HEX":
                # 支持 0x 前缀 和 Verilog h 格式
                raw = re.sub(r"^(0x|0X)", "", raw)
                m = re.match(r"^\d*'[hH]([0-9a-fA-F]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[0-9a-fA-F]+", raw):
                    return None, "HEX 数据包含非法字符"
                bit_str = bin(int(raw, 16))[2:]
                # 补齐到 4 的整数倍（每个 hex digit = 4 bit）
                pad = (4 - len(bit_str) % 4) % 4
                bit_str = bit_str.zfill(len(bit_str) + pad)
            else:  # BIN
                raw = re.sub(r"^(0b|0B)", "", raw)
                m = re.match(r"^\d*'[bB]([01]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[01]+", raw):
                    return None, "BIN 数据包含非法字符（只允许 0/1）"
                bit_str = raw
            return bit_str, None
        except Exception as e:
            return None, str(e)

    def _do_slice(self, *_):
        """主切片逻辑，刷新结果区"""
        raw = self.data_var.get()
        bit_str, err = self._parse_data(raw)

        # 清空旧结果
        for w in self._slice_widgets:
            w.destroy()
        self._slice_widgets.clear()

        if err:
            self.status_var.set(f"⚠  {err}")
            return
        if bit_str is None:
            self.status_var.set("就绪 · 输入数据后自动切片")
            return

        slice_w   = self._get_slice_width()
        total_w   = self._get_total_width(len(bit_str))

        # 补零或截断到 total_w
        if len(bit_str) < total_w:
            bit_str = bit_str.zfill(total_w)
        elif len(bit_str) > total_w:
            bit_str = bit_str[-total_w:]   # 保留低位

        if slice_w <= 0 or slice_w > total_w:
            self.status_var.set(f"⚠  切片宽度 {slice_w} 超出总位宽 {total_w}")
            return

        # 切片
        slices = []
        for i in range(0, total_w, slice_w):
            end   = min(i + slice_w, total_w)
            chunk = bit_str[total_w - end: total_w - i]   # 从高位到低位
            slices.append(chunk)

        # 字节序处理
        if self.endian_var.get() == "Little-Endian":
            slices = slices[::-1]

        n_slices = len(slices)
        self.status_var.set(
            f"✓  总位宽 {total_w} bit  |  切片宽度 {slice_w} bit  |  共 {n_slices} 片  "
            f"|  {self.endian_var.get()}"
        )

        # ── 渲染结果 ──────────────────────────
        # 表头
        header = tk.Frame(self._result_frame, bg=config.BG_DARK)
        header.pack(fill=tk.X, pady=(4, 6))
        self._slice_widgets.append(header)

        cols = [("#",    4,  config.FG_MUTED),
                ("Bit Range", 12, config.FG_MUTED),
                ("HEX",  10, config.ACCENT4),
                ("BIN",  slice_w * 1 + 4, config.ACCENT2),
                ("DEC (U)", 12, config.ACCENT),
                ("DEC (S)", 12, self.COLOR2)]
        if not self.show_bin_var.get():
            cols = [c for c in cols if c[0] != "BIN"]
        if not self.show_dec_var.get():
            cols = [c for c in cols if c[0] not in ("DEC (U)", "DEC (S)")]

        for col_text, col_w, col_fg in cols:
            tk.Label(header, text=col_text, width=col_w,
                    font=("Consolas", 8, "bold"),
                    bg=config.BG_DARK, fg=col_fg,
                    anchor=tk.W).pack(side=tk.LEFT)

        ttk.Separator(self._result_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=(0, 4))
        self._slice_widgets.append(
            self._result_frame.winfo_children()[-1])

        # 每一片
        show_bin = self.show_bin_var.get()
        show_dec = self.show_dec_var.get()

        # 颜色循环，让相邻行有区分
        row_colors = [config.BG_CARD, config.BG_DARK]

        for idx, chunk in enumerate(slices):
            # 位范围标注（基于原始 Big-Endian 索引）
            if self.endian_var.get() == "Big-Endian":
                hi = total_w - 1 - idx * slice_w
                lo = max(total_w - (idx + 1) * slice_w, 0)
            else:
                lo = idx * slice_w
                hi = min((idx + 1) * slice_w - 1, total_w - 1)

            hex_val  = hex(int(chunk, 2))[2:].upper().zfill((len(chunk) + 3) // 4)
            dec_u    = int(chunk, 2)
            dec_s    = dec_u - (1 << len(chunk)) if dec_u >= (1 << (len(chunk) - 1)) else dec_u

            row_bg = row_colors[idx % 2]
            row = tk.Frame(self._result_frame, bg=row_bg, pady=2)
            row.pack(fill=tk.X)
            self._slice_widgets.append(row)

            cells = [
                (f"[{idx}]",         4,  config.FG_MUTED,    None),
                (f"[{hi}:{lo}]",     12, config.FG_SECONDARY, None),
                (hex_val,            10, config.ACCENT4,      f"HEX: {hex_val}"),
            ]
            if show_bin:
                # BIN 每4位加空格
                bin_spaced = " ".join(
                    chunk[max(0, i-4):i] for i in range(len(chunk), 0, -4)
                )[::-1].replace(" ", " ")
                # 更简洁的分组
                grps = [chunk[i:i+4] for i in range(0, len(chunk), 4)]
                bin_display = "_".join(grps)
                cells.append((bin_display, slice_w + 4, config.ACCENT2, f"BIN: {chunk}"))
            if show_dec:
                cells.append((str(dec_u),  12, config.ACCENT,      f"DEC(U): {dec_u}"))
                cells.append((str(dec_s),  12, self.COLOR2,  f"DEC(S): {dec_s}"))

            for cell_text, cell_w, cell_fg, copy_val in cells:
                lbl = tk.Label(
                    row, text=cell_text, width=cell_w,
                    font=("Consolas", 9),
                    bg=row_bg, fg=cell_fg,
                    anchor=tk.W, cursor="hand2" if copy_val else "arrow"
                )
                lbl.pack(side=tk.LEFT)
                if copy_val:
                    lbl.bind("<Button-1>",
                            lambda e, v=copy_val: self._copy_cell(v))
                    lbl.bind("<Enter>",
                            lambda e, w=lbl, bg=row_bg: w.config(bg=config.BG_HOVER))
                    lbl.bind("<Leave>",
                            lambda e, w=lbl, bg=row_bg: w.config(bg=bg))

        # 滚动到顶部
        self._canvas.yview_moveto(0)

    def _copy_cell(self, val):
        """复制单元格内容"""
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(val.split(": ", 1)[-1])
        self.status_var.set(f"✓  已复制: {val}")
