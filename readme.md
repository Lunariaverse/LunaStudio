# LunaStudio - Lightweight VTube Studio Alternative

**LunaStudio** is a lightweight, Python-based alternative to VTube Studio, designed for users with lower-end hardware. Leveraging **Live2D Cubism Native Warped** (via [source](https://github.com/Arkueid/live2d-py)) and **Google's MediaPipe** (via [source](https://ai.google.dev/edge/mediapipe/solutions/guide)), it provides smooth 2D model tracking with significantly reduced resource usage.

### 🔥 Why Choose LunaStudio?

- **85% less RAM usage** compared to VTube Studio (tested with heavy models).
- **20% lower CPU load** under the same conditions.
- **No bloated installations** – lightweight and efficient.
- **EXE release available** – no Python environment required!

## 🛠️ Features

✅ **Low Hardware Requirements** – Perfect for older PCs or integrated graphics.  
✅ **Custom Model Import** – Load models from a specified directory.  
✅ **Standalone EXE** – Available in [Releases](https://github.com/Lunariaverse/LunaStudio/releases/).

**Optimized Performance** – Tested on:

- **OS**: Windows 11 Home
- **CPU**: AMD Ryzen 5 2400G
- **GPU**: NVIDIA GeForce GTX 1050
- **RAM**: 8GB

## 📥 Installation

### Option 1: Standalone EXE (Recommended)

1. Download the latest `.exe` from the [Releases](https://github.com/Lunariaverse/LunaStudio/releases/) page.
2. Run it – no dependencies needed!

### Option 2: Python Setup

```bash
git clone https://github.com/Lunariaverse/LunaStudio.git
cd LunaStudio
pip install -r requirements.txt
python main.py
```

## 📂 Model Import Guide

Place your Live2D models in the `./models/` directory. Supported formats:

- `.model3.json` (Cubism 3.0+)
- `.moc3` (Cubism 4.0+)

## 🤝 Supported By

This project is proudly supported by:

<a href="https://www.aivara.my.id/">
<img src="https://lunariaverse.xyz/partner/Aivara.png"  width="300" >
</a>

## 💬 Feedback & Contributions

- **Issues?** Report them [here](https://github.com/Lunariaverse/LunaStudio/issues).
- **Want to contribute?** PRs are welcome!
