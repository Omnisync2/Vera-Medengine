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

# --- 5. INITIALIZE STATE VARIABLE TRACKERS ---
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = (
        f"You are Vera, a helpful Health Assistant developed by OmniSync. "
        f"The current date and time is {now}. "
        "LANGUAGE RULE: Speak and respond in English by default. You are highly multilingual "
        "and capable of understanding any language perfectly (including Tagalog, Ilocano, Pangasinense, etc.). "
        "Only change your output language if the user explicitly asks you to change it, or if they talk to you directly "
        "in a non-English language. Otherwise, keep your responses in clean, supportive English. "
        "Keep your answers brief, friendly, and concise (1-3 sentences max) so it is fast to process and speak aloud."
    )
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

if "last_response" not in st.session_state:
    st.session_state.last_response = None

# --- 6. ROUTE INCOMING VOICE PARAMS ---
voice_prompt = st.query_params.get("voice_input", None)
exit_signal = st.query_params.get("exit_voice", None)

if exit_signal:
    st.session_state.voice_mode = False
    st.query_params.clear()
    st.rerun()

# --- 7. DISPLAY CHAT MESSAGES CONTENT ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 8. SMART VOICE ENGINE CONTROLLER ---
if st.session_state.voice_mode:
    st.markdown("### 🟢 Continuous Voice Mode Active")
    
    if st.button("❌ Exit Voice Mode & Return to Chat"):
        st.session_state.voice_mode = False
        st.rerun()

    should_speak = "true" if st.session_state.last_response else "false"
    speak_text = st.session_state.last_response.replace('"', '&quot;').replace('\n', ' ') if st.session_state.last_response else ""

    components.html(
        f"""
        <div id="voice-container" style="
            text-align: center; 
            font-family: sans-serif; 
            background: #e8f5e9; 
            padding: 20px; 
            border-radius: 15px; 
            border: 2px dashed #2e7d32;
            cursor: pointer;
        ">
            <h4 style="margin: 0 0 10px 0; color: #2e7d32;">🎙️ Continuous Conversation Active</h4>
            <div id="voice-status" style="font-size: 15px; font-weight: bold; color: #333;">
                Initializing Voice Engine...
            </div>
            <p style="font-size: 12px; color: #666; margin: 10px 0 0 0;">(If listening stops, simply tap inside this green box to reply)</p>
        </div>

        <script>
            if (window.frameElement) {{
                window.frameElement.setAttribute('allow', 'microphone');
            }}

            const container = document.getElementById('voice-container');
            const statusText = document.getElementById('voice-status');
            
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            let recognition = null;
            
            if (SpeechRecognition) {{
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.lang = 'en-US'; 

                recognition.onstart = () => {{
                    container.style.background = '#ffebee';
                    container.style.borderColor = '#d32f2f';
                    statusText.innerHTML = '<span style="color: #d32f2f;">🔴 Vera is listening... Speak now!</span>';
                }};
                
                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    statusText.innerText = "Processing what you said...";
                    
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set("voice_input", transcript);
                    window.parent.location.href = currentUrl.toString();
                }};
                
                recognition.onerror = (event) => {{
                    container.style.background = '#e8f5e9';
                    container.style.borderColor = '#2e7d32';
                    statusText.innerHTML = '✨ Ready! Tap anywhere inside this box to talk.';
                }};
                
                recognition.onend = () => {{
                    if (statusText.innerText.indexOf("Processing") === -1) {{
                        container.style.background = '#e8f5e9';
                        container.style.borderColor = '#2e7d32';
                        statusText.innerHTML = '✨ Ready! Tap anywhere inside this box to talk.';
                    }}
                }};
                
                container.addEventListener('click', () => {{
                    try {{ recognition.start(); }} catch(e) {{}}
                }});
            }}

            const shouldSpeak = {should_speak};
            const textToSpeak = "{speak_text}";

            window.addEventListener('DOMContentLoaded', () => {{
                if (shouldSpeak && 'speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const msg = new SpeechSynthesisUtterance(textToSpeak);
                    
                    msg.rate = 1.1; // Slightly speed up speech delivery
                    msg.pitch = 1.1;
                    
                    msg.onend = () => {{
                        if (recognition) {{
                            try {{ recognition.start(); }} catch(e) {{}}
                        }}
                    }};
                    
                    statusText.innerHTML = '🔊 <strong>Vera is speaking...</strong>';
                    window.speechSynthesis.speak(msg);
                }} else if (recognition) {{
                    setTimeout(() => {{
                        try {{ recognition.start(); }} catch(e) {{}}
                    }}, 300);
                }}
            }});
        </script>
        """,
        height=130,
    )
    # Clear the response flag so it doesn't repeat on a standard refresh
    st.session_state.last_response = None

else:
    st.markdown("---")
    if st.button("🎙️ Enter Continuous Voice Mode"):
        st.session_state.voice_mode = True
        st.rerun()

# --- 9. STREAMING ENGINE PIPELINE CONTEXT ---
prompt = None

if voice_prompt:
    prompt = voice_prompt
    st.query_params.clear()
elif not st.session_state.voice_mode:
    prompt = st.chat_input("Ask me about health, wellness, or anything else...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            valid_messages = [msg for msg in st.session_state.messages if isinstance(msg.get("content"), str)]
            
            # Request streaming text data directly from Groq
            stream = st.session_state.client.chat.completions.create(
                messages=valid_messages,
                model="llama-3.1-8b-instant",
                stream=True 
            )
            
            # Setup a placeholder box so text dynamically renders in real-time
            placeholder = st.empty()
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response) # Streams instantly to the screen!
            
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.last_response = full_response
                
                # If using your voice, instantly rerun once to push the complete sentence to the speech engine
                if st.session_state.voice_mode:
                    st.rerun()
                
        except Exception as e:
            st.error(f"Error: {e}")
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()

# --- 10. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
    
