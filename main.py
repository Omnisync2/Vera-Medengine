import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera: Personal Health Assistant ⚕️", page_icon="⚕️", layout="wide")

# --- 2. CSS STYLING FOR THE UI ---
st.markdown("""
    <style>
        .chat-container { padding: 20px; border-radius: 10px; background: #f8fafc; }
        .stButton button { width: 100%; border-radius: 20px; font-weight: bold; }
        .mic-box { background: #1e293b; padding: 20px; border-radius: 15px; text-align: center; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC FUNCTIONS ---
def get_client():
    if "client" not in st.session_state:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return st.session_state.client

def init_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are Vera, a concise, supportive health assistant. Answer in 1-3 sentences."}
        ]

# --- 4. LIVE CLOCK COMPONENT ---
def render_clock():
    components.html("""
        <div id="clock" style="position:fixed; top:10px; right:20px; font-family:sans-serif; font-size:18px; color:#2e7d32; font-weight:bold; background:white; padding:5px 15px; border-radius:20px; border:1px solid #2e7d32;">--:--</div>
        <script>
            function updateClock() {
                const now = new Date();
                document.getElementById('clock').innerText = now.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
            }
            setInterval(updateClock, 1000); updateClock();
        </script>
    """, height=50)

# --- 5. MAIN APP FLOW ---
def main():
    init_chat()
    render_clock()
    
    st.title("Vera: Your Personal Health Assistant ⚕️")
    st.sidebar.markdown("### Settings")
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = [{"role": "system", "content": "You are Vera, a concise, supportive health assistant."}]
        st.rerun()

    # Voice Input Area
    st.markdown("### 🎙️ Voice Interaction")
    audio_value = st.audio_input("Record your question")
    
    # Process Voice
    if audio_value:
        with st.spinner("Vera is listening..."):
            client = get_client()
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_value.getvalue()),
                model="whisper-large-v3"
            )
            st.session_state.pending_text = transcription.text
            
    # Manual Confirmation Step
    if "pending_text" in st.session_state:
        st.info(f"**Transcription:** {st.session_state.pending_text}")
        if st.button("✅ Send to Vera"):
            st.session_state.messages.append({"role": "user", "content": st.session_state.pending_text})
            del st.session_state.pending_text
            st.rerun()

    # Display Chat
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Text Input
    prompt = st.chat_input("Or type here...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # AI Response Engine
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            client = get_client()
            stream = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.1-8b-instant",
                stream=True
            )
            full_res = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # Browser-based TTS trigger
            components.html(f"""
                <script>
                    const msg = new SpeechSynthesisUtterance("{full_res.replace('"', '')}");
                    window.speechSynthesis.speak(msg);
                </script>
            """, height=0)
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Groq | Developed by OmniSync")

if __name__ == "__main__":
    main()
    
