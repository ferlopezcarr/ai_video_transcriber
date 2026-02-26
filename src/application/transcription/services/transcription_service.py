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
        if 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok' in url:
            return 'tiktok'
        elif 'instagram' in url:
            return 'instagram'
        else:
            # Get main domain from URL and use it as platform name
            return url.split('//')[-1].split('/')[0].split('?')[0]
    
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
        return file_storage.save(data=transcription, file_path=f"transcriptions/{transcription_file_name}.txt")
    
    def _checkExistingTranscription(video_name: str | None) -> str | None:
        """Check if a transcription already exists for this video."""
        if not video_name:
            return None
        file_storage: FileStoragePort = LocalFileStorage()
        file_path = f"transcriptions/{video_name}.txt"
        if file_storage.exists(file_path):
            print(f"\n📄 Found existing transcription: {file_path}")
            print("✅ Loading cached transcription...")
            return file_storage.read(file_path)
        return None

    # Check if transcription already exists
    existing_transcription = _checkExistingTranscription(video_name)
    if existing_transcription:
        return existing_transcription

    print("\n🎬 No cached transcription found. Processing video...")
    video_downloader: VideoDownloaderPort = VideoDownloader()

    platform = _detect_platform(url)
    print(f"Detected platform: {platform}")

    if platform == 'youtube':
        text = video_downloader.download_subtitles(url, lang)
        if text:
            _saveTranscription(text)
            return text

    audio_path = video_downloader.download_audio(url)

    audio_transcriber: AudioTranscriberPort = _getAudioTranscriber(audo_transcriber_model)
    transcription = audio_transcriber.transcribe(audio_path, lang)
    
    # Handle both string and list responses from transcriber
    if isinstance(transcription, list):
        transcription_text = '\n'.join(str(segment) for segment in transcription)
    else:
        transcription_text = transcription
    
    _saveTranscription(transcription_text)
    return transcription_text
