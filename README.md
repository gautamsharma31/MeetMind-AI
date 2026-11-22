::: {align="center"}
# 🧠 MeetMind AI

### Turn every meeting into searchable knowledge.

An AI-powered meeting intelligence workspace that transforms audio and
video recordings into structured insights---summaries, decisions, action
items, open questions, transcripts, and conversational Q&A.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://meetmind-ai-workspace.streamlit.app/)

**[Launch MeetMind AI](https://meetmind-ai-workspace.streamlit.app/) ·
[GitHub Repository](https://github.com/gautamsharma31/MeetMind-AI)**
:::

------------------------------------------------------------------------

## 📌 Table of Contents

-   [Overview](#-overview)
-   [The Problem](#-the-problem)
-   [What MeetMind AI Does](#-what-meetmind-ai-does)
-   [Key Features](#-key-features)
-   [How It Works](#-how-it-works)
-   [Technology Stack](#-technology-stack)
-   [System Architecture](#-system-architecture)
-   [Project Structure](#-project-structure)
-   [Getting Started](#-getting-started)
-   [Environment Configuration](#-environment-configuration)
-   [Run Locally](#-run-locally)
-   [Deployment](#-deployment)
-   [Data and Security](#-data-and-security)
-   [Current Scope and Limitations](#-current-scope-and-limitations)
-   [Future Enhancements](#-future-enhancements)
-   [Contributing](#-contributing)
-   [Author](#-author)

------------------------------------------------------------------------

## 🌟 Overview

MeetMind AI is an AI-powered application designed to make meetings
easier to understand, organize, and revisit.

Meetings often contain important decisions, assigned tasks, unresolved
questions, and useful information. Finding those details later can mean
listening to an entire recording again. MeetMind AI helps reduce that
effort by converting recordings into structured meeting notes and making
the resulting knowledge searchable through a Retrieval-Augmented
Generation (RAG) question-answering experience.

Users can provide a supported YouTube URL or upload an audio/video file,
select the recording language, and generate meeting insights. Saved
meetings can be revisited from a personal library.

**Live application:** https://meetmind-ai-workspace.streamlit.app/

## 🎯 The Problem

Traditional meeting recordings are difficult to work with:

-   Important information is buried in long recordings.
-   Manually preparing meeting minutes takes time.
-   Decisions and action items can be overlooked.
-   Finding a specific discussion requires replaying or searching
    through a transcript.
-   Meeting knowledge becomes scattered across recordings and notes.

## 💡 What MeetMind AI Does

MeetMind AI turns a recording into a structured, reusable meeting
record:

  -----------------------------------------------------------------------
  Input                   Processing              Output
  ----------------------- ----------------------- -----------------------
  Audio/video file or     Audio extraction and    Text transcript
  supported YouTube URL   speech recognition      

  Transcript              LLM-based analysis      Summary and generated
                                                  meeting title

  Transcript              Information extraction  Action items,
                                                  decisions, and open
                                                  questions

  Saved transcript        Embedding and vector    Context-aware meeting
                          retrieval               Q&A

  Saved meeting           Database storage        Personal meeting
                                                  library
  -----------------------------------------------------------------------

## ✨ Key Features

### 1. Audio and Video Ingestion

-   Upload supported audio and video formats.
-   Provide a supported YouTube URL.
-   Extract audio for downstream transcription using the
    media-processing pipeline.

### 2. Multilingual Transcription

-   English transcription using a locally run OpenAI Whisper model.
-   Hinglish transcription through Sarvam AI.
-   Convert spoken content into text for further analysis.

### 3. AI-Powered Meeting Insights

Generate structured information from the transcript: - **Meeting
summary:** A readable overview of the discussion. - **Meeting title:** A
title generated from the meeting content. - **Action items:** Tasks and
follow-ups identified in the conversation. - **Key decisions:**
Important decisions made during the meeting. - **Open questions:**
Questions or topics that remain unresolved.

### 4. Meeting Library

-   Save processed meetings to a personal library.
-   Reopen previously processed meetings.
-   Search saved meetings.
-   Delete meeting records from the account.

### 5. RAG-Based Meeting Assistant

-   Ask natural-language questions about a saved meeting.
-   Retrieve relevant transcript context from the vector store.
-   Generate answers using the configured language model.
-   Keep question-and-answer history associated with the meeting.

### 6. Transcript Language Options

-   Read the original transcript.
-   Generate a Hindi version.
-   Generate a Hinglish (Roman Hindi) version.
-   Reuse saved translations when available.

### 7. Authentication and Persistent Storage

-   User authentication through Supabase.
-   Store meeting records in Supabase.
-   Apply user-level access controls through Supabase Row Level Security
    (RLS).

### 8. Responsive User Interface

-   Desktop dashboard layout.
-   Compact layout for narrower laptop and tablet screens.
-   Mobile-friendly layout for small screens.

------------------------------------------------------------------------

## 🔄 How It Works

1.  **Sign in:** Create an account or log in.
2.  **Choose a source:** Upload an audio/video file or enter a supported
    YouTube URL.
3.  **Select language:** Choose English or Hinglish according to the
    recording.
4.  **Extract audio:** The media-processing pipeline prepares audio for
    transcription.
5.  **Transcribe:** The configured speech-recognition service converts
    speech into text.
6.  **Analyze:** The language model generates a title and summary and
    extracts action items, decisions, and open questions.
7.  **Save:** The meeting record is stored in the user's Supabase-backed
    library.
8.  **Prepare meeting search:** The transcript is indexed for
    retrieval-based question answering.
9.  **Ask questions:** Open the saved meeting and ask questions about
    its content.

------------------------------------------------------------------------

## 🧰 Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Language                Python 3.11             Core application and
                                                  processing logic

  Frontend                Streamlit               Interactive web
                                                  application

  Authentication          Supabase Auth           User sign-up and login

  Database                Supabase / PostgreSQL   Persistent meeting
                                                  records and chat
                                                  history

  English speech          OpenAI Whisper          English transcription
  recognition                                     

  Hinglish speech         Sarvam AI               Hinglish transcription
  recognition                                     

  LLM                     Google Gemini           Summarization, title
                                                  generation, and
                                                  responses

  LLM orchestration       LangChain LCEL          Language-model pipeline
                                                  orchestration

  Vector database         ChromaDB                Transcript chunk
                                                  storage and retrieval

  Embeddings              Hugging Face Embeddings Convert transcript
                                                  chunks into vector
                                                  representations

  Media download          yt-dlp                  Retrieve supported
                                                  video audio

  Media processing        FFmpeg                  Audio extraction and
                                                  conversion

  Translation             deep-translator         Hindi translation

  Transliteration         indic-transliteration   Devanagari-to-Roman
                                                  transliteration

  PDF generation          FPDF2                   PDF document generation
  dependency                                      where enabled
  -----------------------------------------------------------------------

> Exact model names and service availability may change as API providers
> update their offerings. Check the project configuration for the
> currently selected models.

------------------------------------------------------------------------

## 🏗️ System Architecture

``` mermaid
flowchart TD
    A[User] --> B[Streamlit Application]
    B --> C[Supabase Authentication]
    B --> D[Audio / Video Upload or YouTube URL]
    D --> E[FFmpeg / yt-dlp Processing]
    E --> F{Recording Language}
    F -->|English| G[OpenAI Whisper]
    F -->|Hinglish| H[Sarvam AI]
    G --> I[Transcript]
    H --> I
    I --> J[Gemini + LangChain]
    J --> K[Summary and Meeting Title]
    J --> L[Action Items, Decisions, Open Questions]
    I --> M[Hugging Face Embeddings]
    M --> N[ChromaDB Vector Store]
    K --> O[Supabase Meeting Records]
    L --> O
    O --> P[Meeting Library]
    N --> Q[RAG Retrieval]
    P --> R[Meeting Q&A Interface]
    Q --> R
    R --> J
```

### RAG Question-Answering Flow

1.  The meeting transcript is divided into smaller text chunks.
2.  Hugging Face embeddings represent those chunks as vectors.
3.  ChromaDB stores the vectors for retrieval.
4.  When a user asks a question, relevant transcript chunks are
    retrieved.
5.  The retrieved context is passed to the configured language model.
6.  The model generates an answer grounded in the retrieved meeting
    content.

------------------------------------------------------------------------

## 📁 Project Structure

``` text
MeetMind-AI/
│
├── app.py                    # Streamlit interface and application flow
├── main.py                   # Main processing entry point
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages for cloud deployment
├── .env                      # Local environment variables (never commit)
├── .gitignore
│
├── core/
│   ├── transcriber.py        # Speech transcription logic
│   ├── summarizer.py         # Summary and title generation
│   ├── extractor.py          # Action items, decisions, and questions
│   ├── rag_engine.py         # RAG chain and meeting Q&A
│   └── vector_store.py       # ChromaDB operations
│
├── utils/
│   └── audio_processor.py    # Audio/video input processing
│
└── ...
```

The tree above highlights the main files and modules. Your repository
may contain additional folders or files as development continues.

------------------------------------------------------------------------

## 🚀 Getting Started

### Prerequisites

Before running the project locally, make sure you have:

-   Python **3.11**
-   Git
-   FFmpeg installed and available in your system `PATH`
-   A Supabase project and the required project credentials
-   API credentials for the AI services enabled in your project
    configuration
-   Internet access for external APIs and supported URL downloads

### 1. Clone the Repository

``` bash
git clone https://github.com/gautamsharma31/MeetMind-AI.git
cd MeetMind-AI
```

### 2. Create a Virtual Environment

**Windows PowerShell**

``` powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

``` bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, check that the Python version and package
versions are compatible with your operating system.

### 4. Install FFmpeg

Install FFmpeg for your operating system and ensure that the `ffmpeg`
command is available from the terminal.

Verify the installation:

``` bash
ffmpeg -version
```

For Streamlit Community Cloud, system-level packages can be declared in
`packages.txt`.

------------------------------------------------------------------------

## 🔐 Environment Configuration

Create a `.env` file in the project root and add the credentials
required by your local configuration.

At minimum, the application code shown in this repository expects the
Supabase variables below:

``` env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

Add the required Gemini and Sarvam credentials using the exact
environment-variable names read by the corresponding modules in your
current project version. Do not guess variable names; check the
configuration in `core/` before adding them.

**Important:** - Never commit your `.env` file. - Never paste API keys
into source code or public issues. - Add `.env` to `.gitignore`. - Use
Streamlit Community Cloud Secrets for deployed applications. - Use only
the Supabase key appropriate for the operations performed by the app,
and configure Row Level Security policies.

Example `.gitignore` entries:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.streamlit/secrets.toml
uploads/
```

Adjust ignore rules if your project intentionally tracks any of these
paths.

------------------------------------------------------------------------

## ▶️ Run Locally

Start the Streamlit application from the project root:

``` bash
python -m streamlit run app.py
```

Streamlit will print a local address, usually:

``` text
http://localhost:8501
```

To test the app from another device on the same Wi-Fi network:

``` bash
python -m streamlit run app.py --server.address 0.0.0.0
```

Use your computer's local network IP address with port `8501` on the
other device. Only do this on a trusted network.

------------------------------------------------------------------------

## ☁️ Deployment

MeetMind AI is deployed using **Streamlit Community Cloud**.

### Deployment Steps

1.  Push the project to GitHub.
2.  Open [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Create a new app.
4.  Select the GitHub repository and `main` branch.
5.  Set `app.py` as the application entry point.
6.  Add required environment values under the app's **Secrets**
    settings.
7.  Deploy the application.
8.  Review the deployment logs if dependency installation or startup
    fails.

### Live Application

**https://meetmind-ai-workspace.streamlit.app/**

### Cloud Deployment Notes

-   Streamlit Community Cloud uses its own runtime environment; it does
    not use the Python environment or GPU on your personal laptop.
-   Keep cloud dependencies compatible with the cloud runtime.
-   A CUDA-specific PyTorch wheel intended for a local NVIDIA GPU may
    not install in a CPU-based cloud environment.
-   Large speech-recognition and embedding models can require
    substantial memory and startup time.
-   Do not commit secrets to GitHub.

------------------------------------------------------------------------

## 🛡️ Data and Security

MeetMind AI uses Supabase authentication and database storage to
associate meeting records with signed-in users.

Recommended security practices:

-   Enable Row Level Security (RLS) on tables containing user data.
-   Ensure policies restrict users to records belonging to their
    authenticated user ID.
-   Keep API keys and database credentials outside the source code.
-   Do not expose privileged Supabase keys in browser-side code.
-   Avoid uploading confidential meeting recordings unless you have
    permission to process and store them.
-   Review the privacy and retention policies of the external AI
    services used for transcription and language-model processing.

------------------------------------------------------------------------

## ⚠️ Current Scope and Limitations

-   Transcription and analysis time depends on recording duration, model
    selection, hardware, network conditions, and provider limits.
-   External AI services may have rate limits, availability constraints,
    or usage charges.
-   YouTube processing depends on the source being accessible and
    supported by the media download pipeline.
-   RAG answer quality depends on transcript quality, chunking,
    retrieval, and the language model.
-   Local and cloud environments may require different compatible
    dependency builds.
-   The application currently supports the languages and duration limits
    presented in its interface; check the running app for the latest
    limits.

------------------------------------------------------------------------

## 🛣️ Future Enhancements

Potential areas for further development:

-   Speaker identification and diarization.
-   Automatic detection of recording duration and language.
-   Timestamp-linked summaries and searchable transcript segments.
-   Export meeting reports in multiple formats.
-   Background processing for long recordings.
-   Meeting analytics and cross-meeting search.
-   More language support.
-   Improved user preferences and workspace management.

These are possible future enhancements, not claims that the features are
already implemented.

------------------------------------------------------------------------

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1.  Fork the repository.

2.  Create a feature branch:

    ``` bash
    git checkout -b feature/your-feature-name
    ```

3.  Make and test your changes.

4.  Commit your work:

    ``` bash
    git commit -m "Add: describe your change"
    ```

5.  Push the branch and open a Pull Request.

Please do not include secrets, private recordings, or personal data in
commits or issue reports.

------------------------------------------------------------------------

## 👨‍💻 Author

**Gautam Sharma**

-   GitHub: [@gautamsharma31](https://github.com/gautamsharma31)
-   Project: [MeetMind
    AI](https://github.com/gautamsharma31/MeetMind-AI)
-   Live App:
    [meetmind-ai-workspace.streamlit.app](https://meetmind-ai-workspace.streamlit.app/)

------------------------------------------------------------------------

::: {align="center"}
### 🧠 MeetMind AI

**Listen less. Understand more. Never lose an insight.**
:::
