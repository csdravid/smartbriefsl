# smartbriefsl
SmartBriefs

Smart Briefs is a private, zero-maintenance Streamlit web app for Venture Capitalists.  
Given a startup name (and optional URL), it searches the live web and uses an open‑weights LLM to generate a structured, 1‑page “Cheat Sheet” for founder calls — optimized for mobile Safari.

---

## Features

- **Live Web Intelligence**
  - Uses `duckduckgo-search` (no API key required) to pull fresh web signals.
- **Skeptical VC Dossier**
  - LLM (e.g. `meta-llama/Meta-Llama-3-70B-Instruct`) returns:
    - **Icebreakers** (founder background, trivia, recent non‑funding news)
    - **Traction & Cap Table** (rounds, investors, stage when public)
    - **Bear Case / Red Flags**
    - **Interrogation Questions** (3 sharp questions to test the thesis)
    - **Competitor Radar** (2–3 inferred competitors)
    - **Live Sources** (links to underlying articles)
- **Mobile‑First, iOS‑like Experience**
  - Custom `<meta>` tags for Safari
  - Tight mobile CSS, minimal chrome, 44px+ touch targets
  - Print‑optimized CSS for “Share → Print → Save to Files”.
- **Feedback Loop**
  - Uses `st.feedback("thumbs")` to rate briefs and inform future tuning.

---

## Tech Stack

- **Frontend / Framework**: `streamlit`
- **Search**: `duckduckgo-search`
- **LLM Client**: `openai` Python client (pointed to DeepInfra/Groq–style OpenAI endpoint)
- **Language**: Python 3.9+
