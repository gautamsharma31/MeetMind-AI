import html
import json
import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()
st.set_page_config(page_title="MeetMind AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
:root{--bg:#0b1020;--panel:#11182b;--border:rgba(158,174,210,.16);--text:#eef2ff;--muted:#9aa8c7;--purple:#8b7cff;--cyan:#65d6e8;--green:#57d6a0}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 10% 0%,#1b2450 0%,var(--bg) 45%);color:var(--text)}
[data-testid="stSidebar"]{background:#0e1527;border-right:1px solid var(--border)}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:var(--text)!important;letter-spacing:-.03em}
[data-testid="stMarkdownContainer"] p{color:var(--muted)}
.brand{display:flex;gap:12px;align-items:center;margin:4px 0 26px}
.brand-icon{width:43px;height:43px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#8b7cff,#5dd6e7);color:#091020;font-size:23px;font-weight:800}
.brand-name{font-family:'Manrope',sans-serif;font-size:20px;font-weight:800;color:var(--text)}
.brand-sub,.caption{color:var(--muted);font-size:11px;letter-spacing:.09em;text-transform:uppercase}
.eyebrow{color:var(--cyan);font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;margin-bottom:10px}
.hero h1{font-size:clamp(2rem,4vw,3.1rem);line-height:1.12;margin:0 0 10px}
.gradient{background:linear-gradient(90deg,#a99cff,#69dce8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.panel,.meeting-card,.metric{background:rgba(17,26,46,.9);border:1px solid var(--border);border-radius:16px;padding:18px;margin-bottom:13px}
.panel-title{font-family:'Manrope',sans-serif;font-size:17px;font-weight:800;color:var(--text);margin-bottom:5px}
.muted,.meeting-meta{color:var(--muted);font-size:13px;line-height:1.65}
.metric-label{color:var(--muted);font-size:12px}.metric-value{color:var(--text);font-size:27px;font-weight:800;font-family:'Manrope',sans-serif}.metric-note{color:var(--green);font-size:11px;margin-top:4px}
.meeting-title{font-weight:700;color:var(--text);font-size:15px;margin-bottom:7px}
.tag{display:inline-block;border:1px solid var(--border);border-radius:99px;padding:4px 9px;font-size:11px;color:#c9d4f0;margin-right:5px}
.notice{background:rgba(139,124,255,.1);border:1px solid rgba(139,124,255,.25);border-radius:12px;padding:12px 14px;color:#dcd7ff;font-size:13px}
div.stButton>button{border-radius:10px;min-height:40px;font-weight:700;border:1px solid rgba(139,124,255,.45)}
div.stButton>button[kind="primary"]{background:linear-gradient(100deg,#8b7cff,#5bbfd7);color:#091020;border:0}
[data-testid="stFileUploader"]{background:rgba(9,15,29,.42);border:1px dashed rgba(139,124,255,.45);border-radius:14px}
hr{border-color:var(--border)}
</style>
""", unsafe_allow_html=True)

def brand():
    st.markdown('<div class="brand"><div class="brand-icon">✦</div><div><div class="brand-name">MeetMind AI</div><div class="brand-sub">Meeting intelligence</div></div></div>', unsafe_allow_html=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase configuration is missing. Check SUPABASE_URL and SUPABASE_KEY in your .env file.")
    st.stop()

# A separate client is kept in each Streamlit user's session.
if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = st.session_state.supabase_client

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "selected" not in st.session_state:
    st.session_state.selected = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "meetings" not in st.session_state:
    st.session_state.meetings = []
if "meetings_loaded_for" not in st.session_state:
    st.session_state.meetings_loaded_for = None

def get_display_transcript(meeting, display_language):
    """Load a saved translation or generate it once and persist it in Supabase."""
    original_transcript = meeting.get("transcript", "")
    if display_language == "Original":
        return original_transcript

    if not meeting.get("id"):
        raise RuntimeError("This meeting has no database ID, so its translation cannot be saved.")

    column = (
        "transcript_hindi"
        if display_language == "Hindi (हिंदी)"
        else "transcript_hinglish"
    )
    saved_translation = meeting.get(column)
    if saved_translation:
        return saved_translation

    cache = st.session_state.setdefault("transcript_translation_cache", {})
    cache_key = f"{meeting['id']}:{display_language}"
    if cache_key in cache:
        return cache[cache_key]

    # Translate to Hindi first. Hinglish is the Hindi translation transliterated to Latin script.
    hindi_text = GoogleTranslator(source="auto", target="hi").translate(original_transcript)
    result = (
        hindi_text
        if display_language == "Hindi (हिंदी)"
        else transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
    )

    # Persist only to the current user's own meeting. RLS remains the primary access control.
    (supabase.table("meetings")
        .update({column: result})
        .eq("id", meeting["id"])
        .eq("user_id", st.session_state.auth_user["id"])
        .execute())
    meeting[column] = result
    cache[cache_key] = result
    return result


def set_authenticated_user(auth_response):
    user = getattr(auth_response, "user", None)
    session = getattr(auth_response, "session", None)
    if user and session:
        st.session_state.auth_user = {"id": user.id, "email": user.email}
        return True
    return False

def _as_list(value):
    """Normalize JSON/list/text extractor output for storage and display."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
            if isinstance(decoded, list):
                return [str(item).strip() for item in decoded if str(item).strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        return [line.strip().lstrip("- •\t ") for line in value.splitlines() if line.strip()]
    return [str(value)]


def _as_chat_history(value):
    """Normalize stored chat history to question/answer dictionaries."""
    if not isinstance(value, list):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                value = []
        else:
            value = []
    return [
        {"question": str(item.get("question", "")), "answer": str(item.get("answer", ""))}
        for item in value
        if isinstance(item, dict) and item.get("question") is not None
    ]


def _meeting_from_row(row):
    created = row.get("created_at") or ""
    date_label = created[:10] if created else "Saved meeting"
    duration_minutes = row.get("duration_minutes")
    if duration_minutes:
        duration_label = (f"{duration_minutes // 60} hr {duration_minutes % 60} min"
                          if duration_minutes >= 60 and duration_minutes % 60
                          else f"{duration_minutes // 60} hr" if duration_minutes >= 60
                          else f"{duration_minutes} min")
    else:
        duration_label = "Not specified"
    language = row.get("language") or "Not specified"
    return {
        "id": row.get("id"),
        "title": row.get("title") or "Untitled meeting",
        "date": date_label,
        "duration": duration_label,
        "duration_minutes": duration_minutes,
        "language": language,
        "status": "Completed",
        "summary": row.get("summary") or "",
        "actions": _as_list(row.get("action_items")),
        "decisions": _as_list(row.get("key_decisions")),
        "questions": _as_list(row.get("open_questions")),
        "transcript": row.get("transcript") or "",
        "transcript_hindi": row.get("transcript_hindi") or "",
        "transcript_hinglish": row.get("transcript_hinglish") or "",
        "chat_history": _as_chat_history(row.get("chat_history")),
        # RAG chains are rebuilt lazily from the saved transcript when needed.
        "rag_chain": None,
        "source_type": row.get("source_type") or "upload",
        "source_url": row.get("source_url"),
    }


def load_user_meetings():
    """Load only the signed-in user's meetings; RLS also enforces ownership."""
    user_id = st.session_state.auth_user["id"]
    response = (supabase.table("meetings").select("*")
                .eq("user_id", user_id).order("created_at", desc=True).execute())
    st.session_state.meetings = [_meeting_from_row(row) for row in (response.data or [])]
    st.session_state.meetings_loaded_for = user_id


# Require authentication before showing the workspace.
if not st.session_state.auth_user:
    brand()
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.markdown(
            '<div class="hero"><div class="eyebrow">One conversation. Every insight.</div>'
            '<h1>Meetings are full of ideas.<br><span class="gradient">Don’t lose a single one.</span></h1>'
            '<p>Turn long recordings into clear summaries, decisions, action items, and searchable meeting knowledge.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel"><div class="panel-title">Meeting intelligence, in one place</div>'
            '<p class="muted">✦ Summaries and key decisions</p><p class="muted">✦ English and Hinglish transcription</p>'
            '<p class="muted">✦ Ask questions about recordings</p><p class="muted">✦ Revisit your meeting library</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            brand()
            mode = st.radio("Welcome", ["Log in", "Create account"], horizontal=True)
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 8 characters")
            confirm = ""
            if mode == "Create account":
                confirm = st.text_input("Confirm password", type="password")

            if st.button("Continue", type="primary", use_container_width=True):
                if not email or "@" not in email:
                    st.error("Enter a valid email address.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif mode == "Create account" and password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        if mode == "Create account":
                            response = supabase.auth.sign_up({
                                "email": email.strip(),
                                "password": password,
                            })
                            if set_authenticated_user(response):
                                st.success("Account created and signed in.")
                                st.rerun()
                            else:
                                st.success("Account created. Check your email to confirm your address, then log in.")
                        else:
                            response = supabase.auth.sign_in_with_password({
                                "email": email.strip(),
                                "password": password,
                            })
                            if set_authenticated_user(response):
                                st.session_state.page = "Dashboard"
                                st.rerun()
                            else:
                                st.error("Login did not return an active session. Check your email confirmation settings.")
                    except Exception as exc:
                        st.error(f"Authentication failed: {exc}")

            st.caption("Your account is authenticated through Supabase. Keep your password private.")
    st.stop()

if st.session_state.meetings_loaded_for != st.session_state.auth_user["id"]:
    try:
        load_user_meetings()
    except Exception as exc:
        st.error(f"Could not load your saved meetings: {exc}")
        st.session_state.meetings = []

with st.sidebar:
    brand()
    st.caption("WORKSPACE")
    for p in ["Dashboard","New analysis","Meeting library","Settings"]:
        if st.button(("✦  " if st.session_state.page==p else "　")+p,use_container_width=True,type="primary" if st.session_state.page==p else "secondary",key="nav_"+p):
            st.session_state.page=p; st.rerun()
    st.divider()
    st.markdown('<div class="notice">VERSION 1<br><b>English · up to 6 hours</b><br><b>Hinglish · up to 90 minutes</b></div>',unsafe_allow_html=True)
    st.divider()
    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        finally:
            st.session_state.auth_user = None
            st.session_state.page = "Dashboard"
            st.session_state.selected = 0
            st.session_state.chat_history = []
            st.session_state.active_chat_meeting_id = None
            st.session_state.meetings = []
            st.session_state.meetings_loaded_for = None
            st.rerun()

meetings=st.session_state.meetings
st.markdown('<div class="hero"><div class="eyebrow">Your workspace</div><h1>Good to see you again.</h1><p>Your conversations, organized into clear insights. Start a new analysis or pick up where you left off.</p></div>',unsafe_allow_html=True)

if st.session_state.page=="Dashboard":
    a,b,c=st.columns(3)
    with a: st.markdown(f'<div class="metric"><div class="metric-label">Meetings in library</div><div class="metric-value">{len(meetings):02d}</div><div class="metric-note">Across your workspace</div></div>',unsafe_allow_html=True)
    with b: st.markdown(f'<div class="metric"><div class="metric-label">Completed analyses</div><div class="metric-value">{sum(m["status"]=="Completed" for m in meetings):02d}</div><div class="metric-note">Ready to revisit</div></div>',unsafe_allow_html=True)
    with c: st.markdown('<div class="metric"><div class="metric-label">Languages supported</div><div class="metric-value">02</div><div class="metric-note">English + Hinglish</div></div>',unsafe_allow_html=True)
    main,side=st.columns([1.6,1],gap="large")
    with main:
        st.subheader("Recent meetings")
        if not meetings:
            st.info("Your meeting library is empty. Start a new analysis to create your first meeting.")
        for i,m in enumerate(meetings[:3]):
            st.markdown(f'<div class="meeting-card"><div class="meeting-title">{html.escape(m["title"])} <span class="tag">{html.escape(m["status"])}</span></div><div class="meeting-meta">{html.escape(m["date"])} · {html.escape(m["duration"])} · {html.escape(m["language"])}</div></div>',unsafe_allow_html=True)
            if st.button("Open meeting →",key=f"open_{i}"):
                st.session_state.selected=i; st.session_state.page="Meeting details"; st.rerun()
        if st.button("View all meetings",use_container_width=True): st.session_state.page="Meeting library"; st.rerun()
    with side:
        st.markdown('<div class="panel"><div class="panel-title">Start with a recording</div><p class="muted">Upload a file or paste a supported video URL.</p></div>',unsafe_allow_html=True)
        if st.button("＋ New analysis",type="primary",use_container_width=True): st.session_state.page="New analysis"; st.rerun()
        st.markdown('<div class="panel"><div class="panel-title">What MeetMind extracts</div><p class="muted">📝 Clear summaries</p><p class="muted">✓ Action items</p><p class="muted">◆ Key decisions</p><p class="muted">? Open questions</p><p class="muted">✦ Meeting Q&A with RAG</p></div>',unsafe_allow_html=True)

elif st.session_state.page=="New analysis":
    st.subheader("Create a new analysis")
    st.markdown('<div class="notice">Processing runs locally. Analysis results are saved to your private Supabase meeting library; uploaded media remains on this PC temporarily.</div>',unsafe_allow_html=True)
    tab1,tab2=st.tabs(["Upload a file","Video URL"])
    with tab1: uploaded=st.file_uploader("Choose an audio or video file",type=["mp4","mov","mkv","webm","mp3","wav","m4a","mpeg","mpga","ogg"])
    with tab2: url=st.text_input("Supported video URL",placeholder="Paste a YouTube URL")
    language=st.radio("Recording language",["English","Hinglish"],horizontal=True)
    limit=360 if language=="English" else 90
    st.markdown(f'<div class="notice">{language} · Maximum duration for version 1: <b>{"6 hours" if language=="English" else "90 minutes"}</b></div>',unsafe_allow_html=True)
    duration=st.number_input("Duration in minutes (if known)",min_value=1,max_value=1000,value=30,step=5)
    meeting_name=st.text_input("Meeting name (optional)",placeholder="e.g. Weekly product sync")
    if duration>limit: st.error(f"{language} recordings must be no longer than {limit} minutes.")
    if st.button("Start analysis", type="primary", use_container_width=True):
        if duration > limit:
            st.error("This recording exceeds the selected language's duration limit.")
        elif not uploaded and not (url and url.strip()):
            st.error("Upload a file or enter a YouTube URL.")
        else:
            source = None
            try:
                st.session_state.chat_history = []
                with st.status("MeetMind AI is analysing your recording...", expanded=True) as status:
                    if uploaded:
                        # Save the Streamlit upload to disk because process_input() accepts a file path.
                        upload_dir = Path("uploads")
                        upload_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = Path(uploaded.name).name
                        saved_path = upload_dir / f"{uuid.uuid4().hex}_{safe_name}"
                        saved_path.write_bytes(uploaded.getvalue())
                        source = str(saved_path.resolve())
                        st.write("1/6 · File uploaded and saved locally.")
                    else:
                        source = url.strip()
                        st.write("1/6 · YouTube URL received.")

                    st.write("2/6 · Extracting audio and creating chunks...")
                    chunks = process_input(source)

                    st.write("3/6 · Transcribing audio...")
                    language_code = "english" if language == "English" else "hinglish"
                    transcript = transcribe_all(chunks, language_code)
                    if not transcript or not transcript.strip():
                        raise RuntimeError("Transcription returned no text. Try another file or URL.")

                    st.write("4/6 · Generating title and summary...")
                    generated_title = generate_title(transcript)
                    summary = summarize(transcript)

                    st.write("5/6 · Extracting action items, decisions, and questions...")
                    action_items = extract_action_items(transcript)
                    decisions = extract_key_decisions(transcript)
                    questions = extract_questions(transcript)

                    st.write("6/6 · Building meeting Q&A (RAG)...")
                    rag_chain = build_rag_chain(transcript)

                    final_title = meeting_name.strip() if meeting_name.strip() else str(generated_title).strip()
                    duration_label = (
                        f"{duration // 60} hr {duration % 60} min"
                        if duration >= 60 and duration % 60
                        else f"{duration // 60} hr" if duration >= 60
                        else f"{duration} min"
                    )
                    new_meeting = {
                        "title": final_title or "Untitled meeting",
                        "date": "Just now",
                        "duration": duration_label,
                        "language": language,
                        "status": "Completed",
                        "summary": summary,
                        "actions": action_items if isinstance(action_items, list) else str(action_items).splitlines(),
                        "decisions": decisions if isinstance(decisions, list) else str(decisions).splitlines(),
                        "questions": questions if isinstance(questions, list) else str(questions).splitlines(),
                        "transcript": transcript,
                        "rag_chain": rag_chain,
                    }
                    source_type = "youtube" if isinstance(source, str) and source.strip().lower().startswith(("https://", "http://")) else "upload"
                    payload = {
                        "user_id": st.session_state.auth_user["id"],
                        "title": new_meeting["title"],
                        "source_type": source_type,
                        "source_url": source if source_type == "youtube" else None,
                        "summary": str(summary),
                        "transcript": str(transcript),
                        "transcript_hindi": None,
                        "transcript_hinglish": None,
                        "chat_history": [],
                        "action_items": _as_list(action_items),
                        "key_decisions": _as_list(decisions),
                        "open_questions": _as_list(questions),
                        "duration_minutes": int(duration),
                        "language": language,
                    }
                    saved_response = supabase.table("meetings").insert(payload).execute()
                    if not saved_response.data:
                        raise RuntimeError("Supabase did not return the saved meeting record.")
                    saved_meeting = _meeting_from_row(saved_response.data[0])
                    saved_meeting["rag_chain"] = rag_chain
                    st.session_state.meetings.insert(0, saved_meeting)
                    st.session_state.selected = 0
                    st.session_state.page = "Meeting details"
                    status.update(label="Analysis complete and saved!", state="complete", expanded=False)
                st.success("Analysis complete. Your results are ready.")
                st.rerun()
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.caption("Check the terminal for the full error traceback. Your existing app.py has not been changed.")

    st.caption("This first integration runs processing locally and synchronously. Cloud storage, background jobs, and automatic media-duration detection are not connected yet.")

elif st.session_state.page=="Meeting library":
    st.subheader("Meeting library")
    q=st.text_input("Search meetings",placeholder="Search by title, language, or status")
    filtered=[m for m in meetings if q.lower() in (m["title"]+" "+m["language"]+" "+m["status"]).lower()]
    if not filtered: st.info("No saved meetings yet. Run a new analysis to see it here.")
    for m in filtered:
        i=meetings.index(m)
        st.markdown(f'<div class="meeting-card"><div class="meeting-title">{html.escape(m["title"])}</div><div class="meeting-meta">{html.escape(m["date"])} · {html.escape(m["duration"])} · {html.escape(m["language"])} · {html.escape(m["status"])}</div></div>',unsafe_allow_html=True)
        if st.button("View results",key=f"lib_{i}"): st.session_state.selected=i; st.session_state.page="Meeting details"; st.rerun()

elif st.session_state.page=="Meeting details":
    i=st.session_state.selected
    m=meetings[i]
    st.title(m["title"])
    st.markdown(f'<span class="tag">{html.escape(m["language"])}</span><span class="tag">{html.escape(m["duration"])}</span><span class="tag">{html.escape(m["status"])}</span>',unsafe_allow_html=True)
    t1,t2,t3,t4,t5=st.tabs(["Summary","Action items","Decisions","Open questions","Transcript"])
    with t1: st.write(m["summary"])
    with t2:
        action_values = m.get("actions", [])
        action_values = [str(x).strip("- •\\t ") for x in action_values if str(x).strip()] if isinstance(action_values, list) else [line.strip("- •\\t ") for line in str(action_values).splitlines() if line.strip()]
        if action_values:
            for action_index, action in enumerate(action_values):
                st.checkbox(action, key=f"act_{i}_{action_index}")
        else:
            st.info("No action items were extracted.")
    with t3:
        decision_values = m.get("decisions", [])
        decision_values = decision_values if isinstance(decision_values, list) else str(decision_values).splitlines()
        decision_values = [str(x).strip("- •\\t ") for x in decision_values if str(x).strip()]
        for x in decision_values:
            st.markdown("- " + x)
        if not decision_values:
            st.info("No decisions were extracted.")
    with t4:
        question_values = m.get("questions", [])
        question_values = question_values if isinstance(question_values, list) else str(question_values).splitlines()
        question_values = [str(x).strip("- •\\t ") for x in question_values if str(x).strip()]
        for x in question_values:
            st.markdown("- " + x)
        if not question_values:
            st.info("No open questions were extracted.")
    with t5:
        transcript_language = st.selectbox(
            "Transcript language",
            ["Original", "Hindi (हिंदी)", "Hinglish (Roman Hindi)"],
            key=f"transcript_language_{i}",
        )
        if transcript_language == "Original":
            display_transcript = m.get("transcript", "")
            st.text_area("Transcript", display_transcript, height=300, disabled=True)
        else:
            try:
                with st.spinner(f"Preparing transcript in {transcript_language}..."):
                    display_transcript = get_display_transcript(m, transcript_language)
                st.text_area("Translated transcript", display_transcript, height=300, disabled=True)
                st.caption("The original transcript remains unchanged. Generated translations are saved to Supabase and reused next time.")
            except Exception as exc:
                st.error(f"Could not translate the transcript: {exc}")
                st.caption("Check your internet connection and install the translation dependencies if needed.")
    # Keep a separate persisted conversation for each meeting.
    active_meeting_id = m.get("id") or f"unsaved-{i}"
    if st.session_state.get("active_chat_meeting_id") != active_meeting_id:
        st.session_state.active_chat_meeting_id = active_meeting_id
        st.session_state.chat_history = list(m.get("chat_history", []))

    st.subheader("Ask this meeting")
    st.caption("Try one of these questions, or write your own.")
    question_key = f"meeting_question_{i}"
    auto_submit_key = f"auto_submit_question_{i}"
    suggestions = [
        "Summarize the key takeaways",
        "What were the main decisions?",
        "What action items were assigned, and to whom?",
        "What questions remain unresolved?",
    ]
    suggestion_columns = st.columns(2)
    for suggestion_index, suggestion in enumerate(suggestions):
        with suggestion_columns[suggestion_index % 2]:
            if st.button(suggestion, key=f"suggestion_{i}_{suggestion_index}", use_container_width=True):
                st.session_state[question_key] = suggestion
                st.session_state[auto_submit_key] = True
                st.rerun()

    question = st.text_input(
        "Your question",
        placeholder="Ask anything about this meeting...",
        key=question_key,
    )
    ask_clicked = st.button("Ask question", type="primary", key=f"ask_question_{i}")
    auto_submit = st.session_state.pop(auto_submit_key, False)
    if ask_clicked or auto_submit:
        question = st.session_state.get(question_key, "")
        rag_chain = m.get("rag_chain")
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Preparing meeting search and finding an answer..."):
                    if not rag_chain:
                        if not m.get("transcript", "").strip():
                            raise RuntimeError("This saved meeting has no transcript to search.")
                        rag_chain = build_rag_chain(m["transcript"])
                        m["rag_chain"] = rag_chain
                    answer = ask_question(rag_chain, question.strip())

                chat_item = {"question": question.strip(), "answer": str(answer)}
                updated_history = list(st.session_state.chat_history) + [chat_item]

                # Save the whole conversation to this user's meeting record.
                if not m.get("id"):
                    raise RuntimeError("This meeting has no saved database ID, so its chat cannot be persisted.")
                (supabase.table("meetings")
                    .update({"chat_history": updated_history})
                    .eq("id", m["id"])
                    .eq("user_id", st.session_state.auth_user["id"])
                    .execute())

                st.session_state.chat_history = updated_history
                m["chat_history"] = updated_history
                st.rerun()
            except Exception as exc:
                st.error(f"Could not answer/save this question: {exc}")

    for chat_index, chat_item in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**You:** {chat_item['question']}")
        st.markdown(f"**MeetMind AI:** {chat_item['answer']}")

elif st.session_state.page=="Settings":
    st.subheader("Settings")
    st.text_input("Display name", value=(st.session_state.auth_user.get("email") or "MeetMind User").split("@")[0])
    st.text_input("Email", value=st.session_state.auth_user.get("email", ""), disabled=True)
    st.selectbox("Default language",["English","Hinglish"])
    st.selectbox("Theme",["Dark","Light"])
    st.markdown('<div class="notice">Your account and meeting library are connected to Supabase. Meeting results are saved privately to your account.</div>', unsafe_allow_html=True)
    if st.button("Save settings",type="primary"): st.success("Demo settings saved for this session.")

st.divider()
st.markdown('<p style="text-align:center;font-size:11px">MeetMind AI · Turn conversations into useful knowledge</p>',unsafe_allow_html=True)