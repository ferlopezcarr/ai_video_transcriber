# 🔧 Troubleshooting Guide

Common issues and solutions for the Video Transcriber & AI Summarizer.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this checklist:

- [ ] Is LM Studio running?
- [ ] Is a model loaded in LM Studio?
- [ ] Is the local server started in LM Studio?
- [ ] Is ffmpeg installed? (`ffmpeg -version`)
- [ ] Is the `.env` file configured correctly?
- [ ] Are all dependencies installed? (`pip list`)
- [ ] Is your virtual environment activated?

## LM Studio Connection Issues

### Error: "Cannot connect to LM Studio"

```
Error: Cannot connect to LM Studio at http://localhost:1234
Cause: Connection refused
```

**Possible Causes & Solutions:**

#### 1. LM Studio is not running

**Solution:**
1. Open LM Studio application
2. Go to "Local Server" tab
3. Click "Start Server"
4. Wait for "Server running" message

#### 2. Wrong port or URL

**Solution:**

Check the port in LM Studio:
- In LM Studio, go to "Local Server" → "Server Settings"
- Note the port number (default: 1234)
- Update your `.env` file:

```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

Verify connectivity:
```bash
curl http://localhost:1234/v1/models
```

#### 3. No model loaded

**Solution:**
1. In LM Studio, go to "Chat" or "Local Server" tab
2. Click the model dropdown
3. Select a model from the list
4. Wait for "Model loaded" message
5. Ensure "Auto-load on server start" is checked (optional)

#### 4. Firewall blocking connection

**Solution:**

**macOS:**
```bash
# Check if port is listening
lsof -i :1234

# Grant LM Studio network permissions in:
System Settings → Privacy & Security → Firewall → Allow LM Studio
```

**Windows:**
```powershell
# Check if port is listening
netstat -ano | findstr :1234

# Allow through firewall:
# Settings → Windows Security → Firewall & network protection → Allow an app
```

**Linux:**
```bash
# Check if port is listening
netstat -tulpn | grep 1234

# Allow through UFW
sudo ufw allow 1234
```

### Error: "Request timed out"

```
APITimeoutError: Request timed out after 300.0 seconds
```

**Possible Causes & Solutions:**

#### 1. Model is slow or overwhelmed

**Solution:**

Increase timeout in `.env`:
```bash
# For longer videos or slower models
LM_STUDIO_TIMEOUT=600.0
```

Or use command-line override:
```bash
python src/main.py "video_url" --timeout 600
```

#### 2. Long video taking too long

**Solution:**

Use a faster model:
```bash
# In .env or LM Studio
LM_STUDIO_MODEL=mistral-7b  # Faster than llama3-70b
```

Or process shorter segments:
- Split very long videos into parts
- Download and transcribe first, summarize separately

#### 3. System resources exhausted

**Solution:**

Check system resources:
```bash
# macOS/Linux
top
htop  # if installed

# Windows
Task Manager → Performance tab
```

**If RAM is maxed out:**
- Close other applications
- Use a smaller model (7B instead of 70B)
- Reduce context window in LM Studio settings

**If GPU is overloaded:**
- Lower GPU layers in LM Studio
- Use CPU-only mode
- Reduce batch size

#### 4. LM Studio frozen or crashed

**Solution:**
1. Check LM Studio UI - is it responding?
2. Restart LM Studio
3. Reload the model
4. Try the request again

### Error: "Health check failed"

```
Health check failed: Could not list models from LM Studio
```

**Possible Causes & Solutions:**

#### 1. Server not fully initialized

**Solution:**

Wait a few seconds after starting the server:
```bash
# Start server, then wait
sleep 5
python src/main.py "video_url"
```

#### 2. API endpoint misconfigured

**Solution:**

Verify the endpoint URL:
```bash
# Test the models endpoint
curl http://localhost:1234/v1/models

# Should return JSON with model list
```

If 404 error, try:
```bash
# Without /v1
curl http://localhost:1234/models
```

Update `.env` accordingly.

## Transcription Issues

### Error: "yt-dlp error"

```
ERROR: Video unavailable
ERROR: Unable to download webpage
```

**Possible Causes & Solutions:**

#### 1. Video is private or removed

**Solution:**
- Verify the URL in a browser
- Check if the video is publicly accessible
- Try a different video

#### 2. yt-dlp is outdated

**Solution:**
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Or with uv
uv pip install --upgrade yt-dlp

# Verify version
yt-dlp --version
```

#### 3. Platform requires authentication

**Solution:**

Some platforms require cookies:
```bash
# Export cookies from browser (using browser extension)
# Then use with yt-dlp
python src/main.py "video_url" --cookies cookies.txt
```

For YouTube age-restricted videos:
```bash
# Add cookies to yt-dlp
yt-dlp --cookies-from-browser chrome "video_url"
```

#### 4. Geographic restrictions

**Solution:**

Use a VPN or proxy:
```bash
# Set proxy in environment
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

python src/main.py "video_url"
```

### Error: "Transcription failed"

```
Error during transcription: ffmpeg not found
```

**Possible Causes & Solutions:**

#### 1. ffmpeg not installed

**Solution:**

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add to PATH

Verify:
```bash
ffmpeg -version
```

#### 2. Audio file corrupted

**Solution:**
1. Delete cached audio file
2. Re-download:

```bash
rm outputs/audio/*
python src/main.py "video_url"
```

#### 3. Unsupported audio format

**Solution:**

Convert manually:
```bash
ffmpeg -i input.webm -ar 16000 -ac 1 output.wav
```

Then process the WAV file directly.

### Error: "Out of memory during transcription"

```
RuntimeError: CUDA out of memory
```

**Possible Causes & Solutions:**

#### 1. Video is very long

**Solution:**

Use the faster-whisper engine (default):
```python
# In transcription_service.py
transcriber = FasterWhisperAudioTranscriber()  # More efficient
```

Or process in segments:
```bash
# Split audio first
ffmpeg -i long_audio.mp3 -f segment -segment_time 600 -c copy part_%03d.mp3
```

#### 2. Model size too large

**Solution:**

Use a smaller Whisper model:
```python
# In faster_whisper_audio_transcriber.py
model = WhisperModel("base", device="cpu")  # Instead of "large-v2"
```

Available models: `tiny`, `base`, `small`, `medium`, `large-v2`

#### 3. GPU memory insufficient

**Solution:**

Force CPU usage:
```python
# In faster_whisper_audio_transcriber.py
model = WhisperModel("medium", device="cpu")
```

Or reduce batch size:
```python
model = WhisperModel("medium", device="cuda", compute_type="int8")
```

## File and Storage Issues

### Error: "Permission denied"

```
PermissionError: [Errno 13] Permission denied: 'outputs/transcriptions/file.txt'
```

**Possible Causes & Solutions:**

#### 1. File is open in another program

**Solution:**
- Close any text editors or viewers with the file open
- On Windows, check if antivirus is scanning the file

#### 2. Insufficient permissions

**Solution:**
```bash
# macOS/Linux
chmod 755 outputs/
chmod 644 outputs/transcriptions/*

# Check ownership
ls -la outputs/
```

#### 3. Disk is full

**Solution:**
```bash
# Check disk space
df -h  # macOS/Linux
wmic logicaldisk get size,freespace,caption  # Windows

# Clean up old files
rm -rf outputs/temp/*
```

### Error: "File not found"

```
FileNotFoundError: outputs/transcriptions/video_name.txt
```

**Possible Causes & Solutions:**

#### 1. Cache directory doesn't exist

**Solution:**
```bash
# Create required directories
mkdir -p outputs/transcriptions
mkdir -p outputs/summaries
mkdir -p outputs/metadata
mkdir -p outputs/audio
```

Or let the application create them:
```python
# In local_file_storage.py
os.makedirs(os.path.dirname(file_path), exist_ok=True)
```

#### 2. File name has invalid characters

**Solution:**

The application should sanitize filenames. If you see this error, check:
```python
# Special characters that might cause issues
invalid_chars = '<>:"/\\|?*'
```

Manually rename if needed:
```bash
mv "video:name.txt" "video_name.txt"
```

## Installation Issues

### Error: "Package not found"

```
ERROR: Could not find a version that satisfies the requirement package-name
```

**Possible Causes & Solutions:**

#### 1. Wrong Python version

**Solution:**
```bash
# Check Python version
python --version

# Requires Python 3.12+
# Install correct version or use pyenv
pyenv install 3.12
pyenv local 3.12
```

#### 2. Package name typo

**Solution:**

Check `requirements.txt` or `pyproject.toml`:
```bash
# Verify package exists
pip search package-name
```

#### 3. Network/proxy issues

**Solution:**
```bash
# Try different index
pip install --index-url https://pypi.org/simple package-name

# Or upgrade pip
pip install --upgrade pip
```

### Error: "uv not found"

```
zsh: command not found: uv
```

**Solution:**

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:
```bash
uv --version
```

## Configuration Issues

### Error: "Environment variable not set"

```
KeyError: 'LM_STUDIO_BASE_URL'
```

**Possible Causes & Solutions:**

#### 1. `.env` file missing

**Solution:**
```bash
# Copy example
cp .env.example .env

# Edit with your settings
nano .env
```

#### 2. `.env` not loaded

**Solution:**

Verify dotenv is installed:
```bash
pip install python-dotenv

# Test loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('LM_STUDIO_BASE_URL'))"
```

#### 3. Wrong working directory

**Solution:**

Ensure you're in the project root:
```bash
# Navigate to project root
cd /path/to/video_transcriber

# Run from there
python src/main.py "video_url"
```

## Performance Issues

### Application is very slow

**Symptoms:**
- Transcription takes hours
- Summarization never completes
- Application freezes

**Solutions:**

#### 1. Use faster models

```bash
# Transcription: Use base model instead of large
# In faster_whisper_audio_transcriber.py
model = WhisperModel("base")  # Fast

# Summarization: Use smaller LLM
LM_STUDIO_MODEL=mistral-7b  # Faster than llama3-70b
```

#### 2. Enable GPU acceleration

Check if GPU is being used:
```python
# In transcriber adapter
print(f"Device: {model.device}")  # Should be "cuda"
```

If using CPU:
- Install CUDA toolkit
- Install PyTorch with CUDA support
- Verify GPU with `nvidia-smi`

#### 3. Reduce quality settings

Trade quality for speed:
```python
# In transcriber
segments, info = model.transcribe(
    audio_path,
    beam_size=1,  # Lower beam size (faster)
    best_of=1,    # Reduce alternatives
)
```

### System runs out of memory

**Symptoms:**
- Application crashes
- OS becomes unresponsive
- "Out of memory" errors

**Solutions:**

#### 1. Use smaller models

```python
# Whisper
WhisperModel("tiny")  # ~1GB RAM

# LLM
LM_STUDIO_MODEL=phi-3-mini  # ~2GB RAM
```

#### 2. Close other applications

```bash
# Check memory usage
free -h  # Linux
vm_stat  # macOS
```

Close unnecessary applications before processing.

#### 3. Process in segments

For very long videos:
1. Download audio
2. Split into 10-minute segments
3. Process each segment separately
4. Combine results

## Still Having Issues?

### Collect Diagnostic Information

```bash
# System information
python --version
ffmpeg -version
pip list

# Test components
curl http://localhost:1234/v1/models
python -c "import faster_whisper; print(faster_whisper.__version__)"

# Check logs
python src/main.py "video_url" --verbose  # If implemented
```

### Enable Debug Mode

Add verbose logging to track issues:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Log Messages

**Normal operation:**
```
✅ LM Studio health check passed
✅ Found 2 models: llama3-8b, mistral-7b
✅ Using cached transcription...
✅ Processing complete!
```

**Warning signs:**
```
⚠️ Transcription file not found, processing...
⚠️ LM Studio response took longer than expected
⚠️ Retrying download...
```

**Errors:**
```
❌ Cannot connect to LM Studio
❌ Transcription failed
❌ API timeout
```

### Get Help

If you're still stuck:

1. **Check the logs** for error messages
2. **Search issues** on GitHub (if repository has issues enabled)
3. **Create a detailed issue** with:
   - Error message (full traceback)
   - System information (OS, Python version, etc.)
   - Steps to reproduce
   - What you've already tried

---

[← Back to README](../README.md) | [Configuration Guide →](CONFIGURATION.md)
