import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("growth.facebook_tracker")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class FacebookTracker:
    """
    Real-time Facebook Reels & Page Analytics Tracker.
    Integrates Meta Graph API for Facebook Page/Reels view counts and follower stats.
    """

    PAGE_URL = "https://www.facebook.com/techhacks.ai"
    PAGE_NAME = "TechHacks AI"

    def __init__(self):
        self.page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.has_api_key = bool(
            self.page_access_token and 
            self.page_id and 
            self.page_access_token != "your_facebook_page_access_token_here"
        )

    def fetch_metrics(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Retrieves real live video view metrics via Meta Facebook Graph API.
        """
        logger.info(f"[FacebookTracker] Syncing Facebook Reels analytics for {self.PAGE_NAME}...")

        total_views = 0
        followers = 0
        reels_count = 0
        is_api_live = False

        if self.has_api_key and REQUESTS_AVAILABLE and not dry_run:
            try:
                # Query Meta Graph API for Facebook Page video views
                url = f"https://graph.facebook.com/v19.0/{self.page_id}"
                params = {
                    "fields": "followers_count,fan_count,video_views,videos{{views,title}}",
                    "access_token": self.page_access_token
                }
                res = requests.get(url, params=params, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    followers = int(data.get("followers_count", data.get("fan_count", 0)))
                    videos = data.get("videos", {}).get("data", [])
                    reels_count = len(videos)
                    total_views = sum(int(v.get("views", 0)) for v in videos)
                    is_api_live = True
                    logger.info(f"[FacebookTracker] Meta Graph API LIVE: {total_views} views | {followers} followers")
                else:
                    logger.error(f"[FacebookTracker] Facebook Graph API error {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"[FacebookTracker] Exception fetching Facebook Graph API: {e}")

        if not is_api_live:
            total_views = int(os.getenv("FACEBOOK_TOTAL_VIEWS", "0"))
            followers = int(os.getenv("FACEBOOK_FOLLOWERS", "0"))
            reels_count = int(os.getenv("FACEBOOK_REELS_COUNT", "0"))

        return {
            "platform": "Facebook",
            "page_name": self.PAGE_NAME,
            "url": self.PAGE_URL,
            "is_live_api": is_api_live,
            "api_configured": self.has_api_key,
            "total_views": total_views,
            "followers": followers,
            "reels_count": reels_count
        }


def fetch_facebook_metrics(dry_run: bool = False) -> Dict[str, Any]:
    tracker = FacebookTracker()
    return tracker.fetch_metrics(dry_run=dry_run)
