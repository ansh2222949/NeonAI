🚀 NeonAI — Local-First Multi-Mode AI System (Experimental)

NeonAI is a local-first AI system designed to run primarily on your own machine using a local LLM pipeline, with optional and controlled internet access for selected features.

What started as an experiment gradually evolved into a complete AI system architecture with multiple operational modes, strict behavior control, and a premium custom UI.

⚠️ This is not a chatbot wrapper.
NeonAI is an AI system with modes, rules, confidence gates, memory, and decision pipelines.

✨ Core Philosophy

🧠 Local LLM First — No mandatory cloud LLM APIs

🔒 Privacy-Focused — Data stays on the user’s machine

🎯 Mode-Driven Intelligence — AI behavior depends on context

🧪 Experimental by Design — Built to explore system ideas

🧩 System > Model — The LLM is a tool, not the decision-maker

🧠 What Is NeonAI?

NeonAI is a multi-mode AI assistant that can switch between different roles, each with its own rules and permissions.

Mode	Purpose
NEON CASUAL	General chat using a local LLM with memory
NEON MOVIES	Movie discovery, recommendations & metadata
NEON STUDY	PDF-based syllabus learning (strict offline, no hallucinations)

Each mode enforces different constraints, memory usage, and access permissions.

🧱 System Architecture (High-Level)
User
 ↓
Frontend UI (HTML / CSS / JS)
 ↓
Flask Backend (server.py)
 ↓
Brain Layer
 ↓
Waterfall Decision Logic
 ↓
Confidence Gate + Mode Rules
 ↓
Local LLM


Key principle:
The LLM never directly decides responses.
All outputs pass through rules, confidence checks, and mode restrictions.

🖥️ Frontend (UI)

Pure HTML, CSS, JavaScript (no frameworks)

GSAP-powered animations

10+ neon themes + Light / Dark mode

Physics-based Liquid Toggle

Fully responsive (Desktop + Mobile)

📌 Static vs Templates (Important)

templates/

Contains UI files (index.html, styles.css, app.js)

Served via Flask for controlled rendering

static/

Used only for static assets

Currently stores user-uploaded wallpapers

The frontend is not an SPA.
It is a controlled UI panel, intentionally simple and stable.

🎬 NEON MOVIES Mode

Displays trending movies

Uses TMDB API (optional)

Auto-scroll carousel with hover/touch pause

Learns user genre preferences

Offline fallback using a local movie database

📚 NEON STUDY (Exam Mode)

RAG Pipeline

Upload a PDF syllabus

Index content locally using a vector database

Strict Rule

If the answer is not present in the PDF → the AI refuses

Internet access is completely blocked in this mode

Designed for exam-safe, hallucination-free learning.

🧠 Local LLM (Important)

NeonAI does not depend on cloud LLM APIs.

Powered by local models (via Ollama)

Fully offline capable

Internet access is optional and gated

External APIs never override system rules

📂 Project Structure (Accurate)
NeonAI/
│
├── server.py              # Flask backend (API + routing)
├── START_NEON.bat         # One-click launcher (Windows)
│
├── brain/                 # Core AI system logic
│   ├── waterfall.py       # Decision flow & routing
│   ├── confidence_gate.py # Confidence & hallucination control
│   ├── memory.py          # Session & long-term memory
│   └── gk_engine.py       # Knowledge & reasoning engine
│
├── models/                # LLM abstraction layer
│   ├── local_llm.py       # Local LLM interface (offline-first)
│   └── hybrid_llm.py      # Local + optional online logic
│
├── exam/                  # NEON STUDY (Exam Mode)
│   ├── indexer.py         # PDF indexing
│   └── retriever.py       # Strict PDF-only retrieval
│
├── movie/                 # NEON MOVIES engine
│   ├── engine.py          # Recommendation logic
│   └── lookup.py          # Movie metadata
│
├── scripts/
│   └── movie_updater.py   # Local movie DB updater
│
├── web/                   # Controlled web adapters
│   ├── search_adapter.py  # Optional web search
│   └── movie_adapter.py   # TMDB logic
│
├── utils/                 # Shared utilities
│   ├── network.py         # Network helpers
│   └── movie_db.py        # Local movie database helpers
│
├── templates/             # Frontend UI (served by Flask)
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── static/
│   └── wallpapers/        # User-uploaded wallpapers
│
└── user_data/
    └── profile.json       # Local user profile & preferences

▶️ How to Run (Windows)
1️⃣ Requirements

Python 3.10+

Local LLM runtime (e.g. Ollama)

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Start NeonAI

Double-click START_NEON.bat
or

python server.py


Open:

http://localhost:5000

🧪 Project Status

✅ Core system functional

✅ UI stable & responsive

✅ Multi-mode logic working

⚠️ Experimental (architecture locked for iteration)

⚠️ Disclaimer

This is an experimental project built for learning, research, and AI system design exploration.
It is not a commercial product.

🧠 Author

Ansh
B.Tech CSE

Focus Areas

AI Systems (not just models)

Offline-first architecture

Controlled & human-aligned AI design

NeonAI is not about how smart the model is.
It’s about how controlled, safe, and purposeful AI should be.