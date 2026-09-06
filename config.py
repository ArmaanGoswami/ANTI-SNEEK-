"""
Anti-Sneak Privacy Shield - Configuration
OLED-optimized privacy protection settings with JSON persistence.
"""

import json
import os

# ─── Paths ───────────────────────────────────────────────────────────────
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# ─── Shield Modes ────────────────────────────────────────────────────────
MODE_OFF = "OFF"
MODE_SPOTLIGHT = "SPOTLIGHT"
MODE_SIDE_BLINDS = "SIDE_BLINDS"
MODE_GRID = "GRID"
MODE_BLACKOUT = "BLACKOUT"

# ─── Spotlight Shapes ────────────────────────────────────────────────────
SHAPE_CIRCLE = "CIRCLE"
SHAPE_RECTANGLE = "RECTANGLE"

# ─── Special Color ───────────────────────────────────────────────────────
# Magenta — used as the Windows transparent-color key.
# Any pixel painted this color becomes fully invisible & click-through.
TRANSPARENT_COLOR = "#FF00FF"

# ─── Presets ─────────────────────────────────────────────────────────────
PRESETS = {
    "office": {
        "mode": MODE_SPOTLIGHT,
        "shape": SHAPE_CIRCLE,
        "spotlight_radius": 250,
        "blinds_left_pct": 20,
        "blinds_right_pct": 20,
        "grid_stripe_width": 3,
        "grid_gap_width": 5,
        "overlay_opacity": 0.95,
    },
    "public": {
        "mode": MODE_SPOTLIGHT,
        "shape": SHAPE_CIRCLE,
        "spotlight_radius": 150,
        "blinds_left_pct": 30,
        "blinds_right_pct": 30,
        "grid_stripe_width": 4,
        "grid_gap_width": 3,
        "overlay_opacity": 1.0,
    },
    "night": {
        "mode": MODE_SPOTLIGHT,
        "shape": SHAPE_RECTANGLE,
        "spotlight_radius": 300,
        "blinds_left_pct": 15,
        "blinds_right_pct": 15,
        "grid_stripe_width": 2,
        "grid_gap_width": 6,
        "overlay_opacity": 0.90,
    },
    "paranoia": {
        "mode": MODE_SPOTLIGHT,
        "shape": SHAPE_CIRCLE,
        "spotlight_radius": 120,
        "blinds_left_pct": 35,
        "blinds_right_pct": 35,
        "grid_stripe_width": 5,
        "grid_gap_width": 2,
        "overlay_opacity": 1.0,
    },
}

# ─── Defaults ────────────────────────────────────────────────────────────
DEFAULTS = {
    "mode": MODE_SPOTLIGHT,
    "shape": SHAPE_CIRCLE,
    "spotlight_radius": 200,
    "blinds_left_pct": 25,       # percentage of screen width
    "blinds_right_pct": 25,
    "grid_stripe_width": 3,      # pixels
    "grid_gap_width": 5,         # pixels
    "overlay_opacity": 0.95,     # 0.0 – 1.0
}


# ─── Config Manager ─────────────────────────────────────────────────────
class Config:
    """Manages application settings with JSON persistence and change callbacks."""

    def __init__(self):
        self._settings: dict = dict(DEFAULTS)
        self._callbacks: list = []
        self._load()

    # ── Persistence ──────────────────────────────────────────────────
    def _load(self):
        """Load settings from JSON file (if exists)."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._settings.update(saved)
            except Exception:
                pass  # Fall back to defaults

    def save(self):
        """Persist current settings to JSON file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except Exception:
            pass

    # ── Getters / Setters ────────────────────────────────────────────
    def get(self, key, default=None):
        """Return a setting value."""
        return self._settings.get(
            key, default if default is not None else DEFAULTS.get(key)
        )

    def set(self, key, value, notify=True):
        """Update a setting, persist, and optionally notify listeners."""
        self._settings[key] = value
        self.save()
        if notify:
            self._notify()

    def apply_preset(self, preset_name: str):
        """Apply a named preset and notify listeners."""
        if preset_name in PRESETS:
            self._settings.update(PRESETS[preset_name])
            self.save()
            self._notify()

    # ── Observer pattern ─────────────────────────────────────────────
    def on_change(self, callback):
        """Register a callback that fires whenever settings change."""
        self._callbacks.append(callback)

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb()
            except Exception:
                pass
