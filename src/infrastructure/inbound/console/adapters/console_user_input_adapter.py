import argparse
from infrastructure.inbound.console.ports.user_input_port import UserInputPort

class ConsoleUserInputAdapter(UserInputPort):
    def get_user_input(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Transcribe YouTube, TikTok or Instagram video using Whisper.")
        parser.add_argument("url", help="Video URL")
        parser.add_argument("-tm", "--transcript-model", choices=["faster-whisper", "openai-whisper"],
                            default="faster-whisper", help="Choose transcription model (default: faster-whisper)")
        parser.add_argument("-l", "--lang", default="en", help="Language code (default: en)")
        parser.add_argument("-llm", "--llm-model", default="openai/gpt-oss-20b", help="LLM model to use for organizing transcription (default: gemma3)")
        parser.add_argument(
            "-e", "--enrich-text", action="store_true",
            help="Enrich the summary by searching for additional information on the internet (experimental)"
        )
        return parser.parse_args()
