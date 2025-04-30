import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchBar from 'components/SearchBar/SearchBar';
import ResultsList from 'components/ResultsList/ResultsList';
import './App.css';

const App = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastQuery, setLastQuery]   = useState('');
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
  }, [darkMode]);
  
  const handleSearch = async (query) => {
    setLoading(true);
    setLastQuery(query);
    try {
      const response = await axios.get(`http://localhost:8000/search?query=${query}`);
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
        <SearchBar onSearch={handleSearch} />
      </header>
      <div className="divider" />
      <main className="results-container">
        {loading && <div className="loading-spinner" />}
        {!loading && <ResultsList articles={articles} query={lastQuery}/>}
      </main>
    </div>
  );
};

export default App;
