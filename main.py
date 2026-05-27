import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Vera: Your Personal Health Assistant ⚕️", page_icon="⚕️", layout="wide")

# --- 2. LIVE CLOCK (FIXED) ---
components.html("""
    <div id="clock" style="position: fixed; top: 10px; right: 20px; font-family: sans-serif; font-size: 16px; color: #2e7d32; font-weight: bold; background: rgba(255, 255, 255, 0.9); padding: 5px 12px; border-radius: 20px; border: 1px solid #2e7d32; z-index: 9999;">--:--</div>
    <script>
        function updateClock() { document.getElementById('clock').innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
        setInterval(updateClock, 1000); updateClock();
    </script>
""", height=40)

st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 3. GROQ CLIENT ---
if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a concise, supportive health assistant. Answer in 1-3 sentences."}]

# --- 4. THE CONTINUOUS LOOP ENGINE ---
components.html("""
    <script>
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        let recognition;

        function startListening() {
            if (recognition) recognition.stop();
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const input = window.parent.document.querySelector('textarea');
                if (input) {
                    input.value = transcript;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', which: 13, keyCode: 13, bubbles: true }));
                }
            };
            recognition.start();
        }

        // --- OUTPUT: TEXT TO SPEECH ---
        function speak(text) {
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.1;
            // INTEGRATED LOOP: When she finishes speaking, trigger the mic again!
            msg.onend = () => { setTimeout(startListening, 500); };
            window.speechSynthesis.speak(msg);
        }

        // Start initial listen
        setTimeout(startListening, 1000);
    </script>
""", height=0)

# --- 5. CHAT UI & PROCESSING ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Ask me about health..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = st.session_state.client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            stream=True
        )
        placeholder = st.empty()
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Trigger the browser to speak and re-link the loop
        # Escaping quotes to prevent syntax errors
        safe_response = full_response.replace("'", "\\'").replace('"', '\\"')
        components.html(f"<script>speak('{safe_response}')</script>", height=0)

# --- 9. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
