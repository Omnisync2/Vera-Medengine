import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a concise, supportive health assistant."}]

# --- 3. LAYOUT: TITLE & LIVE TIMER ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Live timer formatted as HH:MM:SS
    st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")

# --- 4. CHAT HISTORY DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUT ENGINE (Voice or Text) ---
# Native Audio Input for stability
audio_value = st.audio_input("🎙️ Record or type below")

# Text Input
if prompt := st.chat_input("Ask me about health..."):
    audio_value = None # Prioritize text if user types

# Handle the processing logic
input_text = None
if audio_value:
    with st.spinner("Transcribing..."):
        input_text = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        ).text
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
        # Use st.write_stream to safely handle chunks and prevent crashes
        def stream_gen():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        full_response = st.write_stream(stream_gen())
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
    
