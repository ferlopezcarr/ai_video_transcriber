#!/usr/bin/env python
"""Test script to regenerate summary from existing transcription."""

from dotenv import load_dotenv


load_dotenv()

from application.transcription.services.llm_markdown_service import transcription_to_markdown
from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage

# Read existing transcription
storage = LocalFileStorage()
transcription_file = "Curso Inteligencia Artificial para Programadores en 2026 (Conceptos, Herramientas, Claude Code).txt"
transcription = storage.read(f"transcriptions/{transcription_file}")

# Create dummy video info (duration ~17 minutes based on file size)
video_info = {
    'title': 'Curso Inteligencia Artificial para Programadores en 2026 (Conceptos, Herramientas, Claude Code)',
    'duration': 5997,  # 99:57 in seconds
    'uploader': 'Unknown',
    'view_count': 0,
    'like_count': 0,
    'description': 'AI course for programmers',
    'webpage_url': 'https://www.youtube.com/watch?v=2aN_-m1uU4k',
}

print("🧪 Testing summary generation with improved prompt...")
print(f"📄 Transcription file: {transcription_file}")
print(f"📝 Transcription length: {len(transcription)} characters\n")

# Generate summary
result = transcription_to_markdown(
    transcription=transcription,
    model="qwen2.5-coder:32b",  # Or your preferred model
    video_info=video_info,
    lang='es',
    enrich_text=False
)

print(f"\n✅ Summary generated: {result}")
