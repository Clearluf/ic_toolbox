"""
进制转换器 - Base Converter
支持 BIN/OCT/DEC/HEX 进制转换，Verilog 格式，补码，前导零，移位操作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from .. import config


class BaseConverterFrame(tk.Frame):
    """进制转换工具"""

    BASES = [
        ("BIN  二进制", 2,  "01",                 config.COLOR_CONVERTER),
        ("OCT  八进制", 8,  "0-7",                "#89dceb"),
        ("DEC  十进制", 10, "0-9",                config.ACCENT),
        ("HEX  十六进制", 16, "0-9, A-F",         config.ACCENT4),
    ]

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=config.BG_DARK, *args, **kwargs)
        self._updating = False
        self._build_ui()

    def _build_ui(self):
        # ── 标题区 ────────────────────────────────
        title_frame = tk.Frame(self, bg=config.BG_DARK)
        title_frame.pack(fill=tk.X, padx=32, pady=(28, 0))

        tk.Label(
            title_frame, text="⇄  进制转换器",
            font=("Consolas", 20, "bold"),
            bg=config.BG_DARK, fg=config.COLOR_CONVERTER
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="Base Converter",
            font=("Consolas", 11),
            bg=config.BG_DARK, fg=config.FG_MUTED
        ).pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=32, pady=(12, 0))

        # ── 位宽选择 ──────────────────────────────
        opt_frame = tk.Frame(self, bg=config.BG_DARK)
        opt_frame.pack(fill=tk.X, padx=32, pady=(16, 0))

        tk.Label(opt_frame, text="位宽  Width:",
                 font=("Consolas", 10), bg=config.BG_DARK, fg=config.FG_SECONDARY
                 ).pack(side=tk.LEFT)

        self.width_var = tk.StringVar(value="32")
        width_opts = ["4", "8", "16", "32", "64", "自定义"]
        self.width_combo = ttk.Combobox(
            opt_frame, textvariable=self.width_var,
            values=width_opts, width=8, state="readonly",
            font=("Consolas", 10)
        )
        self.width_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.width_combo.bind("<<ComboboxSelected>>", self._on_width_change)

        self.custom_width_entry = tk.Entry(
            opt_frame, width=6, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 10), insertbackground=config.FG_PRIMARY,
            relief=tk.FLAT, bd=4
        )
        # 只有选"自定义"时才显示

        # 有符号/无符号
        self.signed_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt_frame, text="有符号（补码）Signed",
            variable=self.signed_var,
            font=("Consolas", 10),
            bg=config.BG_DARK, fg=config.FG_SECONDARY,
            selectcolor=config.BG_INPUT,
            activebackground=config.BG_DARK,
            activeforeground=config.FG_PRIMARY,
            command=self._refresh_all
        ).pack(side=tk.LEFT, padx=(24, 0))

        # Verilog 格式输出开关
        self.verilog_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opt_frame, text="Verilog 格式",
            variable=self.verilog_var,
            font=("Consolas", 10),
            bg=config.BG_DARK, fg=config.FG_SECONDARY,
            selectcolor=config.BG_INPUT,
            activebackground=config.BG_DARK,
            activeforeground=config.FG_PRIMARY,
            command=self._refresh_all
        ).pack(side=tk.LEFT, padx=(24, 0))

        # 前导零开关
        self.leading_zero_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opt_frame, text="前导零 Leading Zeros",
            variable=self.leading_zero_var,
            font=("Consolas", 10),
            bg=config.BG_DARK, fg=config.FG_SECONDARY,
            selectcolor=config.BG_INPUT,
            activebackground=config.BG_DARK,
            activeforeground=config.FG_PRIMARY,
            command=self._refresh_all
        ).pack(side=tk.LEFT, padx=(24, 0))

        # ── 输入/输出区 ───────────────────────────
        cards_frame = tk.Frame(self, bg=config.BG_DARK)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=(20, 0))

        # 配置列权重，让两列等宽
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)

        self.entries = {}   # base -> StringVar
        self.entry_widgets = {}

        for idx, (label, base, hint, color) in enumerate(self.BASES):
            row, col = divmod(idx, 2)
            self._build_card(cards_frame, row, col, label, base, hint, color)

        # ── 操作按钮 ──────────────────────────────
        btn_frame = tk.Frame(self, bg=config.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=32, pady=(20, 0))

        def styled_btn(parent, text, cmd, color):
            return tk.Button(
                parent, text=text, command=cmd,
                bg=color, fg=config.BG_DARK,
                font=("Consolas", 10, "bold"),
                relief=tk.FLAT, padx=16, pady=6,
                cursor="hand2",
                activebackground=config.FG_PRIMARY,
                activeforeground=config.BG_DARK
            )

        styled_btn(btn_frame, "  清空 Clear", self._clear_all, config.FG_MUTED
                   ).pack(side=tk.LEFT, padx=(0, 12))
        styled_btn(btn_frame, "  复制 HEX", self._copy_hex, config.ACCENT4
                   ).pack(side=tk.LEFT, padx=(0, 12))
        styled_btn(btn_frame, "  复制 BIN", self._copy_bin, config.ACCENT2
                   ).pack(side=tk.LEFT, padx=(0, 12))

        # ── 移位操作面板 ──────────────────────────
        self._build_shift_panel()

        # ── 状态栏 ────────────────────────────────
        self.status_var = tk.StringVar(value="就绪 · 在任意输入框中输入数值，其余进制自动更新")
        tk.Label(
            self, textvariable=self.status_var,
            font=("Consolas", 9), bg=config.BG_DARK, fg=config.FG_MUTED
        ).pack(fill=tk.X, padx=32, pady=(12, 16), anchor=tk.W)

        # ── 快速参考表 ────────────────────────────
        self._build_quick_ref()

    def _build_card(self, parent, row, col, label, base, hint, color):
        """构建单个进制卡片"""
        card = tk.Frame(parent, bg=config.BG_CARD, bd=0, relief=tk.FLAT)
        card.grid(row=row, column=col, padx=(0 if col == 0 else 10, 0),
                  pady=(0, 12), sticky=tk.NSEW)
        parent.rowconfigure(row, weight=1)

        # 左侧彩色指示条
        indicator = tk.Frame(card, bg=color, width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(card, bg=config.BG_CARD)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=12)

        # 标签行
        lbl_frame = tk.Frame(content, bg=config.BG_CARD)
        lbl_frame.pack(fill=tk.X)
        tk.Label(lbl_frame, text=label, font=("Consolas", 11, "bold"),
                 bg=config.BG_CARD, fg=color).pack(side=tk.LEFT)
        tk.Label(lbl_frame, text=f"  [{hint}]", font=("Consolas", 9),
                 bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 输入框
        var = tk.StringVar()
        entry = tk.Entry(
            content, textvariable=var,
            font=("Consolas", 14),
            bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            insertbackground=color,
            relief=tk.FLAT, bd=6,
            selectbackground=config.ACCENT,
            selectforeground=config.BG_DARK
        )
        entry.pack(fill=tk.X, pady=(6, 0))

        # Verilog 格式输出标签
        verilog_lbl = tk.Label(content, text="", font=("Consolas", 9),
                               bg=config.BG_CARD, fg=config.FG_MUTED)
        verilog_lbl.pack(fill=tk.X, pady=(4, 0))

        self.entries[base] = var
        self.entry_widgets[base] = {
            "entry": entry,
            "verilog_lbl": verilog_lbl,
            "color": color
        }

        # 绑定事件：输入时触发转换
        var.trace_add("write", lambda *a, b=base: self._on_input(b))

    def _build_shift_panel(self):
        """移位操作面板"""
        shift_frame = tk.Frame(self, bg=config.BG_CARD, bd=0)
        shift_frame.pack(fill=tk.X, padx=32, pady=(14, 0))

        # 左侧彩色条
        tk.Frame(shift_frame, bg=config.COLOR_SHIFT, width=4).pack(side=tk.LEFT, fill=tk.Y)

        inner = tk.Frame(shift_frame, bg=config.BG_CARD)
        inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=10)

        # 标题行
        hdr = tk.Frame(inner, bg=config.BG_CARD)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⇐⇒  移位操作  Shift",
                font=("Consolas", 10, "bold"),
                bg=config.BG_CARD, fg=config.COLOR_SHIFT).pack(side=tk.LEFT)

        # 控件行
        ctrl = tk.Frame(inner, bg=config.BG_CARD)
        ctrl.pack(fill=tk.X, pady=(8, 0))

        # 移位类型选择
        tk.Label(ctrl, text="类型:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        self.shift_type_var = tk.StringVar(value="逻辑左移 <<")
        shift_types = ["逻辑左移 <<", "逻辑右移 >>", "算术右移 >>>"]
        shift_combo = ttk.Combobox(
            ctrl, textvariable=self.shift_type_var,
            values=shift_types, width=14, state="readonly",
            font=("Consolas", 9)
        )
        shift_combo.pack(side=tk.LEFT, padx=(6, 0))

        # 位数输入
        tk.Label(ctrl, text="  位数:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)

        self.shift_amount_var = tk.StringVar(value="1")
        shift_entry = tk.Entry(
            ctrl, textvariable=self.shift_amount_var,
            width=5, bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            font=("Consolas", 10), insertbackground=config.COLOR_SHIFT,
            relief=tk.FLAT, bd=4
        )
        shift_entry.pack(side=tk.LEFT, padx=(6, 0))

        # 快捷位数按钮
        for n in [1, 2, 4, 8]:
            tk.Button(
                ctrl, text=str(n),
                command=lambda v=n: self._set_shift_amount(v),
                bg=config.BG_INPUT, fg=config.FG_SECONDARY,
                font=("Consolas", 9), relief=tk.FLAT,
                padx=6, pady=2, cursor="hand2",
                activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
            ).pack(side=tk.LEFT, padx=(4, 0))

        # 执行按钮
        tk.Button(
            ctrl, text="  执行  Apply",
            command=self._do_shift,
            bg=config.COLOR_SHIFT, fg=config.BG_DARK,
            font=("Consolas", 9, "bold"),
            relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2",
            activebackground=config.FG_PRIMARY, activeforeground=config.BG_DARK
        ).pack(side=tk.LEFT, padx=(16, 0))

        # 结果显示行
        res_frame = tk.Frame(inner, bg=config.BG_CARD)
        res_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Label(res_frame, text="结果:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        self.shift_result_var = tk.StringVar(value="—")
        shift_result_lbl = tk.Label(
            res_frame, textvariable=self.shift_result_var,
            font=("Consolas", 10, "bold"),
            bg=config.BG_CARD, fg=config.COLOR_SHIFT
        )
        shift_result_lbl.pack(side=tk.LEFT, padx=(8, 0))

        # 回填按钮
        tk.Button(
            res_frame, text="↩ 回填",
            command=self._shift_fill_back,
            bg=config.BG_INPUT, fg=config.FG_SECONDARY,
            font=("Consolas", 9), relief=tk.FLAT,
            padx=8, pady=2, cursor="hand2",
            activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
        ).pack(side=tk.LEFT, padx=(12, 0))

        self._shift_result_int = None   # 存储整数结果供回填用

    def _set_shift_amount(self, n):
        self.shift_amount_var.set(str(n))

    def _do_shift(self):
        """执行移位操作"""
        # 取当前值（优先 DEC，其次找有值的框）
        cur_val = None
        for b in [10, 16, 2, 8]:
            raw = self.entries[b].get().strip()
            if raw:
                cur_val = self._parse_input(raw, b)
                break

        if cur_val is None:
            self.shift_result_var.set("⚠ 请先输入数值")
            return

        try:
            amount = int(self.shift_amount_var.get())
            if amount < 0:
                raise ValueError
        except ValueError:
            self.shift_result_var.set("⚠ 位数须为非负整数")
            return

        width = self._get_width()
        signed = self.signed_var.get()
        shift_type = self.shift_type_var.get()
        mask = (1 << width) - 1

        if "左移" in shift_type:
            result = (cur_val << amount) & mask
        elif "算术右移" in shift_type:
            # 算术右移：保留符号位
            if signed and cur_val >= (1 << (width - 1)):
                # 负数补码
                raw_signed = cur_val - (1 << width)
                result_signed = raw_signed >> amount
                result = result_signed & mask
            else:
                result = cur_val >> amount
        else:
            # 逻辑右移
            result = (cur_val & mask) >> amount

        self._shift_result_int = result

        # 格式化结果显示
        bin_str  = bin(result)[2:].zfill(width) if self.leading_zero_var.get() else bin(result)[2:]
        hex_str  = hex(result)[2:].upper().zfill(width // 4) if self.leading_zero_var.get() else hex(result)[2:].upper()
        dec_val  = result - (1 << width) if (signed and result >= (1 << (width - 1))) else result

        # 二进制每4位加下划线
        bin_grouped = "_".join(bin_str[max(0, i-4):i] for i in range(len(bin_str), 0, -4))[::-1].lstrip("_")

        self.shift_result_var.set(
            f"DEC: {dec_val}   HEX: {hex_str}   BIN: {bin_grouped}"
        )

    def _shift_fill_back(self):
        """将移位结果回填到转换器"""
        if self._shift_result_int is None:
            return
        self._updating = True
        self.entries[10].set(str(self._shift_result_int))
        self._updating = False
        self._on_input(10)
        self.status_var.set(f"✓  已回填移位结果: {self._shift_result_int}")

    def _build_quick_ref(self):
        """构建十六进制快速参考表"""
        ref_frame = tk.Frame(self, bg=config.BG_CARD, bd=0)
        ref_frame.pack(fill=tk.X, padx=32, pady=(0, 24))

        header = tk.Frame(ref_frame, bg=config.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="▸ 十六进制快速参考表  Hex Quick Reference",
                font=("Consolas", 9, "bold"),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        table_frame = tk.Frame(ref_frame, bg=config.BG_CARD)
        table_frame.pack(fill=tk.X, padx=12, pady=(6, 10))

        ref_data = [
            ("DEC", [str(i) for i in range(16)]),
            ("HEX", [hex(i)[2:].upper() for i in range(16)]),
            ("BIN", [bin(i)[2:].zfill(4) for i in range(16)]),
        ]
        colors = [config.ACCENT, config.ACCENT4, config.ACCENT2]
        for r, (row_label, values) in enumerate(ref_data):
            tk.Label(table_frame, text=f"{row_label:4s}",
                     font=("Consolas", 8, "bold"),
                     bg=config.BG_CARD, fg=colors[r]).grid(
                row=r, column=0, padx=(0, 8), sticky=tk.W)
            for c, val in enumerate(values):
                tk.Label(table_frame, text=val,
                         font=("Consolas", 8),
                         bg=config.BG_CARD, fg=config.FG_SECONDARY,
                         width=5).grid(row=r, column=c + 1)

    # ─────────────── Logic ───────────────────

    def _get_width(self):
        w = self.width_var.get()
        if w == "自定义":
            try:
                return int(self.custom_width_entry.get())
            except ValueError:
                return 32
        return int(w)

    def _on_width_change(self, event=None):
        if self.width_var.get() == "自定义":
            self.custom_width_entry.pack(side=tk.LEFT, padx=(6, 0))
        else:
            self.custom_width_entry.pack_forget()
        self._refresh_all()

    def _on_input(self, source_base):
        if self._updating:
            return
        self._updating = True
        try:
            raw = self.entries[source_base].get().strip()
            if not raw:
                # 清空其他框
                for b in [2, 8, 10, 16]:
                    if b != source_base:
                        self.entries[b].set("")
                        self.entry_widgets[b]["verilog_lbl"].config(text="")
                self.status_var.set("就绪 · 在任意输入框中输入数值，其余进制自动更新")
                return

            # 解析输入（支持 0x / 0b 前缀 和 Verilog 格式）
            value = self._parse_input(raw, source_base)
            if value is None:
                self._set_error(source_base)
                return

            width = self._get_width()
            signed = self.signed_var.get()

            # 有符号处理
            if signed and value >= (1 << (width - 1)):
                value -= (1 << width)

            # 更新所有进制
            self._update_fields(value, source_base, width, signed)
            self.status_var.set(
                f"✓  十进制值: {value}  |  位宽: {width}bit  |  "
                f"{'有符号（补码）' if signed else '无符号'}"
            )
            # 高亮当前输入框
            for b, info in self.entry_widgets.items():
                info["entry"].config(
                    fg=info["color"] if b == source_base else config.FG_PRIMARY
                )

        except Exception as e:
            self.status_var.set(f"⚠  解析错误: {e}")
        finally:
            self._updating = False

    def _parse_input(self, raw, base):
        """解析输入字符串，返回整数值"""
        try:
            raw = raw.strip()
            # 支持 Verilog 格式: 32'h1A, 8'b1010, 'd255
            verilog_match = re.match(
                r"(\d*)'([bBoOdDhH])([0-9a-fA-F_]+)$", raw)
            if verilog_match:
                prefix = verilog_match.group(2).lower()
                num_str = verilog_match.group(3).replace("_", "")
                base_map = {'b': 2, 'o': 8, 'd': 10, 'h': 16}
                return int(num_str, base_map[prefix])

            # 支持 0x / 0b / 0o 前缀
            if raw.startswith(("0x", "0X")):
                return int(raw, 16)
            if raw.startswith(("0b", "0B")):
                return int(raw, 2)
            if raw.startswith(("0o", "0O")):
                return int(raw, 8)

            # 普通输入
            raw_clean = raw.replace("_", "")
            negative = raw_clean.startswith("-")
            if negative:
                raw_clean = raw_clean[1:]
            val = int(raw_clean, base)
            return -val if negative else val
        except Exception:
            return None

    def _update_fields(self, value, source_base, width, signed):
        """将整数值填充到所有进制框"""
        # 处理负数补码
        display_value = value
        if value < 0:
            display_value = value + (1 << width)

        leading_zero = self.leading_zero_var.get()

        # 各进制字符串（带或不带前导零）
        bin_full  = bin(display_value)[2:].zfill(width)
        oct_full  = oct(display_value)[2:].zfill((width + 2) // 3)
        hex_full  = hex(display_value)[2:].upper().zfill((width + 3) // 4)

        bin_str  = bin_full  if leading_zero else bin(display_value)[2:]
        oct_str  = oct_full  if leading_zero else oct(display_value)[2:]
        hex_str  = hex_full  if leading_zero else hex(display_value)[2:].upper()
        dec_str  = str(value)   # 十进制始终显示真实值（含负号）

        base_map = {
            2:  bin_str,
            8:  oct_str,
            10: dec_str,
            16: hex_str,
        }

        verilog_prefix = {2: 'b', 8: 'o', 10: 'd', 16: 'h'}
        show_verilog = self.verilog_var.get()

        for base, text in base_map.items():
            if base != source_base:
                self.entries[base].set(text)

            # Verilog 格式标注（始终使用补零的完整值）
            if show_verilog:
                verilog_val = {2: bin_full, 8: oct_full, 10: dec_str, 16: hex_full}[base]
                # 二进制 Verilog 格式加下划线分组
                if base == 2:
                    groups = [bin_full[max(0, i-4):i] for i in range(len(bin_full), 0, -4)][::-1]
                    verilog_val = "_".join(groups)
                verilog_str = f"{width}'{verilog_prefix[base]}{verilog_val}"
                self.entry_widgets[base]["verilog_lbl"].config(
                    text=f"Verilog: {verilog_str}"
                )
            else:
                self.entry_widgets[base]["verilog_lbl"].config(text="")

    def _set_error(self, source_base):
        self.status_var.set("⚠  输入格式有误，请检查是否与所选进制匹配")
        self.entry_widgets[source_base]["entry"].config(fg=config.ACCENT3)

    def _clear_all(self):
        self._updating = True
        for b in [2, 8, 10, 16]:
            self.entries[b].set("")
            self.entry_widgets[b]["verilog_lbl"].config(text="")
            self.entry_widgets[b]["entry"].config(fg=config.FG_PRIMARY)
        self.status_var.set("已清空 · 在任意输入框中输入数值，其余进制自动更新")
        self._updating = False

    def _refresh_all(self):
        """重新触发当前有值的框"""
        for b in [2, 8, 10, 16]:
            val = self.entries[b].get().strip()
            if val:
                self._on_input(b)
                break

    def _copy_hex(self):
        val = self.entries[16].get()
        if val:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(val)
            self.status_var.set(f"✓  已复制 HEX: {val}")

    def _copy_bin(self):
        val = self.entries[2].get()
        if val:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(val)
            self.status_var.set(f"✓  已复制 BIN: {val}")
