import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 1. SESSION STATE ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Vera, a concise, supportive health assistant."}
    ]

# --- 2. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 3. DISPLAY CHAT ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 4. INPUT HANDLER ---
# Using a key helps Streamlit manage the input state better
audio_value = st.audio_input("🎙️ Record your question", key="voice_input")
prompt = st.chat_input("Or type here...", key="text_input")

input_text = None

# If user used voice
if audio_value:
    with st.spinner("Transcribing..."):
        transcription = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3"
        )
        input_text = transcription.text
    # Clear the audio widget by setting to None after processing
    audio_value = None 

# If user typed text
elif prompt:
    input_text = prompt

# --- 5. PROCESSING ---
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
        
        def response_generator():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        full_response = st.write_stream(response_generator())
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Rerun to show the assistant response immediately
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
