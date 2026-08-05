#!/usr/bin/env python3
"""
youtube_shorts: CapCut-Style High-Retention Faceless Video Automation Suite with Autonomous Playwright Trend-Jacking
Features:
- Global Autonomous Trend-Jacking Engine across ALL niches (--auto-viral).
- Transcript Extractor for YouTube URLs (--topic "https://www.youtube.com/watch?v=...").
- Gemini 1.5 Pro Retention Script Rewriter (65-75 words, complete payoff, contextual scenes).
- High-Retention Gameplay Fallback Mode (GTA V Ramps / Minecraft Parkour / Cyber Loop 60fps).
- Audio Duration Strictly Controls Video Duration (Zero sentence truncation!).
- 100% Free Neural Italian Speech Synthesis (+15% rate boost) + Mixed Dark Suspense Background Music (15% vol).
- Telegram Bot Dispatcher with AI-Recommended Multi-Platform Publishing Schedules.
"""

import os
import sys
import time
import argparse
import logging
from typing import Dict, Any

# Ensure project root is in python path for clean package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("youtube_shorts.main")

# Import Modules
from youtube_shorts.config import NICHES, OUTPUTS_DIR, TTS_VOICE
from youtube_shorts.viral_scraper import get_viral_topic_data
from youtube_shorts.generator import generate_retention_script
from youtube_shorts.tts_engine import generate_speech
from youtube_shorts.media_fetcher import download_media_clips
from youtube_shorts.video_builder import build_youtube_short
from youtube_shorts.telegram_publisher import send_video_to_telegram


def run_pipeline(
    niche_key: str = None,
    topic_input: str = None,
    auto_viral: bool = False,
    dry_run: bool = False,
    send_telegram: bool = True
) -> Dict[str, Any]:
    """
    Executes the full CapCut-Style faceless shorts automation pipeline.
    """
    start_time = time.time()

    logger.info("=" * 65)
    logger.info("⚡ CAPCUT-STYLE AUTONOMOUS SHORTS PIPELINE")
    logger.info("=" * 65)

    # STEP 1: Viral Topic / Playwright Global Trend-Jacking / Transcript Extraction
    logger.info("\n[STEP 1/6] Estrazione Argomento / Playwright Global Trend-Jacking Virale...")
    topic_data = get_viral_topic_data(niche_key=niche_key, custom_input=topic_input, auto_viral=auto_viral)
    
    resolved_niche_key = topic_data.get("niche_key", niche_key or "tech_oscura")
    niche_data = NICHES.get(resolved_niche_key, NICHES["tech_oscura"])

    logger.info(f"Nicchia Riconosciuta: '{niche_data['name']}' (Durata Target: {niche_data['target_duration']})")
    logger.info(f"Argomento / Trend Selezionato: '{topic_data['raw_topic']}' (Fonte: {topic_data.get('source')})")
    if topic_data.get("url"):
        logger.info(f"URL YouTube Virale #1: {topic_data['url']}")

    # STEP 2: Gemini Retention JSON Script (Strict 65-75 words, Complete Payoff, Contextual Scenes)
    logger.info("\n[STEP 2/6] Generazione Script JSON ad Altissima Retention (65-75 parole compiute & scene)...")
    script_data = generate_retention_script(topic_data, niche_key=resolved_niche_key, dry_run=dry_run)
    logger.info(f"Titolo Virale Generato: \"{script_data.get('title')}\"")
    logger.info(f"Script Text ({len(script_data.get('script_text', '').split())} parole): \"{script_data.get('script_text')[:90]}...\"")

    # STEP 3: Edge-TTS Neural Speech Synthesis (it-IT-DiegoNeural - 100% Free + 15% Rate Boost)
    logger.info(f"\n[STEP 3/6] Sintesi Vocale Neurale Italiana (+15% rate boost: {TTS_VOICE})...")
    audio_output_path = os.path.join(os.path.dirname(__file__), "assets", "audio", "speech_narration.mp3")
    audio_data = generate_speech(script_data["script_text"], output_path=audio_output_path, voice=TTS_VOICE)
    logger.info(f"Audio Voce sintetizzato: {audio_data['audio_path']} (Durata: {audio_data['duration']:.2f}s)")

    # STEP 4: Contextual Scene B-Roll Downloads / User Clips / High-Retention Gameplay Fallback
    logger.info("\n[STEP 4/6] Recupero Clip Video Contestuali / User Clips / Gameplay Fallback...")
    clip_paths = download_media_clips(queries=[], script_data=script_data)
    logger.info(f"Acquisite {len(clip_paths)} clip video verticali per il montaggio dinamico.")

    # STEP 5: MoviePy CapCut-Style 1080x1920 (9:16) Video Builder (AUDIO COMMANDS DURATION)
    logger.info("\n[STEP 5/6] Rendering Video Full Screen 9:16 CapCut-Style & Sottotitoli Centrati...")
    output_video_path = os.path.join(OUTPUTS_DIR, "output_viral_short.mp4")
    final_mp4 = build_youtube_short(script_data, audio_data, clip_paths, output_path=output_video_path)

    # STEP 6: Telegram Bot Dispatcher with AI Multi-Platform Publishing Schedules
    telegram_res = {"status": "disabled"}
    if send_telegram:
        logger.info("\n[STEP 6/6] Invio Video MP4 e Kit di Pubblicazione su Telegram...")
        telegram_res = send_video_to_telegram(final_mp4, script_data, dry_run=dry_run, force_send=True)

    elapsed = time.time() - start_time

    # Pipeline Execution Summary
    logger.info("\n" + "=" * 65)
    logger.info("🎬 CAPCUT-STYLE AUTONOMOUS SHORTS PIPELINE: ESECUZIONE COMPLETATA!")
    logger.info("=" * 65)
    logger.info(f"• Nicchia:           {niche_data['name']}")
    logger.info(f"• Titolo Short:      {script_data.get('title')}")
    logger.info(f"• Durata Effettiva:  {audio_data['duration']:.2f}s (Audio-Video Sync Perfetto)")
    logger.info(f"• Output Video MP4:  {final_mp4}")
    logger.info(f"• Stile Montaggio:   CapCut Clean Full Screen 9:16 (Tagli 1.8s + Zoom Pulse)")
    logger.info(f"• Motore Vocale:     Edge-TTS (+15% Rate Boost - 100% Gratuito)")
    logger.info(f"• Telegram Status:   {telegram_res.get('status')}")
    logger.info(f"• Tempo Esecuzione:  {elapsed:.2f} secondi")
    logger.info("=" * 65 + "\n")

    return {
        "status": "success",
        "output_path": final_mp4,
        "script_data": script_data,
        "audio_data": audio_data,
        "telegram_status": telegram_res.get("status")
    }


def main():
    parser = argparse.ArgumentParser(
        description="CapCut-Style High-Retention Faceless Shorts Video Automation Suite with Playwright Trend-Jacking"
    )
    parser.add_argument(
        "--niche",
        type=str,
        default=None,
        choices=["tech_oscura", "storie_oscure", "misteri"],
        help="Seleziona la nicchia (opzionale - se omesso l'agente individuerà il video più virale su YouTube in automatico)"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Argomento personalizzato o URL di un video YouTube virale da cui estrarre il transcript (es. https://www.youtube.com/watch?v=...)"
    )
    parser.add_argument(
        "--auto-viral",
        action="store_true",
        help="Avvia Playwright per trovare automaticamente il video più virale su tutto YouTube in assoluto ed estrarne il transcript"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Esegue la pipeline in modalità test senza chiamare API o inviare messaggi"
    )
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="Disabilita l'invio del video finale su Telegram"
    )

    args = parser.parse_args()
    send_telegram = not args.no_telegram

    run_pipeline(
        niche_key=args.niche,
        topic_input=args.topic,
        auto_viral=args.auto_viral if hasattr(args, 'auto_viral') else getattr(args, 'auto_viral', False),
        dry_run=args.dry_run,
        send_telegram=send_telegram
    )


if __name__ == "__main__":
    main()
