# NewsFinder

NewsFinder is a hybrid news‐search application combining keyword (BM25) and vector (kNN) search to deliver high-precision and high-recall news discovery across multiple sources. It features faceted filtering (date range, source, author, language), dynamic date controls, and a responsive React frontend. Local news integration and a privacy-first design ensure users get the most relevant and trustworthy stories without invasive tracking.

---

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/newsfinder.git
   cd newsfinder
   ```

2. **Install Python dependencies**  
   Make sure you have Python 3.9+ installed, then:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**  
   Ensure Node.js 16+ and npm 8+ are installed:
   ```bash
   cd news_aggregator
   npm install
   cd ..
   ```

---

## Local Development Setup

### Elasticsearch (via Docker)

We recommend running Elasticsearch in Docker for ease:

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.5.3
docker run -d --name newsfinder-es -p 9200:9200 -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.5.3
```

### Kibana (optional, via Docker)

To explore your cluster visually, pull and run Kibana:

```bash
docker pull docker.elastic.co/kibana/kibana:8.5.3
docker run -d --name newsfinder-kb -p 5601:5601 \
  --link newsfinder-es:elasticsearch \
  docker.elastic.co/kibana/kibana:8.5.3
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

You can start both backend and frontend together:

- **Windows**: Double-click `start-newsfinder.bat` (or run `.\start-newsfinder.bat` in PowerShell).

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

---

## Acknowledgments

We gratefully acknowledge the creators of **news-please**, the news crawler framework that powers our ingestion pipeline:

> **Hamborg, Felix; Meuschke, Norman; Breitinger, Corinna; Gipp, Bela.**  
> *news-please: A Generic News Crawler and Extractor.*  
> In Proceedings of the 15th International Symposium of Information Science, Berlin, March 2017. doi:10.5281/zenodo.4120316

---