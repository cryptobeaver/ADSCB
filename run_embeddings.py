import os
import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
registry = EmbeddingFunctionRegistry().get_instance()
cohere = registry.get(
    "cohere"
).create()  # uses multi-lingual model by default (768 dim)


class Schema(LanceModel):
    vector: Vector(cohere.ndims()) = cohere.VectorField()
    text: str = cohere.SourceField()
    url: str
    path: str
    id: str


def create_table(db, table_name, schema, mode="overwrite"):
    return db.create_table(table_name, schema=schema, mode=mode)


def add_data_to_table(table, data):
    table.add(data)


def read_file_content(file_path):
    with open(file_path, "r") as f:
        return f.read()


def create_data_object(content, url, file_path):
    md5_hash = hashlib.md5(file_path.encode()).hexdigest()
    return {
        "text": content,
        "url": url,
        "path": file_path,
        "id": md5_hash,
    }


def read_parsed_files(folder_path, base_url):
    datasets = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".parsed"):
                file_path = os.path.join(root, file)
                content = read_file_content(file_path)
                url = (
                    base_url + file_path[len(folder_path) : -7]
                )  # Remove ".parsed" extension
                data_object = create_data_object(content, url, file_path)
                datasets.append(data_object)
    return datasets


def process_batch(batch):
    data = []
    for x in batch:
        data.append(
            {"text": x["text"], "url": x["url"], "path": x["path"], "id": x["id"]}
        )
    return data


def process_datasets_in_batches(datasets, batch_size, table):
    for i in range(0, len(datasets), batch_size):
        batch = datasets[i : i + batch_size]
        data = process_batch(batch)
        if data:
            add_data_to_table(table, data)


def main():
    db = lancedb.connect("lancedb")
    base_url_for_docs = "https://python.langchain.com"
    table_name = "langchain"
    folder_path = f"./{table_name}-docs/"

    tbl_cohere = create_table(db, table_name, Schema)
    print(f"Reading files from {folder_path}")
    datasets = read_parsed_files(folder_path, base_url=base_url_for_docs)

    batch_size = 1000
    process_datasets_in_batches(datasets, batch_size, tbl_cohere)

    print(f"Added {len(datasets)} documents to table {table_name}")


if __name__ == "__main__":
    main()
