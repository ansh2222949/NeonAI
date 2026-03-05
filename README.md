<div align="center">

  <img src="https://img.shields.io/badge/-%E2%9A%A1_NeonAI_V5-000?style=for-the-badge&labelColor=000&color=00ffc8" alt="NeonAI V5" height="40">

  <br><br>

  <h3>⚡ Local-First AI System with Voice Assistant & Tool Calling</h3>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Flask-Backend-000?style=flat-square&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Ollama-LLM-f97316?style=flat-square" alt="Ollama">
    <img src="https://img.shields.io/badge/Whisper-STT-0ea5e9?style=flat-square" alt="Whisper">
    <img src="https://img.shields.io/badge/GPT--SoVITS-TTS-a855f7?style=flat-square" alt="TTS">
    <img src="https://img.shields.io/badge/Offline_First-✓-22c55e?style=flat-square" alt="Offline">
  </p>

  <p><b>Mode-Driven Intelligence • Voice Assistant • Tool Calling • Privacy Focused</b></p>

  <br>

  <img width="1916" height="945" alt="NeonAI Screenshot" src="https://github.com/user-attachments/assets/ffe4d47e-c869-4e87-8715-db17f9ada04d" />

</div>

<br>

---

## 🧠 What Is NeonAI?

**NeonAI V5** is a fully local AI system with mode-driven intelligence, tool calling, voice assistant, and a premium UI — running entirely on your machine.

> ⚠️ **This is not a chatbot wrapper.**  
> NeonAI is an AI *system* — with modes, rules, confidence gates, tool calling, memory, voice control, and decision pipelines. The LLM is a component, not the decision-maker.

---

## ✨ What Makes NeonAI Different

| Principle | Description |
|:---|:---|
| 🧠 **System > Model** | AI logic governs the LLM, not the other way around |
| 🔒 **Privacy First** | Everything runs locally — your data never leaves your machine |
| 🎯 **Mode-Driven** | Each mode has its own rules, memory, tools, and constraints |
| 🛠️ **Tool Calling** | Real tools (weather, calculator, browser, notes) — instant, no LLM needed |
| 🎤 **Voice Control** | Full voice assistant with system commands, TTS, and tool access |
| 🧪 **Experimental** | Built to explore controlled AI design, not to be a product |

---

## 🎮 Modes

<table>
<tr><td width="160"><b>🤖 NEON AI</b></td><td>General chat with smart web search + local LLM hybrid. Calculator & weather tools built-in.</td></tr>
<tr><td><b>💻 NEON CODE</b></td><td>Copy-paste ready code generation. Auto-detects coding queries from casual mode.</td></tr>
<tr><td><b>🎬 NEON MOVIES</b></td><td>Trending carousel, movie details with genres/director/trailer/recommendations via TMDB.</td></tr>
<tr><td><b>📚 NEON STUDY</b></td><td>PDF-based RAG pipeline. Internet blocked. If the answer isn't in the PDF → AI refuses.</td></tr>
<tr><td><b>🎤 VOICE ASSISTANT</b></td><td>Full voice control — talk to Neon, use tools, control your PC. 20+ command types.</td></tr>
</table>

> 💡 Each mode has **isolated chat history** — switching modes keeps each mode's conversation separate.

---

## 🛠️ Tool Calling

NeonAI has built-in tools that respond **instantly** without waiting for the LLM.

| Tool | Trigger Examples | Available In |
|:---|:---|:---|
| 🌤️ **Weather** | "Weather in Delhi", "Temperature in New York" | Chat + Voice |
| 🧮 **Calculator** | "Calculate 25 × 4 + 10", "Convert 100 km to miles" | Chat + Voice |
| 💻 **System Info** | "Battery level", "RAM usage", "CPU status" | Voice |
| 📝 **Notes** | "Save note: buy groceries", "Show my notes" | Voice |
| 🌐 **Web Reader** | "Read this https://example.com" | Voice |
| 🎵 **Music Selection** | "Top 10 songs", "Play Drake", "Recommend some hip-hop" | Chat + Voice |
| 🔍 **Browser** | "Search on YouTube", "Google machine learning" | Voice |

```
User: "Weather in Delhi"
  → Tool Router detects: weather
  → Instant response: 🌤️ 28°C, Partly Cloudy
  → No LLM call needed (< 1 second)
```

---

## 🎤 Voice Assistant

Talk to Neon using **Whisper** (STT) + **Llama 3** (brain) + **GPT-SoVITS** (TTS).

<table>
<tr><td><b>Category</b></td><td><b>Examples</b></td></tr>
<tr><td>🖥️ Apps</td><td>"Open Chrome", "Launch Spotify", "Open VS Code"</td></tr>
<tr><td>🌐 Web</td><td>"Open YouTube", "Go to GitHub"</td></tr>
<tr><td>🔍 Search</td><td>"Search Python tutorials", "Google the news"</td></tr>
<tr><td>▶️ YouTube</td><td>"Play lofi music on YouTube"</td></tr>
<tr><td>🎵 Media</td><td>"Pause", "Next song", "Stop music"</td></tr>
<tr><td>🔊 Volume</td><td>"Volume up", "Set volume to 50", "Mute"</td></tr>
<tr><td>💡 Brightness</td><td>"Increase brightness", "Set brightness to 70"</td></tr>
<tr><td>📶 Connectivity</td><td>"Turn on Bluetooth", "WiFi off", "Airplane mode"</td></tr>
<tr><td>⚡ System</td><td>"Shutdown", "Restart", "Lock screen", "Sleep"</td></tr>
<tr><td>🌤️ Tools</td><td>"What's the weather?", "System info", "Save a note"</td></tr>
</table>

---

## 🏗️ Architecture

```text
[ Backend Execution Architecture ]

  (HTTP/WebSocket)      (Media Blob)
    Text Query          Voice Audio
        │                    │
        ▼                    ▼
   tool_router        whisper_engine (STT)
        │                    │
  Is it a Tool?          Command?
  ├── YES ──► Execute    ├── YES ──► command_router
  │           Local      │           (OS Actions)
  ▼           Script     ▼
  NO                     NO
  │                      │
  └─────────► waterfall ◄┘
                  │
             Need Web?
             ├── YES ──► search_adapter
             ▼
        Mistral / Llama 3
             (Local LLM)
                  │
           confidence_gate
                  │
        Pass? ── NO ──► Block/Regenerate
        │
        ▼
   Return Text / TTS (GPT-SoVITS)
```

---

## 🖥️ UI & Application Flow

```text
[ Frontend UI State Machine ]

      (Launch)
          │
          ▼
   Splash Screen (css animation)
          │
          ▼
      Login/Register
    (Auth Verification)
          │
          ▼
      Main Dashboard (index.html) ◄──┐
          │                          │
          ├──► Chat Mode (Text)      │ (Settings/Theme)
          │    - Markdown Render     ├─► UI Customization
          │    - Glass Widgets       │
          │                          │
          ├──► Voice Mode (Audio)    │ (Study Mode)
          │    - Video Wallpaper     ├─► RAG Interface
          │    - Audio Visualizer    │
          │                          │
          └──► Web Workers ──────────┘
               (Audio/Media Recording)
```

---

## 🎨 Premium UI Features

- 🚀 **Animated Splash Screen** — Spinning ring, progress bar, "NEON AI" reveal on startup
- 🎨 **15+ Neon Themes** + Light/Dark mode with physics-based liquid toggle
- 💬 **Rich Message Rendering** — Bold, headers, numbered lists as glass cards, rating badges
- 📊 **Confidence Scoring Badges** — AI self-evaluates (0-100%) and displays a confidence metric badge under every answer
- 🎥 **Voice Customization** — Upload your own looping 15-second background video for the Voice UI panel
- 🎵 **Music Cards** — Rich, clickable YouTube-linked gradient cards natively rendered in chat
- 📋 **Code Blocks** — Syntax highlighted with copy-to-clipboard button
- 🌐 **Web Source Icons** — Favicon pills show which websites sourced the answer
- 🎬 **Movie Detail Cards** — Genre tags, director, runtime, trailer button, recommendation carousel
- 🎙️ **Draggable Voice Button** — GSAP Draggable, saves position
- 📱 **Fully Responsive** — Desktop + Mobile

---

## 📂 Project Structure

```text
NeonAI/
│
├── server.py                  # Flask backend + API routing
├── START_NEON.bat             # One-click launcher (Windows)
│
├── brain/                     # Core AI logic
│   ├── waterfall.py           # Decision flow & smart routing
│   ├── confidence_gate.py     # Hallucination control
│   └── memory.py              # Session & preference memory
│
├── models/                    # LLM layer
│   ├── local_llm.py           # Mistral (chat) via Ollama
│   ├── hybrid_llm.py          # Web + LLM fusion
│   └── assistant_llm.py       # Llama 3 (voice) via Ollama
│
├── tools/                     # 🆕 Tool Calling System
│   ├── tool_router.py         # Intent detection & routing
│   ├── weather.py             # Weather (wttr.in, free)
│   ├── calculator.py          # Math + unit conversions
│   ├── system_info.py         # CPU/RAM/disk/battery
│   ├── notes.py               # Save/read/delete notes
│   ├── web_reader.py          # Fetch & read URLs
│   └── browser_control.py     # Google/YouTube/URL opener
│
├── voice/                     # Voice Assistant
│   ├── whisper_engine.py      # Speech-to-text (Whisper)
│   ├── tts_engine.py          # Text-to-speech (GPT-SoVITS)
│   ├── command_router.py      # NLP → action routing
│   ├── llm_command_executor.py # System command execution
│   ├── model_loader.py        # Voice model management
│   └── reference_loader.py    # TTS reference audio
│
├── exam/                      # NEON STUDY (PDF RAG)
│   ├── indexer.py             # PDF indexing
│   ├── retriever.py           # Strict PDF-only retrieval
│   └── uploads/               # User PDFs
│
├── web/                       # Web adapters
│   ├── search_adapter.py      # Tavily / DuckDuckGo
│   └── movie_adapter.py       # TMDB (genres, trailer, recs)
│
├── utils/                     # Utilities
│   ├── network.py             # Internet policy
│   └── movie_db.py            # Local movie cache (SQLite)
│
├── user_data/                 # 🆕 User data storage
│   └── notes.json             # Saved notes
│
├── templates/index.html       # Frontend
└── static/
    ├── app.js                 # Frontend logic
    ├── styles.css             # Premium styling (2500+ lines)
    └── wallpapers/            # Custom backgrounds
```

---

## ▶️ Quick Start

### Requirements

**Software:**
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Models: `ollama pull mistral` + `ollama pull llama3.2:3b`
- (Optional) [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) for voice TTS

**Hardware:**
- **CPU**: Multi-core processor (Intel i5/Ryzen 5 or better recommended)
- **RAM**: Minimum 8GB (16GB recommended for running Ollama LLMs smoothly)
- **GPU** (Optional but recommended): NVIDIA GPU with 6GB+ VRAM (e.g., RTX 3060) to hardware-accelerate Whisper and GPT-SoVITS.
- **Storage**: Minimum 10GB free space for Python environments, models, and databases (SSD preferred)

### Install & Run

```bash
pip install -r requirements.txt
python server.py
```

**Or double-click** `START_NEON.bat`

**Open:** `http://localhost:5000`

### Optional API Keys (in Settings ⚙️)
- **TMDB** — Movie posters, details, recommendations
- **Tavily** — Higher quality web search (free tier available)

---

## 🧪 Status

- ✅ Multi-mode AI system with isolated history
- ✅ Tool calling (weather, calculator, notes, system, browser, music)
- ✅ Voice assistant with 20+ command types and Smart Browser Control
- ✅ Premium UI with splash screen, 15+ themes, animations, microinteractions
- ✅ Confidence Gate scoring (0-100% evaluation metric)
- ✅ Smart web search + local LLM hybrid
- ✅ Movie mode with trailer, genres, recommendations
- ✅ Code blocks syntax highlighted with copy-to-clipboard button
- ✅ Rich markdown rendering (lists, headers, ratings)
- ⚠️ Experimental — Architecture locked for iteration

---

## 🚀 Future Enhancements & Scope

While NeonAI V5 is feature-rich, the architecture allows for significant future scalability:
1. **Vision Integration**: Integrating models like Llama-3-Vision to allow Neon to "see" via the webcam or analyze user-uploaded images/screenshots locally.
2. **Long-Term Vector Memory**: Expanding the current session tracking into a persistent vector database (like ChromaDB or FAISS) to allow Neon to remember conversations and user preferences across months.
3. **Autonomous Agents (Agentic Workflows)**: Upgrading the Tool Router to an autonomous agent system (using frameworks like LangChain or AutoGen) to chain complex tools together automatically without immediate user input.

---

## ⚠️ Disclaimer

This is an **experimental project** built for learning, research, and AI system design exploration. Not a commercial product.

---

<div align="center">

  <h3>🧠 Built by Ansh</h3>

  <i>B.Tech CSE</i>

  <br><br>

  <b>AI Systems • Voice Assistants • Tool Calling • Offline-First Architecture</b>

  <br><br>

  <i>"NeonAI is not about how smart the model is. It's about how controlled, safe, and purposeful AI should be."</i>

</div>
