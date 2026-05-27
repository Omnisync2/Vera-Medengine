import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera | Personal AI Health Companion", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. JS ENGINE (Speech) ---
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

# --- 3. SIDEBAR DASHBOARD ---
with st.sidebar:
    st.header("Vera OS")
    components.html("""
        <div style="font-family:sans-serif; padding:10px; border:1px solid #ddd; border-radius:10px; background:#f9f9f9;">
            <div id="date" style="font-size:12px; color:#666; text-align:center;"></div>
            <div id="clock" style="font-size:20px; font-weight:bold; color:#2e7d32; text-align:center;">00:00:00</div>
            <hr style="margin: 10px 0;">
            <div id="stopwatch" style="font-size:18px; text-align:center; font-family:monospace;">00:00:00</div>
            <div style="text-align:center; margin-top:10px;">
                <button onclick="startStop()">Start/Stop</button>
                <button onclick="reset()">Reset</button>
            </div>
        </div>
        <script>
            function update() {
                const now = new Date();
                document.getElementById('clock').innerText = now.toLocaleTimeString();
                document.getElementById('date').innerText = now.toLocaleDateString(undefined, {weekday:'short', month:'short', day:'numeric'});
            }
            setInterval(update, 1000); update();
            
            let timer, ms = 0, running = false;
            function startStop() {
                if (running) { clearInterval(timer); running = false; }
                else { timer = setInterval(() => { ms+=1000; updateDisplay(); }, 1000); running = true; }
            }
            function reset() { clearInterval(timer); ms=0; running=false; updateDisplay(); }
            function updateDisplay() {
                let s = Math.floor(ms/1000)%60, m = Math.floor(ms/60000)%60, h = Math.floor(ms/3600000);
                document.getElementById('stopwatch').innerText = [h,m,s].map(v => v.toString().padStart(2, '0')).join(':');
            }
        </script>
    """, height=180)
    
    if st.button("Clear History 🔄"):
        st.session_state.messages = []
        st.rerun()

# --- 4. MAIN UI ---
st.title("Vera | Personal AI Health Companion ⚕️")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 5. PROCESSING ENGINE ---
if prompt := st.chat_input("Talk to Vera..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # We inject the current time from the server so the AI is context-aware
        current_time = datetime.now().strftime("%I:%M %p, %A")
        system_prompt = f"""
        You are Vera, a sentient-feeling AI Health Companion. 
        Current Date/Time: {current_time}. 
        Mirror the user's emotional state. Be proactive about health. 
        If the user mentions being tired, offer rest advice.
        """
        
        stream = st.session_state.client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            model="llama-3.1-8b-instant", stream=True
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

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Developed by **OmniSync** | Powered by **Groq**")
        
