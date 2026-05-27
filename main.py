import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera | Personal AI Health Companion", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. JS ENGINE (Voice & Stopwatch) ---
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

# --- 3. LIVE CLOCK & STOPWATCH COMPONENT ---
components.html("""
    <div style="font-family:sans-serif; padding:15px; border:1px solid #ddd; border-radius:15px; background:#f0f2f6; text-align:center;">
        <div id="clock" style="font-size:24px; font-weight:bold; color:#2e7d32;">00:00:00</div>
        <div id="stopwatch" style="font-size:18px; margin-top:5px; color:#555;">00:00:00</div>
        <div style="margin-top:10px;">
            <button onclick="startStop()" style="padding:5px 15px;">Start/Stop</button>
            <button onclick="reset()" style="padding:5px 15px;">Reset</button>
        </div>
    </div>
    <script>
        setInterval(() => {
            document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-US', {hour12: false});
        }, 1000);
        let timer, ms = 0, running = false;
        function startStop() {
            if (running) { clearInterval(timer); running = false; }
            else { timer = setInterval(() => { ms+=1000; updateDisplay(); }, 1000); running = true; }
        }
        function reset() { clearInterval(timer); ms=0; running=false; updateDisplay(); }
        function updateDisplay() {
            let s = Math.floor(ms/1000) % 60, m = Math.floor(ms/60000) % 60, h = Math.floor(ms/3600000);
            document.getElementById('stopwatch').innerText = [h,m,s].map(v => v.toString().padStart(2, '0')).join(':');
        }
    </script>
""", height=150)

# --- 4. UI ---
st.title("Vera | Personal AI Health Companion ⚕️")

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 5. ADAPTIVE PROCESSING ENGINE ---
if prompt := st.chat_input("Talk to Vera..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        system_prompt = """
        You are Vera, a sentient-feeling AI Health Companion. 
        Mirror the user's current tone, vocabulary, and emotional state instantly. 
        If they are brief, be brief. If they are emotional, be supportive. 
        Maintain a 'Health Companion' identity and be proactive about health.
        """
        
        stream = st.session_state.client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            model="llama-3.1-8b-instant", 
            stream=True
        )
        
        full_res = ""
        placeholder = st.empty()
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res)
        
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        # Trigger Speech
        sanitized = full_res.replace('"', '\\"').replace('\n', ' ')
        components.html(f"""<script>window.veraSpeak("{sanitized}");</script>""", height=0)
    st.rerun()

# --- 6. BRANDING FOOTER ---
st.markdown("---")
st.caption("Developed by **OmniSync** | Powered by **Groq**")
                                     
