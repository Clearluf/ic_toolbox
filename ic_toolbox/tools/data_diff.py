"""
数据比对器 - Data Diff
逐 bit 比较两段数据，高亮差异并标注位置
"""

import tkinter as tk
from tkinter import ttk
import re
from .. import config


class DataDiffFrame(tk.Frame):
    """数据比对器：逐 bit 比较两段数据，高亮差异并标注位置"""

    COLOR      = config.COLOR_DIFF   # 红/粉主题
    COLOR_SAME = config.ACCENT2     # 相同位 - 绿
    COLOR_DIFF = config.ACCENT3     # 不同位 - 红
    COLOR_A    = config.ACCENT      # 数据A - 蓝
    COLOR_B    = config.ACCENT4     # 数据B - 橙

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=config.BG_DARK, *args, **kwargs)
        self._result_widgets = []
        self._build_ui()

    # ──────────────────── UI ─────────────────

    def _build_ui(self):
        # ── 标题 ──────────────────────────────
        title_frame = tk.Frame(self, bg=config.BG_DARK)
        title_frame.pack(fill=tk.X, padx=32, pady=(28, 0))

        tk.Label(title_frame, text="≠  数据比对器",
                font=("Consolas", 20, "bold"),
                bg=config.BG_DARK, fg=self.COLOR).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Data Diff",
                font=("Consolas", 11),
                bg=config.BG_DARK, fg=config.FG_MUTED).pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=32, pady=(12, 0))

        # ── 选项行 ────────────────────────────
        opt_card = tk.Frame(self, bg=config.BG_CARD)
        opt_card.pack(fill=tk.X, padx=32, pady=(16, 0))
        tk.Frame(opt_card, bg=self.COLOR, width=4).pack(side=tk.LEFT, fill=tk.Y)
        oc = tk.Frame(opt_card, bg=config.BG_CARD)
        oc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=12)

        row_opt = tk.Frame(oc, bg=config.BG_CARD)
        row_opt.pack(fill=tk.X)

        # 输入格式
        tk.Label(row_opt, text="输入格式:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.fmt_var = tk.StringVar(value="HEX")
        for fmt in ["HEX", "BIN"]:
            tk.Radiobutton(
                row_opt, text=fmt, variable=self.fmt_var, value=fmt,
                font=("Consolas", 9), bg=config.BG_CARD, fg=config.FG_PRIMARY,
                selectcolor=config.BG_INPUT, activebackground=config.BG_CARD,
                command=self._on_change
            ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(row_opt, text="  |  ", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 对齐方式
        tk.Label(row_opt, text="位宽对齐:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.align_var = tk.StringVar(value="右对齐（低位对齐）")
        for a in ["右对齐（低位对齐）", "左对齐（高位对齐）"]:
            tk.Radiobutton(
                row_opt, text=a, variable=self.align_var, value=a,
                font=("Consolas", 9), bg=config.BG_CARD, fg=config.FG_PRIMARY,
                selectcolor=config.BG_INPUT, activebackground=config.BG_CARD,
                command=self._on_change
            ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(row_opt, text="  |  ", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_MUTED).pack(side=tk.LEFT)

        # 分组显示粒度
        tk.Label(row_opt, text="分组:", font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_SECONDARY).pack(side=tk.LEFT)
        self.group_var = tk.StringVar(value="4")
        for g in ["1", "4", "8"]:
            tk.Radiobutton(
                row_opt, text=f"{g}bit", variable=self.group_var, value=g,
                font=("Consolas", 9), bg=config.BG_CARD, fg=config.FG_PRIMARY,
                selectcolor=config.BG_INPUT, activebackground=config.BG_CARD,
                command=self._on_change
            ).pack(side=tk.LEFT, padx=(6, 0))

        # ── 数据 A 输入 ───────────────────────
        self._build_input_row("A", self.COLOR_A)

        # ── 数据 B 输入 ───────────────────────
        self._build_input_row("B", self.COLOR_B)

        # ── 操作按钮 ──────────────────────────
        btn_row = tk.Frame(self, bg=config.BG_DARK)
        btn_row.pack(fill=tk.X, padx=32, pady=(10, 0))

        tk.Button(
            btn_row, text="  比对 Diff",
            command=self._do_diff,
            bg=self.COLOR, fg=config.BG_DARK,
            font=("Consolas", 10, "bold"),
            relief=tk.FLAT, padx=18, pady=6,
            cursor="hand2",
            activebackground=config.FG_PRIMARY, activeforeground=config.BG_DARK
        ).pack(side=tk.LEFT)

        tk.Button(
            btn_row, text="  清空",
            command=self._clear_all,
            bg=config.BG_INPUT, fg=config.FG_SECONDARY,
            font=("Consolas", 10), relief=tk.FLAT,
            padx=12, pady=6, cursor="hand2",
            activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
        ).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            btn_row, text="  互换 A↔B",
            command=self._swap_ab,
            bg=config.BG_INPUT, fg=config.FG_SECONDARY,
            font=("Consolas", 10), relief=tk.FLAT,
            padx=12, pady=6, cursor="hand2",
            activebackground=config.BG_HOVER, activeforeground=config.FG_PRIMARY
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── 状态行 ────────────────────────────
        self.status_var = tk.StringVar(value="就绪 · 输入两段数据，点击比对")
        tk.Label(self, textvariable=self.status_var,
                font=("Consolas", 9), bg=config.BG_DARK, fg=config.FG_MUTED
                ).pack(fill=tk.X, padx=32, pady=(8, 4), anchor=tk.W)

        # ── 结果区（可滚动） ──────────────────
        result_outer = tk.Frame(self, bg=config.BG_DARK)
        result_outer.pack(fill=tk.BOTH, expand=True, padx=32, pady=(0, 16))

        self._canvas = tk.Canvas(result_outer, bg=config.BG_DARK,
                                 highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(result_outer, orient=tk.VERTICAL,
                                  command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._result_frame = tk.Frame(self._canvas, bg=config.BG_DARK)
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._result_frame, anchor=tk.NW)

        self._result_frame.bind("<Configure>", self._on_frame_cfg)
        self._canvas.bind("<Configure>", self._on_canvas_cfg)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_input_row(self, label, color):
        card = tk.Frame(self, bg=config.BG_CARD)
        card.pack(fill=tk.X, padx=32, pady=(10, 0))
        tk.Frame(card, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y)
        inner = tk.Frame(card, bg=config.BG_CARD)
        inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14, pady=10)

        row = tk.Frame(inner, bg=config.BG_CARD)
        row.pack(fill=tk.X)

        tk.Label(row, text=f"数据 {label}:",
                font=("Consolas", 10, "bold"),
                bg=config.BG_CARD, fg=color, width=7).pack(side=tk.LEFT)

        var = tk.StringVar()
        entry = tk.Entry(
            row, textvariable=var,
            font=("Consolas", 13),
            bg=config.BG_INPUT, fg=config.FG_PRIMARY,
            insertbackground=color,
            relief=tk.FLAT, bd=6,
            selectbackground=config.ACCENT,
            selectforeground=config.BG_DARK
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        var.trace_add("write", lambda *a: self._on_change())

        # 位宽显示标签
        wlbl = tk.Label(row, text="", font=("Consolas", 9),
                        bg=config.BG_CARD, fg=config.FG_MUTED, width=10)
        wlbl.pack(side=tk.LEFT, padx=(8, 0))

        setattr(self, f"_var_{label}", var)
        setattr(self, f"_entry_{label}", entry)
        setattr(self, f"_wlbl_{label}", wlbl)

    # ──────────────────── Events ──────────────

    def _on_frame_cfg(self, e=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_cfg(self, e):
        self._canvas.itemconfig(self._canvas_win, width=e.width)

    def _on_mousewheel(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _on_change(self, *_):
        """输入变化时更新位宽标注，不自动触发 diff"""
        for lbl in ["A", "B"]:
            raw = getattr(self, f"_var_{lbl}").get().strip()
            bits = self._parse(raw)
            wlbl = getattr(self, f"_wlbl_{lbl}")
            if bits is not None:
                wlbl.config(text=f"{len(bits)}bit", fg=config.FG_SECONDARY)
            else:
                wlbl.config(text="—" if not raw else "格式错误", fg=self.COLOR_DIFF)

    def _clear_all(self):
        self._var_A.set("")
        self._var_B.set("")
        self._clear_results()
        self.status_var.set("已清空")

    def _swap_ab(self):
        a, b = self._var_A.get(), self._var_B.get()
        self._var_A.set(b)
        self._var_B.set(a)

    def _clear_results(self):
        for w in self._result_widgets:
            w.destroy()
        self._result_widgets.clear()

    # ──────────────────── Core ────────────────

    def _parse(self, raw):
        """返回 bit 字符串，失败返回 None"""
        raw = raw.strip().replace("_", "").replace(" ", "")
        if not raw:
            return None
        fmt = self.fmt_var.get()
        try:
            if fmt == "HEX":
                raw = re.sub(r"^(0x|0X)", "", raw)
                m = re.match(r"^\d*'[hH]([0-9a-fA-F]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[0-9a-fA-F]+", raw):
                    return None
                bits = bin(int(raw, 16))[2:]
                # 补到 4 的倍数
                pad = (4 - len(bits) % 4) % 4
                return bits.zfill(len(bits) + pad)
            else:
                raw = re.sub(r"^(0b|0B)", "", raw)
                m = re.match(r"^\d*'[bB]([01]+)$", raw)
                if m:
                    raw = m.group(1)
                if not re.fullmatch(r"[01]+", raw):
                    return None
                return raw
        except Exception:
            return None

    def _align(self, ba, bb):
        """对齐两段 bit 串，返回 (ba_aligned, bb_aligned, width)"""
        w = max(len(ba), len(bb))
        if self.align_var.get().startswith("右"):
            # 右对齐：高位补零
            return ba.zfill(w), bb.zfill(w), w
        else:
            # 左对齐：低位补零
            return ba.ljust(w, "0"), bb.ljust(w, "0"), w

    def _do_diff(self):
        raw_a = self._var_A.get().strip()
        raw_b = self._var_B.get().strip()

        ba = self._parse(raw_a)
        bb = self._parse(raw_b)

        self._clear_results()

        if ba is None or bb is None:
            self.status_var.set("⚠  输入格式有误，请检查 HEX/BIN 数据")
            return

        ba, bb, width = self._align(ba, bb)

        # 逐 bit 比较
        diff_mask = [ba[i] != bb[i] for i in range(width)]
        n_diff = sum(diff_mask)

        if n_diff == 0:
            self.status_var.set(f"✓  两段数据完全相同（{width} bit）")
            self._render_identical(width)
            return

        self.status_var.set(
            f"≠  共 {width} bit  |  差异 {n_diff} bit  "
            f"|  相同 {width - n_diff} bit  "
            f"|  差异率 {n_diff / width * 100:.1f}%"
        )

        # ── 渲染 ──────────────────────────────
        self._render_bitview(ba, bb, diff_mask, width)
        self._render_diff_table(ba, bb, diff_mask, width)

    def _render_identical(self, width):
        lbl = tk.Label(
            self._result_frame,
            text=f"✓  两段数据完全相同，共 {width} bit，无任何差异",
            font=("Consolas", 11), bg=config.BG_DARK, fg=self.COLOR_SAME
        )
        lbl.pack(pady=20)
        self._result_widgets.append(lbl)

    def _render_bitview(self, ba, bb, diff_mask, width):
        """逐 bit 可视化视图，按分组宽度排布"""
        group = int(self.group_var.get())

        hdr = tk.Label(self._result_frame,
                       text="▸ Bit 可视化  （红色 = 差异位）",
                       font=("Consolas", 9, "bold"),
                       bg=config.BG_DARK, fg=config.FG_MUTED)
        hdr.pack(anchor=tk.W, pady=(8, 4))
        self._result_widgets.append(hdr)

        # 每行最多显示 64 bit（受窗口宽度限制）
        BITS_PER_ROW = 64

        for row_start in range(0, width, BITS_PER_ROW):
            row_end = min(row_start + BITS_PER_ROW, width)
            row_frame = tk.Frame(self._result_frame, bg=config.BG_DARK)
            row_frame.pack(anchor=tk.W, pady=1)
            self._result_widgets.append(row_frame)

            # 行号标注（最高 bit 索引）
            hi_bit = width - 1 - row_start
            lo_bit = width - row_end
            tk.Label(row_frame,
                     text=f"[{hi_bit:3d}:{lo_bit:3d}] ",
                     font=("Consolas", 8), bg=config.BG_DARK, fg=config.FG_MUTED
                     ).pack(side=tk.LEFT)

            # 两行：A 和 B
            col_a = tk.Frame(row_frame, bg=config.BG_DARK)
            col_a.pack(side=tk.LEFT)
            col_b = tk.Frame(row_frame, bg=config.BG_DARK)

            # 标签
            tk.Label(col_a, text="A:", font=("Consolas", 8),
                    bg=config.BG_DARK, fg=self.COLOR_A).pack(side=tk.LEFT)
            tk.Label(col_b, text="B:", font=("Consolas", 8),
                    bg=config.BG_DARK, fg=self.COLOR_B).pack(side=tk.LEFT)

            # 逐 bit 渲染（按 group 分块）
            for i in range(row_start, row_end):
                if i > row_start and (i - row_start) % group == 0:
                    # 组间小间隔
                    tk.Label(col_a, text=" ", font=("Consolas", 9),
                            bg=config.BG_DARK, fg=config.BG_DARK).pack(side=tk.LEFT)
                    tk.Label(col_b, text=" ", font=("Consolas", 9),
                            bg=config.BG_DARK, fg=config.BG_DARK).pack(side=tk.LEFT)

                is_diff = diff_mask[i]
                fg_a = self.COLOR_DIFF if is_diff else self.COLOR_SAME
                fg_b = self.COLOR_DIFF if is_diff else self.COLOR_SAME
                bg_diff = "#3d1a1a" if is_diff else config.BG_DARK

                tk.Label(col_a, text=ba[i], font=("Consolas", 9, "bold"),
                        bg=bg_diff, fg=fg_a).pack(side=tk.LEFT)
                tk.Label(col_b, text=bb[i], font=("Consolas", 9, "bold"),
                        bg=bg_diff, fg=fg_b).pack(side=tk.LEFT)

            col_b.pack(side=tk.LEFT)

        sep = ttk.Separator(self._result_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=(8, 4))
        self._result_widgets.append(sep)

    def _render_diff_table(self, ba, bb, diff_mask, width):
        """差异段汇总表"""
        hdr = tk.Label(self._result_frame,
                       text="▸ 差异段汇总  Diff Segments",
                       font=("Consolas", 9, "bold"),
                       bg=config.BG_DARK, fg=config.FG_MUTED)
        hdr.pack(anchor=tk.W, pady=(4, 6))
        self._result_widgets.append(hdr)

        # 收集连续差异段
        segments = []
        in_diff = False
        seg_start = 0
        for i in range(width):
            if diff_mask[i] and not in_diff:
                seg_start = i
                in_diff = True
            elif not diff_mask[i] and in_diff:
                segments.append((seg_start, i - 1))
                in_diff = False
        if in_diff:
            segments.append((seg_start, width - 1))

        # 表头
        col_defs = [
            ("段 #",      5,  config.FG_MUTED),
            ("Bit Range", 14, config.FG_MUTED),
            ("长度(bit)", 9,  config.FG_MUTED),
            ("值 A (HEX)", 14, self.COLOR_A),
            ("值 B (HEX)", 14, self.COLOR_B),
            ("值 A (BIN)", 20, self.COLOR_A),
            ("值 B (BIN)", 20, self.COLOR_B),
        ]
        thead = tk.Frame(self._result_frame, bg=config.BG_DARK)
        thead.pack(fill=tk.X)
        self._result_widgets.append(thead)
        for col_text, col_w, col_fg in col_defs:
            tk.Label(thead, text=col_text, width=col_w,
                    font=("Consolas", 8, "bold"),
                    bg=config.BG_DARK, fg=col_fg,
                    anchor=tk.W).pack(side=tk.LEFT)

        sep2 = ttk.Separator(self._result_frame, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X, pady=(2, 4))
        self._result_widgets.append(sep2)

        row_colors = [config.BG_CARD, config.BG_DARK]

        for seg_idx, (si, ei) in enumerate(segments):
            # bit 索引转换：i=0 是最高位
            hi_bit = width - 1 - si
            lo_bit = width - 1 - ei
            seg_len = ei - si + 1

            seg_a = ba[si:ei + 1]
            seg_b = bb[si:ei + 1]
            val_a = int(seg_a, 2)
            val_b = int(seg_b, 2)
            hex_a = hex(val_a)[2:].upper().zfill((seg_len + 3) // 4)
            hex_b = hex(val_b)[2:].upper().zfill((seg_len + 3) // 4)

            # BIN 分组（每4位下划线）
            def bin_grouped(s):
                return "_".join(s[i:i+4] for i in range(0, len(s), 4))

            row_bg = row_colors[seg_idx % 2]
            row = tk.Frame(self._result_frame, bg=row_bg, pady=3)
            row.pack(fill=tk.X)
            self._result_widgets.append(row)

            cells = [
                (f"[{seg_idx}]",           5,  config.FG_MUTED,    None),
                (f"[{hi_bit}:{lo_bit}]",   14, self.COLOR,  None),
                (str(seg_len),              9,  config.FG_SECONDARY, None),
                (hex_a,                     14, self.COLOR_A, f"HEX_A: {hex_a}"),
                (hex_b,                     14, self.COLOR_B, f"HEX_B: {hex_b}"),
                (bin_grouped(seg_a),        20, self.COLOR_A, f"BIN_A: {seg_a}"),
                (bin_grouped(seg_b),        20, self.COLOR_B, f"BIN_B: {seg_b}"),
            ]

            for cell_text, cell_w, cell_fg, copy_val in cells:
                lbl = tk.Label(
                    row, text=cell_text, width=cell_w,
                    font=("Consolas", 9),
                    bg=row_bg, fg=cell_fg,
                    anchor=tk.W,
                    cursor="hand2" if copy_val else "arrow"
                )
                lbl.pack(side=tk.LEFT)
                if copy_val:
                    lbl.bind("<Button-1>",
                            lambda e, v=copy_val: self._copy_cell(v))
                    lbl.bind("<Enter>",
                            lambda e, w=lbl, bg=row_bg: w.config(bg=config.BG_HOVER))
                    lbl.bind("<Leave>",
                            lambda e, w=lbl, bg=row_bg: w.config(bg=bg))

        # 底部统计
        stats = tk.Frame(self._result_frame, bg=config.BG_CARD)
        stats.pack(fill=tk.X, pady=(10, 4))
        self._result_widgets.append(stats)
        tk.Frame(stats, bg=self.COLOR, width=4).pack(side=tk.LEFT, fill=tk.Y)
        si = tk.Frame(stats, bg=config.BG_CARD)
        si.pack(side=tk.LEFT, padx=14, pady=8, fill=tk.X)
        total_diff = sum(diff_mask)
        tk.Label(si,
                text=f"共 {len(segments)} 个差异段  |  "
                    f"差异 {total_diff} bit  |  "
                    f"相同 {width - total_diff} bit  |  "
                    f"差异率 {total_diff / width * 100:.1f}%",
                font=("Consolas", 9),
                bg=config.BG_CARD, fg=config.FG_PRIMARY).pack(anchor=tk.W)

        self._canvas.yview_moveto(0)

    def _copy_cell(self, val):
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(val.split(": ", 1)[-1])
        self.status_var.set(f"✓  已复制: {val}")
