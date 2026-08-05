import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("growth.reporter")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class GrowthReporter:
    """
    Telegram Growth Reporter module.
    Formats and dispatches the 4-Platform Video Analytics Report (YouTube, Instagram, Facebook, TikTok) to Telegram.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "870620791")
        self.is_configured = bool(
            self.bot_token and 
            self.chat_id and 
            self.bot_token != "your_telegram_bot_token_here"
        )

    def create_report_payload(
        self,
        yt_data: Dict[str, Any],
        ig_data: Dict[str, Any],
        fb_data: Dict[str, Any],
        tt_data: Dict[str, Any],
        growth_plan: Dict[str, Any]
    ) -> str:
        """
        Formats a clean, 4-Platform Video Views Telegram report.
        """
        total_aggregate_views = (
            yt_data.get('total_views', 0) +
            ig_data.get('estimated_weekly_reach', 0) +
            fb_data.get('total_views', 0) +
            tt_data.get('total_views', 0)
        )

        yt_api_status = "🟢 LIVE API/RSS" if (yt_data.get('is_live_api') or yt_data.get('is_live_rss')) else "🟡 CONFIGURA KEY"
        ig_api_status = "🟢 LIVE API" if ig_data.get('is_live_api') else "🟡 CONFIGURA TOKEN"
        fb_api_status = "🟢 LIVE API" if fb_data.get('is_live_api') else "🟡 CONFIGURA TOKEN"
        tt_api_status = "🟢 LIVE API" if tt_data.get('is_live_api') else "🟡 CONFIGURA TOKEN"

        recent_shorts = yt_data.get('recent_published_shorts', [])
        latest_yt_title = recent_shorts[0]['title'] if recent_shorts else "N/A"

        report = (
            f"📈 <b>[REPORT GIORNALIERO VISUALIZZAZIONI MULTI-PIATTAFORMA]</b>\n\n"
            f"🔥 <b>VISUALIZZAZIONI TOTALI AGGREGATE: {total_aggregate_views:,}</b>\n\n"

            f"🔴 <b>YOUTUBE SHORTS (@techhacks_aii):</b> {yt_api_status}\n"
            f"• Visualizzazioni Totali: <b>{yt_data.get('total_views', 0):,}</b>\n"
            f"• Iscritti: <b>{yt_data.get('subscribers', 0)}</b>\n"
            f"• Video Pubblicati: <b>{yt_data.get('videos_count', 0)}</b>\n"
            f"• Ultimo Short: <i>\"{latest_yt_title}\"</i>\n\n"

            f"📸 <b>INSTAGRAM REELS (@techs_ai1):</b> {ig_api_status}\n"
            f"• Copertura/Views Reels: <b>{ig_data.get('estimated_weekly_reach', 0):,}</b>\n"
            f"• Follower: <b>{ig_data.get('followers', 0)}</b>\n"
            f"• Post Pubblicati: <b>{ig_data.get('posts_count', 0)}</b>\n\n"

            f"🔵 <b>FACEBOOK REELS (TechHacks AI):</b> {fb_api_status}\n"
            f"• Visualizzazioni Reels Totali: <b>{fb_data.get('total_views', 0):,}</b>\n"
            f"• Follower Pagina: <b>{fb_data.get('followers', 0)}</b>\n\n"

            f"🎵 <b>TIKTOK SHORTS (@techhacks.ai):</b> {tt_api_status}\n"
            f"• Visualizzazioni Video Totali: <b>{tt_data.get('total_views', 0):,}</b>\n"
            f"• Follower: <b>{tt_data.get('followers', 0)}</b>\n"
            f"• Mi Piace Totali: <b>{tt_data.get('likes', 0)}</b>\n\n"

            f"🎯 <b>STRATEGIA PER ANDARE IN TENDENZA:</b>\n"
            f"<b>{growth_plan.get('headline', '')}</b>\n\n"
            f"• <b>Tool consigliato:</b> {growth_plan.get('recommended_tool_today', 'ElevenLabs')}\n"
            f"• <b>Orari di picco Italia:</b> {', '.join(growth_plan.get('optimal_posting_times', ['12:30', '18:30']))}\n\n"
            f"💡 <b>AZIONI VIRALI CONSIGLIATE:</b>\n"
        )

        for act in growth_plan.get("growth_actions", []):
            report += f"• {act}\n"

        return report

    def send_report(
        self,
        yt_data: Dict[str, Any],
        ig_data: Dict[str, Any],
        fb_data: Dict[str, Any],
        tt_data: Dict[str, Any],
        growth_plan: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Dispatches 4-platform daily report to Telegram or simulates output in dry-run mode.
        """
        payload_text = self.create_report_payload(yt_data, ig_data, fb_data, tt_data, growth_plan)

        if dry_run or not self.is_configured:
            logger.info("[GrowthReporter] Dry-run active or Telegram credentials missing. Simulating report dispatch.")
            print("\n" + "=" * 65)
            print("📱 [TELEGRAM 4-PLATFORM GROWTH REPORT SIMULATION]")
            print(f"To Chat ID: {self.chat_id}")
            print("-" * 65)
            print(payload_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
            print("=" * 65 + "\n")
            return {"status": "simulated", "report": payload_text}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": payload_text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            res = requests.post(url, data=data, timeout=30)
            if res.status_code == 200:
                logger.info(f"[GrowthReporter] 4-Platform analytics report sent to Telegram Chat ID: {self.chat_id}")
                return {"status": "success", "response": res.json()}
            else:
                logger.error(f"[GrowthReporter] Failed to send Telegram report ({res.status_code}): {res.text}")
                return {"status": "failed", "error": res.text}
        except Exception as e:
            logger.error(f"[GrowthReporter] Exception sending Telegram report: {e}")
            return {"status": "error", "message": str(e)}


def send_growth_report(
    yt_data: Dict[str, Any],
    ig_data: Dict[str, Any],
    fb_data: Dict[str, Any],
    tt_data: Dict[str, Any],
    growth_plan: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    reporter = GrowthReporter()
    return reporter.send_report(yt_data, ig_data, fb_data, tt_data, growth_plan, dry_run=dry_run)
