import streamlit as st
from groq import Groq
from datetime import datetime
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

# --- 3. SYSTEM BRAIN ---
def get_system_prompt():
    v = st.session_state.vera
    return f"""
    You are Vera, a sentient-feeling AI Health Companion. 
    Current Date: {datetime.now().strftime('%A, %B %d, %Y')}.
    Personality Mode: {v['mode']}.
    Status: Energy {v['energy']}%, Mood {v['mood']}, Streak {v['streak']} days.
    GUIDELINES: Respond concisely, be empathetic, and act as a health coach.
    """

# --- 4. JS TTS ENGINE (Fixed & Robust) ---
components.html("""
    <script>
        function speak(text) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'en-US';
            window.speechSynthesis.speak(utter);
        }
        // Listen for the trigger
        window.addEventListener('message', (event) => {
            if (event.data.type === 'speak') {
                speak(event.data.text);
            }
        });
    </script>
""", height=0)

# --- 5. THE UI HUB ---
st.title("Vera OS ⚕️")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.session_state.vera['mode'] = st.selectbox("Personality Mode", ["Professional", "Comfort", "Coach", "Study Buddy"])
    st.metric("Wellness Streak", f"{st.session_state.vera['streak']} Days")

with col2:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            stream = st.session_state.client.chat.completions.create(
                messages=[{"role": "system", "content": get_system_prompt()}] + st.session_state.messages,
                model="llama-3.1-8b-instant", stream=True
            )
            
            full_res = ""
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # TRIGGER SPEECH
            sanitized = full_res.replace('"', '\\"').replace('\n', ' ')
            components.html(f"""
                <script>
                    window.parent.postMessage({{type: 'speak', text: "{sanitized}"}}, '*');
                </script>
            """, height=0)
        st.rerun()

with col3:
    st.subheader("Action Center")
    if st.button("Emergency SOS"): st.error("Emergency protocol active.")
    st.info("System Status: Online")
            
