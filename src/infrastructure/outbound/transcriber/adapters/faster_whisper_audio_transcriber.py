from infrastructure.outbound.transcriber.ports.audio_transcriber_port import AudioTranscriberPort

class FasterWhisperAudioTranscriber(AudioTranscriberPort):
    def transcribe(self, audio_path: str, _) -> str:
        print("Using faster-whisper for transcription...")
        from faster_whisper import WhisperModel
        model = WhisperModel("base", compute_type="int8")
        segments, _ = model.transcribe(audio_path)
        return "\n".join([seg.text for seg in segments])
