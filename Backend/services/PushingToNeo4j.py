from neo4j import GraphDatabase
import pandas as pd
import numpy as np
import re
import os
from dotenv import load_dotenv

load_dotenv()


USERNAME = os.getenv('NEO4J_USERNAME')
PASSWORD = os.getenv('NEO4J_PASSWORD')
URL = os.getenv('NEO4J_URL')

# Load your CSV
df = pd.read_csv("Final_Embeddings.csv")
driver = GraphDatabase.driver(URL, auth=(USERNAME, PASSWORD))

def convert_str_to_array(s):
    """Convert vectors stored in string format into array"""
    l = re.sub("\n", "", s)[1:-1].split(" ")  # noqa: E741
    for e in l:
        if e == "":
            l.remove(e)
    return np.array(list(map(np.float32, l)))


with driver.session() as session:
    session.run("""
        CALL db.index.vector.createNodeIndex(
            $index_name,
            $node_label,
            $property_name,
            $dimension,
            $similarity_function
        )
    """,
    index_name="clauseVectorIndex",
    node_label="Node",
    property_name="Vectors",
    dimension=384,  
    similarity_function="cosine"
    )

driver.close()


with driver.session() as session:

        # Create chapter nodes
        for _, row in df.iterrows():
          session.run("""
                CREATE (c:Node {
                  Filename: $file_name,
                  Page: $page,
                  Chunk: $chunk,
                  Chunk_Text: $chunk_text,
                  Type: $type,
                  Genre: $genre,
                  Vectors: $vectors
                })
            """,
                file_name= row['File'],
                page = row['Page'],
                chunk = row['Chunk'],
                chunk_text = row['Chunk_Text'],
                type = row['Type'],
                genre = row['Genre'],
                vectors = convert_str_to_array(row['Vectors']))
driver.close()

