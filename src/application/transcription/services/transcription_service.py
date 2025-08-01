from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage
from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort
from infrastructure.outbound.transcriber.ports.audio_transcriber_port import AudioTranscriberPort
from infrastructure.outbound.video_downloader.adapters.video_downloader import VideoDownloader
from infrastructure.outbound.video_downloader.ports.video_downloader_port import VideoDownloaderPort

def transcribe(url: str, video_name: str | None, audo_transcriber_model: str = 'faster-whisper', lang: str = 'en'):
    """
    Get the transcript of a video from YouTube, TikTok, or Instagram.
    :param url: The URL of the video to transcribe.
    :param model_choice: The transcription model to use ('faster-whisper' or 'openai-whisper').
    :param lang: The language code for the transcription.
    """
    def _detect_platform(url: str):
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url:
            return 'instagram'
        return 'unknown'
    
    def _getAudioTranscriber(audo_transcriber_model: str):
        if audo_transcriber_model == 'openai-whisper':
            from infrastructure.outbound.transcriber.adapters.openai_whisper_audio_transcriber import OpenAiWhisperAudioTranscriberAdapter
            return OpenAiWhisperAudioTranscriberAdapter()
        else:
            from infrastructure.outbound.transcriber.adapters.faster_whisper_audio_transcriber import FasterWhisperAudioTranscriber
            return FasterWhisperAudioTranscriber()
    
    def _saveTranscription(transcription: str) -> str:
        file_storage: FileStoragePort = LocalFileStorage()
        transcription_file_name: str = video_name if video_name else 'transcription_summary'
        return file_storage.save(data=transcription, file_path=f"{transcription_file_name}.txt")

    video_downloader: VideoDownloaderPort = VideoDownloader()

    platform = _detect_platform(url)
    print(f"Detected platform: {platform}")

    if platform == 'youtube':
        text = video_downloader.download_subtitles(url, lang)
        if text:
            return text

    audio_path = video_downloader.download_audio(url)

    audio_transcriber: AudioTranscriberPort = _getAudioTranscriber(audo_transcriber_model)
    transcription = audio_transcriber.transcribe(audio_path, lang)
    _saveTranscription(transcription)
    return transcription
