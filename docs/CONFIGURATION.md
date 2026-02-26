# ⚙️ Configuration Guide

Complete configuration guide for the Video Transcriber & AI Summarizer.

## Overview

The application uses environment variables for configuration, managed through a `.env` file for convenience.

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
python src/main.py --help
```

## Configuration File (`.env`)

### Complete Example

```bash
# LM Studio Configuration
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=not-needed
LM_STUDIO_MODEL=local-model

# Timeout in seconds for LM Studio API requests
# Increase for very long videos or slower systems
LM_STUDIO_TIMEOUT=300.0
```

## Configuration Options

### LM Studio Settings

#### `LM_STUDIO_BASE_URL`

**Purpose:** API endpoint for LM Studio server

**Default:** `http://localhost:1234/v1`

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

**Default:** `not-needed`

**Usage:**
- LM Studio doesn't require authentication by default
- Use `not-needed` or any placeholder value
- If you've configured LM Studio with authentication, provide the actual key

```bash
# Default (no auth)
LM_STUDIO_API_KEY=not-needed

# With authentication
LM_STUDIO_API_KEY=your-secret-key-here
```

#### `LM_STUDIO_MODEL`

**Purpose:** Name of the model to use

**Default:** `local-model`

**Usage:**
- The application auto-detects available models
- This is used as a fallback or preference
- Can be overridden with `--llm-model` command-line option

```bash
# Use any available model
LM_STUDIO_MODEL=local-model

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

**Purpose:** Request timeout in seconds

**Default:** `300.0` (5 minutes)

**Usage:**
- How long to wait for LLM responses
- Longer videos need more time
- Slower systems need more time

```bash
# Short videos (under 5 minutes)
LM_STUDIO_TIMEOUT=180.0

# Standard (5-20 minute videos)
LM_STUDIO_TIMEOUT=300.0

# Long videos (20-60 minutes)
LM_STUDIO_TIMEOUT=600.0

# Very long videos (1+ hour)
LM_STUDIO_TIMEOUT=1200.0
```

**Recommendations:**
- Start with default (300 seconds)
- Increase if you see timeout errors
- Monitor LM Studio's processing time during first run

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
python src/main.py "video_url" --llm-model mistral-7b
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
LM_STUDIO_BASE_URL=$LM_STUDIO_BASE_URL_DEV python src/main.py "url"

# Use prod config
LM_STUDIO_BASE_URL=$LM_STUDIO_BASE_URL_PROD python src/main.py "url"
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
1. Increase `LM_STUDIO_TIMEOUT` in `.env`
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
