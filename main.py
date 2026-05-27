import streamlit as st
from groq import Groq

# Configure the page
st.set_page_config(page_title="Vera Medical Study Partner")
st.title("Vera - Medical Study Partner")

# Initialize the Groq client using the secret key from Streamlit settings
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you study?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Groq
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        # Display and store assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"Error: {e}")
