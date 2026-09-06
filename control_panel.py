"""
Anti-Sneak Privacy Shield - Control Panel v2.0
Sleek, modern, dark-themed privacy control center with spacious responsive layout,
interactive visual cards, spotlight resizing controls (Bdha / Chota), presets, and custom scrollbar.
"""

import tkinter as tk
from config import (
    MODE_SPOTLIGHT, MODE_SIDE_BLINDS, MODE_GRID, MODE_BLACKOUT,
    SHAPE_CIRCLE, SHAPE_RECTANGLE,
)


class CustomScrollbar(tk.Canvas):
    """Sleek modern dark-themed custom scrollbar."""

    def __init__(self, parent, target_canvas, bg="#0A0E17", thumb_color="#1E293B", thumb_hover="#38BDF8", **kwargs):
        super().__init__(parent, bg=bg, width=10, highlightthickness=0, bd=0, **kwargs)
        self.target = target_canvas
        self.thumb_color = thumb_color
        self.thumb_hover = thumb_hover
        self._bg = bg
        self._dragging = False

        self.thumb = self.create_rectangle(2, 0, 8, 40, fill=thumb_color, outline="")

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Enter>", lambda e: self.itemconfig(self.thumb, fill=self.thumb_hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.thumb, fill=self.thumb_color) if not self._dragging else None)
        
        self.target.config(yscrollcommand=self.set)

    def set(self, low, high):
        l = float(low)
        h = float(high)
        height = self.winfo_height()
        if height <= 1:
            return
        top = int(l * height)
        bottom = int(h * height)
        thumb_h = max(30, bottom - top)
        self.coords(self.thumb, 2, top, 8, top + thumb_h)

    def _on_click(self, event):
        height = self.winfo_height()
        if height > 0:
            fraction = event.y / height
            self.target.yview_moveto(fraction)

    def _on_drag(self, event):
        height = self.winfo_height()
        if height > 0:
            fraction = event.y / height
            self.target.yview_moveto(fraction)


class ControlPanel:
    """A sleek, modern dark-themed control panel for live shield configuration."""

    # ─── Modern Color Palette ──────────────────────────────────────────
    BG                  = "#0A0E17"  # Deep space slate background
    CARD_BG             = "#131C2E"  # Slate card surface
    CARD_HOVER          = "#1A263E"  # Hover slate card surface
    CARD_ACTIVE         = "#1E2D4A"  # Active mode card surface
    BORDER              = "#223252"  # Card subtle border
    BORDER_ACTIVE       = "#38BDF8"  # Active cyan border
    
    TEXT                = "#F8FAFC"  # Crisp white text
    TEXT_MUTED          = "#94A3B8"  # Secondary text
    TEXT_DIM            = "#64748B"  # Subtitle grey
    
    ACCENT              = "#38BDF8"  # Vibrant electric cyan
    ACCENT_DARK         = "#0284C7"  # Dark cyan hover
    ACCENT_PURPLE       = "#818CF8"  # Soft indigo highlight
    
    RED                 = "#EF4444"  # Crimson red disabled/blackout
    RED_DARK            = "#DC2626"  # Red hover
    GREEN               = "#10B981"  # Emerald green active
    GREEN_DARK          = "#059669"  # Green hover

    def __init__(self, root, config, overlay, toggle_callback=None):
        self.root = root
        self.config = config
        self.overlay = overlay
        self.toggle_callback = toggle_callback

        # ── Window Setup (Spacious 680x840) ──────────────────────────
        self.window = tk.Toplevel(root)
        self.window.title("Anti-Sneak Privacy Shield v2.0")
        self.window.geometry("680x840")
        self.window.minsize(620, 720)
        self.window.configure(bg=self.BG)
        self.window.protocol("WM_DELETE_WINDOW", self._close)

        # Center on primary screen
        self.window.update_idletasks()
        cx = max(0, (self.window.winfo_screenwidth() - 680) // 2)
        cy = max(0, (self.window.winfo_screenheight() - 840) // 2)
        self.window.geometry(f"680x840+{cx}+{cy}")

        self._build_ui()
        self._sync_ui_from_config()

        # Listen for live config changes
        self.config.on_change(self._sync_ui_from_config)

        # Start hidden by default
        self.window.withdraw()

    def show(self):
        self._sync_ui_from_config()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def hide(self):
        self.window.withdraw()

    def _close(self):
        self.hide()

    # ─── UI Construction ─────────────────────────────────────────────
    def _build_ui(self):
        # Outer container
        outer = tk.Frame(self.window, bg=self.BG)
        outer.pack(fill="both", expand=True)

        # Canvas with Custom Scrollbar
        self.canvas = tk.Canvas(outer, bg=self.BG, highlightthickness=0, bd=0)
        self.scrollbar = CustomScrollbar(outer, self.canvas, bg=self.BG, thumb_color="#1E293B", thumb_hover=self.ACCENT)
        
        self.scroll_content = tk.Frame(self.canvas, bg=self.BG)
        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self._canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 6), pady=18)
        self.scrollbar.pack(side="right", fill="y", pady=18, padx=(0, 10))

        # Mousewheel binding
        self.window.bind_all("<MouseWheel>", self._on_mousewheel)

        f = self.scroll_content

        # ─── 1. Header Banner ────────────────────────────────────────
        header_frame = tk.Frame(f, bg=self.BG)
        header_frame.pack(fill="x", pady=(0, 16))

        title_row = tk.Frame(header_frame, bg=self.BG)
        title_row.pack(fill="x", anchor="w")

        tk.Label(title_row, text="🛡️ ANTI-SNEAK PRIVACY SHIELD",
                 font=("Segoe UI", 20, "bold"),
                 fg=self.ACCENT, bg=self.BG).pack(side="left")

        # Version Pill
        ver_lbl = tk.Label(title_row, text=" v2.0 OLED PRO ",
                           font=("Segoe UI", 9, "bold"),
                           fg="#38BDF8", bg="#0F2942", padx=8, pady=2)
        ver_lbl.pack(side="left", padx=12)

        tk.Label(header_frame, text="OLED Privacy Protection & Anti-Peeping Control Center for Windows",
                 font=("Segoe UI", 10), fg=self.TEXT_MUTED,
                 bg=self.BG).pack(anchor="w", pady=(4, 0))

        # ─── 2. Master Hero Control Card ─────────────────────────────
        hero_card = tk.Frame(f, bg=self.CARD_BG, highlightbackground=self.BORDER, highlightthickness=1)
        hero_card.pack(fill="x", pady=(0, 20), ipady=12)

        hero_inner = tk.Frame(hero_card, bg=self.CARD_BG)
        hero_inner.pack(fill="x", padx=20, pady=6)

        # Left status text
        status_box = tk.Frame(hero_inner, bg=self.CARD_BG)
        status_box.pack(side="left", fill="y")

        self._status_title = tk.Label(status_box, text="SHIELD STATUS", font=("Segoe UI", 9, "bold"),
                                       fg=self.TEXT_MUTED, bg=self.CARD_BG)
        self._status_title.pack(anchor="w")

        self._status_lbl = tk.Label(
            status_box, text="● Shield INACTIVE",
            font=("Segoe UI", 15, "bold"),
            fg=self.RED, bg=self.CARD_BG
        )
        self._status_lbl.pack(anchor="w", pady=(2, 0))

        # Right big power action button
        self._btn_toggle = tk.Button(
            hero_inner, text="⚡ ENABLE SHIELD",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg=self.ACCENT,
            activebackground=self.ACCENT_DARK, activeforeground="white",
            relief="flat", bd=0, padx=28, pady=12,
            cursor="hand2", command=self._on_toggle_click,
        )
        self._btn_toggle.pack(side="right", padx=(10, 0))

        # ─── 3. Shield Mode Selection (2x2 Visual Cards) ─────────────
        self._section_title(f, "🛡️ SHIELD MODE SELECTOR")

        modes_frame = tk.Frame(f, bg=self.BG)
        modes_frame.pack(fill="x", pady=(0, 20))

        self._mode_var = tk.StringVar(value=self.config.get("mode"))
        self._mode_card_widgets = {}

        mode_defs = [
            (MODE_SPOTLIGHT,   "🎯 Spotlight Mode",   "Cursor area crystal clear, surrounding screen pure OLED black"),
            (MODE_SIDE_BLINDS, "🪟 Side Blinds",     "Left & right screen side edges blocked from side peeping"),
            (MODE_GRID,        "🏁 Grid Louver",     "Vertical anti-peeping stripe louver privacy filter"),
            (MODE_BLACKOUT,    "🚨 Full Blackout",   "Instant 100% screen blackout (Boss Key Emergency)"),
        ]

        # Render as a 2x2 grid of cards
        for idx, (m_val, m_title, m_desc) in enumerate(mode_defs):
            row_i = idx // 2
            col_i = idx % 2

            m_card = tk.Frame(
                modes_frame, bg=self.CARD_BG,
                highlightbackground=self.BORDER, highlightthickness=2,
                cursor="hand2"
            )
            m_card.grid(row=row_i, column=col_i, sticky="nsew", padx=6, pady=6, ipady=8)
            modes_frame.grid_columnconfigure(col_i, weight=1)

            # Title label inside card
            lbl_title = tk.Label(
                m_card, text=m_title, font=("Segoe UI", 11, "bold"),
                fg=self.TEXT, bg=self.CARD_BG, anchor="w", cursor="hand2"
            )
            lbl_title.pack(fill="x", padx=14, pady=(10, 4))

            # Description label
            lbl_desc = tk.Label(
                m_card, text=m_desc, font=("Segoe UI", 9),
                fg=self.TEXT_MUTED, bg=self.CARD_BG, anchor="w",
                justify="left", wraplength=260, cursor="hand2"
            )
            lbl_desc.pack(fill="x", padx=14, pady=(0, 10))

            # Click handlers on card and all children
            def make_click_fn(val):
                return lambda e: self._select_mode(val)

            click_fn = make_click_fn(m_val)
            m_card.bind("<Button-1>", click_fn)
            lbl_title.bind("<Button-1>", click_fn)
            lbl_desc.bind("<Button-1>", click_fn)

            self._mode_card_widgets[m_val] = {
                "card": m_card,
                "title": lbl_title,
                "desc": lbl_desc
            }

        # ─── 4. Spotlight Size Controls (Bdha / Chota Option) ────────
        self._section_title(f, "🔍 SPOTLIGHT CONTROL (BDHA / CHOTA)")

        spot_card = tk.Frame(f, bg=self.CARD_BG, highlightbackground=self.BORDER, highlightthickness=1)
        spot_card.pack(fill="x", pady=(0, 20), ipadx=14, ipady=12)

        # Header with size callout
        size_hdr = tk.Frame(spot_card, bg=self.CARD_BG)
        size_hdr.pack(fill="x", padx=16, pady=(6, 12))

        tk.Label(size_hdr, text="Current Spotlight Radius:",
                 font=("Segoe UI", 11, "bold"),
                 fg=self.TEXT, bg=self.CARD_BG).pack(side="left")

        self._size_val_lbl = tk.Label(
            size_hdr, text=f"{self.config.get('spotlight_radius')} px",
            font=("Segoe UI", 14, "bold"),
            fg=self.ACCENT, bg="#0F243A", padx=14, pady=4
        )
        self._size_val_lbl.pack(side="right")

        # Big Step Action Buttons: [- Smaller (Chota)]  [+ Bigger (Bdha)]
        step_row = tk.Frame(spot_card, bg=self.CARD_BG)
        step_row.pack(fill="x", padx=16, pady=4)

        btn_minus = tk.Button(
            step_row, text="➖ Smaller (Chota)",
            font=("Segoe UI", 10, "bold"), fg=self.TEXT, bg="#1E2B45",
            activebackground=self.ACCENT, activeforeground="white",
            relief="flat", bd=1, padx=16, pady=10, cursor="hand2",
            command=self._on_decrease_size,
        )
        btn_minus.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_plus = tk.Button(
            step_row, text="➕ Bigger (Bdha)",
            font=("Segoe UI", 10, "bold"), fg=self.TEXT, bg="#1E2B45",
            activebackground=self.ACCENT, activeforeground="white",
            relief="flat", bd=1, padx=16, pady=10, cursor="hand2",
            command=self._on_increase_size,
        )
        btn_plus.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # Quick Size Preset Pills
        pills_row = tk.Frame(spot_card, bg=self.CARD_BG)
        pills_row.pack(fill="x", padx=16, pady=10)

        size_presets = [
            ("Small (100px)", 100),
            ("Medium (200px)", 200),
            ("Large (350px)", 350),
            ("Huge (500px)", 500),
        ]
        for label, px_val in size_presets:
            btn_pill = tk.Button(
                pills_row, text=label, font=("Segoe UI", 9, "bold"),
                fg=self.TEXT_MUTED, bg="#0F172A",
                activebackground=self.ACCENT, activeforeground="white",
                relief="flat", bd=0, padx=6, pady=6, cursor="hand2",
                command=lambda val=px_val: self._set_radius(val),
            )
            btn_pill.pack(side="left", expand=True, fill="x", padx=3)

        # Fine Precision Slider
        self._radius_var = tk.IntVar(value=self.config.get("spotlight_radius"))
        self._slider_raw(spot_card, "Fine Spotlight Radius Adjustment", self._radius_var,
                         50, 600, self._on_radius)

        # Shape Selector Buttons
        shf = tk.Frame(spot_card, bg=self.CARD_BG)
        shf.pack(fill="x", padx=16, pady=(10, 4))

        tk.Label(shf, text="Spotlight Shape:", font=("Segoe UI", 10, "bold"),
                 fg=self.TEXT, bg=self.CARD_BG).pack(side="left", padx=(0, 14))

        self._shape_var = tk.StringVar(value=self.config.get("shape"))
        self._shape_btn_circle = tk.Button(
            shf, text="● Circle", font=("Segoe UI", 9, "bold"),
            fg=self.TEXT, bg="#1E2B45", relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2", command=lambda: self._set_shape(SHAPE_CIRCLE)
        )
        self._shape_btn_circle.pack(side="left", padx=4)

        self._shape_btn_rect = tk.Button(
            shf, text="■ Rectangle", font=("Segoe UI", 9, "bold"),
            fg=self.TEXT, bg="#1E2B45", relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2", command=lambda: self._set_shape(SHAPE_RECTANGLE)
        )
        self._shape_btn_rect.pack(side="left", padx=4)

        # ─── 5. Quick Presets ────────────────────────────────────────
        self._section_title(f, "⚡ QUICK PRIVACY PRESETS")
        pf = tk.Frame(f, bg=self.BG)
        pf.pack(fill="x", pady=(0, 20))

        presets = [
            ("🏢 Office Mode", "office", "Balanced 250px spotlight, 20% side blinds"),
            ("🌐 Public / Cafe", "public", "Strict 150px spotlight, 30% side blinds"),
            ("🌙 Night Shift",  "night",  "Rectangle spotlight 300px, soft opacity"),
            ("🔐 Maximum Stealth", "paranoia", "Tight 120px spotlight, 100% OLED black"),
        ]

        for idx, (p_title, p_name, p_desc) in enumerate(presets):
            p_btn = tk.Button(
                pf, text=f"{p_title}\n{p_desc}",
                font=("Segoe UI", 9, "bold"), justify="center",
                fg=self.TEXT, bg=self.CARD_BG,
                activebackground=self.ACCENT, activeforeground="white",
                relief="flat", bd=1, padx=10, pady=10, cursor="hand2",
                command=lambda n=p_name: self._preset(n),
            )
            p_btn.pack(side="left", expand=True, fill="x", padx=4)

        # ─── 6. Fine Tuning & Sliders ────────────────────────────────
        self._section_title(f, "⚙️ SHIELD FINE-TUNING & SLIDERS")
        fine_card = tk.Frame(f, bg=self.CARD_BG, highlightbackground=self.BORDER, highlightthickness=1)
        fine_card.pack(fill="x", pady=(0, 20), ipady=8)

        self._blinds_var = tk.IntVar(value=self.config.get("blinds_left_pct"))
        self._slider_raw(fine_card, "Side Blinds Width (% per edge)", self._blinds_var,
                         5, 45, self._on_blinds)

        self._grid_var = tk.IntVar(value=self.config.get("grid_stripe_width"))
        self._slider_raw(fine_card, "Grid Louver Stripe Width (px)", self._grid_var,
                         1, 15, self._on_grid)

        self._opacity_var = tk.IntVar(value=int(self.config.get("overlay_opacity") * 100))
        self._slider_raw(fine_card, "Shield Darkness Opacity (%)", self._opacity_var,
                         50, 100, self._on_opacity)

        # ─── 7. Hotkeys & Background System Card ────────────────────
        self._section_title(f, "⌨️ KEYBOARD SHORTCUTS & SYSTEM STATUS")
        hk_card = tk.Frame(f, bg=self.CARD_BG, highlightbackground=self.BORDER, highlightthickness=1)
        hk_card.pack(fill="x", pady=(0, 16), ipady=8)

        # Active Hotkey System Badge
        badge_frame = tk.Frame(hk_card, bg="#0E2135")
        badge_frame.pack(fill="x", padx=14, pady=(12, 10))

        tk.Label(
            badge_frame,
            text="🟢 Global System Hotkeys Active — Shortcuts work background without panel open!",
            font=("Segoe UI", 9, "bold"), fg="#38BDF8", bg="#0E2135", padx=10, pady=6
        ).pack(anchor="w")

        hotkeys = [
            ("Ctrl + Alt + S", "Toggle Privacy Shield ON / OFF"),
            ("Ctrl + Alt + X", "Instant Full Blackout (Panic Boss Key)"),
            ("Ctrl + Alt + Up / Right / +", "Increase Spotlight Size (Bdha)"),
            ("Ctrl + Alt + Down / Left / -", "Decrease Spotlight Size (Chota)"),
            ("Ctrl + Mouse Scroll", "Resize spotlight live on screen"),
        ]

        for key, action in hotkeys:
            row = tk.Frame(hk_card, bg=self.CARD_BG)
            row.pack(fill="x", padx=14, pady=3)
            
            tk.Label(row, text=key, font=("Consolas", 9, "bold"),
                     fg=self.ACCENT, bg="#0B132B", width=28,
                     anchor="w", padx=8, pady=3).pack(side="left")
            
            tk.Label(row, text=action, font=("Segoe UI", 9),
                     fg=self.TEXT, bg=self.CARD_BG,
                     anchor="w", padx=10).pack(side="left")

        tk.Label(hk_card, text="", bg=self.CARD_BG).pack(pady=4)

    # ─── Helpers & UI Building Blocks ────────────────────────────────
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.window.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _section_title(self, parent, title: str):
        tk.Label(parent, text=title, font=("Segoe UI", 10, "bold"),
                 fg=self.ACCENT_PURPLE, bg=self.BG).pack(anchor="w", pady=(0, 6))

    def _slider_raw(self, parent, label, var, lo, hi, cmd):
        sf = tk.Frame(parent, bg=self.CARD_BG)
        sf.pack(fill="x", padx=16, pady=6)
        
        tk.Label(sf, text=label, font=("Segoe UI", 9, "bold"),
                 fg=self.TEXT, bg=self.CARD_BG).pack(anchor="w")
        
        tk.Scale(sf, from_=lo, to=hi, orient="horizontal", variable=var,
                 command=cmd, font=("Segoe UI", 8),
                 fg=self.TEXT, bg=self.CARD_BG, troughcolor="#0F172A",
                 activebackground=self.ACCENT, highlightthickness=0,
                 length=420).pack(fill="x")

    # ─── Action Callbacks ────────────────────────────────────────────
    def _on_toggle_click(self):
        if self.toggle_callback:
            self.toggle_callback()
        self._sync_ui_from_config()

    def _select_mode(self, mode_val: str):
        self._mode_var.set(mode_val)
        self.config.set("mode", mode_val)
        if self.overlay.active:
            self.overlay.activate()
        self._sync_ui_from_config()

    def _set_shape(self, shape_val: str):
        self._shape_var.set(shape_val)
        self.config.set("shape", shape_val)
        self._sync_ui_from_config()

    def _on_radius(self, v):
        val = int(v)
        self.config.set("spotlight_radius", val)
        self._size_val_lbl.config(text=f"{val} px")

    def _set_radius(self, val):
        self.config.set("spotlight_radius", val)
        self._radius_var.set(val)
        self._size_val_lbl.config(text=f"{val} px")

    def _on_increase_size(self):
        r = self.config.get("spotlight_radius")
        new_r = min(r + 25, 600)
        self._set_radius(new_r)

    def _on_decrease_size(self):
        r = self.config.get("spotlight_radius")
        new_r = max(r - 25, 50)
        self._set_radius(new_r)

    def _on_blinds(self, v):
        val = int(v)
        self.config.set("blinds_left_pct", val, notify=False)
        self.config.set("blinds_right_pct", val, notify=True)

    def _on_grid(self, v):
        self.config.set("grid_stripe_width", int(v))

    def _on_opacity(self, v):
        self.config.set("overlay_opacity", int(v) / 100.0)

    def _preset(self, name):
        self.config.apply_preset(name)
        if self.overlay.active:
            self.overlay.activate()
        self._sync_ui_from_config()

    # ─── Sync UI with State ──────────────────────────────────────────
    def _sync_ui_from_config(self):
        curr_mode = self.config.get("mode")
        curr_shape = self.config.get("shape")
        self._mode_var.set(curr_mode)
        self._shape_var.set(curr_shape)

        r = self.config.get("spotlight_radius")
        self._radius_var.set(r)
        self._size_val_lbl.config(text=f"{r} px")

        self._blinds_var.set(self.config.get("blinds_left_pct"))
        self._grid_var.set(self.config.get("grid_stripe_width"))
        self._opacity_var.set(int(self.config.get("overlay_opacity") * 100))

        # Highlight selected mode card with glowing cyan border
        for m_val, widgets in self._mode_card_widgets.items():
            card = widgets["card"]
            title = widgets["title"]
            desc = widgets["desc"]
            
            if m_val == curr_mode:
                card.config(bg=self.CARD_ACTIVE, highlightbackground=self.BORDER_ACTIVE, highlightthickness=2)
                title.config(bg=self.CARD_ACTIVE, fg=self.ACCENT)
                desc.config(bg=self.CARD_ACTIVE, fg=self.TEXT)
            else:
                card.config(bg=self.CARD_BG, highlightbackground=self.BORDER, highlightthickness=1)
                title.config(bg=self.CARD_BG, fg=self.TEXT)
                desc.config(bg=self.CARD_BG, fg=self.TEXT_MUTED)

        # Highlight shape toggle buttons
        if curr_shape == SHAPE_CIRCLE:
            self._shape_btn_circle.config(bg=self.ACCENT, fg="white")
            self._shape_btn_rect.config(bg="#1E2B45", fg=self.TEXT)
        else:
            self._shape_btn_circle.config(bg="#1E2B45", fg=self.TEXT)
            self._shape_btn_rect.config(bg=self.ACCENT, fg="white")

        # Sync master toggle status button
        if self.overlay.active:
            self._status_lbl.config(text="● Shield ACTIVE", fg=self.GREEN)
            self._btn_toggle.config(text="⏹ DISABLE SHIELD", bg=self.RED, activebackground=self.RED_DARK)
        else:
            self._status_lbl.config(text="● Shield INACTIVE", fg=self.RED)
            self._btn_toggle.config(text="⚡ ENABLE SHIELD", bg=self.ACCENT, activebackground=self.ACCENT_DARK)

