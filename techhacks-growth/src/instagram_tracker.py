import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("growth.instagram_tracker")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class InstagramTracker:
    """
    Real-time Instagram Reels analytics tracker for @techs_ai1.
    Integrates Meta Instagram Graph API for live follower count, media count, and engagement stats.
    """

    PROFILE_URL = "https://www.instagram.com/techs_ai1/"
    PROFILE_HANDLE = "@techs_ai1"

    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.has_api_key = bool(
            self.access_token and 
            self.account_id and 
            self.access_token != "your_instagram_access_token_here"
        )

    def fetch_metrics(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Retrieves real live profile metrics via Instagram Graph API.
        """
        logger.info(f"[InstagramTracker] Syncing live profile analytics for {self.PROFILE_HANDLE}...")

        followers = 0
        posts_count = 0
        is_api_live = False

        if self.has_api_key and REQUESTS_AVAILABLE and not dry_run:
            try:
                url = f"https://graph.facebook.com/v19.0/{self.account_id}"
                params = {
                    "fields": "followers_count,media_count,name,username",
                    "access_token": self.access_token
                }
                res = requests.get(url, params=params, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    followers = int(data.get("followers_count", 0))
                    posts_count = int(data.get("media_count", 0))
                    is_api_live = True
                    logger.info(f"[InstagramTracker] Meta Graph API LIVE: {followers} followers | {posts_count} posts")
                else:
                    logger.error(f"[InstagramTracker] Instagram Graph API error {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"[InstagramTracker] Exception fetching Instagram Graph API: {e}")

        # Fallback to .env values if API key is not configured
        if not is_api_live:
            followers = int(os.getenv("INSTAGRAM_FOLLOWERS", "0"))
            posts_count = int(os.getenv("INSTAGRAM_POSTS_COUNT", "0"))

        return {
            "profile": self.PROFILE_HANDLE,
            "url": self.PROFILE_URL,
            "is_live_api": is_api_live,
            "api_configured": self.has_api_key,
            "followers": followers,
            "posts_count": posts_count,
            "estimated_weekly_reach": followers * 12 if followers > 0 else 0
        }


def fetch_instagram_metrics(dry_run: bool = False) -> Dict[str, Any]:
    tracker = InstagramTracker()
    return tracker.fetch_metrics(dry_run=dry_run)
