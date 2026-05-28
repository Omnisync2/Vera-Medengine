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
# 4. LIVE CLOCK + STOPWATCH (RESTORED)
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
# 5. SIDEBAR
# ----------------------------
st.sidebar.title("Vera Control Panel")

enable_upload = st.sidebar.toggle("Enable Document Upload")
enable_voice = st.sidebar.toggle("Enable Voice Output", value=True)

if st.sidebar.button("🧹 Reset Chat"):
    st.session_state.messages = []
    st.session_state.doc_text = ""
    st.rerun()

uploaded_file = None
if enable_upload:
    uploaded_file = st.sidebar.file_uploader("Upload TXT or PDF", type=["txt", "pdf"])

# ----------------------------
# 6. DOCUMENT PROCESSOR (SAFE)
# ----------------------------
def process_document(file):
    try:
        if file.type == "application/pdf":
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text.strip()
        else:
            return file.getvalue().decode("utf-8")
    except Exception as e:
        return f"[Error reading document: {str(e)}]"

if uploaded_file:
    st.session_state.doc_text = process_document(uploaded_file)
    st.sidebar.success("Document loaded")

# ----------------------------
# 7. MOOD DETECTION
# ----------------------------
def detect_mood(text):
    text = text.lower()
    if any(w in text for w in ["stress", "tired", "overwhelmed", "anxious"]):
        return "stress"
    if any(w in text for w in ["happy", "good", "great", "love"]):
        return "positive"
    return "neutral"

# ----------------------------
# 8. SYSTEM PROMPT
# ----------------------------
def build_system_prompt():
    base = (
        "You are Vera, an AI health companion. "
        "Be calm, helpful, and concise. "
        "Adapt tone based on user emotional state."
    )

    if st.session_state.mood == "stress":
        base += " The user seems stressed. Respond gently and supportively."

    if st.session_state.doc_text:
        base += " A document is available for analysis if needed."

    return base

# ----------------------------
# 9. UI TITLE
# ----------------------------
st.title("Vera ⚕️ AI Health Companion")

# ----------------------------
# 10. CHAT HISTORY
# ----------------------------
for msg in st.session_state.messages[-12:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# 11. CHAT INPUT
# ----------------------------
if prompt := st.chat_input("Talk to Vera..."):

    st.session_state.mood = detect_mood(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    extra_context = []

    if st.session_state.doc_text:
        if "document" in prompt.lower() or "this" in prompt.lower():
            extra_context.append({
                "role": "system",
                "content": f"DOCUMENT:\n{st.session_state.doc_text[:12000]}"
            })

    system_prompt = {"role": "system", "content": build_system_prompt()}

    messages = (
        [system_prompt]
        + extra_context
        + st.session_state.messages[-12:]
    )

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
                box.markdown(full)

        st.session_state.messages.append({"role": "assistant", "content": full})

        # ----------------------------
        # VOICE OUTPUT (SAFE)
        # ----------------------------
        if enable_voice:
            safe_text = json.dumps(full)
            components.html(
                f"<script>window.veraSpeak({safe_text});</script>",
                height=0
            )

    st.rerun()

# ----------------------------
# 12. FOOTER
# ----------------------------
st.markdown("---")
st.caption(
    f"Vera v2 • Developed by OmniSync • {datetime.now().strftime('%B %d, %Y')} • Powered by Groq"
)
