import os
import json
from fastapi import FastAPI, Depends, Query
from elasticsearch import AsyncElasticsearch
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
        
app = FastAPI()

# Load the API key
def load_api_key(filepath):
    try:
        with open(filepath, 'r') as f:
            api = json.load(f)
            return api.get("api_key")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{filepath}' was not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON format in '{filepath}'.")
    
api_key_path = os.path.join(os.path.expanduser("~"), "Desktop", "ES_API_KEY.json")
es_client = AsyncElasticsearch(            
            hosts=[{"host": "localhost", "port": 9200, "scheme": "https"}],
            verify_certs=False,
            api_key=load_api_key(api_key_path)
)

# Initialize the SentenceTransformer model
model = SentenceTransformer("infly/inf-retriever-v1-1.5b", trust_remote_code=True)

app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],  # Adjust this to your React app's URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )

async def get_es_client():
    yield es_client

@app.get("/search/")
async def search(query: str = Query(..., min_length=1), es: AsyncElasticsearch = Depends(get_es_client)):
    # Generate embedding for the query
    task = 'Given a search query, retrieve relevant news articles'
    prompt = f"Instruct: {task}\nQuery: {query}"
    query_embedding = model.encode(prompt)

    # Construct the hybrid search query
    search_query = {
        "query": {
            "match": {
                "title": {
                    "query": query,
                    "boost": 0.9
                }
            }
        },
        "knn": {
            "field": "maintext_vector",
            "query_vector": query_embedding.tolist(),
            "k": 5,
            "num_candidates": 200,
            "boost": 0.1
        },
        "size": 10
    }

    # Perform the search
    response = await es.search(index="*", body=search_query)

    # Extract and return the hits
    # hits = response["hits"]["hits"]
    # return [
    #     {
    #         "source": hit["_source"]["source_domain"],
    #         "title": hit["_source"]["title"],
    #         "date published": hit["_source"]["date_publish"],
    #         "url": hit["_source"]["url"],
    #         "image": hit["_source"]["image_url"],
    #         "score": hit["_score"]
    #     }
    #     for hit in hits
    # ]
    hits = [
      {"title": hit["_source"]["title"],
       "url": hit["_source"]["url"],
       "description": hit["_source"].get("description", ""),
       "source": hit["_source"]["source_domain"],
       "date published": hit["_source"]["date_publish"],
       "image": hit["_source"]["image_url"],
       "score": hit["_score"]}
      for hit in response["hits"]["hits"]
    ]
    return {"results": hits}

@app.on_event("shutdown")
async def shutdown():
    await es_client.close()