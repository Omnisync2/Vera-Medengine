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

# --- 3. LAYOUT: CLOCK TOP RIGHT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Clock placeholder in top right
    clock_placeholder = st.empty()
    now = datetime.now().strftime("%H:%M:%S")
    clock_placeholder.markdown(f"**{now}**")

# --- 4. CHAT BOX & VOICE INPUT ---
# Display history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. STABLE VOICE ENGINE ---
audio_value = st.audio_input("🎙️ Record your health question")

if audio_value:
    # Fix: Ensure audio data is processed correctly for Groq
    with st.spinner("Processing..."):
        # We pass a proper filename to help Groq's API identify the format
        transcript = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        ).text
    
    # Process the transcription
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
    
    # Force a rerun to refresh the UI and clear the audio input
    st.rerun()

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
        
