import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. INITIALIZATION & MEMORY ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Vera, a concise, supportive health assistant. You have access to our previous conversation history for the last 24 hours."}
    ]
    st.session_state.start_time = datetime.now()

# Reset memory after 24 hours
if datetime.now() - st.session_state.start_time > timedelta(hours=24):
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise, supportive health assistant."}]
    st.session_state.start_time = datetime.now()

if "last_input_id" not in st.session_state:
    st.session_state.last_input_id = None

# --- 3. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Manila time
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 4. DISPLAY CHAT ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUT & PROCESSING ---
audio_value = st.audio_input("🎙️ Record your question")
prompt = st.chat_input("Or type here...")

current_input_id = str(audio_value) + str(prompt)

if (audio_value or prompt) and current_input_id != st.session_state.last_input_id:
    st.session_state.last_input_id = current_input_id
    input_text = None
    
    if audio_value:
        with st.spinner("Transcribing..."):
            transcription = st.session_state.client.audio.transcriptions.create(
                file=("audio.wav", audio_value.getvalue()),
                model="whisper-large-v3"
            )
            input_text = transcription.text
    else:
        input_text = prompt

    if input_text:
        st.session_state.messages.append({"role": "user", "content": input_text})
        with st.chat_message("user"):
            st.markdown(input_text)
            
        with st.chat_message("assistant"):
            # Clean stream: only extract content
            stream = st.session_state.client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.1-8b-instant",
                stream=True
            )
            
            # Use a generator to ensure we only get text content
            def response_generator():
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            
            full_response = st.write_stream(response_generator())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
