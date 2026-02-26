# 📦 Installation Guide

Complete installation instructions for the Video Transcriber & AI Summarizer.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Git** for cloning the repository
- **ffmpeg** for audio/video processing
- **LM Studio** for local LLM inference

## System Dependencies

### Install ffmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
1. Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH: System Properties → Environment Variables → Path → Add `C:\ffmpeg\bin`

#### Verify Installation
```bash
ffmpeg -version
```

### Install LM Studio

1. Download from [https://lmstudio.ai/](https://lmstudio.ai/)
2. Install the application for your OS
3. Open LM Studio

## Installation Methods

### Option 1: Using `uv` ⭐ Recommended

**Why `uv`?**
- ⚡ 10-100x faster than pip
- 🔒 Built-in lock files
- 🎯 Deterministic installs
- 🚀 Modern Python tooling

#### Install `uv`

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/) for more options.

#### Setup Project

```bash
# Clone repository
git clone https://github.com/ferlopezcarr/video_transcriber.git
cd video_transcriber

# Install dependencies (creates .venv and installs everything)
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate      # Windows
```

#### Running Without Activation

With `uv`, you can run commands without activating the environment:

```bash
uv run python src/main.py "https://www.youtube.com/watch?v=video_id"
```

### Option 2: Using Traditional `venv` & `pip`

#### Clone Repository
```bash
git clone https://github.com/ferlopezcarr/video_transcriber.git
cd video_transcriber
```

#### Create Virtual Environment

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies

```bash
# Install in development mode
pip install -e .

# Or install from requirements (if available)
pip install -r requirements.txt
```

## Verify Installation

Run these commands to verify everything is installed correctly:

```bash
# Check Python version
python --version

# Check ffmpeg
ffmpeg -version

# Check installed packages
pip list | grep -E "yt-dlp|whisper|openai|dotenv"

# Test the application
python src/main.py --help
```

You should see the help message with all available options.

## Install Optional JavaScript Runtime

For better YouTube support, install a JavaScript runtime:

### Deno (Recommended)

**macOS:**
```bash
brew install deno
```

**Linux:**
```bash
curl -fsSL https://deno.land/install.sh | sh
```

**Windows:**
```powershell
irm https://deno.land/install.ps1 | iex
```

### Node.js (Alternative)

**Using nvm (recommended):**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js
nvm install node
```

**Or download from:** [https://nodejs.org/](https://nodejs.org/)

## Development Installation

If you're planning to contribute or modify the code:

```bash
# Install with development dependencies
pip install -e .[dev]

# Or with uv
uv sync --all-extras
```

This installs additional tools:
- `pytest` - Testing framework
- `black` - Code formatter
- `ruff` - Fast Python linter

## Troubleshooting Installation

### `uv` not found after installation

Add `uv` to your PATH:

**macOS/Linux:**
```bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
The installer should handle this automatically. If not, add `%USERPROFILE%\.cargo\bin` to your PATH.

### Python version mismatch

The project requires Python 3.12+. Check your version:

```bash
python --version
```

If you have multiple Python versions, you can specify one:

```bash
# With uv
uv venv --python 3.12

# With venv
python3.12 -m venv venv
```

### Permission errors on Linux/macOS

If you get permission errors:

```bash
# Don't use sudo with pip!
# Instead, ensure you're in a virtual environment

# Check if venv is activated
which python
# Should show path inside your project's venv
```

### Windows long path issues

Enable long paths in Windows:

1. Open Registry Editor (regedit)
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` to `1`
4. Restart your computer

Or use PowerShell (as Administrator):
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Installation hangs or is very slow

If installation is taking too long:

**With pip:**
```bash
# Use a different mirror
pip install -e . --index-url https://pypi.org/simple
```

**With uv:**
```bash
# uv is already optimized, but you can clear cache if needed
uv cache clean
uv sync
```

## Updating

### Update the Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
uv sync  # or pip install -e . --upgrade
```

### Update Individual Packages

```bash
# Update a specific package
pip install --upgrade package-name

# Or with uv
uv pip install --upgrade package-name
```

## Uninstalling

### Remove Virtual Environment

```bash
# Deactivate first
deactivate

# Remove the entire environment
rm -rf .venv  # for uv
# or
rm -rf venv   # for pip
```

### Remove Application

```bash
cd ..
rm -rf video_transcriber
```

## Next Steps

After installation:
1. [Configure LM Studio →](CONFIGURATION.md)
2. [Read Usage Examples →](../README.md#-usage)
3. [Learn About Architecture →](ARCHITECTURE.md)

---

[← Back to README](../README.md)
