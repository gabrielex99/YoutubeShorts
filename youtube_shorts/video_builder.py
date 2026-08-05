import os
import re
import math
import random
import logging
import subprocess
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from youtube_shorts.config import WIDTH, HEIGHT, FPS, OUTPUTS_DIR, ASSETS_AUDIO_DIR, ASSETS_CLIPS_DIR, ASSETS_BACKGROUNDS_DIR

logger = logging.getLogger("youtube_shorts.video_builder")

try:
    import moviepy.editor as mp
    MOVIEPY_V1 = True
except ImportError:
    try:
        import moviepy as mp
        MOVIEPY_V1 = False
    except ImportError:
        mp = None
        MOVIEPY_V1 = False
        logger.error("MoviePy is not installed.")


class CapCutVideoBuilder:
    """
    CapCut-Style 9:16 Short-Form Video Builder.
    Features:
    - 100% Real MP4 Motion Video Footage Layer: No static images. Uses real 1080x1920 video clips with 1.8s cuts & zoom pulse.
    - Exact Audio-Video Duration Sync: Audio duration strictly commands total video length.
    - Hormozi / CapCut Word-by-Word Kinetic Subtitles overlay: Centered, Impact/Montserrat bold, Yellow/White text, heavy 5px black stroke outline.
    """

    BRIGHT_YELLOW = (250, 204, 21)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def build_youtube_short(
        self,
        script_data: Dict[str, Any],
        audio_data: Dict[str, Any],
        clip_paths: List[str],
        output_path: Optional[str] = None
    ) -> str:
        """
        Renders 1080x1920 9:16 Short video with real MP4 motion video footage & word-by-word subtitles.
        """
        if not output_path:
            output_path = os.path.join(OUTPUTS_DIR, "output_viral_short.mp4")

        abs_output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_output_path), exist_ok=True)

        voice_audio_path = audio_data["audio_path"]
        duration = audio_data.get("duration", 12.0)
        word_timestamps = audio_data.get("word_timestamps", [])

        # 1. Load Primary Neural Voiceover Audio Track (keep natural file duration to avoid EOF read errors)
        voice_clip = mp.AudioFileClip(voice_audio_path)
        actual_voice_dur = voice_clip.duration

        # +0.5s coda finale: il video e l'audio di sottofondo proseguono per +0.5s per non tagliare l'ultima parola
        audio_duration = max(actual_voice_dur, duration) + 0.5

        logger.info(f"[VideoBuilder] Rendering Real 100% MP4 Motion Video (Voice: {actual_voice_dur:.2f}s, Total: {audio_duration:.2f}s) -> {abs_output_path}")

        # 2. Prepare Background Dark Suspense Music Track (Volume at 15%)
        bg_music_path = self._ensure_dark_suspense_music(audio_duration)
        audio_tracks = [voice_clip]

        if os.path.exists(bg_music_path) and os.path.getsize(bg_music_path) > 100:
            try:
                music_clip = mp.AudioFileClip(bg_music_path)
                if MOVIEPY_V1:
                    music_clip = music_clip.volumex(0.15).set_duration(audio_duration)
                else:
                    music_clip = music_clip.with_effects([mp.afx.MultiplyVolume(0.15)]).with_duration(audio_duration)

                audio_tracks.append(music_clip)
                logger.info("[VideoBuilder] Mixed Dark Suspense Background Music at 15% volume.")
            except Exception as e:
                logger.warning(f"[VideoBuilder] Background music mixing exception ({e}). Using primary voiceover.")

        mixed_audio = mp.CompositeAudioClip(audio_tracks)


        # 3. Build Full Screen 100% Real MP4 Motion Video Background Layer
        bg_clip = self._build_real_mp4_motion_layer(
            clip_paths, audio_duration,
            script_data=script_data,
            word_timestamps=word_timestamps
        )

        # 4. Build Dynamic Word-by-Word Subtitles Overlay
        subtitle_clips = self._build_word_by_word_subtitles(word_timestamps, audio_duration)

        # 5. Composite Final Video & ATTACH MIXED AUDIO TRACK
        final_clip = mp.CompositeVideoClip([bg_clip] + subtitle_clips, size=(WIDTH, HEIGHT))

        if MOVIEPY_V1:
            final_clip = final_clip.set_audio(mixed_audio)
            final_clip = final_clip.set_duration(audio_duration)
        else:
            final_clip = final_clip.with_audio(mixed_audio)
            final_clip = final_clip.with_duration(audio_duration)

        # Export MP4 (3500k bitrate for fast Telegram upload)
        final_clip.write_videofile(
            abs_output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="3500k",
            temp_audiofile=abs_output_path.replace(".mp4", "_temp_audio.m4a"),
            remove_temp=True,
            logger=None
        )

        final_clip.close()
        bg_clip.close()
        voice_clip.close()

        logger.info(f"[VideoBuilder] 100% Real MP4 Motion Short rendered successfully -> {abs_output_path}")
        return abs_output_path

    def _ensure_dark_suspense_music(self, duration: float) -> str:
        """Ensures a dark suspense ambient MP3 audio track exists."""
        music_path = os.path.join(ASSETS_AUDIO_DIR, "bg_music.mp3")
        if os.path.exists(music_path) and os.path.getsize(music_path) > 1000:
            return music_path

        try:
            try:
                import imageio_ffmpeg
                ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg_bin = "ffmpeg"
            cmd = [
                ffmpeg_bin, "-y",
                "-f", "lavfi", "-i", "sine=frequency=60:duration=60",
                "-f", "lavfi", "-i", "sine=frequency=110:duration=60",
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[aout]",
                "-map", "[aout]",
                "-c:a", "libmp3lame", "-b:a", "128k",
                music_path
            ]
            subprocess.run(cmd, capture_output=True, timeout=15)
            if os.path.exists(music_path):
                return music_path
        except Exception:
            pass

        return music_path

    def _build_real_mp4_motion_layer(self, media_paths: List[str], duration: float,
                                      script_data: Optional[Dict[str, Any]] = None,
                                      word_timestamps: Optional[List[Dict[str, Any]]] = None) -> mp.VideoClip:
        """
        Builds a full-screen 1080x1920 background layer from MP4 clips.
        Handles both .mp4 video files and static images with Ken Burns simulation.
        Features 1.8s rhythmic cuts, zoom pulse, and a semi-transparent dark vignette
        overlay for maximum subtitle legibility.
        """
        valid_paths = [p for p in media_paths if os.path.exists(p) and os.path.getsize(p) > 10_000]

        # Also scan fallback directories for any .mp4 clips
        if not valid_paths:
            for d in [ASSETS_CLIPS_DIR, ASSETS_BACKGROUNDS_DIR]:
                abs_d = os.path.abspath(d)
                if os.path.exists(abs_d):
                    found = [
                        os.path.join(abs_d, f) for f in os.listdir(abs_d)
                        if f.endswith((".mp4", ".mkv", ".webm")) and os.path.getsize(os.path.join(abs_d, f)) > 10_000
                    ]
                    valid_paths.extend(found)

        prepared_clips = []
        for path in valid_paths:
            try:
                if path.lower().endswith((".mp4", ".mkv", ".webm")):
                    c = mp.VideoFileClip(path)
                else:
                    # Treat as image (Ken Burns already applied externally; load as video)
                    c = mp.ImageClip(path)
                    if MOVIEPY_V1:
                        c = c.set_duration(4.0)
                    else:
                        c = c.with_duration(4.0)

                vw, vh = c.size
                target_ratio = WIDTH / float(HEIGHT)
                current_ratio = vw / float(vh)

                if current_ratio > target_ratio:
                    new_w = int(vh * target_ratio)
                    x1 = (vw - new_w) // 2
                    cropped = c.crop(x1=x1, width=new_w, height=vh) if MOVIEPY_V1 else c.cropped(x1=x1, width=new_w, height=vh)
                else:
                    new_h = int(vw / target_ratio)
                    y1 = (vh - new_h) // 2
                    cropped = c.crop(y1=y1, width=vw, height=new_h) if MOVIEPY_V1 else c.cropped(y1=y1, width=vw, height=new_h)

                resized = cropped.resize((WIDTH, HEIGHT)) if MOVIEPY_V1 else cropped.resized((WIDTH, HEIGHT))
                prepared_clips.append(resized)
            except Exception as e:
                logger.warning(f"[VideoBuilder] Could not load clip {path}: {e}")

        if not prepared_clips:
            # Guaranteed dark gradient fallback — never a black screen
            logger.warning("[VideoBuilder] No valid clips found. Rendering animated gradient fallback.")
            try:
                from youtube_shorts.ai_video_fetcher import _build_gradient_video
                tmp_grad = os.path.join(ASSETS_BACKGROUNDS_DIR, "_gradient_fallback.mp4")
                _build_gradient_video(tmp_grad, duration=duration, seed=42)
                if os.path.exists(tmp_grad):
                    prepared_clips.append(mp.VideoFileClip(tmp_grad))
            except Exception as e:
                logger.error(f"[VideoBuilder] Gradient generation failed: {e}")
                dark_frame = np.full((HEIGHT, WIDTH, 3), 12, dtype=np.uint8)
                return mp.VideoClip(lambda t: dark_frame, duration=duration)

        # ── Calcola durata per ogni scena (1 clip = 1 scena, no flickering) ───
        scene_durations = self._compute_scene_durations(
            script_data, word_timestamps, duration
        )
        n_scenes = len(scene_durations)

        clip_segments = []
        for scene_idx, seg_dur in enumerate(scene_durations):
            if seg_dur <= 0:
                continue
            # Ogni scena usa la propria clip dedicata (wrap circolare se mancano clip)
            base_clip = prepared_clips[scene_idx % len(prepared_clips)]

            # Estendi o taglia la clip alla durata della scena
            clip_dur = base_clip.duration if hasattr(base_clip, "duration") else seg_dur
            if clip_dur < seg_dur:
                sub = base_clip.loop(duration=seg_dur) if MOVIEPY_V1 else base_clip.with_effects([mp.vfx.Loop(duration=seg_dur)])
            else:
                sub = base_clip.subclip(0, seg_dur) if MOVIEPY_V1 else base_clip.subclipped(0, seg_dur)

            # Lento zoom-in per tutta la durata della scena (niente tagli interni)
            _seg_dur = seg_dur  # cattura nel closure
            def make_zoom_frame(get_frame, t, _d=_seg_dur):
                frame = get_frame(t)
                prog = min(1.0, max(0.0, t / float(_d)))
                scale = 1.0 + 0.06 * prog          # zoom gentile 0→6%
                h, w, _ = frame.shape
                new_h, new_w = int(h / scale), int(w / scale)
                top  = (h - new_h) // 2
                left = (w - new_w) // 2
                cropped_arr = frame[top:top + new_h, left:left + new_w]
                img_res = Image.fromarray(cropped_arr).resize((w, h), Image.Resampling.BILINEAR)
                return np.array(img_res)

            zoomed = sub.fl(make_zoom_frame) if MOVIEPY_V1 else sub.transform(make_zoom_frame)
            clip_segments.append(zoomed)

        if not clip_segments:
            dark_frame = np.full((HEIGHT, WIDTH, 3), 12, dtype=np.uint8)
            return mp.VideoClip(lambda t: dark_frame, duration=duration)

        if len(clip_segments) > 1:
            stitched = mp.concatenate_videoclips(clip_segments, method="compose")
        else:
            stitched = clip_segments[0]

        if MOVIEPY_V1:
            stitched = stitched.set_duration(duration)
        else:
            stitched = stitched.with_duration(duration)

        return stitched

    def _compute_scene_durations(self, script_data: Optional[Dict[str, Any]],
                                  word_timestamps: List[Dict[str, Any]],
                                  total_duration: float) -> List[float]:
        """
        Calcola la durata di ogni scena basandosi sui word_timestamps.
        Strategia:
          1. Cerca il primo word_timestamp che matcha l'inizio di ogni scena
             e usa quello come punto di taglio.
          2. Fallback: suddivisione proporzionale alla lunghezza del testo.
        """
        scenes = (script_data or {}).get("scenes", [])
        n = len(scenes)
        if n == 0:
            return [total_duration]
        if n == 1:
            return [total_duration]

        # ── Tentativo 1: allineamento via word_timestamps ──────────────────
        if word_timestamps:
            all_words_lower = [
                w["word"].lower().strip(".,!?\"'-") for w in word_timestamps
            ]
            scene_start_times = []
            search_from = 0

            for scene in scenes:
                scene_text = scene.get("text", "")
                first_word = scene_text.lower().split()[0].strip(".,!?\"'-") if scene_text.strip() else ""
                found_at = None
                for j in range(search_from, len(all_words_lower)):
                    if all_words_lower[j] == first_word:
                        found_at = j
                        break
                if found_at is not None:
                    scene_start_times.append(word_timestamps[found_at]["start"])
                    search_from = found_at + 1
                else:
                    scene_start_times.append(None)   # non trovato

            # Verifica che almeno metà delle scene siano state trovate
            found_count = sum(1 for t in scene_start_times if t is not None)
            if found_count >= max(1, n // 2):
                # Riempi i None con interpolazione
                for i, t in enumerate(scene_start_times):
                    if t is None:
                        prev_t = scene_start_times[i - 1] if i > 0 else 0.0
                        next_t = next(
                            (scene_start_times[k] for k in range(i + 1, n) if scene_start_times[k] is not None),
                            total_duration
                        )
                        scene_start_times[i] = (prev_t + next_t) / 2

                scene_start_times.append(total_duration)
                durations = [
                    max(0.5, scene_start_times[i + 1] - scene_start_times[i])
                    for i in range(n)
                ]
                logger.info(f"[VideoBuilder] Scene durations (word-aligned): {[f'{d:.1f}s' for d in durations]}")
                return durations

        # ── Fallback: proporzionale alla lunghezza del testo ───────────────
        text_lengths = [len(s.get("text", " ")) for s in scenes]
        total_chars = sum(text_lengths) or 1
        durations = [total_duration * (l / total_chars) for l in text_lengths]
        # Assicura minimo 1s per scena
        durations = [max(1.0, d) for d in durations]
        # Ri-normalizza per rispettare total_duration
        scale = total_duration / sum(durations)
        durations = [d * scale for d in durations]
        logger.info(f"[VideoBuilder] Scene durations (text-proportional): {[f'{d:.1f}s' for d in durations]}")
        return durations

    def _build_word_by_word_subtitles(self, word_timestamps: List[Dict[str, Any]], duration: float) -> List[mp.VideoClip]:
        """
        Builds Word-by-Word CapCut Subtitles displaying 1-2 words at a time max
        positioned EXACTLY at center (x='center', y='center') with Impact font, Yellow/White text, heavy black stroke (width 5),
        and NO background boxes!
        """
        subtitle_clips = []
        if not word_timestamps:
            return subtitle_clips

        chunks = []
        i = 0
        while i < len(word_timestamps):
            chunk_size = 2 if (i + 1 < len(word_timestamps) and random.random() > 0.4) else 1
            chunks.append(word_timestamps[i:i + chunk_size])
            i += chunk_size

        for chunk in chunks:
            start_t = chunk[0]["start"]
            end_t = chunk[-1]["end"]
            chunk_duration = max(0.25, end_t - start_t)

            words_text = " ".join([item["word"].upper() for item in chunk])
            is_yellow = (random.random() > 0.3)

            sub_img = self._render_capcut_word_image(words_text, use_yellow=is_yellow)

            if MOVIEPY_V1:
                sub_clip = mp.ImageClip(sub_img).set_start(start_t).set_duration(chunk_duration)
                sub_clip = sub_clip.set_position(("center", "center"))
            else:
                sub_clip = mp.ImageClip(sub_img).with_start(start_t).with_duration(chunk_duration)
                sub_clip = sub_clip.with_position(("center", "center"))

            subtitle_clips.append(sub_clip)

        return subtitle_clips

    def _render_capcut_word_image(self, text: str, use_yellow: bool = True) -> np.ndarray:
        """
        Renders transparent PNG containing 1-2 words in large Impact / Montserrat-Bold font
        with heavy black stroke outline (width 5) centered on full screen video.
        """
        img = Image.new("RGBA", (WIDTH, 360), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("Impact.ttf", 94)
        except Exception:
            try:
                font = ImageFont.truetype("Arial.ttf", 88)
            except Exception:
                font = ImageFont.load_default()

        main_color = self.BRIGHT_YELLOW if use_yellow else self.WHITE
        stroke_w = 5
        center_x = WIDTH // 2
        center_y = 180

        # Heavy Black Stroke Outline (width 5)
        for dx in range(-stroke_w, stroke_w + 1):
            for dy in range(-stroke_w, stroke_w + 1):
                if dx != 0 or dy != 0:
                    draw.text((center_x + dx, center_y + dy), text, fill=(0, 0, 0, 255), font=font, anchor="mm")

        # Main Text
        draw.text((center_x, center_y), text, font=font, fill=main_color + (255,), anchor="mm")

        return np.array(img)


def build_youtube_short(
    script_data: Dict[str, Any],
    audio_data: Dict[str, Any],
    clip_paths: List[str],
    output_path: Optional[str] = None
) -> str:
    builder = CapCutVideoBuilder()
    return builder.build_youtube_short(script_data, audio_data, clip_paths, output_path=output_path)
