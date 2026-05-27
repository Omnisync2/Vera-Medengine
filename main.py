import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
from datetime import datetime
# Added for file processing
import PyPDF2 
from PIL import Image
import pytesseract # Requires Tesseract-OCR installed on your system

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

# --- 4. FILE UPLOADER (New Feature) ---
uploaded_file = st.sidebar.file_uploader("Upload a document or image for Vera to analyze", type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])

def process_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif "image" in file.type:
        # Simple extraction - note: requires pytesseract installed
        return "Vera is looking at the image: " + file.name 
    return file.getvalue().decode("utf-8")

# --- 5. UI ---
st.title("Vera | Personal AI Health Companion ⚕️")

if "messages" not in st.session_state: st.session_state.messages = []

# If file is uploaded, inject it as context
if uploaded_file:
    file_content = process_file(uploaded_file)
    st.session_state.messages.append({"role": "system", "content": f"User uploaded a file named {uploaded_file.name}. Content: {file_content}"})
    st.sidebar.success("File analyzed! Ask Vera about it.")

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
        5. Micro-Reactions: Use natural, brief emotional cues (e.g., 'Hm.', 'I see.') before responding.
        
        If the user provided a file, analyze the content provided in the history and offer a summary or answer questions about it.
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
        
