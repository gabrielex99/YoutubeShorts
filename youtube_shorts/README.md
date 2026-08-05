# 🎬 YouTube Shorts AI — Pipeline Automatica per Faceless Video Virali

> Genera 1 video al giorno completamente in automatico: dalla ricerca del trend virale alla consegna su Telegram, pronto da pubblicare.

---

## ✨ Cosa Fa in Automatico

```
🔍 Trova il trend più virale  →  🧠 Scrive lo script con Gemini  →  🎙️ Sintetizza la voce
       ↓
🎬 Genera i video per scena   →  🎞️ Monta il video finale         →  📱 Invia su Telegram
```

**6 step completamente autonomi:**

| Step | Descrizione |
|------|-------------|
| 🔍 **Trend Jacking** | Playwright esplora YouTube e trova il video più virale per nicchia |
| 🧠 **Script Gemini** | Riscrive lo script con Hook psicologico + Retention Architecture (0 copyright) |
| 🎙️ **Voce Neurale** | Edge-TTS italiano (`it-IT-DiegoNeural`) +15% velocità, sincronizzazione audio-video perfetta |
| 🎬 **Video AI** | Scena 1 → HuggingFace Wan AI reale · Scene 2-3 → Ken Burns cinematografico su foto tematiche |
| 🎞️ **Montaggio** | MoviePy: tagli 1.8s, zoom pulse, sottotitoli CapCut word-by-word gialli, musica suspense |
| 📱 **Telegram** | Invia il video MP4 + titolo + caption + orari di pubblicazione ottimali |

---

## 🎯 Nicchie Supportate

| Nicchia | Esempi di contenuti |
|---------|---------------------|
| `storie_oscure` | *"La storia dell'hacker che ha sconvolto i servizi segreti"* · *"La truffa da 300 milioni"* |
| `misteri` | *"Cosa succede se ti tuffi in un buco nero"* · *"Il suono misterioso dagli abissi"* |
| `tech_oscura` | *"3 siti web segreti quasi illegali"* · *"Il codice segreto del tuo smartphone"* |

---

## 🏗️ Architettura

```
youtube_shorts/
├── main.py                  # CLI orchestrator — lancia l'intera pipeline
├── config.py                # API keys, risoluzione 1080×1920, 30fps, nicchie
│
├── viral_scraper.py         # Playwright: trova trend virali e trascrizioni YouTube
├── generator.py             # Gemini: genera script JSON con scene e visual_prompt
│                            #   → angoli narrativi casuali (6 stili)
│                            #   → stili visivi cinematografici (6 palette)
│                            #   → temperatura 0.92 per massima creatività
│
├── tts_engine.py            # Edge-TTS: voce italiana neurale + word timestamps
├── ai_video_fetcher.py      # Engine video a 3 tier (vedi sotto)
├── media_fetcher.py         # Orchestratore: chiama ai_video_fetcher per ogni scena
├── video_builder.py         # MoviePy: monta clip + sottotitoli CapCut + audio mix
│
├── telegram_publisher.py    # Bot Telegram: invia video + kit di pubblicazione
├── transcript_extractor.py  # Estrae transcript da URL YouTube
├── viral_scraper.py         # Scraper Playwright per trend virali globali
│
├── assets/
│   ├── audio/               # Voce sintetizzata + musica background
│   ├── generated_ai_videos/ # Clip video generate per ogni scena
│   └── video_clips/         # Clip locali opzionali (aggiungi le tue!)
│
├── outputs/                 # Video finali pronti per la pubblicazione
└── requirements.txt
```

---

## 🎬 Engine Video — 3 Tier Intelligenti

La strategia usa i crediti AI in modo intelligente, massimizzando qualità e risparmio:

```
Scena 1 (HOOK) ─→ 🤖 HuggingFace Wan AI  (video AI reale 5s — usa ~$0.04 di crediti)
Scena 2        ─→ 📷 Ken Burns su foto tematica (GRATIS — illimitato)
Scena 3        ─→ 📷 Ken Burns su foto tematica (GRATIS — illimitato)
                        ↓ se internet non disponibile
                   🌑 Gradiente cinematografico animato (GRATIS — offline)
```

**Ken Burns Engine** (Tier 2): ogni foto viene animata con:
- Zoom in/out + pan cinematografico (5 preset di movimento)
- Vignette radiale scura
- Color grading (schiaccia i neri, alza il contrasto)
- Film grain 35mm

---

## ⚙️ Setup

### 1. Installa le dipendenze
```bash
cd AI-AGENT
python3 -m venv venv
source venv/bin/activate
pip install -r youtube_shorts/requirements.txt
playwright install chromium
```

### 2. Configura le API Keys nel file `.env`
```env
# Gemini — per la generazione dello script
# Ottieni da: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSy...

# HuggingFace — per video AI reale sulla scena 1 (hook)
# Ottieni GRATIS da: https://huggingface.co → Settings → Access Tokens
HF_TOKEN=hf_...

# Telegram — per ricevere il video pronto
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

> **Note sui crediti HuggingFace:**
> - Piano free: ~$0.10/mese → ~2-3 giorni di hook AI
> - Aggiungendo $1/mese → 25 giorni di hook AI
> - Costo per video: ~$0.04 (solo scena 1, le altre sono gratuite)

---

## 🚀 Utilizzo

```bash
# Genera 1 Short per la nicchia "Storie Oscure"
python -m youtube_shorts.main --niche storie_oscure

# Genera per "Misteri & Scienza"
python -m youtube_shorts.main --niche misteri

# Genera per "Tech Oscura"
python -m youtube_shorts.main --niche tech_oscura

# Auto-viral: trova automaticamente il trend più virale del momento
python -m youtube_shorts.main --auto-viral

# Argomento personalizzato
python -m youtube_shorts.main --topic "Il mistero del satellite scomparso nel 1990"

# Test senza API (usa fallback locali)
python -m youtube_shorts.main --niche storie_oscure --dry-run --no-telegram
```

---

## 📊 Output Tipico

```
⚡ CAPCUT-STYLE AUTONOMOUS SHORTS PIPELINE
═══════════════════════════════════════════════════════════════
• Nicchia:           Mini-Documentari & Storie Oscure
• Titolo Short:      "La storia oscura dell'hacker da 500 milioni"
• Durata Effettiva:  17.6s (Audio-Video Sync Perfetto)
• Output Video MP4:  youtube_shorts/outputs/output_viral_short.mp4
• Stile Montaggio:   CapCut 9:16 (Tagli 1.8s + Zoom Pulse)
• Motore Vocale:     Edge-TTS it-IT-DiegoNeural (+15% Rate)
• Telegram Status:   sent
• Tempo Esecuzione:  ~90 secondi
═══════════════════════════════════════════════════════════════
```

---

## 💰 Costo Operativo Stimato

| Componente | Costo |
|-----------|-------|
| Script Gemini | Gratis (1500 req/giorno con chiave AIza) |
| Voce Edge-TTS | **Gratis** (illimitato) |
| Video Hook (HF Wan) | ~$0.04/video |
| Video Ken Burns | **Gratis** (illimitato) |
| Montaggio MoviePy | **Gratis** (locale) |
| Telegram | **Gratis** |
| **Totale/mese** | **~$1.20** (30 video) |

---

## 🛠️ Requisiti

- Python 3.9+
- `imageio-ffmpeg` (bundled — nessun ffmpeg di sistema richiesto)
- macOS / Linux
- Connessione internet (per HF, Gemini, Edge-TTS, Telegram)
