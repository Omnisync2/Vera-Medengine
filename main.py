import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Personal AI Health Companion", page_icon="⚕️", layout="wide")

# --- 2. JAVASCRIPT ENGINE (TTS Bridge) ---
components.html("""
    <script>
        function speakVera(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }
        window.addEventListener('message', (event) => {
            if (event.data.type === 'speak') {
                speakVera(event.data.text);
            }
        });
    </script>
""", height=0)

# --- 3. INITIALIZATION ---
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

# --- 4. LIVE CLOCK COMPONENT ---
components.html("""
    <div id="clock" style="position:fixed; top:10px; right:20px; font-family:sans-serif; font-size:16px; color:#2e7d32; font-weight:bold; background:white; padding:5px 12px; border-radius:20px; border:1px solid #2e7d32; z-index:9999;">--:--</div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
        }
        setInterval(updateClock, 1000); updateClock();
    </script>
""", height=40)

# --- 5. UI LAYOUT ---
st.title("Vera ⚕️ | Personal AI Health Companion")

# --- 6. VOICE INPUT (Native & Stable) ---
audio_value = st.audio_input("🎙️ Record your symptoms or question")
if audio_value:
    with st.spinner("Analyzing audio..."):
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

# --- 7. CHAT DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 8. PROCESSING ENGINE ---
prompt = st.chat_input("Or type here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        st.session_state.messages[0]["content"] = get_system_prompt()
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages, model="llama-3.1-8b-instant", stream=True
        )
        
        full_res = ""
        placeholder = st.empty()
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res)
        
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        # Audio Button
        sanitized = full_res.replace('"', '\\"').replace('\n', ' ')
        if st.button("🔊 Hear Vera Speak"):
            components.html(f"""
                <script>
                    window.parent.postMessage({{type: 'speak', text: "{sanitized}"}}, '*');
                </script>
            """, height=0)
    st.rerun()

st.markdown("---")
st.caption("Powered by Groq | Vera AI Engine")
        
