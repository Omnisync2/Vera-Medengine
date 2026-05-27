import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit as st

# --- LIVE CLOCK COMPONENT ---
st.markdown("""
    <div id="clock" style="
        position: fixed; 
        top: 15px; 
        right: 20px; 
        font-family: sans-serif; 
        font-size: 16px; 
        color: #333; 
        font-weight: bold; 
        background: rgba(255, 255, 255, 0.9); 
        padding: 5px 12px; 
        border-radius: 20px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 9999;">
        --:--
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
""", unsafe_allow_html=True)

# --- YOUR VERA CODE STARTS HERE ---
# Everything else for Vera goes below this line
st.title("Hello! I am Vera.")
st.write("How can I help you with your health today?")

# Example of where your existing logic would continue:
# if st.button("Check status"):
#    st.write("Vera is online!")

# Configure the page
st.set_page_config(page_title="Vera: Your Personal Health Assistant", page_icon="🩺")
st.title("Vera: Your Personal Health Assistant")

# Connect to Groq
if "client" not in st.session_state:
    try:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("API Key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
        st.stop()

# Initialize History with Vera's Identity
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # This is the "Origin Story" instruction
    system_instruction = (
        f"You are Vera, a helpful Health Assistant. "
        f"You were created by OmniSync. "
        f"The current date and time is {now}. "
        "If asked about your creator, state that you were developed by OmniSync."
    )
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

# Display Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask me about health, wellness, or anything else..."):
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        try:
            # Filter the list to ensure only strings are passed
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

# Footer Crediting Groq
st.markdown("---")
st.caption("Powered by Groq | Developed by OmniSync")
