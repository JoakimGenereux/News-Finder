import React, { useState, useRef, useEffect } from 'react';
import './SearchBar.css';

const DATE_OPTIONS = [
  { label: 'Today', value: 'today' },
  { label: 'Past 24h', value: '24h' },
  { label: 'Past week', value: 'week' },
  { label: 'Past month', value: 'month' },
  { label: 'Past 3 months', value: '3months' },
];

const SOURCE_OPTIONS = [
  'bbc.com',
  'abcnews.go.com',
  'foxnews.com',
  'apnews.com',
  'dailymail.co.uk',
  'cbsnews.com',
  'cbc.ca',
  'rawstory.com'
];

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);

  const [dateFilter,    setDateFilter]    = useState('');
  const [authorsFilter, setAuthorsFilter] = useState('');
  const [sourcesFilter, setSourcesFilter] = useState([]);

  const dropdownRef = useRef(null);
  useEffect(() => {
    const onClickOutside = e => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setFiltersOpen(false);
      }
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const toggleSource = src =>
    setSourcesFilter(s =>
      s.includes(src) ? s.filter(x => x !== src) : [...s, src]
    );

  const handleSearchClick = () => {
    onSearch(query, {
      date: dateFilter,
      authors: authorsFilter.trim(),
      sources: sourcesFilter
    });
  };

  const handleClear = () => {
    setDateFilter('');
    setAuthorsFilter('');
    setSourcesFilter([]);
  };

  const handleApply = () => {
    setFiltersOpen(false);
  };

  return (
    <div className="search-bar">
      {/* Search button on the left */}
      <button
        className="search-toggle-btn"
        onClick={handleSearchClick}
      >🔍</button>

      {/* text input */}
      <input
        type="text"
        placeholder="Search for articles..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handleSearchClick()}
      />

      {/* Filter ▲/▼ on the right */}
      <button
        className="filter-toggle-btn"
        onClick={() => setFiltersOpen(o => !o)}
      >
        {filtersOpen ? '▲' : '▼'}
      </button>

      {filtersOpen && (
        <div className="filters-dropdown" ref={dropdownRef}>
          {/* …all your filter-box sections… */}
          <div className="filter-buttons">
            <button className="btn-clear" onClick={handleClear}>Clear</button>
            <button className="btn-apply" onClick={handleApply}>Apply</button>
          </div>
        </div>
      )}

      {/* Dropdown panel */}
      {filtersOpen && (
        <div className="filters-dropdown" ref={dropdownRef}>
          <div className="filter-box">
            <span className="filter-title">Date</span>
            {DATE_OPTIONS.map(opt => (
              <label key={opt.value} className="filter-label">
                <input
                  type="radio"
                  name="dateFilter"
                  value={opt.value}
                  checked={dateFilter === opt.value}
                  onChange={e => setDateFilter(e.target.value)}
                />
                {opt.label}
              </label>
            ))}
          </div>

          <div className="filter-box">
            <span className="filter-title">Authors</span>
            <input
              type="text"
              className="filter-text-input"
              placeholder="Type author name..."
              value={authorsFilter}
              onChange={e => setAuthorsFilter(e.target.value)}
            />
          </div>

          <div className="filter-box">
            <span className="filter-title">Sources</span>
            {SOURCE_OPTIONS.map(src => (
              <label key={src} className="filter-label">
                <input
                  type="checkbox"
                  checked={sourcesFilter.includes(src)}
                  onChange={() => toggleSource(src)}
                />
                {src}
              </label>
            ))}
          </div>

          <div className="filter-buttons">
            <button className="btn-clear" onClick={handleClear}>
              Clear
            </button>
            <button className="btn-apply" onClick={handleApply}>
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
