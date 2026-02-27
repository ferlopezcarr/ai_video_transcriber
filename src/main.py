from dotenv import load_dotenv
import re

from infrastructure.inbound.console.adapters.console_user_input_adapter import ConsoleUserInputAdapter
from infrastructure.inbound.console.ports.user_input_port import UserInputPort
from application.transcription.services.transcription_service import transcribe
from application.transcription.services.video_downloader_service import get_video_info
from application.transcription.services.llm_markdown_service import transcription_to_markdown
from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage
from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort

load_dotenv()

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL as fallback."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&?/\s]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return "video"

# === Main ===
def main():
    # Dependencies
    user_input: UserInputPort = ConsoleUserInputAdapter()
    args = user_input.get_user_input()

    # Get video metadata (lightweight operation, just fetches info)
    print("\n📹 Fetching video information...")
    try:
        video_info = get_video_info(args.url)
        video_title = video_info.get('title')
    except Exception as e:
        print(f"\n⚠️  Could not fetch video info: {str(e)[:100]}...")
        print("   This may be due to YouTube bot detection.")
        print("   Continuing with fallback video ID...\n")
        video_id = extract_video_id(args.url)
        video_title = f"video_{video_id}"
        video_info = {
            'title': video_title,
            'duration': 0,
            'webpage_url': args.url,
        }
    
    # Check if this video has already been processed
    file_storage: FileStoragePort = LocalFileStorage()
    transcription_path = f"transcriptions/{video_title}.txt"
    summary_path = f"summaries/{video_title}.md"
    
    transcription_exists = file_storage.exists(transcription_path)
    summary_exists = file_storage.exists(summary_path)
    
    if transcription_exists and summary_exists:
        print(f"\n✅ Video already fully processed!")
        print(f"   📄 Transcription: {transcription_path}")
        print(f"   📝 Summary: {summary_path}")
        print(f"\n💡 Tip: Delete these files if you want to reprocess the video.")
        return
    
    if transcription_exists:
        print(f"\n📄 Found existing transcription, skipping video download...")
    
    if summary_exists:
        print(f"\n📝 Found existing summary, will skip LLM processing...")

    transcription = transcribe(
        url=args.url,
        video_name=video_title,
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
