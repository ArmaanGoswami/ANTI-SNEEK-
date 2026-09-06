"""
Anti-Sneak Privacy Shield - Overlay Engine
Full-screen transparent click-through overlay for OLED privacy protection.

How it works
────────────
• A borderless, always-on-top Tkinter Toplevel fills the primary monitor.
• The canvas background is set to TRANSPARENT_COLOR (magenta).
  Windows' -transparentcolor flag makes every magenta pixel invisible.
• Shield regions are painted BLACK (OLED pixels OFF → zero light → invisible
  from side angles).
• Win32 WS_EX_TRANSPARENT + WS_EX_LAYERED makes the ENTIRE window
  click-through so the user's mouse/keyboard works normally beneath it.
"""

import tkinter as tk
import ctypes
import ctypes.wintypes

from config import (
    TRANSPARENT_COLOR,
    MODE_SPOTLIGHT,
    MODE_SIDE_BLINDS,
    MODE_GRID,
    MODE_BLACKOUT,
    SHAPE_CIRCLE,
    SHAPE_RECTANGLE,
)

# ─── Win32 Constants ─────────────────────────────────────────────────────
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW  = 0x00000080
WS_EX_NOACTIVATE  = 0x08000000

HWND_TOPMOST      = -1
SWP_NOSIZE        = 0x0001
SWP_NOMOVE        = 0x0002
SWP_NOACTIVATE    = 0x0010
SWP_SHOWWINDOW    = 0x0040
SM_CXSCREEN       = 0
SM_CYSCREEN       = 1


class OverlayWindow:
    """Renders the privacy shield as a transparent click-through overlay."""

    # ─── Initialisation ──────────────────────────────────────────────
    def __init__(self, root: tk.Tk, config):
        self.root = root
        self.config = config
        self.active = False
        self._mouse_x = 0
        self._mouse_y = 0

        # Real pixel dimensions of the primary monitor (DPI-aware)
        self.screen_w = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
        self.screen_h = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

        # ── Build overlay Toplevel ───────────────────────────────────
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.attributes("-alpha", self.config.get("overlay_opacity"))
        self.window.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        # ── Drawing canvas ───────────────────────────────────────────
        self.canvas = tk.Canvas(
            self.window,
            width=self.screen_w,
            height=self.screen_h,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # ── Win32 click-through & no-activate ───────────────────────
        self._apply_click_through()

        # ── Pre-create reusable canvas items ─────────────────────────
        self._build_canvas_items()

        # ── Start hidden ─────────────────────────────────────────────
        self.window.withdraw()

        # ── Continuous loops ─────────────────────────────────────────
        self._track_mouse_loop()
        self._keep_on_top_loop()

        # ── React to live config changes ─────────────────────────────
        self.config.on_change(self._on_config_change)

    # ─── Win32 helpers ───────────────────────────────────────────────
    def _apply_click_through(self):
        """Set WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE."""
        self.window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
        self._hwnd = hwnd
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd,
            GWL_EXSTYLE,
            style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE,
        )

    # ─── Canvas item creation ────────────────────────────────────────
    def _build_canvas_items(self):
        """Pre-create all canvas items (hidden). Avoids per-frame alloc."""

        # -- Spotlight ------------------------------------------------
        # A full-screen black rect, then a magenta "hole" drawn on top.
        self._spot_bg = self.canvas.create_rectangle(
            0, 0, self.screen_w, self.screen_h,
            fill="black", outline="", state="hidden",
        )
        self._spot_hole = self.canvas.create_oval(
            0, 0, 0, 0,
            fill=TRANSPARENT_COLOR, outline="#333333", width=1, state="hidden",
        )
        # Subtle soft-edge rings around the spotlight
        self._spot_rings = []
        for color in ("#111111", "#0a0a0a", "#050505"):
            ring = self.canvas.create_oval(
                0, 0, 0, 0,
                fill="", outline=color, width=4, state="hidden",
            )
            self._spot_rings.append(ring)

        # -- Side Blinds ----------------------------------------------
        self._blind_left = self.canvas.create_rectangle(
            0, 0, 0, self.screen_h,
            fill="black", outline="", state="hidden",
        )
        self._blind_right = self.canvas.create_rectangle(
            self.screen_w, 0, self.screen_w, self.screen_h,
            fill="black", outline="", state="hidden",
        )

        # -- Grid / Louver (created dynamically) ----------------------
        self._grid_items: list[int] = []

        # -- Full Blackout --------------------------------------------
        self._blackout_bg = self.canvas.create_rectangle(
            0, 0, self.screen_w, self.screen_h,
            fill="black", outline="", state="hidden",
        )

    # ─── Mouse tracking (≈60 fps) ────────────────────────────────────
    def _track_mouse_loop(self):
        if self.active and self.config.get("mode") == MODE_SPOTLIGHT:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            if pt.x != self._mouse_x or pt.y != self._mouse_y:
                self._mouse_x, self._mouse_y = pt.x, pt.y
                self._move_spotlight()
        self.root.after(16, self._track_mouse_loop)

    def _keep_on_top_loop(self):
        """Periodically re-raise overlay without activating or stealing focus."""
        if self.active and hasattr(self, "_hwnd") and self._hwnd:
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )
        self.root.after(2000, self._keep_on_top_loop)

    # ─── Spotlight position update ───────────────────────────────────
    def _move_spotlight(self):
        mx, my = self._mouse_x, self._mouse_y
        r = self.config.get("spotlight_radius")
        shape = self.config.get("shape")

        if shape == SHAPE_RECTANGLE:
            rw, rh = int(r * 1.6), r
            self.canvas.coords(self._spot_hole, mx - rw, my - rh, mx + rw, my + rh)
            for i, ring in enumerate(self._spot_rings):
                off = (i + 1) * 5
                self.canvas.coords(ring, mx - rw - off, my - rh - off,
                                   mx + rw + off, my + rh + off)
        else:  # circle
            self.canvas.coords(self._spot_hole, mx - r, my - r, mx + r, my + r)
            for i, ring in enumerate(self._spot_rings):
                off = (i + 1) * 5
                self.canvas.coords(ring, mx - r - off, my - r - off,
                                   mx + r + off, my + r + off)

    # ─── Mode activators ─────────────────────────────────────────────
    def activate(self):
        """Show the overlay in the currently configured mode."""
        self.active = True
        self._hide_all()

        mode = self.config.get("mode")
        if mode == MODE_SPOTLIGHT:
            self._activate_spotlight()
        elif mode == MODE_SIDE_BLINDS:
            self._activate_blinds()
        elif mode == MODE_GRID:
            self._activate_grid()
        elif mode == MODE_BLACKOUT:
            self._activate_blackout()

        self.window.attributes("-alpha", self.config.get("overlay_opacity"))
        self.window.deiconify()
        self.window.lift()
        self._apply_click_through()

    def deactivate(self):
        """Hide the overlay."""
        self.active = False
        self.window.withdraw()

    def toggle(self) -> bool:
        """Toggle on/off. Returns new active state."""
        if self.active:
            self.deactivate()
        else:
            self.activate()
        return self.active

    # ── Spotlight ────────────────────────────────────────────────────
    def _activate_spotlight(self):
        shape = self.config.get("shape")

        # Show black background
        self.canvas.itemconfigure(self._spot_bg, state="normal")

        # Recreate hole with correct shape type (oval vs rect)
        self.canvas.delete(self._spot_hole)
        r = self.config.get("spotlight_radius")
        mx, my = self._get_cursor_pos()
        self._mouse_x, self._mouse_y = mx, my

        if shape == SHAPE_RECTANGLE:
            rw, rh = int(r * 1.6), r
            self._spot_hole = self.canvas.create_rectangle(
                mx - rw, my - rh, mx + rw, my + rh,
                fill=TRANSPARENT_COLOR, outline="#333333", width=1,
            )
        else:
            self._spot_hole = self.canvas.create_oval(
                mx - r, my - r, mx + r, my + r,
                fill=TRANSPARENT_COLOR, outline="#333333", width=1,
            )

        # Recreate soft-edge rings matching shape
        for ring in self._spot_rings:
            self.canvas.delete(ring)
        self._spot_rings.clear()
        for color in ("#111111", "#0a0a0a", "#050505"):
            if shape == SHAPE_RECTANGLE:
                ring = self.canvas.create_rectangle(0, 0, 0, 0,
                    fill="", outline=color, width=4)
            else:
                ring = self.canvas.create_oval(0, 0, 0, 0,
                    fill="", outline=color, width=4)
            self._spot_rings.append(ring)

        self._move_spotlight()

    # ── Side Blinds ──────────────────────────────────────────────────
    def _activate_blinds(self):
        lw = int(self.screen_w * self.config.get("blinds_left_pct") / 100)
        rw = int(self.screen_w * self.config.get("blinds_right_pct") / 100)

        self.canvas.coords(self._blind_left, 0, 0, lw, self.screen_h)
        self.canvas.coords(self._blind_right,
                           self.screen_w - rw, 0, self.screen_w, self.screen_h)

        self.canvas.itemconfigure(self._blind_left, state="normal")
        self.canvas.itemconfigure(self._blind_right, state="normal")

    # ── Grid / Louver ────────────────────────────────────────────────
    def _activate_grid(self):
        sw = self.config.get("grid_stripe_width")
        gw = self.config.get("grid_gap_width")
        x = 0
        while x < self.screen_w:
            item = self.canvas.create_rectangle(
                x, 0, x + sw, self.screen_h,
                fill="black", outline="",
            )
            self._grid_items.append(item)
            x += sw + gw

    # ── Full Blackout ────────────────────────────────────────────────
    def _activate_blackout(self):
        self.canvas.itemconfigure(self._blackout_bg, state="normal")

    # ─── Helpers ─────────────────────────────────────────────────────
    def _hide_all(self):
        """Hide every canvas item and clear dynamic ones."""
        self.canvas.itemconfigure(self._spot_bg, state="hidden")
        self.canvas.itemconfigure(self._spot_hole, state="hidden")
        for ring in self._spot_rings:
            self.canvas.itemconfigure(ring, state="hidden")
        self.canvas.itemconfigure(self._blind_left, state="hidden")
        self.canvas.itemconfigure(self._blind_right, state="hidden")
        self.canvas.itemconfigure(self._blackout_bg, state="hidden")
        for item in self._grid_items:
            self.canvas.delete(item)
        self._grid_items.clear()

    def _get_cursor_pos(self) -> tuple[int, int]:
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def _on_config_change(self):
        """Re-apply overlay when settings change mid-session."""
        if self.active:
            self.activate()

    # ─── Public size controls (hotkey targets) ───────────────────────
    def increase_radius(self):
        r = self.config.get("spotlight_radius")
        new_r = min(r + 25, 800)
        self.config.set("spotlight_radius", new_r)
        if self.active and self.config.get("mode") == MODE_SPOTLIGHT:
            self._move_spotlight()
        print(f"[Shield] Spotlight Radius -> {new_r} px")

    def decrease_radius(self):
        r = self.config.get("spotlight_radius")
        new_r = max(r - 25, 50)
        self.config.set("spotlight_radius", new_r)
        if self.active and self.config.get("mode") == MODE_SPOTLIGHT:
            self._move_spotlight()
        print(f"[Shield] Spotlight Radius -> {new_r} px")
