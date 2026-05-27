import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Personal AI Health Companion", page_icon="⚕️", layout="wide")

# --- 2. JAVASCRIPT ENGINE (The Voice) ---
# This is a robust bridge. It will NOT crash your app.
components.html("""
    <script>
        function speakVera(text) {
            window.speechSynthesis.cancel(); // Clear any existing audio
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.pitch = 1.0;
            utterance.rate = 1.0;
            utterance.volume = 1.0;
            window.speechSynthesis.speak(utterance);
        }
        // Listen for message from Python to speak
        window.addEventListener('message', (event) => {
            if (event.data.type === 'speak') {
                speakVera(event.data.text);
            }
        });
    </script>
""", height=0)

# --- 3. SYSTEM INITIALIZATION ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_system_prompt():
    return (
        "You are Vera, a professional, empathetic, and all-knowing AI Health Companion. "
        f"Current date/time: {datetime.now().strftime('%A, %B %d, %Y, %H:%M:%S')}. "
        "You possess vast medical knowledge. You are supportive, precise, and professional. "
        "Your answers are always accurate, scientifically grounded, and empathetic. "
        "If a user mentions a critical emergency, advise them to seek professional medical help immediately. "
        "Keep responses conversational yet expert-level."
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# --- 4. UI COMPONENTS ---
st.title("Vera ⚕️ | Personal AI Health Companion")

# Live Clock
st.sidebar.markdown(f"**Local Time:** {datetime.now().strftime('%H:%M:%S')}")

# --- 5. VOICE INPUT (Native) ---
audio_value = st.audio_input("🎙️ Record your symptoms or questions")

if audio_value:
    with st.spinner("Analyzing..."):
        trans = st.session_state.client.audio.transcriptions.create(
            file=("audio.wav", audio_value.getvalue()), model="whisper-large-v3"
        ).text
        st.session_state.pending_text = trans

if "pending_text" in st.session_state:
    st.info(f"Captured: {st.session_state.pending_text}")
    if st.button("✅ Consult Vera"):
        st.session_state.messages.append({"role": "user", "content": st.session_state.pending_text})
        del st.session_state.pending_text
        st.rerun()

# --- 6. CHAT DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 7. PROCESSING & TTS TRIGGER ---
prompt = st.chat_input("Type your question here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        st.session_state.messages[0]["content"] = get_system_prompt()
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages, model="llama-3.1-8b-instant", stream=True
        )
        full_res = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        # Trigger Speech via JS
        components.html(f"""
            <script>
                window.parent.postMessage({{type: 'speak', text: "{full_res.replace('"', '')}"}}, '*');
            </script>
        """, height=0)
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Vera AI Engine")
        
