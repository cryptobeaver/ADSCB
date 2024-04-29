import streamlit as st
import cohere
import os
from dotenv import load_dotenv
import lancedb

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
db = lancedb.connect("./lancedb")

def search_table(table, query_text, limit):
    return table.search(query_text).metric("cosine").limit(limit).to_pandas()

def search_db(tbl, question, limit=5):
    results = search_table(tbl, question, limit)
    return results

def ask_question(question: str, table_name: str, prompt: str):
    tbl = db.open_table(table_name)

    result = search_db(tbl, question, limit=10)
    documents = result["text"].to_list()
    filenames = result["path"].to_list()
    print(result.path)
    # Convert each document string to a dictionary with additional metadata
    formatted_documents = [
        {"text": doc, "path": filename} for doc, filename in zip(documents, filenames)
    ]
    # print(formatted_documents)
    response = co.chat(
        model="command-r",
        message=question,
        preamble=prompt,
        temperature=0.1,
        documents=formatted_documents,
    )

    return response

st.title("La Assistanta GPT")

if "messages" not in st.session_state:
    st.session_state.messages = []

options = ["Langchain"]
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
            # Call the ask_question function directly
            response = ask_question(
                question=prompt,
                table_name=table_name.lower(),
                prompt=f"You are a helpful assistant who is answering technical questions about {selected_option}. Your answers always contain multiple fully functional code examples for each topic. You always answer thinking step by step.",
            )

            # Extract the answer text from the response
            parsed_response = response.text
            st.markdown(parsed_response)

    st.session_state.messages.append({"role": "assistant", "content": parsed_response})