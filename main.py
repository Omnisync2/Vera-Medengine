import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. CONNECT TO GROQ ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. INITIALIZE STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Vera, a supportive health assistant. Keep responses brief (1-3 sentences)."}
    ]

st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 4. DISPLAY CHAT ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 5. UNIFIED INPUT (Voice & Text) ---
# st.audio_input automatically handles the mic and returns the audio file
audio_value = st.audio_input("🎙️ Tap to speak")
prompt = st.chat_input("Or type here...")

user_text = None

# If user spoke
if audio_value:
    with st.spinner("Transcribing..."):
        # Send audio directly to Groq Whisper
        transcription = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        )
        user_text = transcription.text

# If user typed
elif prompt:
    user_text = prompt

# --- 6. PROCESS AI RESPONSE ---
if user_text:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    # Rerun to show the user message immediately before waiting for the AI
    st.rerun()

# Logic to generate AI response only if the last message is from the user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True 
        )
        full_response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
    
