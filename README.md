# Warp Account Registrator & Manager

> **📝 Note**: This project is forked from [D3-vin/WARP_reg_and_manager](https://github.com/D3-vin/WARP_reg_and_manager)

## 📢 Connect with Us

- **📢 Channel**: [https://t.me/warp5215](https://t.me/warp5215) - Latest updates and releases
- **💬 Chat**: [https://t.me/warp1215](https://t.me/warp1215) - Community support and discussions
- **📁 GitHub**: [https://github.com/hj01857655/WARP_reg_and_manager](https://github.com/hj01857655/WARP_reg_and_manager) - Source code and development

![Python](https://img.shields.io/badge/Python-3.6+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-Educational%20Use-green)

## Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager (usually comes with Python)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

**Note for Windows users**: You may need to run as Administrator for proxy functionality.

**Note for Linux users**: You may need to use `python3` instead of `python`:
```bash
python3 main.py
```

## Dependencies

All dependencies are managed through `requirements.txt`:

- **PyQt5** - GUI framework
- **requests** - HTTP requests with SOCKS support
- **mitmproxy** - Traffic interception and proxy
- **psutil** - Process management
- **sqlite3** - Database (built-in with Python)

Install all at once:
```bash
pip install -r requirements.txt
```

**Python not found:**
```bash
# Linux/macOS
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                  # macOS with Homebrew

# Windows
# Download from https://python.org
```

**PyQt5 installation issues on Linux:**
```bash
# Try system package first
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets

# Then install other dependencies
pip install -r requirements.txt
```

**Permission issues (Windows):**
- Right-click Command Prompt/PowerShell → "Run as Administrator"
- Or install to user directory: `pip install -r requirements.txt --user`

**Display issues (Linux):**
- Make sure you're running in a desktop environment
- Check that `DISPLAY` or `WAYLAND_DISPLAY` environment variables are set

## License

This project is open source. Please check the license file for details.