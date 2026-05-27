import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image
import io
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera OS", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. JS ENGINE (Fixed Auto-Speak) ---
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

# --- 3. VISION HELPER ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- 4. UI ---
st.title("Vera OS ⚕️")
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Vision")
    if "show_cam" not in st.session_state: st.session_state.show_cam = False
    if st.button("📸 Toggle Camera"): st.session_state.show_cam = not st.session_state.show_cam
    
    img_file = None
    if st.session_state.show_cam:
        img_file = st.camera_input("Take a photo")

with col2:
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Talk to Vera..."):
        content_payload = [{"type": "text", "text": prompt}]
        
        # If camera photo exists, attach it to the vision request
        if img_file:
            img_bytes = img_file.getvalue()
            content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img_bytes)}"}})
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            # Use a Vision-capable model
            stream = st.session_state.client.chat.completions.create(
                messages=[{"role": "user", "content": content_payload}],
                model="llama-3.2-11b-vision-preview", stream=True
            )
            
            full_res = ""
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # TRIGGER SPEECH
            sanitized = full_res.replace('"', '\\"').replace('\n', ' ')
            components.html(f"""<script>window.veraSpeak("{sanitized}");</script>""", height=0)
        st.rerun()
        
