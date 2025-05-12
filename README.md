# NewsFinder

NewsFinder is a hybrid news‐search application combining keyword (BM25) and vector (kNN) search to deliver high-precision and high-recall news discovery across multiple sources. It features faceted filtering (date range, source, author, language), dynamic date controls, and a responsive React frontend.

---

## Getting Started

1. **Install Python dependencies**  
   Make sure you have Python 3.9+ installed, then create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies**  
   Ensure Node.js 16+ and npm 8+ are installed, you can download it on the [nodejs.org](https://nodejs.org/en/download) website:

---

## Local Development Setup

### Elasticsearch (via Docker)

We recommend running Elasticsearch in Docker for ease:

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.4
docker run -d --name newsfinder-es -p 9200:9200 -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.4
```

### Kibana (optional, via Docker)

To explore your cluster visually, pull and run Kibana:

```bash
docker pull docker.elastic.co/kibana/kibana:8.17.4
docker run -d --name newsfinder-kb -p 5601:5601 \
  --link newsfinder-es:elasticsearch \
  docker.elastic.co/kibana/kibana:8.17.4
```

### API Key Configuration

1. Sign in to your Elasticsearch cluster and generate an API key.
2. Save it in a JSON file at the default path:
   ```
   C:\Users\<YourUser>\Desktop\ES_API_KEY.json
   ```
3. File contents should look like:
   ```json
   {
     "api_key": "API_KEY_VALUE"
   }
   ```
4. To change the path, edit:
   - In **news_crawler_manager.py** `__init__`:
     ```python
     self.api_key_path = os.path.join(
       os.path.expanduser("~"), "Desktop", "ES_API_KEY.json"
     )
     ```
   - In **fast_api.py** `load_api_key()`:
     ```python
     api_key_path = os.path.join(
       os.path.expanduser("~"), "Desktop", "ES_API_KEY.json"
     )
     ```

---

## Running the Application

To run the application, ensure your ElasticSearch cluster is running. You can then start both backend and frontend together:

- **Windows**: Double-click `start_newsfinder.bat` (or run `.\start_newsfinder.bat` in PowerShell).

Alternatively, start each in its own terminal:

1. **Backend**  
   ```bash
   uvicorn fast_api:app --reload
   ```
2. **Frontend**  
   ```bash
   cd news_aggregator
   npm start
   ```

To retrieve articles, Double-click `run_crawler.bat` (or run `.\run_crawler.bat` in PowerShell).
Details about the crawling process can be found in `news_crawler_manager.py`.
---

## Acknowledgments

We gratefully acknowledge the creators of **news-please**, the news crawler framework that powers our ingestion pipeline:

> **Hamborg, Felix; Meuschke, Norman; Breitinger, Corinna; Gipp, Bela.**  
> *news-please: A Generic News Crawler and Extractor.*  
> In Proceedings of the 15th International Symposium of Information Science, Berlin, March 2017. doi:10.5281/zenodo.4120316

---