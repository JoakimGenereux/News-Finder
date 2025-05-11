import os
import datetime
import time
import signal
import subprocess
import configparser
import json
import shutil
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
import numpy as np

'''
Citation for News-Please

@InProceedings{Hamborg2017,
  author     = {Hamborg, Felix and Meuschke, Norman and Breitinger, Corinna and Gipp, Bela},
  title      = {news-please: A Generic News Crawler and Extractor},
  year       = {2017},
  booktitle  = {Proceedings of the 15th International Symposium of Information Science},
  location   = {Berlin},
  doi        = {10.5281/zenodo.4120316},
  pages      = {218--223},
  month      = {March}
}
'''

# Class that manages news-please CLI crawler configuration and execution
class NewsCrawlerManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), "news-please-repo", "config", "config.cfg")
        self.config = configparser.ConfigParser()
        self.data_root = os.path.join(os.path.expanduser("~"), "news-please-repo", "data")
        self.jobdir_root = os.path.join(os.path.expanduser("~"), "news-please-repo", ".resume_jobdir")
        self.api_key_path = os.path.join(os.path.expanduser("~"), "Desktop", "ES_API_KEY.json")
        self.es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 9200, "scheme": "https"}],
            verify_certs=False,
            api_key= self.load_api_key()
        )
        self.st_model = SentenceTransformer("infly/inf-retriever-v1-1.5b", trust_remote_code=True)

    # Load the API to the newsCrawlerManager
    def load_api_key(self):
        try:
            with open(self.api_key_path, 'r') as f:
                api = json.load(f)
                return api.get("api_key")
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{self.api_key_path}' was not found.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Invalid JSON format in '{self.api_key_path}'.")
        
    # Read the configuration file
    def load_config(self):
        self.config.read(self.config_path)

    # Save the configuration file
    def save_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
    
    # Update the DateFilter section with a dynamic date range
    def update_date_range(self, start=90, end=0):
        self.load_config() 
        start_date = (datetime.datetime.now() - datetime.timedelta(days=start)).strftime('%Y-%m-%d %H:%M:%S')
        end_date = (datetime.datetime.now() - datetime.timedelta(days=end)).strftime('%Y-%m-%d %H:%M:%S')

        if 'DateFilter' not in self.config:
            self.config.add_section('DateFilter')

        self.config['DateFilter']['start_date'] = f"'{start_date}'"
        self.config['DateFilter']['end_date'] = f"'{end_date}'"
        self.config['DateFilter']['strict_mode'] = 'True'
        self.save_config()
    
    # Update the Crawler section with a specified crawler type
    def update_crawler_type(self, crawler_type):
        valid_crawlers = ['RecursiveCrawler', 'RecursiveSitemapCrawler', 'RssCrawler', 'SitemapCrawler', 'Download']

        if crawler_type not in valid_crawlers:
            raise ValueError(f"Invalid crawler type. Choose from: {valid_crawlers}")
        
        if 'Crawler' not in self.config:
            self.config.add_section('Crawler')

        self.config['Crawler']['default'] = crawler_type
        self.save_config()
    

    # Exercute the news-please command asynchronously
    def run_news_please(self, duration_minutes=15):
        try:
            process = subprocess.Popen(['news-please'], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL, 
                                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            print(f"'news-please' started with PID: {process.pid}")

            time.sleep(duration_minutes*60)

            print(f"'news-please' has been running for {duration_minutes} minutes. Terminating process...")
            process.send_signal(signal.CTRL_BREAK_EVENT)
            process.wait()

        except Exception as e:
            print(f"Failed to start 'news-please': {e}")
        finally:
            print("news-please has been terminated.")

    def ingest_articles_to_elasticsearch(self):
        # Get today's news-please extraction folder
        today = datetime.datetime.now(datetime.timezone.utc)
        today_path = os.path.join(
            self.data_root,
            today.strftime("%Y"),
            today.strftime("%m"),
            today.strftime("%d")
        )
        #today_path = "C:\\Users\Joaki\\news-please-repo\\data\\2025\\04\\15"
        if not os.path.exists(today_path):
            print(f"No data found for today at {today_path}")
            return

        print("Starting ingestion process...")
        # Walk every source folder and read all JSON file
        index_groups = {}
        for root, _, files in os.walk(today_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            article = json.load(f)

                            maintext = article.get("maintext")
                            authors = article.get("authors")
                            language = article.get("language")
                            if not maintext or not authors or language != "en":
                                continue  # Skip if maintext or authors is null or if article language is not english
                            pub_date = article.get("date_publish")
                            if pub_date:
                                pub_date_trunc = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S")
                                index_name = f"news-please-{pub_date_trunc.strftime('%Y-%m-%d')}"
                            else:
                                # Fall back on today's date if no publish-date found
                                index_name = f"news-please-{datetime.datetime.now().strftime('%Y-%m-%d')}"

                            doc_id = article.get("url")
                            if not doc_id:
                                continue  # Skip if no unique identifier

                            # Generate embeddings
                            try:
                                maintext_embedding = self.st_model.encode(maintext)

                            except Exception as e:
                                print(f"Embedding generation failed for {file_path}: {e}")
                                continue  # Skip this article if embedding fails

                            # Add embeddings to the article
                            article["maintext_vector"] = maintext_embedding.tolist()

                            action = {
                                "_op_type": "create",
                                "_index": index_name,
                                "_id": doc_id,
                                "_source": article
                            }

                            index_groups.setdefault(index_name, []).append(action)
                    except Exception as e:
                        print(f"Failed to read {file_path}: {e}")

        print("Starting indexing process...")
        # Ingest all articles to Elasticsearch
        for index_name, actions in index_groups.items():
            if actions:
                try:
                    helpers.bulk(self.es, actions)
                    print(f"Successfully indexed {len(actions)} articles into {index_name}.")
                except Exception as e:
                    print(f"Bulk indexing failed for {index_name}: {e}")

        # Delete the extraction folder
        for entry in os.listdir(self.data_root):
            entry_path = os.path.join(self.data_root, entry)
            if os.path.isdir(entry_path):
                try:
                    shutil.rmtree(entry_path)
                    print(f"Successfully removed directory: {entry_path}")
                except Exception as e:
                    print(f"Failed to remove directory {entry_path}: {e}")

    # Update the config file and run the crawler
    def update_and_run(self, crawler_type='SitemapCrawler', from_days=1, to_days=0, duration_minutes=60):
        self.update_date_range(from_days, to_days)
        self.update_crawler_type(crawler_type)
        self.run_news_please(duration_minutes)
        time.sleep(60)
        self.ingest_articles_to_elasticsearch()

