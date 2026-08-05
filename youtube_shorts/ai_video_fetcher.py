"""
ai_video_fetcher.py  ·  AI Video Engine
=========================================
3-Tier pipeline:

  Tier 1 — HuggingFace Inference API (Wan 2.1)   → real AI video, free HF token
  Tier 2 — Lorem Flickr / Picsum + Ken Burns      → cinematic animated photo
  Tier 3 — Animated dark gradient                 → guaranteed offline fallback

Setup (one-time, 1 minute):
  1. https://huggingface.co → Settings → Access Tokens → New token → add HF_TOKEN to .env
"""

import os
import io
import math
import random
import logging
import urllib.parse
from typing import Dict, Any, Optional

import numpy as np
import requests
from PIL import Image

logger = logging.getLogger("youtube_shorts.ai_video_fetcher")

# ── Bundled ffmpeg ────────────────────────────────────────────────────────────
def _get_ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

# ── Directories ───────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
AI_VIDEOS_DIR = os.path.join(_HERE, "assets", "generated_ai_videos")
os.makedirs(AI_VIDEOS_DIR, exist_ok=True)

# ── API Keys ──────────────────────────────────────────────────────────────────
def _hf_token() -> str:
    return os.environ.get("HF_TOKEN", "")

# ── Video specs ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT, FPS = 1080, 1920, 30
CLIP_DURATION = 5.0

# ── Dark palettes for gradient fallback ──────────────────────────────────────
DARK_PALETTES = [
    [(10, 10, 25), (5, 20, 50)],
    [(20, 5, 5), (50, 10, 10)],
    [(5, 20, 5), (10, 40, 20)],
    [(15, 10, 30), (30, 5, 50)],
    [(5, 5, 5), (25, 25, 30)],
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    )
}


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 1 — HuggingFace Inference API
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_hf_video(prompt: str, target_path: str) -> Optional[str]:
    """
    Generates real AI video via HuggingFace Inference API.
    Free token at https://huggingface.co → Settings → Access Tokens
    """
    token = _hf_token()
    if not token:
        logger.info("[HuggingFace] ℹ️  HF_TOKEN non impostato — aggiungilo al .env per video AI reali")
        return None

    vertical_prompt = f"{prompt}, vertical portrait 9:16, cinematic, dramatic, documentary"

    # Method A: huggingface_hub InferenceClient (modern, supports providers)
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token)
        logger.info(f"[HuggingFace] 🎬 Generando video AI: '{prompt[:55]}'")

        video_bytes = client.text_to_video(
            vertical_prompt,
            model="Wan-AI/Wan2.1-T2V-14B",
        )
        content = video_bytes if isinstance(video_bytes, bytes) else video_bytes.read()
        if content and len(content) > 10_000:
            with open(target_path, "wb") as f:
                f.write(content)
            logger.info(f"[HuggingFace] ✅ Video AI salvato ({len(content)//1024}KB) → {target_path}")
            return target_path
    except Exception as e:
        logger.debug(f"[HuggingFace] InferenceClient: {e}")

    # Method B: raw HTTP to inference API (fallback)
    for model_id in [
        "ali-vilab/text-to-video-ms-1.7b",
        "damo-vilab/text-to-video-ms-1.7b",
    ]:
        try:
            logger.info(f"[HuggingFace] 🎬 Tentativo con modello: {model_id}")
            api_url = f"https://api-inference.huggingface.co/models/{model_id}"
            hf_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = requests.post(
                api_url,
                headers=hf_headers,
                json={"inputs": vertical_prompt},
                timeout=120
            )
            if response.status_code == 200 and len(response.content) > 10_000:
                with open(target_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"[HuggingFace] ✅ Video salvato ({len(response.content)//1024}KB)")
                return target_path
            else:
                logger.debug(f"[HuggingFace] {model_id} → {response.status_code}: {response.text[:120]}")
        except Exception as e:
            logger.debug(f"[HuggingFace] {model_id} errore: {e}")

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 2 — Cinematic Image + Ken Burns Effect
# ═══════════════════════════════════════════════════════════════════════════════

def _fetch_cinematic_image(query: str, seed: int = 0) -> Optional[Image.Image]:
    """
    Fetches a thematic image from reliable free sources (no API key needed):
    1. Lorem Flickr — keyword-based photos
    2. Picsum Photos — beautiful random HD photos
    """
    keywords = _keywords(query, n=3).replace(" ", ",")

    # Source 1: Lorem Flickr — keyword photos, always works, no key
    try:
        res = requests.get(
            f"https://loremflickr.com/1080/1920/{keywords}/all",
            headers=HEADERS, timeout=15, allow_redirects=True
        )
        if res.status_code == 200 and len(res.content) > 5_000:
            img = Image.open(io.BytesIO(res.content)).convert("RGB")
            if img.size[0] > 100:
                logger.info(f"[Image] ✅ Flickr '{keywords}' ({img.size})")
                return img
    except Exception as e:
        logger.debug(f"[Image] Flickr failed: {e}")

    # Source 2: Picsum Photos — always beautiful, always works
    picsum_seed = abs(seed + hash(query[:20]) % 1000)
    try:
        res2 = requests.get(
            f"https://picsum.photos/seed/{picsum_seed}/1080/1920",
            headers=HEADERS, timeout=15, allow_redirects=True
        )
        if res2.status_code == 200 and len(res2.content) > 5_000:
            img2 = Image.open(io.BytesIO(res2.content)).convert("RGB")
            if img2.size[0] > 100:
                logger.info(f"[Image] ✅ Picsum seed={picsum_seed} ({img2.size})")
                return img2
    except Exception as e:
        logger.debug(f"[Image] Picsum failed: {e}")

    # Source 3: broad category on Flickr
    broad = _scene_to_broad_category(query).split(",")[0]
    try:
        res3 = requests.get(
            f"https://loremflickr.com/1080/1920/{broad}",
            headers=HEADERS, timeout=15, allow_redirects=True
        )
        if res3.status_code == 200 and len(res3.content) > 5_000:
            img3 = Image.open(io.BytesIO(res3.content)).convert("RGB")
            if img3.size[0] > 100:
                logger.info(f"[Image] ✅ Flickr broad '{broad}' ({img3.size})")
                return img3
    except Exception as e:
        logger.debug(f"[Image] Flickr broad failed: {e}")

    return None


def _build_ken_burns_video(img: Image.Image, target_path: str,
                            duration: float = CLIP_DURATION) -> str:
    """Renders a cinematic Ken Burns MP4 with zoom/pan + vignette + film grain."""
    import subprocess
    motions = ["zoom_in", "zoom_out", "pan_left", "pan_right", "zoom_in_pan_right"]
    motion = random.choice(motions)

    overscan_w = int(WIDTH * 1.30)
    overscan_h = int(HEIGHT * 1.30)
    base = img.resize((overscan_w, overscan_h), Image.Resampling.LANCZOS).convert("RGB")
    base_arr = np.array(base, dtype=np.float32)
    vignette = _make_vignette(WIDTH, HEIGHT, strength=0.65)
    n_frames = int(duration * FPS)
    H, W = overscan_h, overscan_w

    cmd = [
        _get_ffmpeg(), "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-preset", "veryfast",
        "-crf", "22", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", target_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        frame = _render_ken_burns_frame(base_arr, t, motion, W, H, vignette)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait(timeout=120)
    logger.info(f"[KenBurns] ✅ '{motion}' → {target_path}")
    return target_path


def _render_ken_burns_frame(base_arr, t, motion, W, H, vignette):
    t_ease = t * t * (3 - 2 * t)
    if motion in ("zoom_in", "zoom_in_pan_right"):
        zoom = 1.0 + 0.18 * t_ease
    elif motion == "zoom_out":
        zoom = 1.18 - 0.18 * t_ease
    else:
        zoom = 1.08

    crop_w = int(WIDTH / zoom)
    crop_h = int(HEIGHT / zoom)
    max_pan_x = W - crop_w
    max_pan_y = H - crop_h

    if motion == "pan_left":
        ox, oy = int(max_pan_x * t_ease), max_pan_y // 2
    elif motion == "pan_right":
        ox, oy = int(max_pan_x * (1 - t_ease)), max_pan_y // 2
    elif motion == "zoom_in_pan_right":
        ox, oy = int(max_pan_x * 0.5 * t_ease), max_pan_y // 2
    else:
        ox, oy = max_pan_x // 2, max_pan_y // 2

    ox = max(0, min(ox, W - crop_w))
    oy = max(0, min(oy, H - crop_h))

    crop = base_arr[oy:oy + crop_h, ox:ox + crop_w]
    img_crop = Image.fromarray(crop.astype(np.uint8)).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
    frame = np.array(img_crop, dtype=np.float32)
    frame = np.clip(frame * 0.85, 0, 255)
    frame = np.clip((frame - 30) * 1.12 + 30, 0, 255)
    grain = np.random.normal(0, 4, frame.shape).astype(np.float32)
    frame = np.clip(frame + grain, 0, 255)
    return np.clip(frame * vignette, 0, 255).astype(np.uint8)


def _make_vignette(w, h, strength=0.65):
    cx, cy = w / 2, h / 2
    Y, X = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    mask = 1.0 - strength * np.clip(dist - 0.3, 0, 1) / 0.7
    return np.clip(mask, 0, 1)[:, :, np.newaxis]


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 3 — Animated Dark Gradient (zero-dependency offline fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_gradient_video(target_path: str, duration: float = CLIP_DURATION, seed: int = 0) -> str:
    """Beautiful animated dark gradient — works with zero internet."""
    import subprocess
    rng = random.Random(seed)
    palette = rng.choice(DARK_PALETTES)
    c1 = np.array(palette[0], dtype=np.float32)
    c2 = np.array(palette[1], dtype=np.float32)
    vignette = _make_vignette(WIDTH, HEIGHT, strength=0.75)
    n_frames = int(duration * FPS)
    angle_base = rng.uniform(0, math.pi)
    Y, X = np.mgrid[0:HEIGHT, 0:WIDTH]

    cmd = [
        _get_ffmpeg(), "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-preset", "veryfast",
        "-crf", "24", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", target_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        angle = angle_base + t * math.pi * 0.25
        proj = (X * math.cos(angle) + Y * math.sin(angle)) / (WIDTH + HEIGHT)
        proj = (proj - proj.min()) / (proj.max() - proj.min() + 1e-8)
        pulse = 0.92 + 0.08 * math.sin(t * math.pi * 2)
        frame = (c1[np.newaxis, np.newaxis, :] * (1 - proj[:, :, np.newaxis]) +
                 c2[np.newaxis, np.newaxis, :] * proj[:, :, np.newaxis])
        proc.stdin.write(np.clip(frame * pulse * vignette, 0, 255).astype(np.uint8).tobytes())

    proc.stdin.close()
    proc.wait(timeout=60)
    logger.info(f"[Gradient] ✅ Gradiente cinematografico → {target_path}")
    return target_path


# ═══════════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════════

def _keywords(prompt: str, n: int = 3) -> str:
    _noise = {
        "photorealistic", "cinematic", "8k", "4k", "hdr", "9:16", "vertical",
        "no text", "no logo", "nologo", "sharp", "detailed", "ultra", "dramatic",
        "lighting", "shot", "footage", "video", "film", "frame", "scene",
        "dark", "moody", "noir", "background", "foreground", "close-up", "closeup",
        "gritty", "raw", "shadow", "contrast", "documentary", "style", "aesthetic",
        "photorealistic,", "35mm", "grain", "lens", "anamorphic", "vintage",
        "atmosphere", "mystery", "concept", "surreal", "cosmic", "space", "nebula",
        "abstract", "photography", "natural", "side-lighting", "lensing", "dust",
        "deep", "volumetric", "and", "into", "with", "from", "for", "the", "view",
        "hyperrealistic", "glowing", "rendering", "rendered", "image"
    }
    words = prompt.lower().replace(",", " ").replace(".", " ").replace(";", " ").split()
    filtered = [w for w in words if w not in _noise and len(w) > 2]
    return " ".join(filtered[:n]) if filtered else "gold bars"




def _scene_to_broad_category(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["police", "cop", "detective", "crime", "arrest", "polizia", "poliziotto", "criminale"]):
        return "police,night,city"
    if any(w in p for w in ["hacker", "computer", "code", "server", "cyber", "laptop", "screen"]):
        return "technology,dark,screen"
    if any(w in p for w in ["forest", "tree", "nature", "jungle"]):
        return "forest,dark,moody"
    if any(w in p for w in ["city", "street", "urban", "building", "london", "new york"]):
        return "city,night,urban"
    if any(w in p for w in ["ocean", "sea", "water", "rain", "storm"]):
        return "ocean,dramatic,dark"
    if any(w in p for w in ["fire", "explosion", "flame"]):
        return "fire,dramatic"
    if any(w in p for w in ["space", "cosmos", "galaxy", "star", "nebula", "astronaut"]):
        return "space,cosmos,dark"
    if any(w in p for w in ["gold", "bank", "money", "vault", "treasure"]):
        return "gold,luxury,dramatic"
    return "cinematic,dark,dramatic"


# ═══════════════════════════════════════════════════════════════════════════════
# Public Interface
# ═══════════════════════════════════════════════════════════════════════════════

class AIVideoFetcher:
    """
    3-Tier Cinematic Video Engine:
    Tier 1: HuggingFace Inference API → real AI generated video (needs HF_TOKEN)
    Tier 2: Lorem Flickr/Picsum + Ken Burns → beautiful cinematic animated photo
    Tier 3: Animated dark gradient → always works offline
    """

    def __init__(self, output_dir: str = AI_VIDEOS_DIR):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_ai_video_for_scene(self, scene: Dict[str, Any], idx: int) -> str:
        prompt = scene.get("visual_prompt", scene.get("query", "cinematic dark dramatic scene"))
        target_path = os.path.join(self.output_dir, f"scene_{idx+1:02d}.mp4")

        # Cache: skip if already rendered
        if os.path.exists(target_path) and os.path.getsize(target_path) > 10_000:
            logger.info(f"[Cache] Scena {idx+1} già presente → {target_path}")
            return target_path

        logger.info(f"[AIVideoFetcher] 🎬 Scena {idx+1}: '{prompt[:65]}'")

        # ── Tier 1: HuggingFace AI — SOLO per scena 1 (hook = più importante) ──
        # Le scene 2+ vanno dritte al Ken Burns per risparmiare crediti HF
        if idx == 0:
            if _hf_token():
                logger.info("[AIVideoFetcher] 🤖 Scena 1 → HuggingFace AI (hook scene)")
                result = _generate_hf_video(prompt, target_path)
                if result and os.path.exists(result) and os.path.getsize(result) > 10_000:
                    return result
            else:
                logger.info("[AIVideoFetcher] ℹ️  HF_TOKEN non impostato — aggiungilo al .env per video AI reali sulla scena 1")
        else:
            logger.info(f"[AIVideoFetcher] 💰 Scena {idx+1} → Ken Burns (risparmio crediti HF)")

        # ── Tier 2: Cinematic image + Ken Burns (gratis, illimitato) ─────────
        logger.info(f"[AIVideoFetcher] 📷 Recupero immagine cinematografica per scena {idx+1}...")
        try:
            img = _fetch_cinematic_image(prompt, seed=idx)
            if img is not None:
                result = _build_ken_burns_video(img, target_path, duration=CLIP_DURATION)
                if result and os.path.exists(result) and os.path.getsize(result) > 10_000:
                    return result
        except Exception as e:
            logger.warning(f"[KenBurns] Errore: {e}")

        # ── Tier 3: Animated gradient (sempre funziona offline) ───────────────
        logger.info(f"[AIVideoFetcher] 🌑 Gradiente cinematografico per scena {idx+1}...")
        try:
            return _build_gradient_video(target_path, duration=CLIP_DURATION, seed=idx * 13 + 7)
        except Exception as e:
            logger.error(f"[Gradient] Fallito: {e}")
            return target_path


def fetch_ai_video_for_scene(scene: Dict[str, Any], idx: int) -> str:
    """Funzione di convenienza a livello modulo."""
    return AIVideoFetcher().fetch_ai_video_for_scene(scene, idx)
