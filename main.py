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
# We add a bit of padding at the bottom so content doesn't get hidden behind our new bottom bar
st.markdown("<div style='margin-bottom: 120px;'>", unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. PROCESS VOICE INPUT FROM URL ---
query_params = st.query_params
prompt = query_params.get("voice_input", None)

if prompt:
    st.query_params.clear() # Prevent endless looping reload
    
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
                
                clean_response = response.replace('"', '\\"').replace('\n', ' ')
                
                # Immediate speak output
                components.html(
                    f"""
                    <script>
                        if ('speechSynthesis' in window) {{
                            window.speechSynthesis.cancel();
                            const msg = new SpeechSynthesisUtterance("{clean_response}");
                            msg.lang = 'en-US';
                            msg.rate = 1.0;
                            msg.pitch = 1.1;
                            window.speechSynthesis.speak(msg);
                        }}
                    </script>
                    """,
                    height=0,
                )
        except Exception as e:
            st.error(f"Error: {e}")

# --- 8. FIXED BOTTOM ACCESSIBILITY VOICE BAR ---
# This anchors the microphone directly to the bottom of the mobile screen, replacing the clunky text bar
components.html(
    """
    <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111612;
        padding: 15px 0px;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
        text-align: center;
        font-family: sans-serif;
        z-index: 999999;
    ">
        <button id="mic-btn" style="
            background-color: #2e7d32; 
            color: white; 
            border: none; 
            padding: 15px; 
            font-size: 18px; 
            font-weight: bold; 
            border-radius: 30px; 
            cursor: pointer;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: background 0.2s;
        ">🎙️ Hold or Tap to Speak</button>
        <div id="speech-status" style="color: #a5d6a7; font-size: 14px; margin-top: 8px; font-weight: bold;">
            Ready for voice command...
        </div>
    </div>

    <script>
        const micBtn = document.getElementById('mic-btn');
        const statusText = document.getElementById('speech-status');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            micBtn.disabled = true;
            statusText.innerText = "Voice input unsupported on this browser.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            micBtn.addEventListener('click', () => {
                try {
                    recognition.start();
                    micBtn.style.background = '#d32f2f';
                    micBtn.innerText = "🛑 Vera is Listening...";
                    statusText.innerText = "Speak clearly into your device microphone now.";
                } catch(e) {
                    recognition.stop();
                }
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                statusText.innerText = "Sending query...";
                
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set("voice_input", transcript);
                window.location.href = currentUrl.toString();
            };

            recognition.onerror = (event) => {
                statusText.innerText = "Error: " + event.error;
                resetBtn();
            };
            
            recognition.onend = () => {
                resetBtn();
            };

            function resetBtn() {
                micBtn.style.background = '#2e7d32';
                micBtn.innerText = "🎙️ Hold or Tap to Speak";
            }
        }
    </script>
    """,
    height=110,
)

# --- 9. FOOTER ---
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
