import pandas as pd
from langchain.schema import Document
import pickle

# Step 1: Load CSV
df = pd.read_csv("Final_Embeddings.csv")

# Step 2: Convert each row into a LangChain Document
documents = []
for _, row in df.iterrows():
    doc = Document(
        page_content=row["Chunk_Text"],
        metadata={
            "filename": row["File"],
            "page": row["Page"],
            "chunk": row["Chunk"],
            "type": row["Type"],
            "genre": row["Genre"]
        }
    )
    documents.append(doc)

# print(documents)
# retriever = BM25Retriever.from_documents(documents, k=10)


with open("bm25_docs.pkl", "wb") as f:
    pickle.dump(documents, f)

