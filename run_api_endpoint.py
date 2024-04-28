import cohere
import os
from dotenv import load_dotenv
import lancedb
from fastapi import FastAPI, Body

load_dotenv()

app = FastAPI()
co = cohere.Client(os.getenv("COHERE_API_KEY"))
db = lancedb.connect("~/lancedb")


def search_table(table, query_text, limit):
    return table.search(query_text).metric("cosine").limit(limit).to_pandas()


def search_db(tbl, question, limit=5):
    results = search_table(tbl, question, limit)
    return results


@app.post("/ask")
async def ask_question(
    question: str = Body(...), table_name: str = Body(...), prompt: str = Body(...)
):
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
        temperature=0.0,
        documents=formatted_documents,
    )

    return {"answer": response}
