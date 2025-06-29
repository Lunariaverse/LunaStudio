# LunaStudio - Lightweight VTube Studio Alternative

**LunaStudio** is a lightweight, Python-based alternative to VTube Studio, designed for users with lower-end hardware.
It uses **Live2D Cubism Native Warped** ([source](https://github.com/Arkueid/live2d-py)) and **Google’s MediaPipe** ([source](https://ai.google.dev/edge/mediapipe/solutions/guide)) for smooth 2D model tracking with significantly reduced resource usage.

### 🔥 Why Choose LunaStudio?

- Uses **\~95% less RAM** after the initial stabilization period (about 2 minutes).
- **\~30% lower average CPU usage** compared to VTube Studio when tested with heavy models.
- **Lightweight** – no bloated installation or unnecessary background processes.
- **Standalone EXE release** – no need to set up a Python environment.

## 🛠️ Features

- ✅ **Low hardware requirements** – runs well on older PCs and integrated graphics.
- ✅ **Custom model import** – load models directly from a folder.
- ✅ **Standalone Windows build** – available in [Releases](https://github.com/Lunariaverse/LunaStudio/releases/).

📊 **Tested on:**

- **OS**: Windows 11 Home
- **CPU**: AMD Ryzen 5 2400G
- **GPU**: NVIDIA GeForce GTX 1050
- **RAM**: 16 GB

⚙️ **Current limitations (work in progress):**

- Cannot change background yet
- Settings menu not fully implemented
- Background rendering improvements planned
- More performance optimizations coming soon
- Build For Linux And macOS

## 📥 Installation

### Option 1: Standalone EXE (Recommended)

1. Download the latest `.exe` from the [Releases](https://github.com/Lunariaverse/LunaStudio/releases/) page.
2. Run it – no additional setup required.

### Option 2: Python Setup

```bash
git clone https://github.com/Lunariaverse/LunaStudio.git
cd LunaStudio
pip install -r requirements.txt
python main.py
```

## 🤝 Supported By

<a href="https://www.aivara.my.id/">
<img src="https://lunariaverse.xyz/partner/Aivara.png" width="300">
</a>

## 💬 Feedback & Contributions

- **Found an issue?** Report it [here](https://github.com/Lunariaverse/LunaStudio/issues).
- **Want to help?** Pull requests are welcome!
