import re
import time
import random
import logging
import urllib.parse
from typing import Dict, Any, Optional, List
from youtube_shorts.config import NICHES

logger = logging.getLogger("youtube_shorts.viral_scraper")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# 🚀 QUERY VIRALI MAPPATE ESCLUSIVAMENTE AD ARGOMENTI DI CONTENUTO REALE (0 MARKETING / 0 VIRAL TIPS)
NICHE_QUERIES_MAP = {
    "tech_oscura": [
        "siti segreti utili shorts",
        "siti web quasi illegali tech",
        "trucchi pc da conoscere shorts",
        "funzioni nascoste smartphone",
        "secret websites you should know",
        "dark tech hacks shorts",
        "hidden ai tools you need to try",
        "secret app features shorts"
    ],
    "storie_oscure": [
        "storie incredibili vere shorts",
        "hacker piu famoso del mondo storia",
        "truffe geniali della storia",
        "mistero irrisolto storia vera",
        "dark history facts shorts",
        "crazy true crime stories shorts",
        "unbelievable history shorts",
        "cyber security heist documentary"
    ],
    "misteri": [
        "cosa succede se scienza shorts",
        "fatti assurdi che non sai",
        "curiosita scioccanti universo",
        "misteri dello spazio shorts",
        "disturbing science facts shorts",
        "mind blowing facts you didnt know",
        "what if scenario shorts",
        "scariest space facts"
    ]
}

# STRICT MUSIC & MARKETING EXCLUSION FILTER
EXCLUDED_KEYWORDS = [
    # Termini Musicali (IT / EN)
    "music", "song", "official video", "official audio", "vevo", "lyric", "lyrics",
    "cantante", "brano", "remix", "videoclip", "prod.", "feat", "ft.", "ft ", "album",
    "singolo", "cover", "soundtrack", "ost", "dj", "live performance", "concert",
    "concerto", "karaoke", "instrumental", "radio", "dance", "trap", "rap", "hip hop",
    
    # Termini Marketing / Meta-Viral / Soliti Siti
    "come fare video virali", "diventare virale", "algoritmo youtube", "growth hacks",
    "make money online", "guadagnare online", "views hack", "subscribers hack"
]


class ViralScraper:
    """
    Playwright-Powered Autonomous YouTube Trend Discovery Engine.
    Filters out music clips and marketing meta-content to select ONLY real stories, tech & mysteries!
    """

    def extract_youtube_id(self, url_or_id: str) -> Optional[str]:
        """Extracts 11-char YouTube video ID from URL or raw ID string."""
        match = re.search(r'(?:v=|\/shorts\/|youtu\.be\/|^)([a-zA-Z0-9_-]{11})', url_or_id)
        return match.group(1) if match else None

    def is_excluded_content(self, title: str) -> bool:
        """Checks if a video title contains music or marketing keywords."""
        t_lower = title.lower()
        return any(kw in t_lower for kw in EXCLUDED_KEYWORDS)

    def get_top_global_viral_video(self) -> Dict[str, Any]:
        """
        Scans YouTube Shorts live.
        Picks a RANDOM niche and a RANDOM query from that niche to guarantee 100% consistency!
        """
        chosen_niche = random.choice(["tech_oscura", "storie_oscure", "misteri"])
        niche_queries = NICHE_QUERIES_MAP[chosen_niche]
        chosen_query = random.choice(niche_queries)

        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(chosen_query)}&sp=CAM%253D"
        logger.info(f"[ViralScraper - Playwright] Live trend search for query: '{chosen_query}' (Nicchia: '{chosen_niche}')...")

        found_videos = []

        if PLAYWRIGHT_AVAILABLE:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    )
                    page = context.new_page()
                    page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                    
                    scroll_depth = random.randint(2, 4)
                    for _ in range(scroll_depth):
                        page.evaluate(f"window.scrollBy(0, {random.randint(600, 1000)})")
                        time.sleep(0.8)

                    links = page.query_selector_all("a#video-title, a[href*='/shorts/']")
                    for link in links:
                        href = link.get_attribute("href")
                        title = link.get_attribute("title") or link.text_content().strip()
                        if href and title:
                            if not self.is_excluded_content(title):
                                v_id = self.extract_youtube_id(href)
                                if v_id and not any(v["video_id"] == v_id for v in found_videos):
                                    found_videos.append({
                                        "video_id": v_id,
                                        "title": title,
                                        "url": f"https://www.youtube.com/watch?v={v_id}"
                                    })

                    browser.close()
            except Exception as e:
                logger.warning(f"[ViralScraper - Playwright] Trend search exception for query '{chosen_query}': {e}")

        if found_videos:
            selected_video = random.choice(found_videos[:min(len(found_videos), 6)])
            logger.info(f"[ViralScraper - Playwright] 🏆 CONSISTENT VIRAL SHORT DISCOVERED: '{selected_video['title']}' (Nicchia: '{chosen_niche}') -> {selected_video['url']}")
            return {
                "niche_key": chosen_niche,
                "url": selected_video["url"],
                "title": selected_video["title"]
            }

        return self._http_global_fallback(chosen_niche, chosen_query)

    def _http_global_fallback(self, niche_key: str, query: str) -> Dict[str, Any]:
        """HTTP fallback discovery bound 100% to the selected niche & query."""
        if REQUESTS_AVAILABLE:
            try:
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}&sp=CAM%253D"
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                res = requests.get(search_url, headers=headers, timeout=12)
                if res.status_code == 200:
                    matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', res.text)
                    titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', res.text)
                    valid_options = []
                    for idx, v_id in enumerate(matches):
                        title = titles[idx] if idx < len(titles) else f"Trend Virale {niche_key.replace('_', ' ').capitalize()}"
                        if not self.is_excluded_content(title):
                            valid_options.append((v_id, title))
                    
                    if valid_options:
                        chosen_v_id, chosen_title = random.choice(valid_options[:min(len(valid_options), 5)])
                        return {
                            "niche_key": niche_key,
                            "url": f"https://www.youtube.com/watch?v={chosen_v_id}",
                            "title": chosen_title
                        }
            except Exception as e:
                logger.warning(f"[ViralScraper] HTTP fallback exception: {e}")

        # Real Story / Tech / Science Fallbacks ONLY (0 marketing or viral tips!)
        fallback_pool = {
            "tech_oscura": [
                ("3 Siti Web Segreti Quasi Illegali", "https://www.youtube.com/watch?v=ic4S3-EKOZ0"),
                ("Il Trucco Segreto del Tuo Smartphone", "https://www.youtube.com/watch?v=s9xk77X4m5c")
            ],
            "storie_oscure": [
                ("La Storia Oscura dell'Hacker da 500 Milioni", "https://www.youtube.com/watch?v=jUJmGQS9f10"),
                ("La Truffa Infinita del Falso Milionario", "https://www.youtube.com/watch?v=Hgg7M3kSqyE")
            ],
            "misteri": [
                ("Cosa Succede Se Ti Tuffi in un Buco Nero?", "https://www.youtube.com/watch?v=HxA-OPg7mdo"),
                ("I 3 Fatti Più Disturbanti Sullo Spazio Profondo", "https://www.youtube.com/watch?v=t5JmSkhXy3s")
            ]
        }

        niche_fallbacks = fallback_pool.get(niche_key, fallback_pool["tech_oscura"])
        chosen_title, chosen_url = random.choice(niche_fallbacks)

        return {
            "niche_key": niche_key,
            "url": chosen_url,
            "title": chosen_title
        }

    def get_trending_video_url(self, niche_key: str = "tech_oscura") -> str:
        """Uses Playwright to navigate YouTube live filtering out music & marketing clips."""
        top_info = self.get_top_global_viral_video()
        return top_info["url"]

    def get_viral_topic_data(self, niche_key: Optional[str] = None, custom_input: Optional[str] = None, auto_viral: bool = False) -> Dict[str, Any]:
        """AUTONOMOUS TREND SCRAPER with Dynamic YouTube Trend Discovery."""
        from youtube_shorts.transcript_extractor import extract_youtube_content

        if auto_viral or not niche_key or niche_key == "auto":
            top_info = self.get_top_global_viral_video()
            detected_niche = top_info["niche_key"]
            top_url = top_info["url"]

            niche_info = NICHES.get(detected_niche, NICHES["tech_oscura"])
            yt_content = extract_youtube_content(top_url)

            return {
                "niche_key": detected_niche,
                "niche": niche_info["name"],
                "source": "global_auto_viral_playwright",
                "raw_topic": yt_content.get("title", top_info.get("title", f"Global Top Viral Short ({top_url})")),
                "transcript": yt_content.get("transcript"),
                "description": yt_content.get("description"),
                "url": top_url
            }

        niche_info = NICHES.get(niche_key, NICHES["tech_oscura"])

        if custom_input and ("youtube.com" in custom_input or "youtu.be" in custom_input or len(custom_input) == 11):
            yt_content = extract_youtube_content(custom_input)
            return {
                "niche_key": niche_key,
                "niche": niche_info["name"],
                "source": "user_youtube_url",
                "raw_topic": yt_content.get("title", f"Custom Short ({custom_input})"),
                "transcript": yt_content.get("transcript"),
                "description": yt_content.get("description"),
                "url": yt_content.get("url")
            }

        if custom_input:
            return {
                "niche_key": niche_key,
                "niche": niche_info["name"],
                "source": "custom_user_topic",
                "raw_topic": custom_input,
                "transcript": None,
                "url": None
            }

        top_url = self.get_trending_video_url(niche_key)
        yt_content = extract_youtube_content(top_url)
        return {
            "niche_key": niche_key,
            "niche": niche_info["name"],
            "source": "niche_auto_viral",
            "raw_topic": yt_content.get("title", f"Trending Short ({top_url})"),
            "transcript": yt_content.get("transcript"),
            "description": yt_content.get("description"),
            "url": top_url
        }


def get_trending_video_url(niche_key: str = "tech_oscura") -> str:
    scraper = ViralScraper()
    return scraper.get_trending_video_url(niche_key=niche_key)


def get_viral_topic_data(niche_key: Optional[str] = None, custom_input: Optional[str] = None, auto_viral: bool = False) -> Dict[str, Any]:
    scraper = ViralScraper()
    return scraper.get_viral_topic_data(niche_key=niche_key, custom_input=custom_input, auto_viral=auto_viral)
