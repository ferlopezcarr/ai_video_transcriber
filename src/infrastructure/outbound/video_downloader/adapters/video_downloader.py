import os
import re
from typing import LiteralString
import yt_dlp
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    TextColumn,
)
from src.console import console
from yt_dlp.utils import DownloadError
from src.infrastructure.outbound.video_downloader.ports.video_downloader_port import (
    VideoDownloaderPort,
)


class VideoDownloader(VideoDownloaderPort):
    def _get_subtitles_dir(self) -> str:
        subtitles_dir = os.path.join("outputs", "subtitles")
        os.makedirs(subtitles_dir, exist_ok=True)
        return subtitles_dir

    def _get_base_opts(self) -> dict:
        """
        Get base yt-dlp options. Uses android_vr client by default (yt-dlp default)
        which avoids YouTube bot detection for public videos.
        Set YT_DLP_COOKIES_FILE to a Netscape cookies.txt path for age-restricted content.
        """
        opts = {}
        cookies_file = os.getenv("YT_DLP_COOKIES_FILE")
        if cookies_file and os.path.exists(cookies_file):
            opts["cookiefile"] = cookies_file
            console.print(f"🍪 Using cookies from file: {cookies_file}")

        js_runtimes = os.getenv("YT_DLP_JS_RUNTIMES")
        if js_runtimes:
            runtimes = [runtime.strip() for runtime in js_runtimes.split(",") if runtime.strip()]
            if runtimes:
                opts["js_runtimes"] = runtimes
                print(f"🧠 Using JS runtimes: {', '.join(runtimes)}")
        return opts

    def _clean_vtt(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cleaned = []
        for line in lines:
            if not re.match(r"\d\d:\d\d:\d\d\.\d+", line) and not line.strip().isdigit():
                cleaned.append(line.strip())
        return "\n".join([l for l in cleaned if l])

    def download_subtitles(self, url: str, lang: str) -> LiteralString | None:
        console.print("Trying to download automatic subtitles from YouTube...")
        subtitles_dir = self._get_subtitles_dir()
        ydl_opts = self._get_base_opts()
        ydl_opts.update(
            {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": [lang],
                "retries": 3,
                "fragment_retries": 3,
                "sleep_interval_requests": 1,
                "outtmpl": os.path.join(subtitles_dir, "%(title)s.%(ext)s"),
            }
        )
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=True)
                title = result.get("title", "output")
        except DownloadError as exc:
            error_message = str(exc)
            if "HTTP Error 429" in error_message:
                console.print(
                    "⚠️ YouTube rate-limited subtitle download (HTTP 429). "
                    "Falling back to audio transcription..."
                )
            else:
                console.print(
                    "⚠️ Could not download subtitles. Falling back to audio transcription..."
                )
                console.print(f"Reason: {error_message}")
            return None

        vtt_file = os.path.join(subtitles_dir, f"{title}.{lang}.vtt")
        if os.path.exists(vtt_file):
            return self._clean_vtt(vtt_file)
        else:
            console.print("No subtitles found.")
            return None

    def download_audio(self, url: str) -> str:
        """
        Download the video from the given URL and return the path to the downloaded video file.
        :param url: The URL of the video to download.
        :return: The path to the downloaded video file.
        """
        # Extract video ID from URL
        ydl_opts_info = self._get_base_opts()
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id", "video")

        # Create output directory if it doesn't exist
        audio_dir = "outputs/audio"
        os.makedirs(audio_dir, exist_ok=True)

        # Download audio with unique filename
        audio_filename = f"{video_id}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)

        # Setup progress bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]🎵 Downloading audio..."),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        )

        task_id = None

        def progress_hook(d):
            nonlocal task_id
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)

                if total:
                    if task_id is None:
                        task_id = progress.add_task("download", total=total)
                    progress.update(task_id, completed=downloaded)
            elif d["status"] == "finished":
                if task_id is not None:
                    progress.update(task_id, completed=progress.tasks[0].total)

        ydl_opts = self._get_base_opts()
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(audio_dir, f"{video_id}.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
            }
        )

        with progress:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        return audio_path

    def get_video_info(self, url: str) -> dict:
        """
        Fetch video information (title, duration, etc.) using yt_dlp.
        :param url: The URL of the video.
        :return: A dictionary with video information.
        """
        ydl_opts = self._get_base_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        video_info = {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "description": info.get("description"),
            "webpage_url": info.get("webpage_url"),
        }

        console.print("\n--- VIDEO INFO ---\n")
        for k, v in video_info.items():
            console.print(f"{k}: {v}")
        console.print("\n------------------\n")

        return video_info
