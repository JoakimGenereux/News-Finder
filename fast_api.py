import os
import json
import datetime
from fastapi import FastAPI, Depends, Query, HTTPException
from elasticsearch import AsyncElasticsearch
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Union
        
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


def build_date_range_filter(date_str: str):
    now = datetime.datetime.now(datetime.timezone.utc)
    if date_str == "today":
        gte = "now/d"
    elif date_str == "24h":
        gte = "now-24h"
    elif date_str == "week":
        gte = "now-7d"
    elif date_str == "month":
        gte = "now-30d"
    elif date_str == "3months":
        gte = "now-90d"
    else:
        raise ValueError(f"Invalid date filter: {date_str}")
    return {"range": {"date_publish": {"gte": gte}}}

@app.get("/latest/")
async def latest(es: AsyncElasticsearch = Depends(get_es_client)):
    # Get articles by date_publish in descending order
    body = {
        "sort": [{"date_publish": {"order": "desc"}}],
        "size": 20
    }

    # Perform the search
    response = await es.search(index="*", body=body)
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

@app.get("/search/")
async def search(query: str = Query(..., min_length=1),
                 date: Optional [str] = Query(None, description="today|24h|week|month|3months"),
                 authors: Optional[str] = Query(None, description="Exact author name"),
                 sources: Optional[Union[List[str], str]] = Query(None, description="One or more source domains"),
                es: AsyncElasticsearch = Depends(get_es_client)):
    
    # Generate embedding for the query
    task = 'Given a search query, retrieve relevant news articles.'
    prompt = f"Instruct: {task}\nQuery: {query}"
    query_embedding = model.encode(prompt)

    # Assemble the bool.must
    must_clause = {
        "match": {
            "title": {
                "query": query,
                "boost": 0.9
            }
        }
    }

    # Assemble the optional filters
    filter_clauses = []
    if date:
        try:
            filter_clauses.append(build_date_range_filter(date))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    if authors:
        # exact match on the keyword subfield
        filter_clauses.append({
            "term": {"authors.keyword": authors}
        })
    if sources:
        # normalize to list
        if isinstance(sources, str):
            src_list = [s.strip() for s in sources.split(",") if s.strip()]
        else:
            src_list = sources

        should_clauses = [
        {"match": {"source_domain": s}}
        for s in src_list
        ]
        filter_clauses.append({
        "bool": {"should": should_clauses, "minimum_should_match": 1}
        })

    # Build the final hybrid-search
    body = {
        "query": {
            "bool": {
                "must": [must_clause],
                **({"filter": filter_clauses} if filter_clauses else {})
            }
        },
        "knn": {
            "field": "maintext_vector",
            "query_vector": query_embedding.tolist(),
            "k": 5,
            "num_candidates": 200,
            "boost": 0.1,
            **({"filter": filter_clauses} if filter_clauses else {})
        },
        "size": 10
    }

    # Perform the search
    response = await es.search(index="*", body=body)

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