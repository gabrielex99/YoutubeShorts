import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
parent_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(parent_env):
    load_dotenv(parent_env)

# API Keys & Bot Settings (loaded from local .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# AI Video Generation API Keys
HF_TOKEN    = os.getenv("HF_TOKEN", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")



# Text-to-Speech Settings (100% Free Neural Italian Voice)
TTS_VOICE = os.getenv("TTS_VOICE", "it-IT-DiegoNeural")

# Video Rendering Specifications (Vertical 9:16 Shorts/Reels/TikTok)
WIDTH = 1080
HEIGHT = 1920
FPS = 30
MAX_DURATION_SEC = 50  # Global hard ceiling (never exceed 60s to prevent drop-off)

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
ASSETS_CLIPS_DIR = os.path.join(BASE_DIR, "assets", "video_clips")
ASSETS_BACKGROUNDS_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure required directories exist
os.makedirs(ASSETS_AUDIO_DIR, exist_ok=True)
os.makedirs(ASSETS_CLIPS_DIR, exist_ok=True)
os.makedirs(ASSETS_BACKGROUNDS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# High-Retention Niche Definitions with Optimized Word Count & Target Durations
NICHES = {
    "tech_oscura": {
        "name": "Tech Oscura & Siti Segreti",
        "description": "Siti web quasi illegali, trucchi tecnologici segreti, intelligenza artificiale nascosta.",
        "target_duration": "20-30 secondi",
        "word_count_range": "55-75 parole",
        "sample_topics": [
            "3 siti web segreti che sembrano quasi illegali da conoscere nel 2026",
            "Come capire se il tuo telefono è sotto controllo in 10 secondi",
            "L'IA segreta che sblocca funzioni nascoste sul tuo computer"
        ]
    },
    "misteri": {
        "name": "Misteri, Scienza & Fact-Checking Shock",
        "description": "Fatti scientifici assurdi, misteri dello spazio, verità nascoste e fact-checking shock.",
        "target_duration": "25-35 secondi",
        "word_count_range": "65-85 parole",
        "sample_topics": [
            "Cosa succede davvero se ti tuffi in un buco nero per 5 secondi",
            "La scoperta scientifica segreta dell'Oceano che nessuno vuole rivelare",
            "3 fatti di fisica quantistica che faranno dubitare della tua realtà"
        ]
    },
    "storie_oscure": {
        "name": "Mini-Documentari & Storie Oscure",
        "description": "Storie vere scioccanti, truffe storiche, misteri irrisolti di personaggi famosi e tecnologia.",
        "target_duration": "35-50 secondi",
        "word_count_range": "90-120 parole",
        "sample_topics": [
            "La storia oscura del ragazzo che ha truffato Wall Street usando l'IA",
            "L'errore informatico da 500 milioni di dollari che tutti hanno dimenticato",
            "Il mistero dell'hacker scomparso dopo aver violato i server segreti"
        ]
    }
}
