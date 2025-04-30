import React from 'react';
import './ResultsList.css';

const ResultsList = ({ articles = [], query = '' }) => {
  if (articles.length === 0 && query) {
    return <div className="no-results">No results found</div>;
  }

  return (
    <div className="results-list">
      {articles.map((article) => (
        <div className="article" key={article.url}>
          <div className="article-details">
            <div className="article-meta">
              <span className="source">{article.source}</span>
              <span className="date">{article['date published']}</span>
            </div>
            <a href={article.url} target="_blank" rel="noopener noreferrer" className="article-title">
              {article.title}
            </a>
            <p className="article-description">{article.description}</p>
          </div>
          {article.image && (
            <div className="article-image img">
              <img src={article.image} alt={article.title} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ResultsList;