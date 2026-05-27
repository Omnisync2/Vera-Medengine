import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="Vera: Your Personal Health Assistant", page_icon="🩺")
st.title("Vera: Your Personal Health Assistant")

# Connect to Groq
if "client" not in st.session_state:
    try:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("API Key missing! Please set it in Streamlit Secrets.")
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
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        try:
            # We filter the list to ensure all content is a string
            valid_messages = [msg for msg in st.session_state.messages if isinstance(msg.get("content"), str)]
            
            completion = st.session_state.client.chat.completions.create(
                messages=valid_messages,
                model="llama-3.3-70b-versatile",
                stream=False
            )
            response = completion.choices[0].message.content
            
            # 3. Only save if response is valid
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.warning("Vera returned an empty response.")
                
        except Exception as e:
            st.error(f"Error: {e}")
            # If it breaks, let's clear the last entry to prevent getting stuck
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()
