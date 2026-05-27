import streamlit as st
from groq import Groq
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Vera", page_icon="🤖")
st.title("Vera")

# 2. Secure API Connection
# We use a helper function to avoid repeating the client setup
@st.cache_resource
def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        return None

client = get_groq_client()

if not client:
    st.error("API Key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. Initialize History
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages = [
        {"role": "system", "content": f"You are Vera. Today is {now}."}
    ]

# 4. Display Messages
# We iterate through everything except the system prompt
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Handle User Input
if prompt := st.chat_input("What's on your mind?"):
    # Immediately show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    try:
        with st.chat_message("assistant"):
            # Use the streaming approach for better responsiveness
            stream = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                stream=True,
            )
            response = st.write_stream(stream)
            
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"Something went wrong: {e}")
