import streamlit as st
from groq import Groq
from datetime import datetime
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. SESSION STATE INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a concise, supportive health assistant. Answer in 1-3 sentences."}
    ]

# --- 3. SIDEBAR / TOP LAYOUT ---
# Using columns to put the clock at the top right
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Clock placeholder
    clock_placeholder = st.empty()

# Update clock loop logic
now = datetime.now().strftime("%H:%M:%S")
clock_placeholder.markdown(f"**Current Time:**<br> {now}", unsafe_allow_html=True)

# --- 4. STABLE VOICE ENGINE ---
# This widget is native and won't crash your browser
audio_value = st.audio_input("🎙️ Tap to record your question")

if audio_value:
    # 1. Transcribe (Auto-sent via Groq Whisper)
    with st.spinner("Transcribing..."):
        transcript = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        ).text
    
    # 2. Process (Auto-sent to Groq Llama)
    st.session_state.messages.append({"role": "user", "content": transcript})
    
    with st.chat_message("user"):
        st.markdown(transcript)
        
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True
        )
        full_response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Rerun to clear the audio widget and show the new chat message immediately
    st.rerun()

# --- 5. DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
