import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import keywordsList1 from "./keywordLists/keywordList1.json";
import keywordsList2 from "./keywordLists/keyowrdList2.json";
import Modal from "react-modal";

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

  /*user keyword model pop up*/
  const [isUserKeywordModalOpen, setIsUserKeywordModalOpen] = useState(false);
  const handleUserKeywordViewClick = () => {
    setIsUserKeywordModalOpen(true);
  };

  const handleDeleteKeyword = (indexToDelete) => {
    setUserKeywords(UserKeywords.filter((_, index) => index !== indexToDelete));
  };

  /* predefined keyword lists options*/
  const [selectedList, setSelectedList] = useState([
    "please select a keywords list to view",
  ]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleListSelect = (event) => {
    const selectedOption = event.target.value;
    if (selectedOption === "list0") {
      setSelectedList(["please select a keywords list to view"]);
    } else if (selectedOption === "list1") {
      setSelectedList(keywordsList1);
    } else if (selectedOption === "list2") {
      setSelectedList(keywordsList2);
    }
  };

  Modal.setAppElement("#root");
  const handleViewClick = () => {
    setIsModalOpen(true);
  };

  const [addError, setAddError] = useState(null);

  const handleAddAllClick = () => {
    if (
      JSON.stringify(selectedList) !==
      JSON.stringify(["please select a keywords list to view"])
    ) {
      setUserKeywords([...UserKeywords, ...selectedList]);
      setAddError(null); // Clear the error message when adding is successful
    } else {
      setAddError("Please select a list to add"); // no list is selected
    }
  };

  /* keyword-doc table */
  const Table = ({ documents, keywords }) => {
    return (
      <table className="excel-table">
        <thead>
          <tr>
            <th></th>
            {documents.map((doc, index) => (
              <th key={index}>{doc.split("/")[1]}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {keywords.map((keyword, rowIndex) => (
            <tr key={rowIndex}>
              <td>{keyword}</td>
              {documents.map((doc, colIndex) => (
                <td key={colIndex}>1</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  /* user keyword input func */
  const [UserKeywords, setUserKeywords] = useState([]);
  const [currentUserInput, setCurrentUserInput] = useState(""); // New state variable for current user input
  const handleUserInputChange = (event) => {
    setCurrentUserInput(event.target.value);
  };
  const handleUserInputClear = () => {
    setCurrentUserInput("");
  };
  const handleAddButtonClick = () => {
    setUserKeywords([...UserKeywords, currentUserInput]);
    setCurrentUserInput("");
  };

  /* user search query func */
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

  /* user search history */
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
        <h1>KMAI</h1>
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
              /10 documents
            </div>
          </div>
          <div className="search-container" ref={searchContainerRef}>
            <input
              type="text"
              className="search-bar"
              placeholder="User search query"
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
          <div className="predefined-list-container">
            <select onChange={handleListSelect}>
              <option value="list0">Select a keyword list</option>
              <option value="list1">Keyword List 1</option>
              <option value="list2">Keyword List 2</option>
            </select>
            <button onClick={handleViewClick}>View</button>
            <button onClick={handleAddAllClick}>Add</button>
            {addError && <div className="error-popup">{addError}</div>}
            <Modal
              isOpen={isModalOpen}
              onRequestClose={() => setIsModalOpen(false)}
            >
              {selectedList && selectedList.map((keyword) => <p>{keyword}</p>)}
            </Modal>
          </div>

          <div className="keyword-add-container" ref={searchContainerRef}>
            <input
              type="text"
              className="keyword-bar"
              placeholder="User keywords"
              value={currentUserInput}
              onChange={handleUserInputChange}
            />
            <button
              className="keyword-clear-button"
              onClick={handleUserInputClear}
            >
              x
            </button>
            <button
              className="keyword-add-button"
              onClick={handleAddButtonClick}
            >
              Add
            </button>
          </div>
          <button onClick={handleUserKeywordViewClick}>View User Inputs</button>
          <Modal
            isOpen={isUserKeywordModalOpen}
            onRequestClose={() => setIsUserKeywordModalOpen(false)}
          >
            {UserKeywords.map((input, index) => (
              <div key={index} className="keyword-box">
                {input}
                <button
                  className="delete-button"
                  onClick={() => handleDeleteKeyword(index)}
                >
                  X
                </button>
              </div>
            ))}
          </Modal>
        </div>
        <div className="right-half">
          <div className="domain-list">
            <h3>Document IDs:</h3>
            {documents.slice(0, numDocs).map((doc, index) => (
              <div key={index} className="document-name">
                {doc}
              </div>
            ))}
            <div>doc list output</div>
          </div>
          <Table
            documents={documents.slice(0, numDocs)}
            keywords={UserKeywords}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
