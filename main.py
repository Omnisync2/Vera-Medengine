import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 1. SESSION STATE & CLIENT ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise, supportive health assistant."}]

# --- 2. CALLBACK: The Secret to Stopping Repetitions ---
def process_voice_input():
    """This runs immediately when audio is recorded, before the script reruns."""
    audio_value = st.session_state.voice_key
    if audio_value:
        with st.spinner("Transcribing..."):
            transcription = st.session_state.client.audio.transcriptions.create(
                file=("audio.wav", audio_value.getvalue()),
                model="whisper-large-v3"
            ).text
        
        # Add to history
        st.session_state.messages.append({"role": "user", "content": transcription})
        
        # Clear the audio widget programmatically
        st.session_state.voice_key = None

# --- 3. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 4. DISPLAY CHAT ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUTS ---
# The 'on_change' callback is what prevents the loop
st.audio_input("🎙️ Record your question", key="voice_key", on_change=process_voice_input)
prompt = st.chat_input("Or type here...")

# Handle Typed Input (Separate from voice callback)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# --- 6. AI RESPONSE LOGIC ---
# Only process if the last message is from the user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True
        )
        full_response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
