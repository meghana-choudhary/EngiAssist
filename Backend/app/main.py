from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from Backend.app.Utils import get_wikipedia_context, get_aggregated_query, get_required_context, get_llm_response


load_dotenv()

PORT = os.getenv("PORT")
# OPIK_TRACK = os.getenv("OPIK_TRACK")

app = FastAPI()


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    queries: str
    history: str
    search_web: bool


@app.post("/chat/")
async def search(request: ChatRequest):
    chunks = []
    similar = {"similar_docs":[]}
    query = request.query.lower()
    queries = request.query.lower()
    if request.search_web:
        chunks = get_wikipedia_context(query)

    else:
        agg_query = get_aggregated_query(queries, query)
        chunks = get_required_context(agg_query)
        # print(request.history)
    
    response = get_llm_response(
        chunks, agg_query, request.history
    )
    similar["summary"] = response
    # if OPIK_TRACK == "True":
    #     log_metrics(request.query, response, chunks)
    return similar


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
