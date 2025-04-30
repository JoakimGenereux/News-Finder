import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleInputChange = (e) => setQuery(e.target.value);
  const handleSearch = () => query.trim() && onSearch(query.trim());
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Search for articles..."
      />
      <button onClick={handleSearch} aria-label="Search">🔍</button>
    </div>
  );
};

export default SearchBar;