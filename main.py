import streamlit as st
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo # Standard library, no installation needed!

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a concise, supportive health assistant."}]

# --- 3. LAYOUT: TITLE & DYNAMIC TIMER ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Use the browser's timezone (defaulting to Manila since you are there)
    tz = ZoneInfo("Asia/Manila")
    st.markdown(f"**{datetime.now(tz).strftime('%H:%M:%S')}**")

# --- 4. CHAT HISTORY DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUT ENGINE ---
audio_value = st.audio_input("🎙️ Record or type below")
prompt = st.chat_input("Ask me about health...")

input_text = None
if audio_value:
    with st.spinner("Transcribing..."):
        # Explicit file type ensures Groq doesn't throw BadRequestError
        transcription = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        )
        input_text = transcription.text
elif prompt:
    input_text = prompt

if input_text:
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)
        
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True
        )
        
        def stream_gen():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        full_response = st.write_stream(stream_gen())
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
    
