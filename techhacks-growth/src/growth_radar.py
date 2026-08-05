import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("growth.radar")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GrowthRadar:
    """
    Gemini-powered Growth Recommendation Engine.
    Analyzes 4-platform video metrics (YouTube + Instagram + Facebook + TikTok) and generates
    strategic action plans in Italian to maximize video views and trending algorithms.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                self.configured = True
            except Exception as e:
                logger.error(f"Failed to configure Gemini for Growth Radar: {e}")
                self.configured = False
        else:
            self.configured = False

    def generate_growth_plan(
        self,
        yt_data: Dict[str, Any],
        ig_data: Dict[str, Any],
        fb_data: Dict[str, Any],
        tt_data: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Generates actionable growth strategy and daily recommendations in Italian.
        """
        if not self.configured or dry_run or self.api_key in (None, "", "your_gemini_api_key_here"):
            return self._generate_mock_plan(yt_data, ig_data, fb_data, tt_data)

        prompt = f"""
        Sei il Growth Lead & Social Media Strategist per TechHacks AI (@techhacks_aii / @techs_ai1 / @techhacks.ai).
        Analizza le metriche delle 4 piattaforme video:

        YouTube Shorts: {json.dumps(yt_data)}
        Instagram Reels: {json.dumps(ig_data)}
        Facebook Reels: {json.dumps(fb_data)}
        TikTok Videos: {json.dumps(tt_data)}

        Genera un piano d'azione strategico quotidiano IN ITALIANO per far andare i video in tendenza e moltiplicare le visualizzazioni reali.

        Restituisci ESCLUSIVAMENTE un JSON raw:
        {{
            "headline": "Titolo d'impatto della strategia del giorno",
            "recommended_tool_today": "Nome del tool da spingere oggi",
            "optimal_posting_times": ["12:30", "18:30"],
            "content_angle": "Angolo del video consigliato in italiano",
            "growth_actions": [
                "Azione 1 per massimizzare le views su TikTok ed Instagram",
                "Azione 2 per raddoppiare la retention su YouTube Shorts"
            ]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()
            return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini API request fallback for growth plan: {e}")
            return self._generate_mock_plan(yt_data, ig_data, fb_data, tt_data)

    def _generate_mock_plan(self, yt_data: Dict[str, Any], ig_data: Dict[str, Any], fb_data: Dict[str, Any], tt_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "headline": "🚀 STRATEGIA MULTI-PIATTAFORMA: MASSIMIZZAZIONE VISUALIZZAZIONI REALS & SHORTS",
            "recommended_tool_today": "ElevenLabs",
            "optimal_posting_times": ["12:30", "18:30"],
            "content_angle": "Come creare voci ultra-realistiche in italiano per Reels, Shorts e TikTok in 10 secondi.",
            "growth_actions": [
                "🔥 Pubblica contemporaneamente lo stesso video 9:16 su YouTube Shorts, Instagram Reels, Facebook Reels e TikTok.",
                "📈 Usa un Hook ad altissima curiosità nei primi 1.5 secondi per bloccare lo scrolling.",
                "💬 Inserisci nei primi 2 secondi sottotitoli cinetici gialli neon ad alto contrasto per alzare la retention."
            ]
        }


def generate_growth_plan(yt_data: Dict[str, Any], ig_data: Dict[str, Any], fb_data: Dict[str, Any], tt_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    radar = GrowthRadar()
    return radar.generate_growth_plan(yt_data, ig_data, fb_data, tt_data, dry_run=dry_run)
