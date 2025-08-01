from infrastructure.outbound.video_downloader.adapters.video_downloader import VideoDownloader
from infrastructure.outbound.video_downloader.ports.video_downloader_port import VideoDownloaderPort

def get_video_info(url: str) -> dict:
    """
    Get video information (title, duration, etc.) for a given URL.
    :param url: Video url
    """
    video_downloader: VideoDownloaderPort = VideoDownloader()
    return video_downloader.get_video_info(url)

