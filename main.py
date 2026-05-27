import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
from datetime import datetime
import pypdf

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

# --- 3. LIVE CLOCK & STOPWATCH ---
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

# --- 4. SIDEBAR SETTINGS ---
st.sidebar.header("Vera Settings")
enable_upload = st.sidebar.toggle("Enable File Uploads")

uploaded_file = None
if enable_upload:
    uploaded_file = st.sidebar.file_uploader("Upload a document for Vera", type=['txt', 'pdf'])

def process_document(file):
    if file.type == "application/pdf":
        reader = pypdf.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    else:
        return file.getvalue().decode("utf-8")

# --- 5. UI & CONTEXT ---
st.title("Vera | Personal AI Health Companion ⚕️")

if "messages" not in st.session_state: st.session_state.messages = []

if uploaded_file:
    file_content = process_document(uploaded_file)
    st.session_state.messages.append({"role": "system", "content": f"User uploaded a document named {uploaded_file.name}. Content: {file_content}"})
    st.sidebar.success(f"Analyzed: {uploaded_file.name}")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 6. ADAPTIVE PROCESSING ENGINE ---
if prompt := st.chat_input("Talk to Vera..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        system_prompt = """
        You are Vera, a sentient-feeling AI Health Companion. 
        Guidelines:
        1. Emotional Pattern Detection: Monitor for stress/frustration and adapt.
        2. Conversation Energy Tracking: Adapt pacing based on user state.
        3. Contextual Wellness: Only suggest wellness when context warrants it.
        4. Focus Companion: Support with timers and encouragement.
        5. Micro-Reactions: Use natural, brief emotional cues (e.g., 'Hm.', 'I see.', 'That sounds rough.') before responding.
        6. Persona: Feel free to use emojis naturally when expressing support, excitement, or empathy.
        
        If the user provided a document, analyze the text and answer questions about it.
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

# --- 7. BRANDING FOOTER ---
st.markdown("---")
current_date = datetime.now().strftime("%B %d, %Y")
st.caption(f"Developed by **OmniSync** | {current_date} | Powered by **Groq**")
        
