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

# --- 7. SAFE VOICE DICTATION BOX ---
st.markdown("### 🎙️ Voice Dictation")
components.html(
    """
    <div style="text-align: center; font-family: sans-serif;">
        <button id="mic-btn" style="
            background-color: #2e7d32; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 30px; 
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 85%;
        ">Tap to Speak</button>
        <div id="speech-status" style="color: #444; font-size: 15px; margin-top: 10px; padding: 5px; border-radius: 5px; background: #f9f9f9; min-height: 20px;">
            Click to start speaking...
        </div>
    </div>

    <script>
        const micBtn = document.getElementById('mic-btn');
        const statusText = document.getElementById('speech-status');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            micBtn.disabled = true;
            statusText.innerText = "Voice input not supported on this browser version.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            micBtn.addEventListener('click', () => {
                try {
                    recognition.start();
                    micBtn.style.background = '#d32f2f';
                    micBtn.innerText = "Listening...";
                    statusText.innerText = "Speak now...";
                } catch(e) {
                    recognition.stop();
                }
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                statusText.innerHTML = "<strong>Copy this:</strong> " + transcript;
                micBtn.style.background = '#2e7d32';
                micBtn.innerText = "Tap to Speak";
            };

            recognition.onerror = (event) => {
                statusText.innerText = "Microphone error: " + event.error;
                micBtn.style.background = '#2e7d32';
                micBtn.innerText = "Tap to Speak";
            };

            recognition.onend = () => {
                micBtn.style.background = '#2e7d32';
                micBtn.innerText = "Tap to Speak";
            };
        }
    </script>
    """,
    height=100,
)

# --- 8. HANDLE USER INPUT ---
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
        except Exception as e:
            st.error(f"Error: {e}")
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()

# --- 9. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
