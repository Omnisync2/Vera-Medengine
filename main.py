import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Health Assistant", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a supportive health assistant."}]

st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 2. VOICE TO TEXT ENGINE ---
# We use a separate column for the mic so it stays clean
audio_value = st.audio_input("🎙️ Record your question")

if audio_value:
    with st.spinner("Transcribing..."):
        transcription = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()),
            model="whisper-large-v3",
        ).text
    
    # Store the transcription in session state so it doesn't disappear
    st.session_state.pending_text = transcription

# --- 3. THE "MANUAL SEND" UI ---
if "pending_text" in st.session_state:
    st.info(f"Transcription: {st.session_state.pending_text}")
    if st.button("✅ Send to Vera"):
        # Add to history and send
        st.session_state.messages.append({"role": "user", "content": st.session_state.pending_text})
        del st.session_state.pending_text
        st.rerun()

# --- 4. DISPLAY CHAT & PROCESS ---
# We only process if the LAST message was a user message
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Standard chat input for typing
prompt = st.chat_input("Or type your message here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# --- 5. AI RESPONSE ---
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True 
        )
        full_response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
