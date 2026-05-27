import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Vera: Your Personal Health Assistant ⚕️", page_icon="⚕️", layout="wide")

# --- 2. LIVE CLOCK COMPONENT ---
components.html("""
    <div id="clock" style="position:fixed; top:5px; right:15px; font-family:sans-serif; font-size:16px; color:#2e7d32; font-weight:bold; background:rgba(255,255,255,0.9); padding:5px 12px; border-radius:20px; border:1px solid #2e7d32; box-shadow:0 2px 8px rgba(0,0,0,0.15); z-index:9999;">--:--</div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
        }
        setInterval(updateClock, 1000); updateClock();
    </script>
""", height=45)

# --- 3. INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise health assistant."}]

st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 4. VOICE & TTS ENGINE ---
components.html("""
    <script>
        function speak(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }
    </script>
""", height=0)

# --- 5. VOICE INPUT WORKFLOW ---
audio_value = st.audio_input("🎙️ Record your voice (Transcribe, then click Send)")

if audio_value:
    with st.spinner("Transcribing..."):
        trans = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()), model="whisper-large-v3"
        ).text
        st.session_state.pending_text = trans

if "pending_text" in st.session_state:
    st.info(f"Captured: {st.session_state.pending_text}")
    if st.button("✅ Send to Vera"):
        st.session_state.messages.append({"role": "user", "content": st.session_state.pending_text})
        del st.session_state.pending_text
        st.rerun()

# --- 6. CHAT & PROCESSING ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = st.chat_input("Or type here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Process response if last message is user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages, model="llama-3.1-8b-instant", stream=True
        )
        full_response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Trigger browser speech
    components.html(f"""
        <script>
            const utterance = new SpeechSynthesisUtterance("{full_response.replace('"', '')}");
            window.speechSynthesis.speak(utterance);
        </script>
    """, height=0)
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
