# 🛡️ Anti-Sneak Privacy Shield v2.0

> **OLED-Optimized Screen Privacy Protection & Anti-Peeping Control Center for Windows**



---

## 🌟 Key Features

- **🎯 Spotlight Privacy Mode**: Keeps your active cursor region crystal clear while dimming the surrounding screen to pure OLED black ($0\%$-$100\%$ opacity).
- **🪟 Side Blinds Filter**: Blocks left and right screen side angles to prevent shoulder surfing and side-angle peeping in public spaces.
- **🏁 Grid Louver Matrix**: Anti-peeping vertical stripe louver filter for stealth screen privacy.
- **🚨 Panic Boss Blackout**: Instant $100\%$ full screen blackout shortcut for emergency privacy.
- **⚡ Native Win32 System Hotkeys**: Global shortcuts (`Ctrl+Alt+S`, `Ctrl+Alt+X`, `Ctrl+Alt+Up/Down`) work background 24/7 without needing the Control Panel open.
- **🔍 Spotlight Size Controls (Bdha / Chota)**: One-click `➕ Bigger` and `➖ Smaller` buttons, digital radius callout, preset size pills (`Small`, `Medium`, `Large`, `Huge`), and Circle vs Rectangle shape toggling.
- **⚡ Quick Privacy Presets**: Built-in 1-click profiles for **Office**, **Public / Cafe**, **Night Shift**, and **Maximum Stealth**.
- **🔒 Zero Focus-Stealing Engine**: Uses Win32 `WS_EX_NOACTIVATE` and `SWP_NOACTIVATE` window flags so the overlay screen never interrupts typing or steals keyboard focus from active apps.

---

## ⌨️ Global Keyboard Shortcuts

| Shortcut Key | Function / Description |
| :--- | :--- |
| `Ctrl + Alt + S` | Toggle Privacy Shield ON / OFF |
| `Ctrl + Alt + X` | Instant Full Screen Blackout (Panic Boss Key) |
| `Ctrl + Alt + Up / Right / +` | Increase Spotlight Size (Bdha) |
| `Ctrl + Alt + Down / Left / -` | Decrease Spotlight Size (Chota) |
| `Ctrl + Shift + S / X` | Alternative secondary hotkeys |
| `Ctrl + Mouse Scroll` | Live spotlight radius scaling on screen |

> 🟢 **Note:** Global hotkeys run as a background system daemon and work at all times across all Windows applications even when the Control Panel window is hidden or minimized to system tray.

---

## 🚀 Quick Start / Installation

### Prerequisites
* Windows 10 or Windows 11
* Python 3.9+ (Python 3.11 recommended)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ArmaanGoswami/ANTI-SNEEK-.git
cd ANTI-SNEEK-
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run Application
Double-click `install_and_run.bat` or `Launch_AntiSneak_GUI.vbs`, or run in terminal:
```bash
python main.py
```

---

## 🛠️ Project Architecture

```
ANTI-SNEEK-/
├── main.py                # Top-level application launcher & tray integration
├── control_panel.py       # Modern 680x840 dark-mode Tkinter GUI control center
├── overlay.py             # Win32 click-through transparent screen overlay engine
├── hotkey_manager.py      # Win32 RegisterHotKey system-wide background daemon
├── config.py              # Settings persistence & preset manager (settings.json)
├── Launch_AntiSneak_GUI.vbs# Background launcher script (no console window)
├── install_and_run.bat    # Quick installer & setup batch script
├── requirements.txt       # Python dependencies (pynput, Pillow, pystray)
├── preview.jpg            # Application UI Preview Screenshot
└── README.md              # Project documentation
```

---

## 👨‍💻 Author & Contact

* **Author:** Armaan Goswami
* **Email:** `armaangoswami00@gmail.com`
* **GitHub:** [@ArmaanGoswami](https://github.com/ArmaanGoswami)

---
*Created with ❤️ for OLED Privacy & Anti-Peeping Protection on Windows.*
