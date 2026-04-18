"""
chart_widget.py — Canvas-based dual-bar chart for the dashboard.

Shows Stock-In vs Stock-Out volumes grouped by day (weekly/monthly).

Usage:
    from gui.chart_widget import BarChart
    chart = BarChart(parent, width=500, height=220)
    chart.set_data([
        {"label": "Mon", "stock_in": 50, "stock_out": 30},
        ...
    ])
"""

import tkinter as tk
from config import (FONT_FAMILY, WHITE, DARK_BROWN, OLIVE, AMBER,
                    CHART_STOCK_IN, CHART_STOCK_OUT, CHART_GRID,
                    TEXT_MUTED, TEXT_SECONDARY)


class BarChart(tk.Frame):
    """Dual-bar chart (Stock-In vs Stock-Out) rendered on a Tk Canvas."""

    def __init__(self, parent, width=500, height=220, bg=None):
        _bg = bg or WHITE
        super().__init__(parent, bg=_bg)

        self.canvas = tk.Canvas(
            self, width=width, height=height,
            bg=_bg, highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._cw = width
        self._ch = height
        self._bg = _bg
        self._data = []
        self._m = {"left": 52, "right": 20, "top": 24, "bottom": 36}

    # ── public ───────────────────────────────────────────────
    def set_data(self, data):
        """
        data: list of dicts ``{label, stock_in, stock_out}``.
        """
        self._data = data or []
        self._draw()

    def resize(self, width, height):
        self._cw = width
        self._ch = height
        self.canvas.config(width=width, height=height)
        self._draw()

    # ── rendering ────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")

        if not self._data:
            c.create_text(
                self._cw // 2, self._ch // 2,
                text="No transaction data yet",
                font=(FONT_FAMILY, 10), fill=TEXT_MUTED,
            )
            return

        m  = self._m
        pw = self._cw - m["left"] - m["right"]
        ph = self._ch - m["top"]  - m["bottom"]

        # max value
        max_val = max(
            max((d.get("stock_in", 0) for d in self._data), default=0),
            max((d.get("stock_out", 0) for d in self._data), default=0),
            1,
        )
        max_val = self._nice_ceil(max_val)

        # horizontal grid lines
        steps = 4
        for i in range(steps + 1):
            y   = m["top"] + ph - (i / steps * ph)
            val = int(i / steps * max_val)
            c.create_line(m["left"], y, m["left"] + pw, y,
                          fill=CHART_GRID, width=1)
            c.create_text(m["left"] - 8, y, text=str(val),
                          font=(FONT_FAMILY, 8), fill=TEXT_MUTED, anchor="e")

        # bars
        n     = len(self._data)
        gw    = pw / n
        bw    = gw * 0.28
        gap   = gw * 0.06

        for i, d in enumerate(self._data):
            xc = m["left"] + (i + 0.5) * gw

            # Stock-In bar (left)
            h_in = (d["stock_in"] / max_val) * ph if max_val else 0
            if h_in > 0:
                x1 = xc - bw - gap
                y1 = m["top"] + ph - h_in
                x2 = xc - gap
                y2 = m["top"] + ph
                c.create_rectangle(x1, y1, x2, y2,
                                   fill=CHART_STOCK_IN, outline="")

            # Stock-Out bar (right)
            h_out = (d["stock_out"] / max_val) * ph if max_val else 0
            if h_out > 0:
                x1 = xc + gap
                y1 = m["top"] + ph - h_out
                x2 = xc + bw + gap
                y2 = m["top"] + ph
                c.create_rectangle(x1, y1, x2, y2,
                                   fill=CHART_STOCK_OUT, outline="")

            # day label
            c.create_text(xc, m["top"] + ph + 16, text=d["label"],
                          font=(FONT_FAMILY, 8), fill=TEXT_SECONDARY)

        # legend (top-right)
        lx = m["left"] + pw - 150
        ly = m["top"] - 4
        c.create_rectangle(lx, ly, lx + 10, ly + 10,
                           fill=CHART_STOCK_IN, outline="")
        c.create_text(lx + 14, ly + 5, text="Stock In",
                      font=(FONT_FAMILY, 8), fill=TEXT_SECONDARY, anchor="w")
        c.create_rectangle(lx + 76, ly, lx + 86, ly + 10,
                           fill=CHART_STOCK_OUT, outline="")
        c.create_text(lx + 90, ly + 5, text="Stock Out",
                      font=(FONT_FAMILY, 8), fill=TEXT_SECONDARY, anchor="w")

    @staticmethod
    def _nice_ceil(v):
        if v <= 10:
            return 10
        if v <= 50:
            return ((v // 10) + 1) * 10
        if v <= 100:
            return ((v // 25) + 1) * 25
        return ((v // 50) + 1) * 50
