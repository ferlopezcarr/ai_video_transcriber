from src.console import console
from src.infrastructure.outbound.transcriber.ports.audio_transcriber_port import (
    AudioTranscriberPort,
)


class OpenAiWhisperAudioTranscriberAdapter(AudioTranscriberPort):
    def transcribe(self, audio_path: str, lang):
        console.print("Using openai-whisper for transcription...")
        import whisper

        model = whisper.load_model("base")

        with console.status("[bold green]🎙️ Transcribing audio with OpenAI Whisper..."):
            if lang:
                result = model.transcribe(audio_path, language=lang)
            else:
                result = model.transcribe(audio_path)

        return result["text"]
