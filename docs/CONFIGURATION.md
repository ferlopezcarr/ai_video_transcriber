# ⚙️ Configuration Guide

Complete configuration guide for the Video Transcriber & AI Summarizer.

## Overview

The application uses environment variables for configuration, managed through a `.env` file for convenience.

**Note:** The current LLM backend is **LM Studio** (local). A cloud LLM provider is planned as a future replacement. Configuration will change when that migration happens.

## Quick Start

1. Copy the example configuration:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```bash
nano .env  # or use your preferred editor
```

3. Test your configuration:
```bash
python -m src.main --help
```

## Configuration File (`.env`)

### Complete Example

```bash
# LM Studio Configuration (must be explicitly set)
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=
LM_STUDIO_MODEL=openai/gpt-oss-20b

# Timeout in seconds for LM Studio API requests
# Default is 1800.0 (30 minutes) as the minimum timeout floor
LM_STUDIO_TIMEOUT=1800.0

# Additional timeout budget per video minute.
# Default is 120 seconds, so a 60-minute video gets a 7200s timeout.
LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE=120.0

# Optional: path to Netscape cookies.txt for age-restricted videos
# Leave unset for normal public videos
# YT_DLP_COOKIES_FILE=/absolute/path/to/cookies.txt

# Optional: JavaScript runtimes for yt-dlp (comma-separated)
# Helps avoid YouTube warning about missing JS runtime support
# YT_DLP_JS_RUNTIMES=deno,node
```

### YouTube Downloader Notes

- For public YouTube videos, leave `YT_DLP_COOKIES_FILE` unset.
- If yt-dlp warns about missing JavaScript runtimes, set `YT_DLP_JS_RUNTIMES`.
- If YouTube videos are age-restricted, provide a cookies file:

```bash
export YT_DLP_JS_RUNTIMES=deno,node
export YT_DLP_COOKIES_FILE=/absolute/path/to/cookies.txt
python -m src.main "https://www.youtube.com/watch?v=video_id"
```

## Configuration Options

### LM Studio Settings

#### `LM_STUDIO_BASE_URL`

**Purpose:** API endpoint for LM Studio server

**Default:** `''` (empty string - must be explicitly set)

**Examples:**
```bash
# Local instance (most common)
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# Different port
LM_STUDIO_BASE_URL=http://localhost:8080/v1

# Remote server
LM_STUDIO_BASE_URL=http://192.168.1.100:1234/v1

# Different machine on network
LM_STUDIO_BASE_URL=http://my-llm-server.local:1234/v1
```

**Note:** Always include `/v1` at the end for OpenAI-compatible API.

#### `LM_STUDIO_API_KEY`

**Purpose:** API authentication key

**Default:** `''` (empty string)

**Usage:**
- LM Studio doesn't require authentication by default
- Can be left empty or set to any placeholder value
- If you've configured LM Studio with authentication, provide the actual key

```bash
# Default (no auth) - leave empty
LM_STUDIO_API_KEY=

# With authentication
LM_STUDIO_API_KEY=your-secret-key-here
```

#### `LM_STUDIO_MODEL`

**Purpose:** Name of the model to use

**Default:** `openai/gpt-oss-20b`

**Usage:**
- Specify the exact model name you want to use
- Can be overridden with `--llm-model` command-line option
- The application performs a health check that lists available models on startup

```bash
# Use default model
LM_STUDIO_MODEL=openai/gpt-oss-20b

# Specify exact model
LM_STUDIO_MODEL=llama3-8b

# Use model with version
LM_STUDIO_MODEL=mistral-7b-instruct-v0.2
```

**Finding Model Names:**
```bash
# List available models
curl http://localhost:1234/v1/models
```

#### `LM_STUDIO_TIMEOUT`

**Purpose:** Minimum request timeout in seconds

**Default:** `1800.0` (30 minutes)

**Usage:**
- Acts as the minimum timeout floor for summary generation
- Short videos keep this minimum timeout
- Longer videos scale above this floor based on `LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE`
- Slower systems may need a higher floor

```bash
# Conservative minimum for all videos
LM_STUDIO_TIMEOUT=900.0

# Recommended default minimum
LM_STUDIO_TIMEOUT=1800.0

# Extra-slow machine or large model
LM_STUDIO_TIMEOUT=2400.0
```

**Recommendations:**
- Default (1800 seconds / 30 minutes) is a good floor for most setups
- Raise it if model loading or prompt ingestion is slow on your machine
- Keep it lower only if you want timeouts to fail faster on shorter jobs

#### `LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE`

**Purpose:** Additional timeout budget per minute of video

**Default:** `120.0`

**Usage:**
- Controls how aggressively timeout grows with video length
- The effective timeout is `max(LM_STUDIO_TIMEOUT, video_minutes * LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE)`
- Useful when your local model runs slower or faster than real time

```bash
# 1 minute of timeout budget per video minute
LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE=60.0

# 2 minutes of timeout budget per video minute (default)
LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE=120.0

# 3 minutes of timeout budget per video minute
LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE=180.0
```

**Examples:**
- 10-minute video: `max(1800, 10 * 120) = 1800s`
- 30-minute video: `max(1800, 30 * 120) = 3600s`
- 60-minute video: `max(1800, 60 * 120) = 7200s`

## LM Studio Setup

### 1. Download and Install

1. Visit [https://lmstudio.ai/](https://lmstudio.ai/)
2. Download for your operating system
3. Install the application

### 2. Download a Model

**Option A: Through LM Studio UI**
1. Open LM Studio
2. Go to "Discover" or "Models" tab
3. Search for a model (recommended: `llama3-8b`, `mistral-7b`)
4. Click "Download"
5. Wait for download to complete

**Option B: Load Local GGUF File**
1. Download GGUF file from Hugging Face
2. In LM Studio, go to "Local Models"
3. Click "Load Model"
4. Select your GGUF file

### 3. Load the Model

1. In LM Studio, go to "Chat" or "Local Server" tab
2. Click on the model name dropdown
3. Select your downloaded model
4. Wait for the model to load into memory

### 4. Start the Server

1. Click on the "Local Server" tab in LM Studio
2. Click "Start Server" button
3. Note the server address (usually `http://localhost:1234`)
4. Keep LM Studio running while using the application

### 5. Verify Connection

Test the server is running:

```bash
# Check server health
curl http://localhost:1234/v1/models

# You should see a JSON response with available models
```

## Recommended Models

### For Different Use Cases

| Use Case | Model | Size | Reason |
|----------|-------|------|--------|
| **General Use** | `llama3-8b` | ~5GB | Best balance of quality and speed |
| **High Quality** | `llama3-70b` | ~40GB | Best quality, requires powerful hardware |
| **Quick Processing** | `mistral-7b` | ~4GB | Fast, good quality |
| **Low Resource** | `phi-3-mini` | ~2GB | Minimal resource usage |
| **Technical Content** | `neural-chat-7b` | ~4GB | Good for technical explanations |

### Hardware Requirements

| Model Size | RAM Required | GPU VRAM (Recommended) | Expected Speed |
|------------|--------------|------------------------|----------------|
| 7-8B | 8-16 GB | 6-8 GB | Fast (~30 tokens/sec) |
| 13B | 16-32 GB | 8-12 GB | Medium (~20 tokens/sec) |
| 70B | 64+ GB | 40+ GB | Slow (~5 tokens/sec) |

**Note:** Models can run on CPU, but GPU acceleration significantly improves speed.

## Environment Variables vs Command-Line Options

Some settings can be configured both ways.The command-line option takes precedence.

### Configuration Priority

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`.env` file)
3. **Default values** (lowest priority)

### Example

```bash
# In .env
LM_STUDIO_MODEL=llama3-8b

# Command line overrides .env
python -m src.main "video_url" --llm-model mistral-7b
# Uses: mistral-7b (from command line)
```

## Advanced Configuration

### Using Multiple LM Studio Instances

You can run multiple configurations:

```bash
# Development instance
LM_STUDIO_BASE_URL_DEV=http://localhost:1234/v1
LM_STUDIO_MODEL_DEV=mistral-7b

# Production instance (remote server)
LM_STUDIO_BASE_URL_PROD=http://production-server:1234/v1
LM_STUDIO_MODEL_PROD=llama3-70b
```

Then use environment variable selection:

```bash
# Use dev config
LM_STUDIO_BASE_URL=$LM_STUDIO_BASE_URL_DEV python -m src.main "url"

# Use prod config
LM_STUDIO_BASE_URL=$LM_STUDIO_BASE_URL_PROD python -m src.main "url"
```

### Network Configuration

#### Remote LM Studio Server

If LM Studio is running on a different machine:

1. **On the LM Studio machine:**
   - In LM Studio, go to "Local Server" → "Settings"
   - Change binding from `localhost` to `0.0.0.0` (allow external connections)
   - Note the IP address of the machine

2. **On the client machine:**
   ```bash
   LM_STUDIO_BASE_URL=http://192.168.1.100:1234/v1
   ```

3. **Firewall configuration:**
   - Allow port 1234 (or your chosen port) through firewall
   - Ensure both machines are on the same network or use VPN

#### Security Considerations

**Warning:** By default, LM Studio has no authentication.

If exposing to network:
- Use firewall rules to limit access
- Consider using VPN or SSH tunnel
- Don't expose to public internet without authentication

**SSH Tunnel Example:**
```bash
# Create tunnel to remote server
ssh -L 1234:localhost:1234 user@remote-server

# Use local endpoint
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

## Troubleshooting Configuration

### Connection Refused

**Symptom:** `Cannot connect to LM Studio at http://localhost:1234`

**Solutions:**
1. Check LM Studio is running
2. Verify server is started in LM Studio
3. Check port number matches
4. Try `curl http://localhost:1234/v1/models`

### Wrong Model Used

**Symptom:** Different model responds than expected

**Solutions:**
1. Check model is loaded in LM Studio
2. Verify `--llm-model` argument or `LM_STUDIO_MODEL` env var
3. List available models: `curl http://localhost:1234/v1/models`

### Timeout Errors

**Symptom:** `Request timed out` during processing

**Solutions:**
1. Increase `LM_STUDIO_TIMEOUT` if even short videos fail early
2. Increase `LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE` if longer videos time out disproportionately
2. Check LM Studio isn't frozen
3. Try smaller/faster model
4. Monitor system resources (RAM, CPU, GPU)

### Environment Variables Not Loading

**Symptom:** Application uses defaults instead of `.env` values

**Solutions:**
1. Verify `.env` file exists in project root
2. Check file name is exactly `.env` (not `.env.txt`)
3. Restart terminal/IDE after editing `.env`
4. Test: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('LM_STUDIO_BASE_URL'))"`

## Configuration Best Practices

1. **Use `.env` for local development**
   - Easy to edit
   - Not committed to git
   - Machine-specific settings

2. **Use environment variables for production**
   - Set in deployment environment
   - More secure
   - Easier to manage secrets

3. **Document your configuration**
   - Add comments to `.env` file
   - Update `.env.example` when adding new options

4. **Test configuration changes**
   - Use `--help` to verify
   - Run with short video first
   - Monitor health check messages

---

[← Back to README](../README.md) | [Troubleshooting →](TROUBLESHOOTING.md)
