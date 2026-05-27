import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 1. MEMORY ENGINE ---
# We store the conversation start time. If > 24 hours, we clear the memory.
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
    st.session_state.messages = [{"role": "system", "content": "You are a concise, supportive health assistant. You remember the user's history from today."}]

if datetime.now() - st.session_state.start_time > timedelta(hours=24):
    st.session_state.messages = [{"role": "system", "content": "You are a concise, supportive health assistant."}]
    st.session_state.start_time = datetime.now()

# --- 2. CLIENT & STATE ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "last_input_id" not in st.session_state:
    st.session_state.last_input_id = None

# --- 3. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 4. CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUT & PROCESSING ---
audio_value = st.audio_input("🎙️ Record or type below")
prompt = st.chat_input("Ask me about health...")

current_input_id = str(audio_value) + str(prompt)

if (audio_value or prompt) and current_input_id != st.session_state.last_input_id:
    st.session_state.last_input_id = current_input_id
    input_text = None
    
    if audio_value:
        with st.spinner("Transcribing..."):
            input_text = st.session_state.client.audio.transcriptions.create(
                file=("audio.wav", audio_value.getvalue()),
                model="whisper-large-v3"
            ).text
    else:
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
            full_response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
