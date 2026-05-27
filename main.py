import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

# --- 2. INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Vera, a concise, supportive health assistant."}
    ]
    st.session_state.start_time = datetime.now()

# --- 3. LAYOUT ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("Vera: Your Personal Health Assistant ⚕️")
with col2:
    # Use built-in ZoneInfo, no need for 'pytz' library
    st.markdown(f"**{datetime.now(ZoneInfo('Asia/Manila')).strftime('%H:%M:%S')}**")

# --- 4. CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. INPUT ENGINE ---
# We store the input in a variable, but do not trigger rerun until AFTER processing
audio_value = st.audio_input("🎙️ Record your question")
prompt = st.chat_input("Or type here...")

input_text = None

if audio_value:
    with st.spinner("Transcribing..."):
        try:
            transcription = st.session_state.client.audio.transcriptions.create(
                file=("audio.wav", audio_value.getvalue()),
                model="whisper-large-v3"
            )
            input_text = transcription.text
        except Exception as e:
            st.error("Could not transcribe audio. Please try again.")
            st.stop()
elif prompt:
    input_text = prompt

# --- 6. PROCESSING (Linear Flow) ---
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
        
        # Generator for clean text-only output
        def stream_generator(stream_obj):
            for chunk in stream_obj:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        full_response = st.write_stream(stream_generator(stream))
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Force clean refresh to wipe inputs
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
            
