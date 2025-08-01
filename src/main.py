from infrastructure.inbound.console.adapters.console_user_input_adapter import ConsoleUserInputAdapter
from infrastructure.inbound.console.ports.user_input_port import UserInputPort
from application.transcription.services.transcription_service import transcribe
from application.transcription.services.video_downloader_service import get_video_info
from application.transcription.services.llm_markdown_service import transcription_to_markdown
from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage
from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort


# === Main ===
def main():
    # Dependencies
    user_input: UserInputPort = ConsoleUserInputAdapter()
    args = user_input.get_user_input()

    video_info = get_video_info(args.url)

    transcription = transcribe(
        url=args.url,
        video_name=video_info.get('title'),
        audo_transcriber_model=args.transcript_model,    
        lang=args.lang
    )

    transcription_to_markdown(
        transcription,
        model=args.llm_model,
        video_info=video_info,
        lang=args.lang,
        enrich_text=args.enrich_text
    )

if __name__ == "__main__":
    main()
