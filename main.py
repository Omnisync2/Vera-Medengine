import streamlit as st
from groq import Groq
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Vera: Your Personal Health Assistant ⚕️", page_icon="⚕️")
st.title("Vera: Your Personal Health Assistant ⚕️")

# --- 2. CONNECT TO GROQ ---
if "client" not in st.session_state:
    try:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("API Key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a concise and helpful health assistant."}]

# --- 3. THE "INSTANT" VOICE LISTENER (INJECTED JS) ---
# This script runs in the background, listens continuously, and types into the chat input.
components.html("""
    <script>
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[event.results.length - 1][0].transcript;
                
                // Finds the first available input box in the Streamlit app
                const input = window.parent.document.querySelector('textarea');
                
                if (input) {
                    input.value = transcript;
                    // Trigger standard events to ensure Streamlit registers the input
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', which: 13, keyCode: 13, bubbles: true
                    }));
                }
            };
            
            // Ensures the mic stays active even after periods of silence
            recognition.onend = () => { setTimeout(() => recognition.start(), 500); };
            recognition.start();
        }
    </script>
""", height=0)

# --- 4. CHAT ENGINE ---
# Displays previous messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handles user input and streaming response
if prompt := st.chat_input("Ask me about health, wellness, or anything else..."):
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
        
