"""
Anti-Sneak Privacy Shield - Robust System-Wide Hotkey Manager
Uses native Windows Win32 RegisterHotKey API with pynput fallback to ensure
shortcuts ALWAYS work system-wide regardless of whether Control Panel is open,
minimized, or hidden in the system tray.
"""

import ctypes
import ctypes.wintypes
import threading
import time

# ─── Win32 Constants ─────────────────────────────────────────────────────
MOD_ALT      = 0x0001
MOD_CONTROL  = 0x0002
MOD_SHIFT    = 0x0004
MOD_WIN      = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY    = 0x0312

# Virtual key codes
VK_S     = 0x53
VK_X     = 0x58
VK_UP    = 0x26
VK_DOWN  = 0x28
VK_LEFT  = 0x25
VK_RIGHT = 0x27
VK_PLUS  = 0xBB  # '+' / '='
VK_MINUS = 0xBD  # '-' / '_'


class HotkeyManager:
    """Manages system-wide global hotkeys reliably using Win32 RegisterHotKey."""

    def __init__(self, callbacks: dict):
        """
        callbacks dictionary mapping action string to callable:
        {
            "toggle": func,
            "blackout": func,
            "increase_size": func,
            "decrease_size": func,
        }
        """
        self.callbacks = callbacks
        self._running = False
        self._thread = None
        self._pynput_listener = None
        self.active_engine = "None"

    def start(self):
        """Start global hotkey listener in background daemon thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run_win32_loop, daemon=True)
        self._thread.start()

    def _run_win32_loop(self):
        user32 = ctypes.windll.user32
        
        # Hotkey registrations: (id, modifiers, vk, action_name)
        hotkeys = [
            # Primary Ctrl + Alt
            (1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_S, "toggle"),
            (2, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_X, "blackout"),
            (3, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_UP, "increase_size"),
            (4, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_DOWN, "decrease_size"),
            (5, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_RIGHT, "increase_size"),
            (6, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_LEFT, "decrease_size"),
            (7, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_PLUS, "increase_size"),
            (8, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_MINUS, "decrease_size"),
            
            # Backup Ctrl + Shift
            (9,  MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_S, "toggle"),
            (10, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_X, "blackout"),
            (11, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_UP, "increase_size"),
            (12, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_DOWN, "decrease_size"),
        ]

        action_map = {}
        registered_count = 0

        for hk_id, mods, vk, action in hotkeys:
            res = user32.RegisterHotKey(None, hk_id, mods, vk)
            if res:
                action_map[hk_id] = action
                registered_count += 1

        if registered_count > 0:
            self.active_engine = f"Win32 RegisterHotKey ({registered_count} active)"
            print(f"[+] HotkeyManager: Registered {registered_count} global hotkeys via Win32 API.")
            
            msg = ctypes.wintypes.MSG()
            while self._running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == WM_HOTKEY:
                    hk_id = msg.wParam
                    if hk_id in action_map:
                        act_name = action_map[hk_id]
                        fn = self.callbacks.get(act_name)
                        if fn:
                            try:
                                fn()
                            except Exception as e:
                                print(f"[!] Hotkey callback error: {e}")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

            # Cleanup on exit
            for hk_id in action_map:
                user32.UnregisterHotKey(None, hk_id)
        else:
            print("[!] Win32 RegisterHotKey returned 0 matches, falling back to pynput...")
            self._start_pynput_fallback()

    def _start_pynput_fallback(self):
        try:
            from pynput import keyboard

            bindings = {
                "<ctrl>+<alt>+s": self.callbacks.get("toggle"),
                "<ctrl>+<alt>+x": self.callbacks.get("blackout"),
                "<ctrl>+<alt>+<up>": self.callbacks.get("increase_size"),
                "<ctrl>+<alt>+<down>": self.callbacks.get("decrease_size"),
            }
            self._pynput_listener = keyboard.GlobalHotKeys(bindings)
            self._pynput_listener.daemon = True
            self._pynput_listener.start()
            self.active_engine = "Pynput GlobalHotKeys"
            print("[+] HotkeyManager: Pynput fallback activated.")
        except Exception as e:
            print(f"[!] Pynput hotkey fallback error: {e}")

    def stop(self):
        self._running = False
        if self._pynput_listener:
            try:
                self._pynput_listener.stop()
            except Exception:
                pass
