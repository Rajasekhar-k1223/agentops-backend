# task_memory.py - FAISS Memory Store for Task Logs (Optional)

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
import os

# Load API key from environment or .env
from dotenv import load_dotenv
load_dotenv()

embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# In-memory FAISS store (use persistent later)
faiss_index = FAISS(embedding_function=embedding)

def store_log(task_id: str, log: str):
    doc = Document(page_content=log, metadata={"task_id": task_id})
    faiss_index.add_documents([doc])

def query_logs(query: str, k=3):
    return faiss_index.similarity_search(query, k=k)

# Test
if __name__ == "__main__":
    store_log("task-1", "nginx failed: permission denied")
    print("\n=== Similar Logs ===")
    print(query_logs("Why did nginx fail?"))
