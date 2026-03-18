from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from src.console import console
from src.infrastructure.outbound.transcriber.ports.audio_transcriber_port import (
    AudioTranscriberPort,
)


class FasterWhisperAudioTranscriber(AudioTranscriberPort):
    def transcribe(self, audio_path: str, lang) -> str:
        console.print("Using faster-whisper for transcription...")
        from faster_whisper import WhisperModel

        with console.status("[bold yellow]🦠 Loading Whisper model..."):
            model = WhisperModel("base", compute_type="int8")
        if lang:
            segments_generator, info = model.transcribe(audio_path, language=lang)
        else:
            segments_generator, info = model.transcribe(audio_path)

        # Use rich progress bar to show transcription progress
        with Progress(
            TextColumn("[bold green]🎙️ Transcribing audio"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("transcribe", total=info.duration)
            segments = []
            for segment in segments_generator:
                segments.append(segment.text)
                progress.update(task, completed=segment.end)

        return "\n".join(segments)
