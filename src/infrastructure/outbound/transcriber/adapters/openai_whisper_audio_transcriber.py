from src.infrastructure.outbound.transcriber.ports.audio_transcriber_port import (
    AudioTranscriberPort,
)


class OpenAiWhisperAudioTranscriberAdapter(AudioTranscriberPort):
    def transcribe(self, audio_path: str, lang):
        print("Using openai-whisper for transcription...")
        import whisper

        model = whisper.load_model("base")
        if lang:
            result = model.transcribe(audio_path, language=lang)
        else:
            result = model.transcribe(audio_path)
        return result["text"]
