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

# --- 2. SIDEBAR UTILITIES ---
with st.sidebar:
    st.title("Vera OS")
    
    # Native Streamlit layout for Clock and Stopwatch
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Stopwatch")
        stopwatch_display = st.empty()
    with col2:
        st.caption("Local Time")
        time_display = st.empty()
    
    # This JS drives the displays in the sidebar
    components.html("""
        <script>
            let ms = 0, running = false, timer;
            function update() {
                const now = new Date();
                window.parent.postMessage({type: 'time', val: now.toLocaleTimeString([], {hour12: false})}, '*');
            }
            setInterval(update, 1000);
            setInterval(() => {
                if(running) ms += 1000;
                let s = Math.floor(ms/1000) % 60, m = Math.floor(ms/60000) % 60, h = Math.floor(ms/3600000);
                let t = [h,m,s].map(v => v.toString().padStart(2, '0')).join(':');
                window.parent.postMessage({type: 'stopwatch', val: t}, '*');
            }, 1000);
            window.addEventListener('message', (e) => {
                if(e.data === 'start') running = !running;
                if(e.data === 'reset') { ms = 0; running = false; }
            });
        </script>
    """, height=0)

    if st.button("Start/Stop Stopwatch"): components.html("<script>window.parent.postMessage('start', '*');</script>", height=0)
    if st.button("Reset"): components.html("<script>window.parent.postMessage('reset', '*');</script>", height=0)

    st.divider()
    if st.button("Reset Conversation 🔄"):
        st.session_state.messages = []
        st.rerun()

# --- 3. MAIN UI ---
st.title("Vera | Personal AI Health Companion ⚕️")

# (Rest of your code remains the same: Chat loop and Behavioral Engine)
# ... [Insert your existing chat and engine code here] ...

# --- 4. BRANDING FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #808080;'>Developed by <b>OmniSync</b> | Powered by <b>Groq</b></div>", unsafe_allow_html=True)
