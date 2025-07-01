# 🌙 LunaStudio - Lightweight VTube Studio Alternative

**LunaStudio** is a lightweight, Python-based alternative to VTube Studio, designed especially for users on lower-end hardware.
Built with **Live2D Cubism Native Warped** ([source](https://github.com/Arkueid/live2d-py)) and **Google MediaPipe** ([source](https://ai.google.dev/edge/mediapipe/solutions/guide)), it delivers smooth, efficient 2D model tracking without heavy resource usage.

## 🔥 Why Choose LunaStudio?

- **85% less RAM usage** compared to VTube Studio (tested with heavy models)
- **20% lower CPU load** under similar conditions
- **Lightweight & portable** – no bloated installers
- **EXE build available** – no Python environment required!

> _Tested on: Windows 11 • AMD Ryzen 5 2400G • GTX 1050 • 16 GB RAM_

## 🛠️ Features

- Low hardware requirements – suitable for integrated graphics and older PCs.
- Custom model import – load your own Live2D models.
- Standalone EXE release in [Releases](https://github.com/Lunariaverse/LunaStudio/releases/).
- Manual configuration via `config.json`:

  - Change background image (must be in `Media/Assets`)
  - Adjust window size, FPS cap, and auto blink/breath features.

## 📦 Latest Release – v1.1.2

### ✅ Highlights:

- Load and switch between models seamlessly.
- Improved webcam detection across different systems.
- Manual config allows fine-tuning without restarting the app.
- Change background by placing your image in `Media/Assets` and setting the file name in `config.json`.

### ⚙️ How to configure:

Example `Media/Config/config.json`:

```json
{
  "Auto Breath": false,
  "Auto Blink": false,
  "CapFPS": {
    "capFps": true,
    "CapFpsValue": 30
  },
  "display": [800, 900],
  "background": "background.jpg"
}
```

> **Note:** background images **must** be in `Media/Assets`. Files outside this folder won’t load.

## 📥 Installation

### Option 1: Standalone EXE (Recommended)

1. Download the latest `.exe` from the [Releases](https://github.com/Lunariaverse/LunaStudio/releases/) page.
2. Run it – no setup or dependencies needed!

### Option 2: Python Source

```bash
git clone https://github.com/Lunariaverse/LunaStudio.git
cd LunaStudio
pip install -r requirements.txt
python main.py
```

## 📂 Importing Models

Just place your Live2D models inside the `./models/` folder.

## 🚀 What’s next

- Builds for macOS and Linux.
- More user customization and UI improvements.

## 🤝 Supported By

<a href="https://www.aivara.my.id/">
  <img src="https://lunariaverse.xyz/partner/Aivara.png" width="300">
</a>

Maintained by [Lunaria Entertainment](https://www.lunariaverse.xyz/) & community.

## 💬 Feedback & Contributions

- **Found an issue?** Report it on [GitHub Issues](https://github.com/Lunariaverse/LunaStudio/issues).
- **Want to contribute?** Pull requests are always welcome!

Thank you for using LunaStudio! 🌙✨
