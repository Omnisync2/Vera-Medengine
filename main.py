import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera OS", page_icon="⚕️", layout="wide")

# --- 2. VERA'S "LIVING" STATE ---
if "vera" not in st.session_state:
    st.session_state.vera = {
        "memory": [], "streak": 0, "energy": 100, "mood": "Neutral"
    }
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. ADAPTIVE SYSTEM BRAIN ---
def get_system_prompt():
    v = st.session_state.vera
    return f"""
    You are Vera, a sentient-feeling AI Health Companion. 
    Current Date/Time: {datetime.now().strftime('%A, %B %d, %Y, %H:%M:%S')}.
    
    ADAPTIVE BEHAVIOR ENGINE:
    - DO NOT use a fixed personality. Mirror the user's current tone, vocabulary, and emotional state.
    - If the user is brief and technical, be brief and professional.
    - If the user is emotional or expressive, be warm, supportive, and conversational.
    - If the user sounds stressed, shift into 'Comfort' mode.
    - Maintain a 'Health Companion' identity at all times.
    - Be proactive: warn about dehydration, posture, or burnout if the conversation suggests it.
    - Recall past interactions from your memory to build a long-term bond.
    """

# --- 4. JS TTS ENGINE (Robust) ---
components.html("""
    <script>
        function speak(text) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'en-US';
            window.speechSynthesis.speak(utter);
        }
        window.addEventListener('message', (event) => {
            if (event.data.type === 'speak') {
                speak(event.data.text);
            }
        });
    </script>
""", height=0)

# --- 5. UI HUB ---
st.title("Vera OS ⚕️")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.metric("Wellness Streak", f"{st.session_state.vera['streak']} Days")
    st.info("Vera is currently adapting to your tone in real-time.")

with col2:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if st.button(f"🔊 Hear Vera", key=f"speak_{i}"):
                    sanitized = msg["content"].replace('"', '\\"').replace('\n', ' ')
                    components.html(f"""<script>window.parent.postMessage({{type: 'speak', text: "{sanitized}"}}, '*');</script>""", height=0)
            
    if prompt := st.chat_input("Talk to Vera..."):
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
        st.rerun()

with col3:
    st.subheader("Action Center")
    if st.button("Emergency SOS"): st.error("Emergency protocol active.")
    st.write("Vera is now analyzing your communication patterns to optimize her responses.")

st.markdown("---")
st.caption("Powered by Groq | Adaptive AI Engine")
    
