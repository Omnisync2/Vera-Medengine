import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vera OS", page_icon="⚕️", layout="wide")

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. JS ENGINE ---
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

# --- 3. UI ---
st.title("Vera OS ⚕️")

if "messages" not in st.session_state: 
    st.session_state.messages = []

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# --- 4. PROCESSING ---
if prompt := st.chat_input("Talk to Vera..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        # We are using the standard, stable model only.
        stream = st.session_state.client.chat.completions.create(
            messages=[{"role": "system", "content": "You are Vera, a health assistant."}] + st.session_state.messages,
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
        
        # TRIGGER SPEECH
        sanitized = full_res.replace('"', '\\"').replace('\n', ' ')
        components.html(f"""<script>window.veraSpeak("{sanitized}");</script>""", height=0)
    st.rerun()
    
