# 🎙️ Video Transcriber & AI Summarizer

A modern Python application that **extracts, transcribes, and intelligently organizes audio from videos** on **YouTube**, **TikTok**, and **Instagram**, using local speech-to-text models and AI-powered content organization via LM Studio.

Built with **hexagonal architecture** for maintainability and extensibility, featuring smart caching, health checks, and comprehensive error handling.

---

## ✨ Features

- 🎥 **Multi-Platform Support**: YouTube, TikTok, and Instagram
- 🎯 **Smart Transcription**: Automatic subtitle extraction and audio transcription (faster-whisper/openai-whisper)
- 🤖 **AI-Powered Summaries**: Local LLM integration via LM Studio for structured markdown summaries
- ⚡ **Smart Caching**: Automatically reuses existing transcriptions and summaries
- 🏗️ **Hexagonal Architecture**: Clean, testable, and easily extensible
- 🌐 **Multi-Language**: Generate summaries in any language
- 🔧 **Configurable**: Environment-based configuration with dotenv
- 📦 **Modern Tooling**: Support for `uv` (fast) and traditional `pip`

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions for all platforms
- **[Configuration Guide](docs/CONFIGURATION.md)** - LM Studio setup and environment configuration
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and component interactions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solutions to common issues
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and extending the application

## 🚀 Quick Start

### Requirements

- Python 3.12+
- ffmpeg
- LM Studio (for AI summaries)

### Installation

**Using uv (recommended):**

```bash
# Clone repository
git clone https://github.com/ferlopezcarr/video_transcriber.git
cd video_transcriber

# Install dependencies
uv sync

# Activate environment
source .venv/bin/activate
```

**Using pip:**

```bash
git clone https://github.com/ferlopezcarr/video_transcriber.git
cd video_transcriber
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### Configuration

1. Install [LM Studio](https://lmstudio.ai/) and start the local server
2. Copy environment template: `cp .env.example .env`
3. Edit `.env` with your LM Studio server address

```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=not-needed
LM_STUDIO_MODEL=local-model
LM_STUDIO_TIMEOUT=300.0
```

**See [Configuration Guide](docs/CONFIGURATION.md) for detailed setup.**

## 📖 Usage

### Basic Command

```bash
python src/main.py <VIDEO_URL> [OPTIONS]
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `url` | - | Video URL (YouTube, TikTok, Instagram) | **Required** |
| `--transcript-model` | `-tm` | Transcription engine: `faster-whisper` or `openai-whisper` | `faster-whisper` |
| `--lang` | `-l` | Output language code (`en`, `es`, `fr`, `de`, etc.) | `en` |
| `--llm-model` | `-llm` | LM Studio model name | `local-model` |
| `--enrich-text` | `-e` | Enable internet research for richer context | `False` |

### Examples

**Basic usage:**
```bash
python src/main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Spanish output:**
```bash
python src/main.py "https://www.youtube.com/watch?v=video_id" --lang es
```

**With uv (no activation needed):**
```bash
uv run python src/main.py "https://www.youtube.com/watch?v=video_id"
```

### Smart Caching

The application automatically caches processed videos. Running the same video URL again will skip processing and show cached file locations.

**To reprocess a video, delete the cached files:**
```bash
rm outputs/transcriptions/"Video Title.txt"
rm outputs/summaries/"Video Title.md"
```

## 📦 Output Structure

Generated files are organized in the `outputs/` directory:

```
outputs/
├── transcriptions/          # Plain text transcriptions
│   └── Video Title.txt
└── summaries/              # AI-organized summaries
    └── Video Title.md
```

**Transcriptions** (`*.txt`):
- Raw or subtitle-based transcription
- Plain text format
- Timestamped (if from audio transcription)

**Summaries** (`*.md`):
- Structured Markdown document
- Organized by topics and sections
- Includes title, table of contents, topic-based sections, and source link

## 🔧 Available LLM Models

Popular models you can load in LM Studio:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `llama3-8b` | ⭐⭐ | Fast | High | General use, recommended |
| `llama3-70b` | ⭐⭐⭐⭐⭐ | Slow | Excellent | Detailed analysis |
| `mistral-7b` | ⭐⭐ | Very Fast | Good | Quick summaries |
| `neural-chat-7b` | ⭐⭐ | Fast | Good | Conversational style |
| `phi-3-mini` | ⭐ | Very Fast | Moderate | Low-resource systems |

Download models directly in LM Studio from Hugging Face or load GGUF files.

**See [Configuration Guide](docs/CONFIGURATION.md) for model selection and hardware requirements.**

## 🌐 Internet Enrichment

Enable with `--enrich-text` flag to enhance summaries with:
- Research on mentioned topics and concepts
- Historical context and background information
- Relevant external links and references
- Enhanced technical explanations

**Note**: Requires internet connection and increases processing time.

## 🐛 Troubleshooting

### Quick Solutions

**LM Studio connection issues:**
1. Verify LM Studio is running and server is started
2. Check `.env` configuration matches server address
3. Test manually: `curl http://localhost:1234/v1/models`

**Transcription errors:**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Try alternative model: `--transcript-model openai-whisper`

**Memory issues:**
- Use smaller models (faster-whisper, 7B LLMs)
- Increase system swap/virtual memory

**For detailed troubleshooting, see [Troubleshooting Guide](docs/TROUBLESHOOTING.md)**

## 🛠️ Development

The project follows hexagonal architecture with clean separation between business logic and infrastructure.

**Project structure:**
```
src/
├── main.py              # Entry point
├── config/              # Configuration management
├── application/         # Business logic
└── infrastructure/      # External integrations
```

**Development tools:**
- `black` - Code formatting
- `ruff` - Linting
- `pytest` - Testing
- `mypy` - Type checking

**For detailed development information, see [Development Guide](docs/DEVELOPMENT.md)**

## 🚀 Future Enhancements

- [ ] Database integration for transcription search
- [ ] Web UI for easier interaction
- [ ] Batch processing for multiple videos
- [ ] Support for more LLM providers (OpenAI, Anthropic, Google)
- [ ] Real-time transcription for live streams
- [ ] Export to different formats (PDF, DOCX, HTML)

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast transcription
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [LM Studio](https://lmstudio.ai/) - Local LLM inference

## 🤝 Contributing

Contributions are welcome! Please see the [Development Guide](docs/DEVELOPMENT.md) for details on:
- Setting up your development environment
- Code style and quality standards
- Testing requirements
- Pull request guidelines

---

Made with ❤️ by [ferlopezcarr](https://github.com/ferlopezcarr)
