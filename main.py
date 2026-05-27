import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(page_title="Vera: Your Personal Health Assistant ⚕️", page_icon="⚕️")

# --- 2. FIXED LIVE CLOCK COMPONENT ---
components.html(
    """
    <div id="clock" style="
        position: fixed; 
        top: 5px; 
        right: 15px; 
        font-family: sans-serif; 
        font-size: 16px; 
        color: #2e7d32; 
        font-weight: bold; 
        background: rgba(255, 255, 255, 0.9); 
        padding: 5px 12px; 
        border-radius: 20px; 
        border: 1px solid #2e7d32;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 999999;
        text-align: center;
        width: 100px;
    ">
        --:--
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """,
    height=45,
)

# --- 3. APP TITLE ---
st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 4. CONNECT TO GROQ ---
if "client" not in st.session_state:
    try:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("API Key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
        st.stop()

# --- 5. INITIALIZE HISTORY WITH VERA'S IDENTITY ---
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = (
        f"You are Vera, a helpful Health Assistant. "
        f"You were created by OmniSync. "
        f"The current date and time is {now}. "
        "If asked about your creator, state that you were developed by OmniSync."
    )
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

# --- 6. DISPLAY MESSAGES ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 7. SAFE VOICE INPUT COMPONENT ---
st.markdown("### 🎙️ Voice Input Accessibility")
components.html(
    """
    <div style="text-align: center; font-family: sans-serif;">
        <button id="mic-btn" style="
            background-color: #2e7d32; 
            color: white; 
            border: none; 
            padding: 15px; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 30px; 
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 85%;
            max-width: 400px;
        ">🎙️ Tap to Speak</button>
        <div id="speech-status" style="color: #444; font-size: 14px; margin-top: 10px; font-weight: bold; min-height: 20px;">
            Tap the button to dictate your query...
        </div>
    </div>

    <script>
        const micBtn = document.getElementById('mic-btn');
        const statusText = document.getElementById('speech-status');
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        
        if (!SpeechRecognition) {
            micBtn.disabled = true;
            statusText.innerText = "Voice feature unavailable on this browser version.";
        } else {

    
