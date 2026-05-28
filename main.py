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
    page_title="Vera | AI Companion",
    page_icon="⚕️",
    layout="wide"
)

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ----------------------------
# 2. MEMORY STRUCTURE
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "mood" not in st.session_state:
    st.session_state.mood = "neutral"

# ----------------------------
# 3. SAFE VOICE ENGINE
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
# 4. SIDEBAR CONTROLS
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
# 5. DOCUMENT PROCESSOR (FIXED)
# ----------------------------
def process_document(file):
    try:
        if file.type == "application/pdf":
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text.strip()

        return file.getvalue().decode("utf-8")

    except Exception as e:
        return f"[Document Error: {str(e)}]"

if uploaded_file:
    st.session_state.doc_text = process_document(uploaded_file)
    st.sidebar.success("Document loaded successfully")

# ----------------------------
# 6. SIMPLE STATE DETECTOR (V1)
# ----------------------------
def detect_mood(text):
    text = text.lower()
    if any(w in text for w in ["stress", "tired", "overwhelmed", "anxious"]):
        return "stress"
    if any(w in text for w in ["happy", "good", "great", "love"]):
        return "positive"
    return "neutral"

# ----------------------------
# 7. SYSTEM PROMPT (STABLE CORE)
# ----------------------------
def build_system_prompt():
    base = (
        "You are Vera, an AI companion. "
        "Be calm, helpful, and concise. "
        "Adapt tone based on user mood. "
    )

    if st.session_state.mood == "stress":
        base += "User seems stressed. Be supportive and gentle."

    if st.session_state.doc_text:
        base += " A document is available for analysis when needed."

    return base

# ----------------------------
# 8. CHAT UI
# ----------------------------
st.title("Vera ⚕️ AI Companion")

for msg in st.session_state.messages[-12:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# 9. INPUT HANDLING
# ----------------------------
if prompt := st.chat_input("Talk to Vera..."):

    st.session_state.mood = detect_mood(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Inject document only when relevant
    context_messages = []

    if st.session_state.doc_text:
        if "document" in prompt.lower() or "this" in prompt.lower():
            context_messages.append({
                "role": "system",
                "content": f"DOCUMENT:\n{st.session_state.doc_text[:12000]}"
            })

    system_prompt = {
        "role": "system",
        "content": build_system_prompt()
    }

    messages = [system_prompt] + context_messages + st.session_state.messages[-12:]

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
        # VOICE (SAFE JSON)
        # ----------------------------
        if enable_voice:
            safe_text = json.dumps(full)
            components.html(
                f"<script>window.veraSpeak({safe_text});</script>",
                height=0
            )

    st.rerun()

# ----------------------------
# 10. FOOTER
# ----------------------------
st.markdown("---")
st.caption(f"Vera v2 • {datetime.now().strftime('%B %d, %Y')} • Powered by Groq")
