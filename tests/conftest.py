"""Shared pytest fixtures for all tests."""

import pytest


@pytest.fixture
def sample_video_info():
    """Sample video info dict used across tests."""
    return {
        "title": "Sample Video Title",
        "duration": 900,  # 15 minutes
        "uploader": "Test Uploader",
        "view_count": 10000,
        "like_count": 500,
        "description": "Sample video description",
        "webpage_url": "https://www.youtube.com/watch?v=sample123",
    }


@pytest.fixture
def sample_vtt_content():
    """Sample VTT content for testing VTT cleaning."""
    return """WEBVTT

00:00:00.000 --> 00:00:02.500
This is the first line

00:00:02.500 --> 00:00:05.000
This is the second line

00:00:05.000 --> 00:00:08.000
This is the third line
"""


@pytest.fixture
def sample_transcription():
    """Sample transcription text."""
    return """This is a sample transcription.
It contains multiple lines.
Each line represents some spoken content."""
