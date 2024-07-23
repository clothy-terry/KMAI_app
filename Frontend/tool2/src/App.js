import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const App = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [documents, setDocuments] = useState([]);
  const [topDocsForTerms, setTopDocsForTerms] = useState({});
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [searchHistory, setSearchHistory] = useState([
    "Previous search 1",
    "Previous search 2",
    "Previous search 3",
  ]);
  const [numDocs, setNumDocs] = useState(5);

  const searchContainerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target)
      ) {
        setShowHistory(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSearch = () => {
    setError(null);
    fetch("http://localhost:5000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: searchTerm }),
    })
      .then((response) => {
        if (!response.ok) {
          if (response.status === 400) {
            return response.json().then((data) => {
              if (data.error === "Query must not be empty") {
                throw new Error(data.error);
              } else if (
                data.error ===
                "No keyword found, results are based on semantic search"
              ) {
                setDocuments(data.doc_ids);
                throw new Error(data.error);
              }
            });
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.doc_ids && data.top_docs_for_terms) {
          setDocuments(data.doc_ids);
          setTopDocsForTerms(data.top_docs_for_terms);
        } else {
          console.log("Response is empty");
        }
      })
      .catch((error) => {
        setError(error.toString());
        console.log("Fetch error: ", error);
      });
  };

  const handleClearSearch = () => {
    setSearchTerm("");
  };

  const handleSearchFocus = () => {
    setShowHistory(true);
  };

  const handleHistoryClick = (query) => {
    setSearchTerm(query);
    setShowHistory(false);
  };

  const handleBlur = (e) => {
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setShowHistory(false);
    }
  };

  return (
    <div className="app">
      <div className="title-section">
        <h1>KM Search Engine</h1>
      </div>
      <div className="search-ui">
        <div className="left-half">
          <div className="results">
            {error && <div className="error-popup">{error}</div>}
          </div>
          <div className="customization-section">
            <div className="numDocs-customization">
              Display
              <input
                type="number"
                min="1"
                max="10"
                value={numDocs}
                onChange={(e) => setNumDocs(e.target.value)}
              />
              /10 documents for each keyword
            </div>
          </div>
          <div className="search-container" ref={searchContainerRef}>
            <input
              type="text"
              className="search-bar"
              placeholder="User query"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={handleSearchFocus}
            />
            <button className="clear-button" onClick={handleClearSearch}>
              x
            </button>
            <button className="search-button" onClick={handleSearch}>
              Search
            </button>
            {showHistory && (
              <div className="search-history">
                {searchHistory.map((history, index) => (
                  <div
                    key={index}
                    className="history-item"
                    onMouseDown={() => handleHistoryClick(history)}
                  >
                    {history}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="right-half">
          <div className="domain-list">
            <h3>Document IDs:</h3>
            {documents.map((doc, index) => (
              <div key={index} className="document-name">
                {doc}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
