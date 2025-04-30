import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import SearchBar from 'components/SearchBar/SearchBar';
import ResultsList from 'components/ResultsList/ResultsList';
import './App.css';

const App = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastQuery, setLastQuery] = useState('');
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
  }, [darkMode]);
  
    // Fetch latest 20 on mount, and whenever tab becomes 'latest'
    const fetchLatest = useCallback(async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/latest');
        const hits = response.data.results ?? response.data;
        setArticles(hits);
      } catch (err) {
        console.error('Error loading latest news:', err);
      } finally {
        setLoading(false);
      }
    }, []);
    
  const handleSearch = async (query, { date, authors, sources }) => {
    setLoading(true);
    setLastQuery(query);
    try {
      const params = { query };
      if (date) params.date = date;
      if (authors) params.authors = authors;
      if (sources && sources.length) {
        // send as comma-separated string
        params.sources = sources.join(',');
      }
      const response = await axios.get('http://localhost:8000/search', {params});
      const hits = response.data.results ?? response.data;
      setArticles(hits);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
    setLoading(false);
    }
  };

  return (
    <div className={`app-container ${darkMode ? 'dark' : ''}`}> 
      <button
        className="dark-toggle"
        onClick={() => setDarkMode(!darkMode)}
        aria-label="Toggle dark mode"
      >
        {darkMode ? '☀️' : '🌙'}
      </button>
      <header className="header">
        <h1>News Aggregator</h1>
      </header>
      <div className="controls">
        <button
              className="latest-button"
              onClick={fetchLatest}
            >
              Latest News
            </button>
            <SearchBar onSearch={handleSearch} />
      </div>
      <div className="divider" />
      <main className="results-container">
        {loading && <div className="loading-spinner" />}
        {!loading && <ResultsList articles={articles} query={lastQuery}/>}
      </main>
    </div>
  );
};

export default App;
