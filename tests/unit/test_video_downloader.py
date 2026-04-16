"""Unit tests for video_downloader.py"""

import pytest
import tempfile
import os


class TestCleanVTT:
    """Tests for the _clean_vtt method in VideoDownloader."""

    def test_clean_vtt_removes_timestamps(self, sample_vtt_content, tmp_path):
        """Test that VTT timestamps are removed from content."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        # Write sample VTT content to a temporary file
        vtt_file = tmp_path / "test.vtt"
        vtt_file.write_text(sample_vtt_content)

        # Create VideoDownloader instance and clean VTT
        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # Check that timestamps are removed
        assert "00:00:00.000" not in result
        assert "00:00:02.500" not in result
        assert "00:00:05.000" not in result

        # Check that actual content is preserved
        assert "This is the first line" in result
        assert "This is the second line" in result
        assert "This is the third line" in result

    def test_clean_vtt_preserves_webvtt_header(self, sample_vtt_content, tmp_path):
        """Test that WEBVTT header is preserved (not filtered as a timestamp)."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        vtt_file = tmp_path / "test.vtt"
        vtt_file.write_text(sample_vtt_content)

        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # WEBVTT header is preserved because the filter only removes timestamps and digit-only lines
        assert "WEBVTT" in result

    def test_clean_vtt_removes_sequence_numbers(self, tmp_path):
        """Test that VTT sequence numbers are removed."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        # VTT content with sequence numbers
        vtt_with_numbers = """WEBVTT

1
00:00:00.000 --> 00:00:02.500
First line

2
00:00:02.500 --> 00:00:05.000
Second line
"""

        vtt_file = tmp_path / "test_numbers.vtt"
        vtt_file.write_text(vtt_with_numbers)

        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # Sequence numbers (single digit lines) should be removed
        lines = result.split("\n")
        assert "1" not in lines
        assert "2" not in lines

        # Content should be preserved
        assert "First line" in result
        assert "Second line" in result

    def test_clean_vtt_preserves_multiline_content(self, tmp_path):
        """Test that multi-line subtitle content is preserved."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        vtt_multiline = """WEBVTT

00:00:00.000 --> 00:00:03.000
This is a long subtitle
that spans multiple lines

00:00:03.000 --> 00:00:06.000
Another subtitle
also with multiple lines
"""

        vtt_file = tmp_path / "test_multiline.vtt"
        vtt_file.write_text(vtt_multiline)

        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # All content lines should be preserved
        assert "This is a long subtitle" in result
        assert "that spans multiple lines" in result
        assert "Another subtitle" in result
        assert "also with multiple lines" in result

    def test_clean_vtt_removes_empty_lines(self, tmp_path):
        """Test that empty lines are removed from cleaned output."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        vtt_with_blanks = """WEBVTT


00:00:00.000 --> 00:00:02.000
First line


00:00:02.000 --> 00:00:04.000
Second line

"""

        vtt_file = tmp_path / "test_blanks.vtt"
        vtt_file.write_text(vtt_with_blanks)

        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # Result should not have multiple consecutive empty lines
        assert "\n\n\n" not in result

        # Content should be preserved
        assert "First line" in result
        assert "Second line" in result

    def test_clean_vtt_handles_unicode(self, tmp_path):
        """Test that VTT cleaner handles Unicode characters correctly."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        vtt_unicode = """WEBVTT

00:00:00.000 --> 00:00:02.000
Hola, ¿cómo estás?

00:00:02.000 --> 00:00:04.000
Emoji test: 👍 ❤️ 🚀
"""

        vtt_file = tmp_path / "test_unicode.vtt"
        vtt_file.write_text(vtt_unicode, encoding="utf-8")

        downloader = VideoDownloader()
        result = downloader._clean_vtt(str(vtt_file))

        # Unicode should be preserved
        assert "Hola, ¿cómo estás?" in result
        assert "👍 ❤️ 🚀" in result


class TestGetBaseOpts:
    """Tests for the _get_base_opts method."""

    def test_get_base_opts_without_cookies(self, monkeypatch):
        """Test that base opts are empty when no cookies file is set."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        # Ensure YT_DLP_COOKIES_FILE is not set
        monkeypatch.delenv("YT_DLP_COOKIES_FILE", raising=False)

        downloader = VideoDownloader()
        opts = downloader._get_base_opts()

        assert opts == {}

    def test_get_base_opts_with_nonexistent_cookies_file(self, monkeypatch):
        """Test that cookies file is not added if file doesn't exist."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        # Set env var to non-existent file
        monkeypatch.setenv("YT_DLP_COOKIES_FILE", "/nonexistent/cookies.txt")

        downloader = VideoDownloader()
        opts = downloader._get_base_opts()

        # Should not include cookiefile if file doesn't exist
        assert "cookiefile" not in opts

    def test_get_base_opts_with_existing_cookies_file(self, monkeypatch, tmp_path):
        """Test that cookies file is added when it exists."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        # Create a temporary cookies file
        cookies_file = tmp_path / "cookies.txt"
        cookies_file.write_text("# Netscape HTTP Cookie File")

        monkeypatch.setenv("YT_DLP_COOKIES_FILE", str(cookies_file))

        downloader = VideoDownloader()
        opts = downloader._get_base_opts()

        # Should include cookiefile
        assert "cookiefile" in opts
        assert opts["cookiefile"] == str(cookies_file)

    def test_get_base_opts_with_js_runtimes(self, monkeypatch):
        """Test that JS runtimes are included when configured via environment variable."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        monkeypatch.delenv("YT_DLP_COOKIES_FILE", raising=False)
        monkeypatch.setenv("YT_DLP_JS_RUNTIMES", "deno,node")

        downloader = VideoDownloader()
        opts = downloader._get_base_opts()

        assert "js_runtimes" in opts
        assert opts["js_runtimes"] == ["deno", "node"]


class TestSubtitleStorage:
    """Tests for subtitle file storage paths."""

    def test_download_subtitles_stores_vtt_under_outputs_subtitles(self, monkeypatch, tmp_path):
        """Test that yt-dlp subtitle files are written under outputs/subtitles."""
        from src.infrastructure.outbound.video_downloader.adapters.video_downloader import (
            VideoDownloader,
        )

        monkeypatch.chdir(tmp_path)

        captured_opts = {}

        class FakeYoutubeDL:
            def __init__(self, opts):
                captured_opts.update(opts)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def extract_info(self, url, download=True):
                subtitle_path = tmp_path / "outputs" / "subtitles" / "Sample Title.es.vtt"
                subtitle_path.parent.mkdir(parents=True, exist_ok=True)
                subtitle_path.write_text("WEBVTT\n\nSubtitle line", encoding="utf-8")
                return {"title": "Sample Title"}

        monkeypatch.setattr("yt_dlp.YoutubeDL", FakeYoutubeDL)

        downloader = VideoDownloader()
        result = downloader.download_subtitles("https://example.com/video", "es")

        assert result == "WEBVTT\nSubtitle line"
        assert captured_opts["outtmpl"] == os.path.join(
            "outputs", "subtitles", "%(title)s.%(ext)s"
        )
