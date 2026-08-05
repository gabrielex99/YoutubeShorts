import os
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("growth.youtube_tracker")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class YouTubeTracker:
    """
    Real-time YouTube Analytics Tracker for @techhacks_aii (Channel ID: UCAd_VYwyU2TP_SOn33SzXHw).
    Integrates YouTube Data API v3 for live subscriber count, view count, and video stats,
    with live RSS feed fallback for recent Shorts tracking.
    """

    CHANNEL_URL = "https://www.youtube.com/@techhacks_aii"
    CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCAd_VYwyU2TP_SOn33SzXHw")
    RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    API_URL = "https://www.googleapis.com/youtube/v3/channels"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.has_api_key = bool(self.api_key and self.api_key != "your_youtube_api_key_here")

    def fetch_metrics(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Fetches REAL live metrics from YouTube Data API v3 and RSS feed.
        """
        logger.info(f"[YouTubeTracker] Fetching LIVE metrics for {self.CHANNEL_URL}...")

        subscribers = 0
        total_views = 0
        video_count = 0
        is_api_live = False

        # 1. Query YouTube Data API v3 if API key is present
        if self.has_api_key and REQUESTS_AVAILABLE and not dry_run:
            try:
                params = {
                    "part": "statistics,snippet",
                    "id": self.CHANNEL_ID,
                    "key": self.api_key
                }
                res = requests.get(self.API_URL, params=params, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    items = data.get("items", [])
                    if items:
                        stats = items[0].get("statistics", {})
                        subscribers = int(stats.get("subscriberCount", 0))
                        total_views = int(stats.get("viewCount", 0))
                        video_count = int(stats.get("videoCount", 0))
                        is_api_live = True
                        logger.info(f"[YouTubeTracker] YouTube Data API v3 LIVE: {subscribers} subs | {total_views} views | {video_count} videos")
                else:
                    logger.error(f"[YouTubeTracker] YouTube API error {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"[YouTubeTracker] YouTube Data API request exception: {e}")

        # 2. Fetch Live Published Shorts from RSS Feed
        live_videos = []
        if REQUESTS_AVAILABLE and not dry_run:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "it-IT,it;q=0.9"
                }
                res_rss = requests.get(self.RSS_URL, headers=headers, timeout=15)
                if res_rss.status_code == 200:
                    root = ET.fromstring(res_rss.text)
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                        published = entry.find('{http://www.w3.org/2005/Atom}published').text
                        live_videos.append({
                            "title": title,
                            "url": link,
                            "published_at": published[:10]
                        })
                    if not is_api_live and len(live_videos) > 0:
                        video_count = len(live_videos)
            except Exception as e:
                logger.error(f"[YouTubeTracker] RSS feed parse exception: {e}")

        return {
            "channel": "@techhacks_aii",
            "channel_id": self.CHANNEL_ID,
            "url": self.CHANNEL_URL,
            "is_live_api": is_api_live,
            "api_configured": self.has_api_key,
            "subscribers": subscribers if is_api_live else int(os.getenv("YOUTUBE_SUBSCRIBERS", "0")),
            "total_views": total_views if is_api_live else int(os.getenv("YOUTUBE_TOTAL_VIEWS", "0")),
            "videos_count": video_count if video_count > 0 else len(live_videos),
            "recent_published_shorts": live_videos
        }


def fetch_youtube_metrics(dry_run: bool = False) -> Dict[str, Any]:
    tracker = YouTubeTracker()
    return tracker.fetch_metrics(dry_run=dry_run)
