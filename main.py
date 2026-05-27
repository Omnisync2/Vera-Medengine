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