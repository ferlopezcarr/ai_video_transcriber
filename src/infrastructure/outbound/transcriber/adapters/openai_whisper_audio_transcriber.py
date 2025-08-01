from infrastructure.outbound.transcriber.ports.audio_transcriber_port import AudioTranscriberPort

class OpenAiWhisperAudioTranscriberAdapter(AudioTranscriberPort):
    def transcribe(self, audio_path: str, _):
        print("Using openai-whisper for transcription...")
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result['text']