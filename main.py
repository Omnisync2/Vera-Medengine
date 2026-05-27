import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
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

# --- 5. INITIALIZE STATE TRACKERS ---
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = (
        f"You are Vera, a helpful Health Assistant developed by OmniSync. "
        f"The current date and time is {now}. "
        "LANGUAGE RULE: Speak and respond in English by default. You are highly multilingual "
        "and capable of understanding any language perfectly (including Tagalog, Ilocano, Pangasinense, etc.). "
        "Only change your output language if the user explicitly asks you to change it, or if they talk to you directly "
        "in a non-English language. Otherwise, keep your responses in clean, supportive English. "
        "Keep your answers brief, friendly, and concise (1-3 sentences max)."
    )
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

# --- 6. HIGH-SPEED ACCESSIBILITY MIC COMPONENT ---
st.markdown("### 🎙️ Voice Input Accessibility")

# Catch input back from the JavaScript microphone component using Streamlit's official query param handler
incoming_speech = st.query_params.get("speech_result", "")

# Fixed the TypeError: removed invalid parameters from components.html
components.html(
    """
    <div id="mic-box" style="
        text-align: center; 
        font-family: sans-serif; 
        background: #1e293b; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #334155;
    ">
        <button id="speak-btn" style="
            background-color: #2e7d32; 
            color: white; 
            border: none; 
            padding: 14px 28px; 
            font-size: 18px; 
            font-weight: bold; 
            border-radius: 30px; 
            cursor: pointer; 
            width: 80%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        ">
            🎙️ Tap to Speak
        </button>
        <p id="mic-status" style="color: #94a3b8; font-size: 14px; margin-top: 10px; font-weight: 500;">
            Ready to listen
        </p>
    </div>

    <script>
        const btn = document.getElementById('speak-btn');
        const status = document.getElementById('mic-status');
        
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US'; 

            btn.addEventListener('click', () => {
                try {
                    recognition.start();
                } catch(e) {
                    status.innerText = "Mic already active.";
                }
            });

            recognition.onstart = () => {
                btn.style.backgroundColor = '#d32f2f';
                btn.innerText = "🛑 Listening...";
                status.innerText = "Speak clearly into your microphone...";
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.innerText = "Captured! Sending to chat...";
                
                // Instantly communicate back to parent window context without frame blockages
                const url = new URL(window.parent.location.href);
                url.searchParams.set("speech_result", transcript);
                window.parent.location.href = url.toString();
            };

            recognition.onerror = (e) => {
                btn.style.backgroundColor = '#2e7d32';
                btn.innerText = "🎙️ Tap to Speak";
                status.innerText = "Error capturing audio. Try again.";
            };

            recognition.onend = () => {
                btn.style.backgroundColor = '#2e7d32';
                btn.innerText = "🎙️ Tap to Speak";
            };
        } else {
            status.innerText = "Speech input not supported on this device window.";
        }
    </script>
    """,
    height=115,
)

# --- 7. DISPLAY CHAT MESSAGES CONTENT ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 8. PROCESSING LOGIC ENGINE ---
prompt = None

if incoming_speech:
    prompt = incoming_speech
    st.query_params.clear()  # Wipes parameter cleanly so it doesn't loop forever
else:
    prompt = st.chat_input("Ask me about health, wellness, or anything else...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            valid_messages = [msg for msg in st.session_state.messages if isinstance(msg.get("content"), str)]
            
            stream = st.session_state.client.chat.completions.create(
                messages=valid_messages,
                model="llama-3.1-8b-instant",
                stream=True 
            )
            
            placeholder = st.empty()
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response)
            
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.rerun()
                
        except Exception as e:
            st.error(f"Error: {e}")
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()

# --- 9. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
            
