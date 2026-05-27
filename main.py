import streamlit as st
from groq import Groq
from datetime import datetime

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

# Initialize History
if "messages" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages = [
        {"role": "system", "content": f"You are Vera, a helpful Health Assistant. Today is {now}."}
    ]

# Display Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask me about health, wellness, or anything else..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        try:
            completion = st.session_state.client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                stream=False
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
