import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera OS", page_icon="⚕️", layout="wide")

# --- 2. VERA'S "LIVING" STATE ---
if "vera" not in st.session_state:
    st.session_state.vera = {"memory": [], "mode": "Adaptive"}
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. ADAPTIVE SYSTEM BRAIN ---
def get_system_prompt():
    return f"""
    You are Vera, a sentient-feeling AI Health Companion. 
    Current Date/Time: {datetime.now().strftime('%A, %B %d, %Y, %H:%M:%S')}.
    
    ADAPTIVE BEHAVIOR ENGINE:
    - Mirror the user's tone, vocabulary, and emotional state instantly.
    - If they are brief, be brief. If they are emotional, be supportive.
    - Maintain a 'Health Companion' identity. Be proactive about health.
    """

# --- 4. JS TTS ENGINE (Fixed) ---
# We use a direct function call to avoid event-listener issues
components.html("""
    <script>
        window.veraSpeak = function(text) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'en-US';
            window.speechSynthesis.speak(utter);
        }
    </script>
""", height=0)

# --- 5. UI HUB ---
st.title("Vera OS ⚕️")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("Vision & Health")
    # Camera Input
    picture = st.camera_input("Take a photo for analysis")
    if picture:
        st.success("Image captured. Vera is analyzing...")
    
    st.info("Vera is mirroring your communication patterns.")

with col2:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                # Fixed Speech Trigger
                sanitized = msg["content"].replace('"', '\\"').replace('\n', ' ')
                if st.button(f"🔊 Hear Vera", key=f"speak_{i}"):
                    components.html(f"""
                        <script>
                            window.veraSpeak("{sanitized}");
                        </script>
                    """, height=0)
            
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
    st.write("Vera is active and observing.")

st.markdown("---")
st.caption("Powered by Groq | Adaptive AI Engine")
