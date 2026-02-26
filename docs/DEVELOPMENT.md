# 🛠️ Development Guide

Guide for developers contributing to or extending the Video Transcriber & AI Summarizer.

## Development Setup

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/ferlopezcarr/video_transcriber.git
cd video_transcriber

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate      # Windows

# Install in development mode
pip install -e .[dev]

# Or with uv
uv sync --all-extras
```

### 2. Install Development Tools

The project uses modern Python development tools:

```bash
pip install black ruff pytest pytest-cov mypy
```

**Tool Overview:**
- **black** - Code formatter (opinionated, consistent)
- **ruff** - Fast linter (replaces flake8, isort, etc.)
- **pytest** - Testing framework
- **mypy** - Static type checker

## Project Structure

### Detailed Directory Layout

```
video_transcriber/
├── src/
│   ├── __init__.py
│   ├── main.py                          # Application entry point
│   ├── requirements.txt                 # Dependencies list
│   │
│   ├── config/                          # Configuration management
│   │   ├── __init__.py
│   │   └── env_service.py               # Environment variables handler
│   │
│   ├── application/                     # Business logic layer
│   │   ├── __init__.py
│   │   └── transcription/
│   │       ├── __init__.py
│   │       └── services/
│   │           ├── __init__.py
│   │           ├── transcription_service.py      # Core transcription orchestration
│   │           ├── video_downloader_service.py   # Video metadata extraction
│   │           └── llm_markdown_service.py       # Summary generation
│   │
│   └── infrastructure/                  # Infrastructure layer (adapters)
│       ├── __init__.py
│       │
│       ├── inbound/                     # Driving adapters (input)
│       │   ├── __init__.py
│       │   └── console/                 # CLI interface
│       │       ├── __init__.py
│       │       ├── ports/
│       │       │   ├── __init__.py
│       │       │   └── user_input_port.py        # Input port interface
│       │       └── adapters/
│       │           ├── __init__.py
│       │           └── console_user_input_adapter.py  # CLI implementation
│       │
│       └── outbound/                    # Driven adapters (output)
│           ├── __init__.py
│           ├── agents/                  # LLM adapters
│           │   ├── __init__.py
│           │   ├── ports/
│           │   │   ├── __init__.py
│           │   │   └── summarizer_agent.py       # LLM port interface
│           │   └── adapters/
│           │       ├── __init__.py
│           │       └── summarizer_lmstudio_agent.py  # LM Studio implementation
│           │
│           ├── transcriber/             # Speech-to-text adapters
│           │   ├── __init__.py
│           │   ├── ports/
│           │   │   ├── __init__.py
│           │   │   └── audio_transcriber_port.py  # Transcriber interface
│           │   └── adapters/
│           │       ├── __init__.py
│           │       ├── faster_whisper_audio_transcriber.py  # faster-whisper impl
│           │       └── openai_whisper_audio_transcriber.py  # openai-whisper impl
│           │
│           ├── video_downloader/        # Video download adapters
│           │   ├── __init__.py
│           │   ├── ports/
│           │   │   ├── __init__.py
│           │   │   └── video_downloader_port.py   # Downloader interface
│           │   └── adapters/
│           │       ├── __init__.py
│           │       └── video_downloader.py        # yt-dlp implementation
│           │
│           └── file_storage/            # File system adapters
│               ├── __init__.py
│               ├── ports/
│               │   ├── __init__.py
│               │   └── file_storage_port.py       # Storage interface
│               └── adapters/
│                   ├── __init__.py
│                   └── local_file_storage.py      # Local filesystem impl
│
├── outputs/                             # Generated files (gitignored)
│   ├── transcriptions/                  # Raw transcription text files
│   ├── summaries/                       # Structured markdown summaries
│   ├── metadata/                        # Video metadata JSON
│   └── audio/                           # Downloaded audio files
│
├── docs/                                # Documentation
│   ├── ARCHITECTURE.md
│   ├── CONFIGURATION.md
│   ├── INSTALLATION.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md                   # This file
│
├── tests/                               # Test files (to be created)
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── .env                                 # Local configuration (gitignored)
├── .env.example                         # Configuration template
├── .gitignore                           # Git ignore patterns
├── pyproject.toml                       # Project metadata & dependencies
├── README.md                            # Main documentation
└── LICENSE                              # MIT License
```

## Code Style & Standards

### Formatting with Black

```bash
# Format all code
black src/

# Check what would change (dry run)
black --check src/

# Format specific file
black src/main.py
```

**Black Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
```

### Linting with Ruff

```bash
# Lint all code
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Lint specific file
ruff check src/main.py
```

**Ruff Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]
```

### Type Checking with mypy

```bash
# Type check all code
mypy src/

# Check specific file
mypy src/main.py

# Strict mode
mypy --strict src/
```

**Best Practices:**
- Always add type hints to function signatures
- Use `Optional[Type]` for nullable values
- Prefer `list[Type]` over `List[Type]` (Python 3.12+)

### Code Quality Checklist

Before committing:
- [ ] Run `black src/` to format code
- [ ] Run `ruff check --fix src/` to fix linting issues
- [ ] Run tests with `pytest`
- [ ] Add docstrings to new functions/classes
- [ ] Update type hints
- [ ] Update documentation if needed

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests (isolated components)
│   ├── test_env_service.py
│   ├── test_transcription_service.py
│   └── test_file_storage.py
│
├── integration/             # Integration tests (component interactions)
│   ├── test_lmstudio_integration.py
│   ├── test_transcription_flow.py
│   └── test_cache_system.py
│
└── fixtures/                # Test data and fixtures
    ├── sample_audio.mp3
    ├── sample_transcription.txt
    └── mock_responses.json
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_env_service.py

# Run specific test
pytest tests/unit/test_env_service.py::test_get_base_url

# Run with verbose output
pytest -v

# Run with output capture disabled (see prints)
pytest -s
```

### Writing Tests

**Example: Unit Test**

```python
# tests/unit/test_env_service.py
import os
import pytest
from src.config.env_service import EnvService

def test_get_lm_studio_base_url():
    """Test LM Studio base URL retrieval."""
    # Set environment variable
    os.environ['LM_STUDIO_BASE_URL'] = 'http://test:1234/v1'
    
    # Test
    url = EnvService.get_lm_studio_base_url()
    
    # Assert
    assert url == 'http://test:1234/v1'

def test_get_lm_studio_base_url_default():
    """Test default value when env var not set."""
    # Remove env var if exists
    os.environ.pop('LM_STUDIO_BASE_URL', None)
    
    # Test with default
    url = EnvService.get_lm_studio_base_url()
    
    # Should return default
    assert url == 'http://localhost:1234/v1'
```

**Example: Integration Test**

```python
# tests/integration/test_cache_system.py
import pytest
from src.application.transcription.services.transcription_service import transcribe
from src.infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage

def test_transcription_caching(tmp_path):
    """Test that transcription is cached correctly."""
    # Setup
    storage = LocalFileStorage(base_path=str(tmp_path))
    video_url = "https://example.com/video.mp4"
    
    # First call - should transcribe
    result1 = transcribe(video_url, storage)
    
    # Second call - should use cache
    result2 = transcribe(video_url, storage)
    
    # Assert same result from cache
    assert result1 == result2
    assert storage.exists("transcriptions/video.txt")
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_output_dir():
    """Provide temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_lm_studio(monkeypatch):
    """Mock LM Studio API responses."""
    class MockClient:
        def list_models(self):
            return ["test-model"]
    
    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: MockClient())
    yield
```

## Adding New Features

### Adding a New LLM Provider

Example: Adding OpenAI support alongside LM Studio

**1. Create Port Interface** (if not exists)

```python
# src/infrastructure/outbound/agents/ports/summarizer_agent.py
from abc import ABC, abstractmethod

class SummarizerAgent(ABC):
    @abstractmethod
    def organize_transcription(self, transcription: str, video_title: str) -> str:
        """Generate structured summary from transcription."""
        pass
```

**2. Create Adapter Implementation**

```python
# src/infrastructure/outbound/agents/adapters/summarizer_openai_agent.py
from openai import OpenAI
from ..ports.summarizer_agent import SummarizerAgent
from src.config.env_service import EnvService

class SummarizerOpenAIAgent(SummarizerAgent):
    def __init__(self):
        self.client = OpenAI(
            api_key=EnvService.get_openai_api_key()
        )
        self.model = EnvService.get_openai_model()
    
    def organize_transcription(self, transcription: str, video_title: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant..."},
                {"role": "user", "content": f"Summarize this: {transcription}"}
            ]
        )
        return response.choices[0].message.content
```

**3. Add Configuration Support**

```python
# src/config/env_service.py
class EnvService:
    # ...existing methods...
    
    @staticmethod
    def get_llm_provider() -> str:
        """Get configured LLM provider (lmstudio or openai)."""
        return os.getenv('LLM_PROVIDER', 'lmstudio')
    
    @staticmethod
    def get_openai_api_key() -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    @staticmethod
    def get_openai_model() -> str:
        return os.getenv('OPENAI_MODEL', 'gpt-4')
```

**4. Update Service to Use New Adapter**

```python
# src/application/transcription/services/llm_markdown_service.py
from src.config.env_service import EnvService

def get_summarizer_agent():
    """Factory function to create appropriate summarizer."""
    provider = EnvService.get_llm_provider()
    
    if provider == 'openai':
        from src.infrastructure.outbound.agents.adapters.summarizer_openai_agent import SummarizerOpenAIAgent
        return SummarizerOpenAIAgent()
    elif provider == 'lmstudio':
        from src.infrastructure.outbound.agents.adapters.summarizer_lmstudio_agent import SummarizerLMStudioAgent
        return SummarizerLMStudioAgent()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

def transcription_to_markdown(video_title: str, transcription_text: str, storage) -> str:
    summarizer = get_summarizer_agent()
    # ...rest of implementation
```

**5. Add Tests**

```python
# tests/integration/test_openai_agent.py
def test_openai_agent(monkeypatch):
    """Test OpenAI agent integration."""
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    
    agent = get_summarizer_agent()
    assert isinstance(agent, SummarizerOpenAIAgent)
```

### Adding a New Transcription Engine

Follow the same pattern as above:
1. Define port interface in `transcriber/ports/`
2. Implement adapter in `transcriber/adapters/`
3. Add configuration support
4. Update service layer
5. Add tests

## Debugging

### IDE Debugging (VS Code)

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "args": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

Then press F5 to start debugging.

### Logging

Add logging to track execution:

```python
import logging

# Configure in main.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Processing video: %s", video_url)
logger.info("Transcription complete")
logger.warning("Cache miss, re-processing")
logger.error("Failed to connect: %s", error)
```

### Print Debugging

For quick debugging:

```python
print(f"DEBUG: video_title = {video_title}")
print(f"DEBUG: type(transcription) = {type(transcription)}")

import json
print(json.dumps(data, indent=2))  # Pretty print dicts
```

## Contributing Guidelines

### Git Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/add-openai-support
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add OpenAI LLM provider support"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/add-openai-support
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(llm): add OpenAI provider support
fix(cache): handle missing transcription file
docs(readme): update installation instructions
refactor(storage): simplify file path handling
test(transcription): add caching tests
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with changes
3. **Create release tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
4. **Build package:**
   ```bash
   python -m build
   ```
5. **Publish** (if applicable):
   ```bash
   twine upload dist/*
   ```

## Useful Commands

```bash
# Format and lint
black src/ && ruff check --fix src/

# Run tests with coverage
pytest --cov=src --cov-report=html

# Type check
mypy src/

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Check package vulnerabilities
pip-audit  # Install: pip install pip-audit
```

---

[← Back to README](../README.md)
