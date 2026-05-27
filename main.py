import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(page_title="Vera: Your Personal Health Assistant ⚕️", page_icon="⚕️")

# --- 2. FIXED LIVE CLOCK COMPONENT ---
components.html(
    """
    <div id="clock" style="
        position: fixed; 
        top: 5px; 
        right: 15px; 
        font-family: sans-serif; 
        font-size: 16px; 
        color: #2e7d32; 
        font-weight: bold; 
        background: rgba(255, 255, 255, 0.9); 
        padding: 5px 12px; 
        border-radius: 20px; 
        border: 1px solid #2e7d32;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 999999;
        text-align: center;
        width: 100px;
    ">
        --:--
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """,
    height=45,
)

# --- 3. APP TITLE ---
st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 4. CONNECT TO GROQ ---
if "client" not in st.session_state:
    try:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("API Key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
        st.stop()

# --- 5. INITIALIZE HISTORY WITH VERA'S IDENTITY ---
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = (
        f"You are Vera, a helpful Health Assistant. "
        f"You were created by OmniSync. "
        f"The current date and time is {now}. "
        "If asked about your creator, state that you were developed by OmniSync."
    )
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

# --- 6. DISPLAY MESSAGES ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 7. SAFE VOICE INPUT COMPONENT ---
st.markdown("### 🎙️ Voice Input Accessibility")
components.html(
    """
    <div style="text-align: center; font-family: sans-serif;">
        <button id="mic-btn" style="
            background-color: #2e7d32; 
            color: white; 
            border: none; 
            padding: 15px; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 30px; 
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 85%;
            max-width: 400px;
        ">🎙️ Tap to Speak</button>
        <div id="speech-status" style="color: #444; font-size: 14px; margin-top: 10px; font-weight: bold; min-height: 20px;">
            Tap the button to dictate your query...
        </div>
    </div>

    <script>
        // Safely auto-request microphone permission for this frame container contextually
        if (window.frameElement) {
            window.frameElement.setAttribute('allow', 'microphone');
        }

        const micBtn = document.getElementById('mic-btn');
        const statusText = document.getElementById('speech-status');
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        
        if (!SpeechRecognition) {
            micBtn.disabled = true;
            statusText.innerText = "Voice feature unavailable on this browser version.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            micBtn.addEventListener('click', () => {
                try {
                    recognition.start();
                    micBtn.style.background = '#d32f2f';
                    micBtn.innerText = "Listening...";
                    statusText.innerText = "Speak clearly into your mic now...";
                } catch(e) {
                    recognition.stop();
                }
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(transcript);
                    statusText.innerHTML = '📋 <strong>Auto-Copied:</strong> "' + transcript + '"<br><span style="color: #2e7d32;">Tap the chatbox below, paste, and hit send!</span>';
                } else {
                    statusText.innerHTML = '<strong>Spoken:</strong> "' + transcript + '"';
                }
                resetBtn();
            };

            recognition.onerror = (event) => {
                statusText.innerText = "Mic error: " + event.error;
                resetBtn();
            };

            recognition.onend = () => {
                resetBtn();
            };

            function resetBtn() {
                micBtn.style.background = '#2e7d32';
                micBtn.innerText = "🎙️ Tap to Speak";
            }
        }
    </script>
    """,
    height=100,
)

# --- 8. STABLE VERA VOICE OUTPUT ENGINE ---
if "last_response" in st.session_state and st.session_state.last_response:
    clean_text = st.session_state.last_response.replace('"', '&quot;').replace('\n', ' ')
    
    components.html(
        f"""
        <div id="tts-data" data-text="{clean_text}"></div>
        <script>
            window.addEventListener('DOMContentLoaded', () => {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const dataEl = document.getElementById('tts-data');
                    if (dataEl) {{
                        const textToSpeak = dataEl.getAttribute('data-text');
                        const msg = new SpeechSynthesisUtterance(textToSpeak);
                        msg.lang = 'en-US';
                        msg.rate = 1.0;
                        msg.pitch = 1.1;
                        window.speechSynthesis.speak(msg);
                    }}
                }}
            }});
        </script>
        """,
        height=0,
    )
    st.session_state.last_response = None

# --- 9. HANDLE CHAT INPUT ---
if prompt := st.chat_input("Ask me about health, wellness, or anything else..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            valid_messages = [msg for msg in st.session_state.messages if isinstance(msg.get("content"), str)]
            
            completion = st.session_state.client.chat.completions.create(
                messages=valid_messages,
                model="llama-3.3-70b-versatile",
                stream=False
            )
            response = completion.choices[0].message.content
            
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.session_state.last_response = response
                st.rerun()
                
        except Exception as e:
            st.error(f"Error: {e}")
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()

# --- 10. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
    
