import os
import re
from typing import LiteralString
import yt_dlp
from infrastructure.outbound.video_downloader.ports.video_downloader_port import VideoDownloaderPort

class VideoDownloader(VideoDownloaderPort):
    def _get_base_opts(self) -> dict:
        """
        Get base yt-dlp options with cookie support to avoid bot detection.
        Uses browser cookies (tries Chrome first, then Firefox, then others).
        Set YT_DLP_COOKIES_BROWSER env var to specify browser (e.g., 'chrome', 'firefox', 'safari').
        """
        browser = os.getenv('YT_DLP_COOKIES_BROWSER', 'chrome')
        opts = {
            # Use iOS and Android TV clients to avoid bot detection
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'skip': ['hls', 'dash'],
                }
            },
            # Add headers to mimic real browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        
        # Try to use cookies from browser to avoid bot detection
        try:
            opts['cookiesfrombrowser'] = (browser,)
            print(f"🍪 Using cookies from {browser} browser")
        except Exception as e:
            print(f"⚠️  Could not load cookies from {browser}: {str(e)}")
            print("   Continuing without cookies - may fail on some videos")
        
        return opts
    
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
        ydl_opts = self._get_base_opts()
        ydl_opts.update({
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'outtmpl': '%(title)s.%(ext)s',
        })
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
        ydl_opts = self._get_base_opts()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'audio.mp3'

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
