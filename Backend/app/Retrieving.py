from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv('NEO4J_USERNAME')
PASSWORD = os.getenv('NEO4J_PASSWORD')
URL = os.getenv('NEO4J_URL')


def create_retriever():
    # Creating vector store retriever 
    vectorstore = Neo4jVector.from_existing_graph(
        embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        url=URL,
        username=USERNAME,
        password=PASSWORD,
        index_name="clauseVectorIndex",  # Optional if default used
        node_label="Node",               # The label of the nodes where the embeddings are stored
        text_node_properties=["Chunk_Text"], # The property that holds the raw text
        embedding_node_property="Vectors"
    )

    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})


    # Creating BM25 Retriever 

    #Loading and rebuilding retriever 
    with open("bm25_docs.pkl", "rb") as f:
        loaded_docs = pickle.load(f)

    bm25_retriever = BM25Retriever.from_documents(loaded_docs, k=10)

    #Combining them

    ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],  # adjust weight if needed
    return_source_documents=True
    )

    return ensemble_retriever

if __name__ == "__main__":
    query = "What is differnce between B2B and B2C models?"
    ensemble_retriever = create_retriever()

    results = ensemble_retriever.get_relevant_documents(query)

    print(results)

