import streamlit as st
from agent import run_agent

st.title("🤖 Multi Tool AI Agent")

query = st.chat_input("Ask anything")

if query:

    st.chat_message("user").write(query)

    response = run_agent(query)

    st.chat_message("assistant").write(response)