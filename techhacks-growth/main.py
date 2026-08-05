#!/usr/bin/env python3
"""
techhacks-growth: Standalone 4-Platform Video Analytics Dashboard & Growth Agent
Dedicated to tracking real video views and scaling performance across:
1. YouTube Shorts (@techhacks_aii)
2. Instagram Reels (@techs_ai1)
3. Facebook Reels (TechHacks AI)
4. TikTok Videos (@techhacks.ai)
"""

import os
import sys
import json
import time
import argparse
import logging
import webbrowser
from datetime import datetime
from typing import Dict, Any

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("growth.main")

# Import Growth Modules
from src.youtube_tracker import fetch_youtube_metrics
from src.instagram_tracker import fetch_instagram_metrics
from src.facebook_tracker import fetch_facebook_metrics
from src.tiktok_tracker import fetch_tiktok_metrics
from src.growth_radar import generate_growth_plan
from src.growth_reporter import send_growth_report


def save_analytics_snapshot(
    yt_data: Dict[str, Any],
    ig_data: Dict[str, Any],
    fb_data: Dict[str, Any],
    tt_data: Dict[str, Any],
    history_file: str = "data/analytics_history.json"
):
    """Saves current metrics snapshot to analytics_history.json."""
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().isoformat()

    snapshot = {
        "timestamp": timestamp,
        "date": today_str,
        "youtube": yt_data,
        "instagram": ig_data,
        "facebook": fb_data,
        "tiktok": tt_data
    }

    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                history = content.get("history", [])
        except Exception:
            history = []

    history.append(snapshot)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump({"history": history}, f, indent=2, ensure_ascii=False)

    logger.info(f"Analytics snapshot saved to {history_file}")


def run_growth_pipeline(dry_run: bool = False, send_telegram: bool = True, open_dashboard: bool = False):
    """
    Executes 4-platform video analytics sync, growth radar recommendation generation,
    and Telegram report dispatch.
    """
    start_time = time.time()
    logger.info("=" * 65)
    logger.info("⚡ TECHHACKS-GROWTH: AVVIO DASHBOARD ANALYTICS 4-PIATTAFORME VIDEO")
    logger.info("=" * 65)

    # Step 1: Sync YouTube Shorts Metrics (@techhacks_aii)
    logger.info("\n[STEP 1/5] Sync Analytics YouTube Shorts (@techhacks_aii)...")
    yt_metrics = fetch_youtube_metrics(dry_run=dry_run)

    # Step 2: Sync Instagram Reels Metrics (@techs_ai1)
    logger.info("\n[STEP 2/5] Sync Analytics Instagram Reels (@techs_ai1)...")
    ig_metrics = fetch_instagram_metrics(dry_run=dry_run)

    # Step 3: Sync Facebook Reels Metrics (TechHacks AI)
    logger.info("\n[STEP 3/5] Sync Analytics Facebook Reels (TechHacks AI)...")
    fb_metrics = fetch_facebook_metrics(dry_run=dry_run)

    # Step 4: Sync TikTok Video Metrics (@techhacks.ai)
    logger.info("\n[STEP 4/5] Sync Analytics TikTok Videos (@techhacks.ai)...")
    tt_metrics = fetch_tiktok_metrics(dry_run=dry_run)

    # Save Snapshot
    save_analytics_snapshot(yt_metrics, ig_metrics, fb_metrics, tt_metrics)

    # Step 5: Growth Radar Strategic Recommendations
    logger.info("\n[STEP 5/5] Generazione Piano d'Azione Virale (Growth Radar)...")
    growth_plan = generate_growth_plan(yt_metrics, ig_metrics, fb_metrics, tt_metrics, dry_run=dry_run)

    # Send Telegram Report
    if send_telegram:
        send_growth_report(yt_metrics, ig_metrics, fb_metrics, tt_metrics, growth_plan, dry_run=dry_run)

    elapsed = time.time() - start_time
    total_aggregate_views = (
        yt_metrics.get('total_views', 0) +
        ig_metrics.get('estimated_weekly_reach', 0) +
        fb_metrics.get('total_views', 0) +
        tt_metrics.get('total_views', 0)
    )

    # Summary Output
    logger.info("\n" + "=" * 65)
    logger.info("📊 TECHHACKS-GROWTH: SOMMARIO ESECUZIONE VISUALIZZAZIONI")
    logger.info("=" * 65)
    logger.info(f"🔥 VISUALIZZAZIONI TOTALI AGGREGATE: {total_aggregate_views:,}")
    logger.info(f"• YouTube Shorts Views:  {yt_metrics['total_views']:,} (@techhacks_aii)")
    logger.info(f"• Instagram Reels Views:  {ig_metrics['estimated_weekly_reach']:,} (@techs_ai1)")
    logger.info(f"• Facebook Reels Views:   {fb_metrics['total_views']:,} (TechHacks AI)")
    logger.info(f"• TikTok Video Views:     {tt_metrics['total_views']:,} (@techhacks.ai)")
    logger.info(f"• Strategia Virale:       {growth_plan['headline']}")
    logger.info(f"• Tempo di Esecuzione:    {elapsed:.2f} secondi")
    logger.info("=" * 65 + "\n")

    if open_dashboard:
        dist_dash_path = os.path.abspath("dashboard/dist/index.html")
        raw_dash_path = os.path.abspath("dashboard/index.html")
        target_path = dist_dash_path if os.path.exists(dist_dash_path) else raw_dash_path
        logger.info(f"Apertura React Dashboard Web nel browser: file://{target_path}")
        webbrowser.open(f"file://{target_path}")


def main():
    parser = argparse.ArgumentParser(
        description="TechHacks Growth Agent & 4-Platform React Dashboard Suite"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Esegue la sincronizzazione in modalità test senza chiamare API di produzione"
    )
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="Disabilita l'invio del report quotidiano su Telegram"
    )
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Apre automaticamente la Dashboard Web React nel browser"
    )

    args = parser.parse_args()
    send_telegram = not args.no_telegram

    run_growth_pipeline(
        dry_run=args.dry_run,
        send_telegram=send_telegram,
        open_dashboard=args.open_dashboard
    )


if __name__ == "__main__":
    main()
