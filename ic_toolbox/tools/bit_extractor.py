"""
位字段提取器 - Bit Field Extractor
从寄存器值中提取指定 [hi:lo] 位
"""

import tkinter as tk
from tkinter import ttk
import re
from .. import config


class BitExtractorFrame(tk.Frame):
    """位字段提取器：从一个值中提取指定位的字段"""

    COLOR = "#94e2d5"  # 青色（不同于数据切片的另一个色调）

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=config.BG_DARK, *args, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # ── 标题 ──────────────────────────────
        title_frame = tk.Frame(self, bg=config.BG_DARK)
        title_frame.pack(fill=tk.X, padx=32, pady=(28, 0))

        tk.Label(title_frame, text="◈  位字段提取器",
                font=("Consolas", 20, "bold"),
                bg=config.BG_DARK, fg=self.COLOR).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Bit Field Extractor",
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

        tk.Label(row1, text="  |  ", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 总位宽
        tk.Label(row1, text="总位宽:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="自动")
        width_opts = ["自动", "8", "16", "32", "64", "自定义"]
        self.width_combo = ttk.Combobox(
            row1, textvariable=self.width_var,
            values=width_opts, width=8, state="readonly",
            font=("Consolas", 9)
        )
        self.width_combo.pack(side=tk.LEFT, padx=(6, 0))
        self.width_combo.bind("<<ComboboxSelected>>", self._on_width_change)

        self.width_custom_entry = tk.Entry(
            row1, width=6, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 9), insertbackground=self.COLOR,
            relief=tk.FLAT, bd=4
        )

        # 第二行：数据输入
        row2 = tk.Frame(ic, bg=config.BG_CARD)
        row2.pack(fill=tk.X, pady=(12, 0))

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
        self.data_var.trace_add("write", lambda *a: self._do_extract())

        # 示例按钮
        for label, val, w in [
            ("示例 32b", "DEADBEEF", "32"),
            ("示例 8b", "A5", "8"),
        ]:
            tk.Button(
                row2, text=label,
                command=lambda v=val, ww=w: self._load_example(v, ww),
                bg=config.BG_INPUT, fg=config.FG_MUTED,
                font=("Consolas", 8), relief=tk.FLAT,
                padx=8, pady=2, cursor="hand2",
                activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
            ).pack(side=tk.LEFT, padx=(6, 0))

        # 第三行：位字段范围
        row3 = tk.Frame(ic, bg=config.BG_CARD)
        row3.pack(fill=tk.X, pady=(12, 0))

        tk.Label(row3, text="提取范围:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        # hi 位
        self.hi_var = tk.StringVar()
        hi_entry = tk.Entry(
            row3, textvariable=self.hi_var,
            width=5, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 10), insertbackground=self.COLOR,
            relief=tk.FLAT, bd=4
        )
        hi_entry.pack(side=tk.LEFT, padx=(8, 0))
        hi_entry.bind("<KeyRelease>", lambda e: self._do_extract())

        tk.Label(row3, text=" : ", font=("Consolas", 10, "bold"),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # lo 位
        self.lo_var = tk.StringVar()
        lo_entry = tk.Entry(
            row3, textvariable=self.lo_var,
            width=5, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 10), insertbackground=self.COLOR,
            relief=tk.FLAT, bd=4
        )
        lo_entry.pack(side=tk.LEFT)
        lo_entry.bind("<KeyRelease>", lambda e: self._do_extract())

        tk.Label(row3, text="  (bit)", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        # 快捷按钮
        tk.Label(row3, text="  快捷:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)
        for label, hi, lo in [("31:24", 31, 24), ("23:16", 23, 16), ("15:8", 15, 8), ("7:0", 7, 0)]:
            tk.Button(
                row3, text=label,
                command=lambda h=label: self._set_range(h),
                bg=config.BG_INPUT, fg=config.FG_SECONDARY,
                font=("Consolas", 8), relief=tk.FLAT,
                padx=6, pady=2, cursor="hand2",
                activebackground=config.BG_HOVER, activeforeground=self.COLOR
            ).pack(side=tk.LEFT, padx=(4, 0))

        # 第四行：提取结果显示选项
        row4 = tk.Frame(ic, bg=config.BG_CARD)
        row4.pack(fill=tk.X, pady=(10, 0))

        tk.Label(row4, text="显示:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)
        self.show_hex_var = tk.BooleanVar(value=True)
        self.show_bin_var = tk.BooleanVar(value=True)
        self.show_dec_var = tk.BooleanVar(value=True)
        for text, var in [("HEX", self.show_hex_var), ("BIN", self.show_bin_var), ("DEC", self.show_dec_var)]:
            tk.Checkbutton(
                row4, text=text, variable=var,
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY,
                selectcolor=config.BG_INPUT,
                activebackground=config.BG_CARD,
                command=self._do_extract
            ).pack(side=tk.LEFT, padx=(6, 0))

        # ── 操作按钮 ──────────────────────────
        btn_frame = tk.Frame(self, bg=config.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=32, pady=(12, 0))

        tk.Button(
            btn_frame, text="  提取 Extract",
            command=self._do_extract,
            bg=self.COLOR, fg=config.BG_DARK,
            font=("Consolas", 10, "bold"),
            relief=tk.FLAT, padx=18, pady=6,
            cursor="hand2",
            activebackground=config.FG_PRIMARY, activeforeground=config.BG_DARK
        ).pack(side=tk.LEFT)

        tk.Button(
            btn_frame, text="  清空",
            command=self._clear_all,
            bg=config.BG_INPUT, fg=config.FG_SECONDARY,
            font=("Consolas", 10), relief=tk.FLAT,
            padx=12, pady=6, cursor="hand2",
            activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── 状态行 ────────────────────────────
        self.status_var = tk.StringVar(value="就绪 · 输入数据并指定位范围进行提取")
        tk.Label(self, textvariable=self.status_var,
                font=("Consolas", 9), bg=config.BG_DARK, fg=config.FG_MUTED
                ).pack(fill=tk.X, padx=32, pady=(10, 4), anchor=tk.W)

        # ── 结果区 ────────────────────────────
        result_card = tk.Frame(self, bg=config.BG_CARD)
        result_card.pack(fill=tk.BOTH, expand=True, padx=32, pady=(12, 20))

        tk.Frame(result_card, bg=self.COLOR, width=4).pack(side=tk.LEFT, fill=tk.Y)

        result_inner = tk.Frame(result_card, bg=config.BG_CARD)
        result_inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=14)

        # 结果标题
        tk.Label(result_inner, text="▸ 提取结果",
                font=("Consolas", 10, "bold"),
                bg=config.BG_CARD, fg=self.COLOR).pack(anchor=tk.W, pady=(0, 8))

        # 结果内容框架
        self.result_frame = tk.Frame(result_inner, bg=config.BG_CARD)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        # 初始占位提示
        self._show_placeholder()

    def _show_placeholder(self):
        placeholder = tk.Label(
            self.result_frame,
            text="输入数据后将在此显示提取结果",
            font=("Consolas", 10),
            bg=config.BG_CARD, fg=config.FG_MUTED
        )
        placeholder.pack(pady=20)
        self._result_widget = placeholder

    def _on_fmt_change(self):
        self._do_extract()

    def _on_width_change(self, event=None):
        if self.width_var.get() == "自定义":
            self.width_custom_entry.pack(side=tk.LEFT, padx=(6, 0))
        else:
            self.width_custom_entry.pack_forget()
        self._do_extract()

    def _set_range(self, r):
        """设置位范围，如 '31:24'"""
        hi, lo = r.split(":")
        self.hi_var.set(hi)
        self.lo_var.set(lo)
        self._do_extract()

    def _load_example(self, val, width):
        self.fmt_var.set("HEX")
        self.data_var.set(val)
        self.width_var.set(width)
        self.width_custom_entry.pack_forget()

    def _clear_all(self):
        self.data_var.set("")
        self.hi_var.set("")
        self.lo_var.set("")
        self._show_placeholder()
        self.status_var.set("已清空")

    def _get_total_width(self, bit_len):
        """返回总位宽"""
        w = self.width_var.get()
        if w == "自动":
            return bit_len
        if w == "自定义":
            try:
                return int(self.width_custom_entry.get())
            except ValueError:
                return bit_len
        return int(w)

    def _parse_data(self, raw):
        """解析输入数据，返回 (bit_string, total_width, err_msg)"""
        raw = raw.strip().replace("_", "").replace(" ", "")
        if not raw:
            return None, None, None

        fmt = self.fmt_var.get()
        try:
            if fmt == "HEX":
                raw = re.sub(r"^(0x|0X)", "", raw)
                m = re.match(r"^\d*'[hH]([0-9a-fA-F]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[0-9a-fA-F]+", raw):
                    return None, None, "HEX 数据包含非法字符"

                bit_str = bin(int(raw, 16))[2:]
                # 补到 4 的倍数
                pad = (4 - len(bit_str) % 4) % 4
                bit_str = bit_str.zfill(len(bit_str) + pad)
                total_w = len(bit_str)
            else:  # BIN
                raw = re.sub(r"^(0b|0B)", "", raw)
                m = re.match(r"^\d*'[bB]([01]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[01]+", raw):
                    return None, None, "BIN 数据包含非法字符"

                bit_str = raw
                total_w = len(bit_str)

            # 应用总位宽设置
            total_w = self._get_total_width(total_w)
            if len(bit_str) < total_w:
                bit_str = bit_str.zfill(total_w)
            elif len(bit_str) > total_w:
                bit_str = bit_str[-total_w:]

            return bit_str, total_w, None

        except Exception as e:
            return None, None, str(e)

    def _do_extract(self, *_):
        """执行位字段提取"""
        raw_data = self.data_var.get()
        raw_hi = self.hi_var.get().strip()
        raw_lo = self.lo_var.get().strip()

        # 解析数据
        bit_str, total_w, err = self._parse_data(raw_data)

        if err:
            self._show_error(f"⚠  {err}")
            return

        if bit_str is None:
            self._show_placeholder()
            self.status_var.set("就绪 · 输入数据并指定位范围进行提取")
            return

        # 解析位范围
        if not raw_hi or not raw_lo:
            self._show_placeholder()
            self.status_var.set("请输入要提取的位范围 [hi:lo]")
            return

        try:
            hi = int(raw_hi)
            lo = int(raw_lo)
        except ValueError:
            self._show_error("⚠  位范围须为整数")
            return

        # 验证位范围
        if hi < lo:
            self._show_error("⚠  hi 必须 >= lo")
            return
        if hi >= total_w:
            self._show_error(f"⚠  hi ({hi}) 超出总位宽 ({total_w})")
            return
        if lo < 0:
            self._show_error("⚠  lo 不能为负数")
            return

        # 提取字段
        # 注意：bit_str[0] 是最高位，bit_str[total_w-1] 是最低位
        # hi:lo 表示从 hi 位到 lo 位
        field_str = bit_str[total_w - 1 - hi : total_w - lo]  # 从高位到低位
        if not field_str:
            field_str = "0"

        # 转换为整数
        field_val = int(field_str, 2)
        field_width = hi - lo + 1

        # 格式化输出
        hex_str = hex(field_val)[2:].upper().zfill((field_width + 3) // 4)
        bin_str = field_str

        # 显示结果
        self._show_result(bit_str, total_w, hi, lo, field_val, hex_str, bin_str, field_width)

        self.status_var.set(
            f"✓  从 [{total_w-1}:0] 中提取 [{hi}:{lo}]，"
            f"字段宽度 {field_width} bit"
        )

    def _show_placeholder(self):
        """显示占位提示"""
        if hasattr(self, '_result_widget') and self._result_widget:
            self._result_widget.destroy()

        placeholder = tk.Label(
            self.result_frame,
            text="输入数据后将在此显示提取结果",
            font=("Consolas", 10),
            bg=config.BG_CARD, fg=config.FG_MUTED
        )
        placeholder.pack(pady=20)
        self._result_widget = placeholder

    def _show_error(self, msg):
        """显示错误信息"""
        if hasattr(self, '_result_widget') and self._result_widget:
            self._result_widget.destroy()

        err_lbl = tk.Label(
            self.result_frame,
            text=msg,
            font=("Consolas", 10),
            bg=config.BG_CARD, fg=config.ACCENT3
        )
        err_lbl.pack(pady=20)
        self._result_widget = err_lbl
        self.status_var.set(msg)

    def _show_result(self, bit_str, total_w, hi, lo, field_val, hex_str, bin_str, field_width):
        """显示提取结果"""
        if hasattr(self, '_result_widget') and self._result_widget:
            self._result_widget.destroy()

        # 容器
        container = tk.Frame(self.result_frame, bg=config.BG_CARD)
        container.pack(fill=tk.BOTH, expand=True)
        self._result_widget = container

        # 可滚动区域
        canvas = tk.Canvas(container, bg=config.BG_CARD, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=config.BG_CARD)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=e.width)

        inner.bind("<Configure>", on_configure)

        # 1. 原始数据概览
        tk.Label(inner, text="原始数据:",
                font=("Consolas", 9, "bold"),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(anchor=tk.W, pady=(0, 4))

        # 原始数据可视化
        orig_frame = tk.Frame(inner, bg=config.BG_CARD)
        orig_frame.pack(fill=tk.X, pady=(0, 10))

        # 按 4 位分组显示
        groups = [bit_str[max(0, i-4):i] for i in range(len(bit_str), 0, -4)][::-1]
        grouped_bits = "_".join(groups)

        tk.Label(orig_frame, text=grouped_bits,
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_PRIMARY,
                anchor=tk.W).pack(side=tk.LEFT)

        # 位号标注
        bit_labels = tk.Frame(inner, bg=config.BG_CARD)
        bit_labels.pack(fill=tk.X)
        for i in range(total_w - 1, -1, -4):
            label_text = f"{i}"
            tk.Label(bit_labels, text=f"[{label_text:>2}]  ",
                    font=("Consolas", 7),
                    bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 2. 提取范围可视化
        tk.Label(inner, text="提取范围:",
                font=("Consolas", 9, "bold"),
                bg=config.BG_CARD, fg=config.FG_SECONDARY
                ).pack(anchor=tk.W, pady=(10, 4))

        range_frame = tk.Frame(inner, bg=config.BG_CARD)
        range_frame.pack(fill=tk.X, pady=(0, 10))

        # 生成带高亮的位视图
        highlight_bits = ""
        for i in range(total_w - 1, -1, -1):
            if hi >= i >= lo:
                highlight_bits += f"[{i}]"
            else:
                highlight_bits += f" {i} "

        tk.Label(range_frame, text=highlight_bits,
                font=("Consolas", 8),
                bg=config.BG_CARD, fg=config.FG_MUTED,
                anchor=tk.W).pack(side=tk.LEFT)

        # 3. 提取结果
        tk.Label(inner, text="提取结果:",
                font=("Consolas", 9, "bold"),
                bg=config.BG_CARD, fg=self.COLOR
                ).pack(anchor=tk.W, pady=(10, 4))

        result_items = []
        if self.show_hex_var.get():
            result_items.append(("HEX", hex_str, config.ACCENT4))
        if self.show_bin_var.get():
            result_items.append(("BIN", bin_str, config.ACCENT2))
        if self.show_dec_var.get():
            result_items.append(("DEC", str(field_val), config.ACCENT))

        for label, value, color in result_items:
            row = tk.Frame(inner, bg=config.BG_CARD)
            row.pack(fill=tk.X, pady=2)

            tk.Label(row, text=f"{label}:",
                    font=("Consolas", 10, "bold"),
                    bg=config.BG_CARD, fg=color,
                    width=6, anchor=tk.W).pack(side=tk.LEFT)

            val_lbl = tk.Label(row, text=value,
                    font=("Consolas", 11, "bold"),
                    bg=config.BG_CARD, fg=config.FG_PRIMARY)
            val_lbl.pack(side=tk.LEFT)

            # 复制功能
            def make_copy(v=value):
                return lambda: self._copy_to_clipboard(v)

            tk.Button(row, text="📋",
                    command=make_copy(),
                    bg=config.BG_INPUT, fg=config.FG_MUTED,
                    font=("Consolas", 8), relief=tk.FLAT,
                    padx=6, cursor="hand2",
                    activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
                    ).pack(side=tk.LEFT, padx=(8, 0))

        # 4. 字段信息
        info_frame = tk.Frame(inner, bg=config.BG_CARD, pady=10)
        info_frame.pack(fill=tk.X)

        tk.Label(info_frame,
                text=f"字段位置: [{hi}:{lo}]  |  字段宽度: {field_width} bit  |  "
                     f"占原数据比例: {field_width/total_w*100:.1f}%",
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(anchor=tk.W)

    def _copy_to_clipboard(self, value):
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(value)
        self.status_var.set(f"✓  已复制: {value}")
