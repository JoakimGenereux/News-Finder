#from news_crawler_manager import NewsCrawlerManager  # Import the class from your module
import asyncio
import os
import time
import datetime
import subprocess
import configparser
import json
import shutil
from elasticsearch import Elasticsearch, helpers

# Create an instance of NewsCrawlerManager
#crawler_manager = NewsCrawlerManager()

# Load the existing config (optional, for verification)
# crawler_manager.load_config()

# Update the date range to only crawl articles from the last 3 months
#crawler_manager.update_date_range(start=2, end=0)

# Set the crawler type to "SitemapCrawler"
#crawler_manager.update_crawler_type("SitemapCrawler")

# Run the news-please command (ensure news-please is installed and accessible)
# Uncomment this line to actually run the crawler
#crawler_manager.run_news_please()

# Alternatively, call the function that updates the config and runs the crawler
# Uncomment to test full functionality
#crawler_manager.update_and_run(crawler_type="SitemapCrawler", start=5, end=0, duration_minutes=2)
#from elasticsearch import Elasticsearch

#client = Elasticsearch("https://localhost:9200",api_key="bGR3eElwWUJ4VzhieUpicW1xWUI6ODFiRjBKVE5SeFNiR0RjRWtwR2hEdw==")
# es_config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "ES_API_KEY.json")
# try:
#     with open(es_config_file_path, 'r') as f:
#         api = json.load(f)
# except FileNotFoundError:
#     raise FileNotFoundError(f"The file '{es_config_file_path}' was not found.")

# es_key =api.get("api_key")

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
es = Elasticsearch(
                hosts=[{"host": "localhost", "port": 9200, "scheme": "https"}],
                verify_certs=False,
                api_key=load_api_key(api_key_path)
        )

#resp = es.indices.delete(
#    index=["news-please-2025-03-27", "news-please-2025-03-28","news-please-2025-03-29", "news-please-2025-03-30",
#           "news-please-2025-03-31","news-please-2025-04-06",
#           "news-please-2025-04-08","news-please-2025-04-10",
#           "news-please-2025-04-12"]
#)
#print(resp)

#resp = es.search(
#    index="*",
#    query={
#        "semantic": {
#            "field": "text",
#            "query": "Ukraine war"
#        }
#    },
#)
#print(resp)

from sentence_transformers import SentenceTransformer

# Initialize the model
model = SentenceTransformer("infly/inf-retriever-v1-1.5b", trust_remote_code=True)

# Generate embedding for the query
task = 'Given a search query, retrieve relevant news articles'
prompt = f"Instruct: {task}\nQuery: "
query = "Diddy Combs Trials"
query_embedding = model.encode(query, prompt=prompt)

# Perform the search
response = es.search(
    index="*",
    query={
        "match": {
            "title": {
                "query": query,
                "boost": 0.9
            }
        }
    },
    knn={
        "field": "maintext_vector",
        "query_vector": query_embedding.tolist(),
        "k": 5,
        "num_candidates": 200,
        "boost": 0.1
    },
    size=10
)

# Display the results
for hit in response["hits"]["hits"]:
    print(hit["_source"]["title"], "\nurl: ", hit["_source"]["url"], "\nscore: ", hit["_score"])
