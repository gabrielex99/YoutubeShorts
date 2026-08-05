import os
import logging
from typing import Dict, Any, Optional
from youtube_shorts.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("youtube_shorts.telegram_publisher")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TelegramPublisher:
    """
    Telegram Bot integration module delivering finished 9:16 MP4 Faceless Shorts video attachments
    alongside AI-Recommended Posting Schedules and Ready-to-Copy Multi-Platform Captions.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.is_configured = bool(
            self.bot_token and 
            self.chat_id and 
            self.bot_token != "your_telegram_bot_token_here"
        )

    def create_publishing_kit_caption(self, script_data: Dict[str, Any]) -> str:
        """Formats clean Italian Publishing Kit text payload with AI posting schedules."""
        niche = script_data.get("niche", "Tech Oscura")
        title = script_data.get("title", "Viral Short")
        caption = script_data.get("caption", "#Shorts #Reels #AI #Viral")

        sched = script_data.get("publishing_schedule", {})
        yt_time = sched.get("youtube_time", "14:30")
        yt_reason = sched.get("youtube_reason", "Picco di traffico pomeridiano post-pausa pranzo")

        ig_time = sched.get("instagram_time", "18:45")
        ig_reason = sched.get("instagram_reason", "Massima interazione serale pre-cena su Reels")

        tt_time = sched.get("tiktok_time", "21:15")
        tt_reason = sched.get("tiktok_reason", "Orario virale FYP per lo scorrimento serale")

        payload = (
            f"🎬 <b>[NUOVO FACELESS SHORT PRONTO - {niche.upper()}]</b>\n\n"
            f"📌 <b>TITOLO CONSIGLIATO:</b>\n"
            f"<i>\"{title}\"</i>\n\n"
            f"⏰ <b>ORARI DI PUBBLICAZIONE CONSIGLIATI DALL'IA:</b>\n"
            f"📺 <b>YouTube Shorts:</b> Ore <b>{yt_time}</b> ({yt_reason})\n"
            f"📸 <b>Instagram Reels:</b> Ore <b>{ig_time}</b> ({ig_reason})\n"
            f"🎵 <b>TikTok:</b> Ore <b>{tt_time}</b> ({tt_reason})\n\n"
            f"📋 <b>MESSAGGIO E HASHTAG PRONTI DA COPIARE:</b>\n"
            f"<code>{caption}</code>\n\n"
            f"🚀 <b>ISTRUZIONI PUBBLICAZIONE:</b>\n"
            f"1. Tocca il testo sopra per copiarlo al volo.\n"
            f"2. Scarica il video allegato in 1080x1920 HD.\n"
            f"3. Pubblica sugli orari indicati dall'IA per massimizzare la viralità!"
        )
        return payload

    def send_video_to_telegram(
        self,
        video_path: str,
        script_data: Dict[str, Any],
        dry_run: bool = False,
        force_send: bool = False
    ) -> Dict[str, Any]:
        """Dispatches MP4 video file and Publishing Kit text to Telegram."""
        if not os.path.exists(video_path):
            error_msg = f"Video file not found at: {video_path}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

        caption_text = self.create_publishing_kit_caption(script_data)

        if (dry_run and not force_send) or not self.is_configured:
            logger.info("[TelegramPublisher] Telegram API unconfigured or dry-run active. Simulating report dispatch.")
            print("\n" + "=" * 65)
            print("📱 [TELEGRAM FACELESS SHORT DISPATCH SIMULATION]")
            print(f"To Chat ID: {self.chat_id}")
            print(f"Attachment: {os.path.basename(video_path)}")
            print("-" * 65)
            print(caption_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<code>", "").replace("</code>", ""))
            print("=" * 65 + "\n")
            return {"status": "simulated", "video_path": video_path}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendVideo"
        logger.info(f"[TelegramPublisher] Dispatching MP4 Short to Telegram Chat ID: {self.chat_id}...")

        try:
            with open(video_path, "rb") as video_file:
                files = {"video": (os.path.basename(video_path), video_file, "video/mp4")}
                data = {
                    "chat_id": self.chat_id,
                    "caption": caption_text[:1024],
                    "parse_mode": "HTML",
                    "supports_streaming": True
                }

                res = requests.post(url, data=data, files=files, timeout=120)
                if res.status_code == 200:
                    logger.info(f"[TelegramPublisher] Successfully delivered Faceless Short to Telegram Chat ID: {self.chat_id}!")
                    return {"status": "success", "response": res.json()}
                else:
                    logger.error(f"[TelegramPublisher] Telegram API error {res.status_code}: {res.text}")
                    # Send text message fallback
                    self._send_text_fallback(caption_text)
                    return {"status": "failed", "error": res.text}
        except Exception as e:
            logger.error(f"[TelegramPublisher] Exception sending video to Telegram: {e}")
            self._send_text_fallback(caption_text)
            return {"status": "error", "message": str(e)}

    def _send_text_fallback(self, caption_text: str):
        """Sends text payload if video file dispatch encounters network limits."""
        try:
            msg_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": caption_text,
                "parse_mode": "HTML"
            }
            requests.post(msg_url, json=payload, timeout=20)
        except Exception:
            pass


def send_video_to_telegram(video_path: str, script_data: Dict[str, Any], dry_run: bool = False, force_send: bool = False) -> Dict[str, Any]:
    publisher = TelegramPublisher()
    return publisher.send_video_to_telegram(video_path, script_data, dry_run=dry_run, force_send=force_send)
