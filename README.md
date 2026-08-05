# ⚡ Faceless Video Automation & Growth Suite (`youtube_shorts`)

Piattaforma autonoma di **Trend-Jacking, Generazione Script ad Alta Ritenzione, Sintesi Vocale Neurale, Montaggio Video CapCut-Style (9:16 Full Screen) ed Invio Telegram** per canali Faceless su **YouTube Shorts, Instagram Reels e TikTok**.

---

## 🌟 Caratteristiche Principali

### 🤖 1. Playwright Autonomous Trend-Jacking Engine (`viral_scraper.py`)
- Scansiona YouTube Shorts in tempo reale via **Playwright (headless Chromium)**.
- Ordina i risultati per **conteggio visualizzazioni (`&sp=CAM%253D`)**.
- Seleziona in autonomia il **#1 video più virale del giorno** o un trend ad alto rendimento.
- **🚫 Filtro Anti-Musica & Anti-Copyright**: Esclude accuratamente brani musicali, VEVO, concerti, remix e contenuti coperti da copyright per garantire la monetizzazione al 100%.

### 🧠 2. Riscrittura Gemini 1.5 Pro ad Altissima Ritenzione (`generator.py`)
- Analizza trascrizioni e metadati dei video virali ricavati da `transcript_extractor.py`.
- Genera uno script **100% originale in italiano** in formato JSON (0 violazioni o contenuti duplicati).
- Rispetta **limiti rigidi di parole e durate** per ogni nicchia:
  - ⚡ **`tech_oscura`** (Tech Oscura & Siti Segreti): 20–30 secondi (55–75 parole)
  - 🌌 **`misteri`** (Misteri, Scienza & Fact-Checking): 25–35 secondi (65–85 parole)
  - 📜 **`storie_oscure`** (Mini-Documentari & Storie): 35–50 secondi (90–120 parole)
- **Seamless Loop Architecture**: La frase finale si ricollega grammaticalmente alla prima parola del video per creare un loop infinito e spingere il *Completion Rate* sopra il 100%.

### 🎙️ 3. Voce Neurale Italiana (+15% Rate Boost) (`tts_engine.py`)
- Sintesi vocale Gratuita `edge-tts` (`it-IT-DiegoNeural`).
- **Accelerazione +15% (`rate='+15%'`)** per mantenere un ritmo incalzante e virale.
- Calcolo automatico dei timbri parola per parola (`SubMaker`) per l'animazione dei sottotitoli.

### 🎬 4. Montaggio CapCut 9:16 Full Screen (`video_builder.py` & `media_fetcher.py`)
- **Visuale 100% Full Screen 1080x1920 HD**: Nessuna cornice, canvas o forma vettoriale procedurale (divieto assoluto di schermate nere).
- **Libreria Clip Video Utente (`assets/video_clips/`)**: Utilizza in via prioritaria le clip MP4 reali presenti nella cartella `assets/video_clips/`.
- **Libreria Sfondi di Riserva (`assets/backgrounds/`)**: Mantiene in locale sfondi dinamici 4K (Cyberpunk, Sci-Fi, Minecraft Parkour, Satisfying ASMR).
- **Tagli Rapidi (1.8s) + Zoom Pulse (100% ➔ 108%)**: Animazione continua della camera per massima stimolazione dopaminergica.
- **Sottotitoli Cinetici Centrati**: 1-2 parole alla volta in grande al centro dello schermo, font Impact/Montserrat, colore Giallo/Bianco, contorno nero marcato (`stroke_width=5`).
- **Audio Mix Suspense (15% Vol)**: Miscelazione automatica della voce narrante con traccia musicale di sottofondo suspense/dark.

### 📱 5. Dispatch Telegram con Scheda Orari IA (`telegram_publisher.py`)
- Invia il video MP4 renderizzato direttamente al tuo Bot Telegram.
- **Scheda Orari IA Multi-Piattaforma**: Genera gli orari ideali di pubblicazione calcolati dall'Intelligenza Artificiale per l'algoritmo di:
  - 📺 **YouTube Shorts** (es. `14:30`)
  - 📸 **Instagram Reels** (es. `18:45`)
  - 🎵 **TikTok** (es. `21:15`)
- **Messaggio Pronto da Copiare**: Formattato in blocchi `<code>` per essere copiato ed incollato al volo sui social con un singolo tocco.

---

## 📁 Struttura del Progetto

```text
AI-AGENT/
├── youtube_shorts/
│   ├── assets/
│   │   ├── audio/           # Tracce voce MP3 e sottofondo musicale bg_music.mp3
│   │   ├── backgrounds/     # Libreria sfondi verticali 4K (bg_1.mp4, bg_2.mp4...)
│   │   └── video_clips/     # Clip video MP4 caricate dall'utente (Fonte Principale)
│   ├── outputs/             # Video MP4 finali renderizzati pronti per social
│   ├── config.py            # Impostazioni, nicchie, durate target e credenziali
│   ├── viral_scraper.py     # Scraper Playwright per trend virali YouTube & filtri 
│   ├── transcript_extractor.py # Estrattore metadati e trascrizioni YouTube
│   ├── generator.py         # Motore Gemini 1.5 Pro per script JSON & orari IA
│   ├── tts_engine.py        # Sintesi vocale Edge-TTS (+15% rate)
│   ├── media_fetcher.py     # Gestore e downloader delle clip video reali
│   ├── video_builder.py     # Renderizzatore video 9:16 CapCut-Style con MoviePy
│   ├── telegram_publisher.py# Bot Telegram per invio video e kit di pubblicazione
│   └── main.py              # Launcher CLI del progetto
├── techhacks-growth/        # Dashboard React per monitoraggio visualizzazioni
├── README.md                # Documentazione del progetto
└── .env                     # Chiavi API (Gemini, Telegram Bot Token, Chat ID)
```

---

## 🚀 Guida all'Installazione

### 1. Clona la repository ed entra nella cartella
```bash
git clone <URL_REPO>
cd AI-AGENT
```

### 2. Configura l'ambiente virtuale Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r youtube_shorts/requirements.txt
python -m playwright install chromium
```

### 3. Configura il file `.env`
Crea o aggiorna il file `.env` nella root del progetto:
```env
GEMINI_API_KEY=LaTuaChiaveGeminiAPI
TELEGRAM_BOT_TOKEN=IlTuoTokenBotTelegram
TELEGRAM_CHAT_ID=IlTuoChatIDTelegram
```

---

## 💻 Esempi di Esecuzione (CLI)

### 1. Trend-Jacking 100% Autonomo (Scansione Globale YouTube):
L'agente cercherà il video #1 più visto su YouTube in assoluto, ne rileverà la nicchia, estrarrà la trascrizione ed invierà lo Short finito su Telegram con gli orari IA:
```bash
./venv/bin/python3 youtube_shorts/main.py --auto-viral
```

### 2. Trend-Jacking da una Nicchia Specifica:
```bash
./venv/bin/python3 youtube_shorts/main.py --niche tech_oscura --auto-viral
```

### 3. Genera uno Short da un URL YouTube Specifico:
```bash
./venv/bin/python3 youtube_shorts/main.py --niche storie_oscure --topic "https://www.youtube.com/watch?v=VIDEO_ID_VIRALE"
```

### 4. Genera uno Short da un Argomento Personalizzato:
```bash
./venv/bin/python3 youtube_shorts/main.py --niche misteri --topic "Cosa succede se ti tuffi in un buco nero"
```

---

## 📊 Canali Ufficiali Collegati

- **YouTube Shorts**: `https://www.youtube.com/@techhacks_aii`
- **Instagram Reels**: `https://www.instagram.com/techs_ai1/`
- **Facebook Reels**: `https://www.facebook.com/techhacks.ai`
- **TikTok**: `https://www.tiktok.com/@techhacks.ai`
