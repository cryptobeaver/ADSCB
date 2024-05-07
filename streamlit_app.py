import streamlit as st
import requests

st.title("La Assistanta GPT")

if "messages" not in st.session_state:
    st.session_state.messages = []

options = ["Langchain", "Streamlit"]
selected_option = st.sidebar.radio("Select an option", options)

# Update table name and prompt based on the selected option
table_name = selected_option

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Waiting for the AI response..."):
            # Make a request to your API endpoint
            response = requests.post(
                "https://api-for-ui-production.up.railway.app/ask",
                json={
                    "question": prompt,
                    "table_name": table_name.lower(),
                    "prompt": f"You are a helpful assistant who is answering technical questions about {selected_option}. Your answers always contain multiple fully functional code examples for each topic. You always answer thinking step by step.",
                },
            )

            # Extract the answer text from the JSON response
            if response.status_code == 200:
                parsed_response = response.json()["answer"]["text"]
                st.markdown(parsed_response)
                st.session_state.messages.append({"role": "assistant", "content": parsed_response})
            else:
                st.error(f"Error: {response.status_code}")
