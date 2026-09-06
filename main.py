"""
╔══════════════════════════════════════════════════════════════╗
║  🛡️  ANTI-SNEAK PRIVACY SHIELD  🛡️                          ║
║  OLED-Optimized Screen Privacy Protection for Windows       ║
║                                                              ║
║  Hotkeys:                                                    ║
║    Ctrl+Alt+S  →  Toggle Shield ON / OFF                    ║
║    Ctrl+Alt+X  →  Instant Full Blackout (Boss Key)          ║
║    Ctrl+Alt+↑  →  Increase Spotlight Size                   ║
║    Ctrl+Alt+↓  →  Decrease Spotlight Size                   ║
╚══════════════════════════════════════════════════════════════╝

Entry point.  Wires together:
    • OverlayWindow  — transparent click-through shield
    • ControlPanel   — dark-themed settings GUI
    • System tray    — pystray background icon
    • Global hotkeys — pynput keyboard shortcuts
"""

import sys
import os
import tkinter as tk
import threading
import ctypes

# Ensure project directory is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, MODE_BLACKOUT, MODE_SPOTLIGHT
from overlay import OverlayWindow
from control_panel import ControlPanel
from hotkey_manager import HotkeyManager


# ─────────────────────────────────────────────────────────────────────────
class AntiSneakApp:
    """Top-level application controller."""

    def __init__(self):
        # ── DPI awareness (call before any window creation) ──────────
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)   # per-monitor v2
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        # ── Hidden root window ───────────────────────────────────────
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Anti-Sneak Shield")

        # ── Core components ──────────────────────────────────────────
        self.config  = Config()
        self.overlay = OverlayWindow(self.root, self.config)
        self.panel   = ControlPanel(self.root, self.config, self.overlay, toggle_callback=self._toggle_shield)
        self.last_mode = MODE_SPOTLIGHT

        # ── Background services ──────────────────────────────────────
        self._init_tray()
        self._init_hotkeys()

        # ── Startup banner ───────────────────────────────────────────
        self._banner()

        # Always show Control Panel GUI on startup
        self.panel.show()

    # ─── System Tray ─────────────────────────────────────────────────
    def _init_tray(self):
        self._has_tray = False
        try:
            import pystray
            from PIL import Image, ImageDraw, ImageFont

            # --- build a tiny shield icon ---
            sz = 64
            img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            # Shield outline
            shield = [(32, 4), (58, 16), (54, 42), (32, 59), (10, 42), (6, 16)]
            d.polygon(shield, fill=(88, 166, 255, 230),
                      outline=(255, 255, 255, 200))
            # Letter "S"
            try:
                fnt = ImageFont.truetype("segoeui.ttf", 26)
            except Exception:
                fnt = ImageFont.load_default()
            d.text((20, 14), "S", fill=(255, 255, 255, 255), font=fnt)

            # --- tray callbacks (thread-safe via root.after) ---
            def _toggle(icon, item):
                self.root.after(0, self._toggle_shield)

            def _mode(m):
                return lambda icon, item: self.root.after(
                    0, lambda: self._set_mode(m))

            def _settings(icon, item):
                self.root.after(0, self.panel.show)

            def _quit(icon, item):
                icon.stop()
                self.root.after(0, self._quit)

            menu = pystray.Menu(
                pystray.MenuItem(
                    "Toggle Shield  (Ctrl+Alt+S)",
                    _toggle, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Spotlight Mode",  _mode("SPOTLIGHT")),
                pystray.MenuItem("Side Blinds",     _mode("SIDE_BLINDS")),
                pystray.MenuItem("Grid Louver",     _mode("GRID")),
                pystray.MenuItem("Full Blackout",   _mode("BLACKOUT")),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Settings",        _settings),
                pystray.MenuItem("Exit",            _quit),
            )

            self._tray = pystray.Icon("AntiSneak", img,
                                       "Anti-Sneak Shield", menu)
            t = threading.Thread(target=self._tray.run, daemon=True)
            t.start()
            self._has_tray = True

        except ImportError:
            self._tray = None
            print("[!] pystray / Pillow not installed -> system tray disabled.")

    # ─── Global Hotkeys ──────────────────────────────────────────────
    def _init_hotkeys(self):
        callbacks = {
            "toggle":        lambda: self.root.after(0, self._toggle_shield),
            "blackout":      lambda: self.root.after(0, self._panic_blackout),
            "increase_size": lambda: self.root.after(0, self.overlay.increase_radius),
            "decrease_size": lambda: self.root.after(0, self.overlay.decrease_radius),
        }
        self.hotkey_mgr = HotkeyManager(callbacks)
        self.hotkey_mgr.start()

    # ─── Actions ─────────────────────────────────────────────────────
    def _toggle_shield(self):
        curr_mode = self.config.get("mode")

        if curr_mode == MODE_BLACKOUT:
            target_mode = self.last_mode if self.last_mode != MODE_BLACKOUT else MODE_SPOTLIGHT
            self.config.set("mode", target_mode)
            if not self.overlay.active:
                self.overlay.activate()
            print(f"[Shield] Exited Blackout -> Restored {target_mode} mode [ACTIVE]")
            self.panel._sync_ui_from_config()
            return

        active = self.overlay.toggle()
        state = "ACTIVE [ON]" if active else "INACTIVE [OFF]"
        print(f"[Shield] {state}  |  Mode: {curr_mode}")
        self.panel._sync_ui_from_config()

    def _panic_blackout(self):
        """Ctrl+Alt+X — instant blackout toggle."""
        curr_mode = self.config.get("mode")

        if self.overlay.active and curr_mode == MODE_BLACKOUT:
            target_mode = self.last_mode if self.last_mode != MODE_BLACKOUT else MODE_SPOTLIGHT
            self.config.set("mode", target_mode)
            self.overlay.activate()
            print(f"[Shield] Blackout Disengaged -> Restored {target_mode} [ACTIVE]")
        else:
            if curr_mode != MODE_BLACKOUT:
                self.last_mode = curr_mode
            self.config.set("mode", MODE_BLACKOUT)
            self.overlay.activate()
            print("[Shield] !! FULL BLACKOUT ENGAGED")
        self.panel._sync_ui_from_config()

    def _set_mode(self, mode: str):
        if mode != MODE_BLACKOUT:
            self.last_mode = mode
        self.config.set("mode", mode)
        self.overlay.activate()
        print(f"[Shield] Mode set -> {mode} [ACTIVE]")
        self.panel._sync_ui_from_config()

    # ─── Lifecycle ───────────────────────────────────────────────────
    def _quit(self):
        if hasattr(self, "hotkey_mgr") and self.hotkey_mgr:
            self.hotkey_mgr.stop()
        self.overlay.deactivate()
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the Tkinter main-loop (blocks until exit)."""
        self.root.mainloop()

    # ─── Banner ──────────────────────────────────────────────────────
    @staticmethod
    def _banner():
        try:
            print()
            print("=" * 60)
            print("  [S]  ANTI-SNEAK PRIVACY SHIELD  [S]")
            print("  OLED-Optimized Screen Protection for Windows")
            print("=" * 60)
            print()
            print("  Hotkeys:")
            print("    Ctrl + Alt + S      -> Toggle Shield (Spotlight/Normal)")
            print("    Ctrl + Alt + X      -> Panic Full Blackout Toggle")
            print("    Ctrl + Alt + UP / RIGHT / = -> Increase Spotlight")
            print("    Ctrl + Alt + DOWN / LEFT / - -> Decrease Spotlight")
            print()
            print("  Right-click system tray icon for options & settings.")
            print("=" * 60)
            print()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AntiSneakApp()
    app.run()
