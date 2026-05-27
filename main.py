import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- 1. SETUP ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise, supportive health assistant."}]
    st.session_state.start_time = datetime.now()

# Memory Reset (24 hours)
if datetime.now() - st.session_state.start_time > timedelta(hours=24):
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise, supportive health assistant."}]
    st.session_state.start_time = datetime.now()

# --- 2. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 3. CHAT DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 4. INPUT LOGIC (Prevents Repetition) ---
# We use a key and check for new input
audio_value = st.audio_input("🎙️ Record your question", key="audio_key")
prompt = st.chat_input("Or type here...", key="text_key")

input_text = None

# Logic to prevent double-processing
if audio_value:
    with st.spinner("Transcribing..."):
        transcription = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3"
        )
        input_text = transcription.text
    # Clear the audio widget
    st.session_state.audio_key = None 

elif prompt:
    input_text = prompt

# --- 5. AI RESPONSE (Clean Stream) ---
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
        
        # Generator ensures only TEXT passes to the UI
        def clean_gen(stream_obj):
            for chunk in stream_obj:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        
        full_response = st.write_stream(clean_gen(stream))
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
