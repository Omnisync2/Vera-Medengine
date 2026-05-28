import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
from datetime import datetime
import pypdf
import json

# ----------------------------
# 1. CONFIG
# ----------------------------
st.set_page_config(
    page_title="Vera | AI Health Companion",
    page_icon="⚕️",
    layout="wide"
)

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ----------------------------
# 2. SESSION STATE
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "mood" not in st.session_state:
    st.session_state.mood = "neutral"

if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now().date()

# Auto daily reset
if st.session_state.last_reset != datetime.now().date():
    st.session_state.messages = []
    st.session_state.last_reset = datetime.now().date()

# ----------------------------
# 3. VOICE ENGINE
# ----------------------------
components.html("""
<script>
window.veraSpeak = function(text) {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    utter.rate = 1;
    window.speechSynthesis.speak(utter);
}
</script>
""", height=0)

# ----------------------------
# 4. LIVE CLOCK + STOPWATCH
# ----------------------------
components.html("""
<div style="
    font-family: sans-serif;
    padding: 15px;
    border-radius: 16px;
    background: #f4f6f8;
    border: 1px solid #ddd;
    text-align: center;
    max-width: 420px;
    margin: auto;
">

    <div style="font-size: 14px; color: #666;">Live System Time</div>
    <div id="clock" style="font-size: 26px; font-weight: bold; color: #2e7d32;"></div>

    <hr style="margin:10px 0;">

    <div style="font-size: 14px; color: #666;">Focus Stopwatch</div>
    <div id="stopwatch" style="font-size: 22px; font-weight: bold;">00:00:00</div>

    <div style="margin-top:10px;">
        <button onclick="startStop()" style="padding:6px 14px; margin-right:5px;">Start / Stop</button>
        <button onclick="reset()" style="padding:6px 14px;">Reset</button>
    </div>
</div>

<script>
setInterval(() => {
    document.getElementById('clock').innerText =
        new Date().toLocaleTimeString('en-US', { hour12: false });
}, 1000);

let ms = 0;
let running = false;
let timer;

function update() {
    let s = Math.floor(ms / 1000) % 60;
    let m = Math.floor(ms / 60000) % 60;
    let h = Math.floor(ms / 3600000);

    document.getElementById('stopwatch').innerText =
        [h, m, s].map(v => v.toString().padStart(2, '0')).join(':');
}

function startStop() {
    if (running) {
        clearInterval(timer);
        running = false;
    } else {
        timer = setInterval(() => {
            ms += 1000;
            update();
        }, 1000);
        running = true;
    }
}

function reset() {
    clearInterval(timer);
    ms = 0;
    running = false;
    update();
}

update();
</script>
""", height=200)

# ----------------------------
# 5. SIDEBAR (FIXED PDF UPLOAD)
# ----------------------------
st.sidebar.title("Vera Control Panel")

enable_voice = st.sidebar.toggle("Enable Voice Output", value=True)

st.sidebar.markdown("### 📄 Document Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF or TXT",
    type=["pdf", "txt"]
)

if uploaded_file:
    st.sidebar.info(f"Loading: {uploaded_file.name}")

    try:
        if uploaded_file.type == "application/pdf":
            reader = pypdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            st.session_state.doc_text = text.strip()
        else:
            st.session_state.doc_text = uploaded_file.getvalue().decode("utf-8")

        st.sidebar.success("Document ready ✔")

    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

if st.sidebar.button("🧹 Reset Chat"):
    st.session_state.messages = []
    st.session_state.doc_text = ""
    st.rerun()

# ----------------------------
# 6. AI STATE ENGINE
# ----------------------------
def detect_state(text):
    text = text.lower()

    if any(w in text for w in ["stress", "tired", "overwhelmed", "anxious", "burnout"]):
        return "stress"
    elif any(w in text for w in ["study", "work", "focus", "task", "homework"]):
        return "focus"
    elif any(w in text for w in ["happy", "good", "great", "love", "amazing"]):
        return "positive"
    return "neutral"

# ----------------------------
# 7. SYSTEM PROMPT
# ----------------------------
def build_system_prompt():
    base = (
        "You are Vera, an advanced AI wellness companion. "
        "You support emotional balance, productivity, and document understanding. "
        "Respond naturally and concisely."
    )

    if st.session_state.mood == "stress":
        base += " User is stressed. Be calm and supportive."

    if st.session_state.mood == "focus":
        base += " User is in focus mode. Be structured and direct."

    if st.session_state.mood == "positive":
        base += " Match the user's positive energy lightly."

    if st.session_state.doc_text:
        base += " A document is available for analysis."

    return base

# ----------------------------
# 8. UI
# ----------------------------
st.title("Vera ⚕️ AI Health Companion")

st.markdown(f"""
### 🧠 Status Panel
- Mood: `{st.session_state.mood}`
- Messages: `{len(st.session_state.messages)}`
- Document: {"Loaded 📄" if st.session_state.doc_text else "None"}
""")

# ----------------------------
# 9. CHAT HISTORY
# ----------------------------
for msg in st.session_state.messages[-12:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# 10. CHAT INPUT
# ----------------------------
if prompt := st.chat_input("Talk to Vera..."):

    st.session_state.mood = detect_state(prompt)

    if "focus" in prompt.lower():
        st.session_state.mood = "focus"
    if "stress" in prompt.lower():
        st.session_state.mood = "stress"

    st.session_state.messages.append({"role": "user", "content": prompt})

    extra_context = []

    if st.session_state.doc_text:
        if any(k in prompt.lower() for k in ["document", "summarize", "this", "file"]):
            extra_context.append({
                "role": "system",
                "content": f"DOCUMENT:\n{st.session_state.doc_text[:12000]}"
            })

    system_prompt = {"role": "system", "content": build_system_prompt()}

    messages = [system_prompt] + extra_context + st.session_state.messages[-12:]

    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            stream=True
        )

        full = ""
        box = st.empty()

        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                box.markdown("🧠 Vera is thinking...\n\n" + full)

        st.session_state.messages.append({"role": "assistant", "content": full})

        if enable_voice:
            safe_text = json.dumps(full)
            components.html(f"<script>window.veraSpeak({safe_text});</script>", height=0)

    st.rerun()

# ----------------------------
# 11. FOOTER
# ----------------------------
st.markdown("---")
st.caption(
    f"Vera v3 • OmniSync • {datetime.now().strftime('%B %d, %Y')} • Powered by Groq"
)
