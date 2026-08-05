"""
ai_image_fetcher.py  ·  Image & Subject Keyword Extractor Module
===================================================================
Alias module pointing to ai_video_fetcher for subject keyword extraction
and image fetching.
"""

from youtube_shorts.ai_video_fetcher import (
    _keywords,
    _fetch_cinematic_image,
    _scene_to_broad_category
)

def extract_subject_keywords(prompt: str, n: int = 3) -> str:
    """Extract top n fundamental subject keywords from prompt."""
    return _keywords(prompt, n=n)

def fetch_ai_image_for_prompt(prompt: str, seed: int = 0):
    """Fetch cinematic image for prompt."""
    return _fetch_cinematic_image(prompt, seed=seed)
