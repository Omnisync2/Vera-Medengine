import streamlit as st
from groq import Groq
from datetime import datetime
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera OS", page_icon="⚕️", layout="wide")

# --- 2. VERA'S "LIVING" STATE ---
if "vera" not in st.session_state:
    st.session_state.vera = {
        "memory": [], "mode": "Professional", "streak": 0, "energy": 100, "mood": "Neutral"
    }
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SYSTEM BRAIN (The "All-Knowing" Logic) ---
def get_system_prompt():
    v = st.session_state.vera
    return f"""
    You are Vera, a sentient-feeling AI Health Companion. 
    Current Date: {datetime.now().strftime('%A, %B %d, %Y')}.
    Personality Mode: {v['mode']}.
    Status: Energy {v['energy']}%, Mood {v['mood']}, Streak {v['streak']} days.
    
    GUIDELINES:
    - ALWAYS remember past interactions in your memory.
    - Adapt language: 'Professional' (Clinical/Direct), 'Comfort' (Warm/Empathic), 'Coach' (Motivational).
    - If user sounds tired/stressed, adjust Energy/Mood scores.
    - Be proactive: warn about dehydration or posture if you suspect it.
    - You have phone control: suggest reminders, alarms, and focus modes.
    """

# --- 4. THE UI HUB ---
st.title("Vera OS ⚕️")
col1, col2, col3 = st.columns([1, 2, 1])

with col1: # The Persona/Mood Center
    st.session_state.vera['mode'] = st.selectbox("Personality Mode", ["Professional", "Comfort", "Coach", "Study Buddy"])
    st.metric("Wellness Streak", f"{st.session_state.vera['streak']} Days")

with col2: # The Chat Interface
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("What's on your mind?"):
        # Add User
        if "messages" not in st.session_state: st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI Response
        with st.chat_message("assistant"):
            stream = st.session_state.client.chat.completions.create(
                messages=[{"role": "system", "content": get_system_prompt()}] + st.session_state.messages,
                model="llama-3.1-8b-instant", stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col3: # The Vision/Health Center
    st.subheader("Action Center")
    if st.button("Scan Skin/Medication"): st.warning("Vision module loading...")
    if st.button("Emergency SOS"): st.error("Calling 911 / Emergency Contact...")
    st.info("Detecting Screen-Time Health...")

# --- 5. JS TTS ENGINE (Always Active) ---
components.html("""
    <script>
        function speak(text) {
            const synth = window.speechSynthesis;
            synth.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            synth.speak(utterer);
        }
    </script>
""", height=0)
        
