"""
Anti-Sneak Privacy Shield v2.0 - PyWebView UI Manager
Provides 100% pixel-perfect Edge WebView2 UI powered by Python backend.
"""

import os
import webview


class WebviewApi:

    def __init__(self, window, config, overlay, toggle_callback=None):
        self._window = window
        self.config = config
        self.overlay = overlay
        self.toggle_callback = toggle_callback

    def set_window_instance(self, window):
        self._window = window

    def toggle_shield(self):
        if self.toggle_callback:
            self.toggle_callback()
        return {"active": self.overlay.active, "mode": self.config.get("mode")}

    def set_mode(self, mode):
        self.config.set("mode", mode)
        if not self.overlay.active:
            self.overlay.activate()
        return {"active": self.overlay.active, "mode": mode}

    def set_radius(self, val):
        self.config.set("spotlight_radius", int(val))
        return int(val)

    def increase_radius(self):
        self.overlay.increase_radius()
        return self.config.get("spotlight_radius")

    def decrease_radius(self):
        self.overlay.decrease_radius()
        return self.config.get("spotlight_radius")

    def apply_preset(self, name):
        self.config.apply_preset(name)
        if self.overlay.active:
            self.overlay.activate()
        return self.config._settings

    def toggle_maximize(self):
        if self._window:
            if getattr(self, "_is_maximized", False):
                self._window.restore()
                self._is_maximized = False
            else:
                self._window.maximize()
                self._is_maximized = True
            return self._is_maximized

    def minimize(self):
        if self._window:
            self._window.minimize()

    def close(self):
        if self._window:
            self._window.hide()


def launch_webview_gui(config, overlay, toggle_callback=None):
    html_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
    api = WebviewApi(None, config, overlay, toggle_callback)

    window = webview.create_window(
        "Anti-Sneak Privacy Shield v2.0",
        url=html_path,
        width=960,
        height=640,
        resizable=True,
        frameless=True,
        easy_drag=True,
        on_top=False,
        js_api=api,
    )
    api.set_window_instance(window)
    return window
