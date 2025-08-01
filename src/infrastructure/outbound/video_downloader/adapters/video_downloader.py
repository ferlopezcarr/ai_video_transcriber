import os
import re
from typing import LiteralString
import yt_dlp
from infrastructure.outbound.video_downloader.ports.video_downloader_port import VideoDownloaderPort

class VideoDownloader(VideoDownloaderPort):
    def _clean_vtt(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        cleaned = []
        for line in lines:
            if not re.match(r'\d\d:\d\d:\d\d\.\d+', line) and not line.strip().isdigit():
                cleaned.append(line.strip())
        return '\n'.join([l for l in cleaned if l])

    def download_subtitles(self, url: str, lang: str) -> LiteralString | None:
        print("Trying to download automatic subtitles from YouTube...")
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'outtmpl': '%(title)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            title = result.get('title', 'output')
        vtt_file = f"{title}.{lang}.vtt"
        if os.path.exists(vtt_file):
            return self._clean_vtt(vtt_file)
        else:
            print("No subtitles found.")
            return None

    def download_audio(self, url: str) -> str:
        """
        Download the video from the given URL and return the path to the downloaded video file.
        :param url: The URL of the video to download.
        :return: The path to the downloaded video file.
        """
        print("Downloading audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'audio.mp3'

    def get_video_info(self, url: str) -> dict:
        """
        Fetch video information (title, duration, etc.) using yt_dlp.
        :param url: The URL of the video.
        :return: A dictionary with video information.
        """
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        video_info = {
            'title': info.get('title'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'description': info.get('description'),
            'webpage_url': info.get('webpage_url'),
        }

        print("\n--- VIDEO INFO ---\n")
        for k, v in video_info.items():
            print(f"{k}: {v}")
        print("\n------------------\n")

        return video_info
