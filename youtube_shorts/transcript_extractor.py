import re
import logging
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger("youtube_shorts.transcript_extractor")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False


def extract_youtube_id(url_or_id: str) -> Optional[str]:
    """Extracts 11-char YouTube video ID from URL or raw ID string."""
    match = re.search(r'(?:v=|\/shorts\/|youtu\.be\/|^)([a-zA-Z0-9_-]{11})', url_or_id)
    return match.group(1) if match else None


def extract_youtube_content(url_or_id: str) -> Dict[str, Any]:
    """
    Extracts title, description, and full transcript text from a YouTube video URL/ID
    using youtube-transcript-api or yt-dlp.
    """
    video_id = extract_youtube_id(url_or_id)
    full_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url_or_id

    title = "Video Virale YouTube"
    description = ""
    transcript = None

    # 1. Fetch metadata (Title & Description) via yt-dlp
    try:
        cmd = ["./venv/bin/yt-dlp", "--dump-json", "--no-playlist", full_url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            import json
            info = json.loads(res.stdout)
            title = info.get("title", title)
            description = info.get("description", description)
    except Exception as e:
        logger.warning(f"[TranscriptExtractor] yt-dlp metadata extraction exception for {full_url}: {e}")

    # 2. Extract Transcript via youtube-transcript-api
    if video_id and TRANSCRIPT_API_AVAILABLE:
        # Fallback 1: YouTubeTranscriptApi.get_transcript
        try:
            if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                t_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['it', 'en'])
                transcript = " ".join([item['text'] for item in t_data])
                logger.info(f"[TranscriptExtractor] Extracted transcript ({len(transcript)} chars) for ID {video_id}")
        except Exception:
            pass

        # Fallback 2: Instance call
        if not transcript:
            try:
                api_obj = YouTubeTranscriptApi()
                if hasattr(api_obj, 'get_transcript'):
                    t_data = api_obj.get_transcript(video_id, languages=['it', 'en'])
                    transcript = " ".join([item['text'] for item in t_data])
                    logger.info(f"[TranscriptExtractor] Extracted transcript ({len(transcript)} chars) for ID {video_id}")
            except Exception:
                pass

        # Fallback 3: list_transcripts
        if not transcript:
            try:
                if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
                    t_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    t_obj = t_list.find_transcript(['it', 'en'])
                    fetched = t_obj.fetch()
                    transcript = " ".join([item['text'] for item in fetched])
                    logger.info(f"[TranscriptExtractor] Extracted transcript via list_transcripts ({len(transcript)} chars)")
            except Exception:
                pass

    return {
        "video_id": video_id,
        "url": full_url,
        "title": title,
        "description": description,
        "transcript": transcript
    }
