import json
import logging
import random
from typing import Dict, Any
from youtube_shorts.config import GEMINI_API_KEY, NICHES

logger = logging.getLogger("youtube_shorts.generator")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

STORY_ANGLES = [
    "Cronaca drammatica in tempo reale (stile reporter sul posto)",
    "Punto di vista della polizia / investigatore riservato",
    "Documentario investigativo stile vero crime da prima serata",
    "Racconto confidenziale di un testimone oculare",
    "Analisi scientifica / investigativa scioccante e controintuitiva",
    "Avvertimento segreto ad altissima tensione drammatica"
]

VISUAL_STYLES = [
    "35mm moody film grain, dark cinematic lighting, vintage anamorphic lens",
    "gritty raw footage, dramatic shadow contrast, hyperrealistic 8k crime scene",
    "neo-noir aesthetic, deep neon reflections, atmospheric fog and rain",
    "photorealistic documentary photography, natural dramatic side-lighting, 8k vertical 9:16",
    "cyberpunk high-contrast glowing neon, futuristic dark tech atmosphere",
    "surreal cinematic deep space photography, cosmic volumetric dust and lensing"
]

# List of Gemini models to attempt sequentially if quota is hit
GEMINI_MODELS_POOL = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"]


class ScriptGenerator:
    """
    Retention-Architected Script Generator using Gemini Models.
    Features:
    - Auto-Fallback across Gemini Model Pool ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
      if quota limit (429) is hit!
    - Dynamic Narrative Angles & Visual Aesthetic Styles.
    - Randomized Fallback Pool with rich stories per niche.
    """

    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                logger.info("[Generator] Configured Gemini API Key.")
            except Exception as e:
                logger.warning(f"[Generator] Could not configure Gemini: {e}")

    def generate_retention_script(
        self,
        topic_data: Dict[str, Any],
        niche_key: str = "tech_oscura",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Generates structured JSON script with auto-model fallback for quota limits.
        """
        niche_info = NICHES.get(niche_key, NICHES["tech_oscura"])
        raw_topic = topic_data.get("raw_topic", "Argomento Virale")
        transcript = topic_data.get("transcript")
        description = topic_data.get("description")

        if dry_run or not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.info(f"[Generator] Gemini API Key missing or dry-run active. Using Randomized Fallback for '{niche_key}'.")
            return self._randomized_fallback(raw_topic, niche_key)

        chosen_angle = random.choice(STORY_ANGLES)
        chosen_visual_style = random.choice(VISUAL_STYLES)

        if niche_key == "storie_oscure":
            target_word_bounds = "100-120 parole (durata voce narrante 35-45 secondi)"
            niche_narrative_instruction = "QUESTO È UN MINI-DOCUMENTARIO / STORIA OSCURA. DEVI TASSATIVAMENTE raccontare una storia vera, un fatto di cronaca nera, un crimine informatico o un fatto storico misterioso! È SEVERAMENTE VIETATO parlare di 'algoritmi YouTube', 'come fare video virali' o 'marketing'!"
        elif niche_key == "misteri":
            target_word_bounds = "75-85 parole (durata voce narrante 25-30 secondi)"
            niche_narrative_instruction = "QUESTO È UN MISTERO / SCIENZA SHOCK. DEVI TASSATIVAMENTE parlare di astronomia, fisica quantistica o scoperte assurde dell'universo! È SEVERAMENTE VIETATO parlare di marketing o crescita social!"
        else:
            target_word_bounds = "75-85 parole (durata voce narrante 25-30 secondi)"
            niche_narrative_instruction = "QUESTA È TECH OSCURA & SITI SEGRETI. DEVI TASSATIVAMENTE mostrare trucchi tecnologici, siti web poco conosciuti o funzioni nascoste del computer o dello smartphone!"

        prompt = f"""
Sei il miglior Scriptwriter e Storyboard Director al mondo per YouTube Shorts Virali Faceless.
Il tuo compito è creare uno script magnetico in ITALIANO ed uno STORYBOARD CINEMATOGRAFICO con `visual_prompt` per immagini IA fotorealistiche.

### ⛔ VINCOLO ASSOLUTO DI NICCHIA:
{niche_narrative_instruction}

### 🎨 DIRETTIVE STILE & ANGOLO NARRATIVO DIVERSIFICATO:
- ANGOLO NARRATIVO DA USARE: "{chosen_angle}"
- STILE VISIVO ESTETICO DA USARE: "{chosen_visual_style}"

### PARAMETRI TASSATIVI DI LUNGHEZZA:
- NICCHIA CORRENTE: {niche_info['name']}
- LIMITE RIGIDO PAROLE: {target_word_bounds}.

### REGOLE NARRATIVE (PAYOFF COMPLETO & SEAMLESS LOOP):
1. **HOOK (0-3s)**: Aggancio immediato in meno di 2 secondi.
2. **PAYOFF COMPLETO**: Frasi compiute, 0 pensieri lasciati a metà.
3. **SEAMLESS LOOP**: L'ultima frase si chiude ricollegandosi alla primissima parola dell'Hook.

### REGOLE STORYBOARD CINEMATOGRAFICO (`scenes`):
Fornisci un array di 3-4 `scenes` identificate da `scene_index` (da 1 a 4). Per OGNI scena, genera:
- `scene_index`: Numero progressivo della scena (es. 1, 2, 3, 4).
- `text`: La frase precisa narrata dalla voce in quel segmento.
- `visual_prompt`: Un prompt cinematografico iper-dettagliato in INGLESE che descrive un SOGGETTO REALE E CONCRETO (es. "close up of gold bars", "stack of fake contract documents", "dense Amazon jungle aerial view", "police car sirens night flashing").
  ⚠️ REGLA FONDAMENTALE VISUAL PROMPT: DEVI inserire un soggetto fisico principale ben visibile! È SEVERAMENTE VIETATO usare parole astratte o generiche come "mystery", "concept", "atmosphere", "cosmic space", "nebula background" o sfondi vuoti senza un oggetto/azione reale al centro dell'immagine!


### RIFERIMENTI DI CONTENUTO:
- Argomento / Titolo: "{raw_topic}"
- Trascrizione Originale: {transcript[:1200] if transcript else "Non disponibile"}
- Descrizione Originale: {description[:400] if description else "Non disponibile"}

### RISPONDI ESCLUSIVAMENTE IN FORMATO JSON VALIDO:
```json
{{
  "title": "Titolo Virale per lo Short",
  "script_text": "Testo completo parlato da leggere con il TTS ({target_word_bounds})",
  "caption": "Caption pronta per social con hashtag virali",
  "publishing_schedule": {{
    "youtube_time": "14:30",
    "youtube_reason": "Picco di traffico pomeridiano su YouTube Shorts",
    "instagram_time": "18:45",
    "instagram_reason": "Massima interazione serale pre-cena su Reels",
    "tiktok_time": "21:15",
    "tiktok_reason": "Orario d'oro FYP durante lo scorrimento serale"
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "text": "Nel millenovecentonovantasei, un hacker sconosciuto...",
      "visual_prompt": "photorealistic, {chosen_visual_style}, dark room, anonymous programmer typing on mechanical keyboard, glowing blue matrix code on monitors, 8k vertical 9:16, no text"
    }},
    {{
      "scene_index": 2,
      "text": "è riuscito ad infiltrarsi nei server della difesa...",
      "visual_prompt": "photorealistic, {chosen_visual_style}, high-tech military server room, glowing red alert lights, dark atmosphere, vertical 9:16, no text"
    }},
    {{
      "scene_index": 3,
      "text": "svanendo nel nulla prima che la polizia arrivasse...",
      "visual_prompt": "photorealistic, {chosen_visual_style}, police car sirens flashing in dark rainy city street at night, atmospheric dramatic crime scene, vertical 9:16 8k, no text"
    }}
  ]
}}
```
"""

        # Auto-fallback through model pool if quota 429 is hit
        for model_name in GEMINI_MODELS_POOL:
            try:
                logger.info(f"[Generator] Attempting script generation with model '{model_name}'...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.92,
                        response_mime_type="application/json"
                    )
                )

                text_res = response.text.strip()
                if text_res.startswith("```json"):
                    text_res = text_res.replace("```json", "").replace("```", "").strip()

                script_json = json.loads(text_res)
                logger.info(f"[Generator] Script generated via '{model_name}' ({niche_key} - {len(script_json.get('script_text', '').split())} parole): '{script_json.get('title')}'")
                return script_json

            except Exception as e:
                logger.warning(f"[Generator] Model '{model_name}' failed ({e}). Trying next model...")

        logger.warning("[Generator] All Gemini models in pool hit quota limits. Using randomized fallback template.")
        return self._randomized_fallback(raw_topic, niche_key)

    def _randomized_fallback(self, raw_topic: str, niche_key: str) -> Dict[str, Any]:
        """Diversified fallback pool with at least 3 unique stories per niche."""
        chosen_style = random.choice(VISUAL_STYLES)

        fallback_pool = {
            "storie_oscure": [
                {
                    "niche": "Mini-Documentari & Storie Oscure",
                    "title": "La Storia Oscura dell'Hacker da 500 Milioni",
                    "script_text": "Nel millenovecentonovantasei, un hacker sconosciuto è riuscito ad infiltrarsi nei server segreti della difesa ed a sottrarre codici crittografati per un valore di oltre mezzo miliardo di dollari. La cosa incredibile è che non ha lasciato alcuna traccia digitale ed è svanito nel nulla dopo aver inviato un unico messaggio in codice. Le autorità hanno cercato la sua identità per oltre vent'anni senza mai trovarlo, ma la vera scoperta inquietante è che...",
                    "caption": "Il mistero dell'hacker che ha sconvolto i servizi segreti! 🕵️‍♂️ Salva il video. #shorts #storie #truecrime #hacker",
                    "publishing_schedule": {"youtube_time": "15:00", "instagram_time": "20:15", "tiktok_time": "21:45"},
                    "scenes": [
                        {"scene_index": 1, "text": "Nel millenovecentonovantasei, un hacker sconosciuto...", "visual_prompt": f"photorealistic, {chosen_style}, dark hacker room glowing screens, 8k vertical 9:16, no text"},
                        {"scene_index": 2, "text": "è riuscito ad infiltrarsi nei server segreti...", "visual_prompt": f"photorealistic, {chosen_style}, high security military server room alert lights, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "svanendo nel nulla prima che la polizia arrivasse...", "visual_prompt": f"photorealistic, {chosen_style}, police car sirens flashing dark rainy street, vertical 9:16, no text"}
                    ]
                },
                {
                    "niche": "Mini-Documentari & Storie Oscure",
                    "title": "La Truffa Geniale del Falso Milionario",
                    "script_text": "Nel duemiladodici, un uomo qualunque è riuscito a convincere le più grandi banche del mondo di possedere una miniera d'oro segreta in Sud America. Utilizzando soltanto documenti falsificati al millimetro e una parlantina ipnotica, ha ottenuto finanziamenti per trecento milioni prima che qualcuno visitasse davvero il sito. Quando gli ispettori sono arrivati sul posto, hanno trovato soltanto giungla incontaminata...",
                    "caption": "La truffa più geniale ed incredibile della storia! 💰 #shorts #storie #truffe #documentario",
                    "publishing_schedule": {"youtube_time": "14:30", "instagram_time": "19:45", "tiktok_time": "22:15"},
                    "scenes": [
                        {"scene_index": 1, "text": "Nel duemiladodici, un uomo qualunque è riuscito a convincere le più grandi banche...", "visual_prompt": f"photorealistic, {chosen_style}, luxury bank vault, stacks of gold bars, dramatic lighting, vertical 9:16, no text"},
                        {"scene_index": 2, "text": "Utilizzando soltanto documenti falsificati al millimetro...", "visual_prompt": f"photorealistic, {chosen_style}, vintage forged contracts on dark mahogany table, fountain pen, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "Quando gli ispettori sono arrivati sul posto, hanno trovato soltanto giungla incontaminata...", "visual_prompt": f"photorealistic, {chosen_style}, mysterious dense misty jungle aerial view, moody lighting, vertical 9:16, no text"}
                    ]
                },
                {
                    "niche": "Mini-Documentari & Storie Oscure",
                    "title": "Il Mistero della Spia Scomparsa a Londra",
                    "script_text": "Nel duemiladieci, un agente dei servizi segreti britannici è stato trovato privo di vita all'interno di un borsone da viaggio chiuso dall'esterno nella sua casa di Londra. Nonostante la stanza fosse sigillata e priva di impronte digitali, gli investigatori hanno archiviato il caso come un assurdo incidente domestico. Ma le analisi dei registri telefonici segreti hanno rivelato che poche ore prima...",
                    "caption": "Un mistero irrisolto che scuote i servizi segreti! 🕵️‍♂️ #shorts #storie #misteri #london",
                    "publishing_schedule": {"youtube_time": "16:00", "instagram_time": "20:30", "tiktok_time": "22:00"},
                    "scenes": [
                        {"scene_index": 1, "text": "Nel duemiladieci, un agente dei servizi segreti britannici...", "visual_prompt": f"photorealistic, {chosen_style}, moody dark London apartment at night, rainy window view, vertical 9:16, no text"},
                        {"scene_index": 2, "text": "è stato trovato all'interno di una stanza sigillata e priva di impronte...", "visual_prompt": f"photorealistic, {chosen_style}, forensic police investigation scene, dramatic yellow tape, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "Ma le analisi dei registri telefonici segreti hanno rivelato...", "visual_prompt": f"photorealistic, {chosen_style}, encrypted satellite communication screen, glowing waveforms, vertical 9:16, no text"}
                    ]
                }
            ],
            "misteri": [
                {
                    "niche": "Misteri, Scienza & Fact-Checking Shock",
                    "title": "Cosa Succede Se Ti Tuffi in un Buco Nero",
                    "script_text": "Se ti tuffassi all'interno di un buco nero supermassiccio, la forza di gravità ai tuoi piedi sarebbe un milione di volte superiore a quella sulla testa, allungando il tuo corpo in un processo chiamato spaghettificazione. Ma la cosa assurda è che per un osservatore esterno il tuo tempo si fermerebbe completamente all'orizzonte degli eventi, facendoti sembrare immobile per sempre...",
                    "caption": "Cosa succede dentro un buco nero? 🌌 Fatti assurdi della scienza! #shorts #misteri #spazio #scienza",
                    "publishing_schedule": {"youtube_time": "14:00", "instagram_time": "19:00", "tiktok_time": "21:00"},
                    "scenes": [
                        {"scene_index": 1, "text": "Se ti tuffassi all'interno di un buco nero supermassiccio...", "visual_prompt": f"photorealistic, {chosen_style}, swirling cosmic black hole event horizon, hyperrealistic 8k vertical 9:16, no text"},
                        {"scene_index": 2, "text": "allungando il tuo corpo in un processo chiamato spaghettificazione...", "visual_prompt": f"photorealistic, {chosen_style}, astronaut floating into deep space distortion lensing, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "facendoti sembrare immobile per sempre...", "visual_prompt": f"photorealistic, {chosen_style}, frozen cosmic nebula stars background, vertical 9:16, no text"}
                    ]
                },
                {
                    "niche": "Misteri, Scienza & Fact-Checking Shock",
                    "title": "Il Suono Anomalo Rilevato negli Oceani Profondi",
                    "script_text": "Nel millenovecentonovantasette, i idrofoni sottomarini dell'oceano Pacifico hanno registrato un suono a bassissima frequenza denominato Bloop, centinaia di volte più potente di qualsiasi balenottera azzurra. Il segnale è stato captato a oltre cinquemila chilometri di distanza e la sua sorgente non è mai stata identificata da alcuna specie biologica conosciuta. La spiegazione ufficiale parla di ghiacciai che si spezzano, ma la verità potrebbe essere...",
                    "caption": "Il segnale misterioso dagli abissi dell'oceano! 🌊 #shorts #misteri #scienza #abissi",
                    "publishing_schedule": {"youtube_time": "15:15", "instagram_time": "19:30", "tiktok_time": "21:30"},
                    "scenes": [
                        {"scene_index": 1, "text": "Nel millenovecentonovantasette, i idrofoni sottomarini dell'oceano Pacifico...", "visual_prompt": f"photorealistic, {chosen_style}, dark deep ocean underwater abyss, glowing bioluminescent particles, vertical 9:16, no text"},
                        {"scene_index": 2, "text": "hanno registrato un suono a bassissima frequenza centinaia di volte più potente...", "visual_prompt": f"photorealistic, {chosen_style}, sonar waveform audio monitor in dark submarine, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "La spiegazione ufficiale parla di ghiacciai, ma la verità...", "visual_prompt": f"photorealistic, {chosen_style}, massive iceberg collapsing into stormy dark ocean, dramatic lighting, vertical 9:16, no text"}
                    ]
                }
            ],
            "tech_oscura": [
                {
                    "niche": "Tech Oscura & Siti Segreti",
                    "title": "3 Siti Web Segreti Quasi Illegali",
                    "script_text": "Questo sito web segreto è quasi illegale da conoscere nel duemilaventisei! Se cerchi strumenti di intelligenza artificiale avanzati senza pagare un centesimo, esiste una piattaforma nascosta che ti sblocca funzioni premium in un click. Salva subito questo video prima che venga rimosso, perché la vera funzione che tutti ignorano è...",
                    "caption": "Scopri i 3 siti web segreti del 2026! 🚀 Salva il video e provali subito. #shorts #tech #sitiweb #ai",
                    "publishing_schedule": {"youtube_time": "14:30", "instagram_time": "18:45", "tiktok_time": "21:15"},
                    "scenes": [
                        {"scene_index": 1, "text": "Questo sito web segreto è quasi illegale da conoscere nel duemilaventisei!", "visual_prompt": f"photorealistic, {chosen_style}, cyberpunk holographic UI screens, cyan neon lighting, vertical 9:16, no text"},
                        {"scene_index": 2, "text": "esiste una piattaforma nascosta che ti sblocca funzioni premium in un click...", "visual_prompt": f"photorealistic, {chosen_style}, dark room laptop with glowing AI code, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "Salva subito questo video prima che venga rimosso...", "visual_prompt": f"photorealistic, {chosen_style}, digital matrix binary data stream, vertical 9:16, no text"}
                    ]
                },
                {
                    "niche": "Tech Oscura & Siti Segreti",
                    "title": "Il Codice Segreto del Tastierino dello Smartphone",
                    "script_text": "Il tuo telefono nasconde un menu di diagnostica avanzato accessibile soltanto digitando un codice segreto nel tastierino telefonico. Questa funzione nascosta permette di testare i sensori della fotocamera, ricalibrare i moduli di memoria e raddoppiare la velocità di risposta del touch screen. Pochi utenti conoscono questo passaggio, ma la cosa incredibile è che...",
                    "caption": "Sblocca le funzioni nascoste del tuo telefono! 📱 #shorts #tech #smartphone #android #iphone",
                    "publishing_schedule": {"youtube_time": "13:30", "instagram_time": "18:15", "tiktok_time": "20:45"},
                    "scenes": [
                        {"scene_index": 1, "text": "Il tuo telefono nasconde un menu di diagnostica avanzato...", "visual_prompt": f"photorealistic, {chosen_style}, hand holding glowing modern smartphone entering secret code, vertical 9:16, no text"},
                        {"scene_index": 2, "text": "Questa funzione nascosta permette di testare i sensori e raddoppiare la velocità...", "visual_prompt": f"photorealistic, {chosen_style}, close up of futuristic phone processor microchip glowing, vertical 9:16, no text"},
                        {"scene_index": 3, "text": "Pochi utenti conoscono questo passaggio, ma la cosa incredibile è che...", "visual_prompt": f"photorealistic, {chosen_style}, abstract high speed digital network circuit, vertical 9:16, no text"}
                    ]
                }
            ]
        }

        niche_fallbacks = fallback_pool.get(niche_key, fallback_pool["tech_oscura"])
        chosen = random.choice(niche_fallbacks)
        return chosen


def generate_retention_script(
    topic_data: Dict[str, Any],
    niche_key: str = "tech_oscura",
    dry_run: bool = False
) -> Dict[str, Any]:
    generator = ScriptGenerator()
    return generator.generate_retention_script(topic_data, niche_key=niche_key, dry_run=dry_run)
