import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import keywordsList1 from "./keywordLists/keywordList1.json";
import keywordsList2 from "./keywordLists/keyowrdList2.json";
import Modal from "react-modal";
import DataGrid from "react-data-grid";
import "react-data-grid/lib/styles.css";
import XLSX from "xlsx";

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

  /* user check, use, or delete index folder*/
  const [userIndexResponse, setUserIndexResponse] = useState("");
  const [indexName, setIndexName] = useState("");
  const handleUseIndex = () => {
    if (indexName === "") {
      setError("Please enter an index name");
      return;
    } else {
      setError(null);
    }
    fetch(`http://localhost:5000/switch_index/${indexName}`)
      .then((response) => response.json())
      .then((data) => {
        setUserIndexResponse(data["message"]);
      });
  };
  const handleCheckIndex = () => {
    if (indexName === "") {
      setError("Please enter an index name");
      return;
    } else {
      setError(null);
    }
    fetch(`http://localhost:5000/check_index/${indexName}`)
      .then((response) => response.json())
      .then((data) => {
        setUserIndexResponse(data["message"]);
      })
      .catch((error) => {
        setError(error);
        console.error("Error:", error);
      });
  };
  const handleDeleteIndex = () => {
    if (indexName === "") {
      setError("Please enter an index name");
      return;
    } else {
      setError(null);
    }
    fetch(`http://localhost:5000/delete_index/${indexName}`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        setUserIndexResponse(data["message"]);
      })
      .catch((error) => {
        setError(error);
        console.error("Error:", error);
      });
  };
  /*user upload documents to build index */
  const fileInputRef = useRef(); // Create a ref for the file input
  const handleUserDocUpload = () => {
    if (indexName === "") {
      setError("Please give index a name");
      return;
    } else {
      // Clear error message
      setError(null);
    }
    const files = fileInputRef.current.files; // Get the selected files from the file input
    if (files.length === 0) {
      setError("Please choose files to upload");
      return;
    }
    const formData = new FormData();
    // Append each file to the form data
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    // Append index name to form data
    formData.append("index_name", indexName);
    // Should takes 1620 documents take 4 mins to build index
    // Not counting text extraction time(scanned pdf that requires OCR takes a long time)
    setUserIndexResponse("Uploading...");
    fetch("http://localhost:5000/extract_and_build_index", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setUserIndexResponse(data["message"]);
      })
      .catch((error) => {
        setError(error);
        console.error("Error:", error);
      });
  };

  /*word-doc-excel generate & download*/
  const handleResultDownload = () => {
    // Create a new array of rows without the 'id' field
    const rowsWithoutId = gridData.rows.map((row) => {
      const { id, ...rowWithoutId } = row;
      return rowWithoutId;
    });

    const ws = XLSX.utils.json_to_sheet(rowsWithoutId);

    // Set the width of each column
    ws["!cols"] = Array(gridData.columns.length).fill({ wch: 40 }); // Adjust the number 20 to your desired width

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Results");
    XLSX.writeFile(wb, "results.xlsx");
  };

  const [excelModalIsOpen, setExcelModalIsOpen] = useState(false);

  const [gridData, setGridData] = useState({ columns: [], rows: [] });

  const generateData = () => {
    fetch("http://localhost:5000/keyword_context", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doc_ids: documents.slice(0, numDocs),
        keywords: UserKeywords,
        window_size: null, // Set to None if require context of entire sentence.
      }),
    })
      .then((response) => response.json())
      .then((doc_keyword_dict) => {
        const data = documents.slice(0, numDocs).map((doc, i) => {
          const row = { id: i, document_name: doc };
          UserKeywords.forEach((keyword, j) => {
            if (doc_keyword_dict[doc] && doc_keyword_dict[doc][keyword]) {
              row[keyword] = doc_keyword_dict[doc][keyword][0];
            } else {
              row[keyword] = `Not Found`; // cell value
            }
          });
          return row;
        });

        const columns = [
          { key: "document_name", name: "Document Name" },
          ...UserKeywords.map((keyword, i) => ({
            key: keyword, // Use keyword as key
            name: keyword,
          })),
        ];

        setGridData({ columns, rows: data });
      });
  };

  const handleExcelGenerate = () => {
    setExcelModalIsOpen(true);
    generateData();
  };

  /*user keyword model pop up*/
  const [isUserKeywordModalOpen, setIsUserKeywordModalOpen] = useState(false);
  const handleUserKeywordViewClick = () => {
    setIsUserKeywordModalOpen(true);
  };

  const handleDeleteKeyword = (indexToDelete) => {
    setUserKeywords(UserKeywords.filter((_, index) => index !== indexToDelete));
  };

  /*user upload customized keyword xlsx */
  const [userUploadedKeywordList, setUserUploadedKeywordList] = useState([]);
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const worksheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
      const keywords = jsonData.slice(1).map((row) => row[0]); //get the first col of xlsx
      setUserUploadedKeywordList(keywords);
    };
    reader.readAsArrayBuffer(file);
  };

  /* predefined keyword lists options*/
  const handleTemplateDownload = () => {
    window.location.href = "/template.xlsx"; // put in the public folder
  };

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
    } else if (selectedOption === "list3") {
      setSelectedList(userUploadedKeywordList);
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
    fetch("http://localhost:5000/v2/search", {
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
              }
            });
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.doc_ids) {
          setDocuments(data.doc_ids);
        } else {
          setError("Response is empty");
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
          <div className="user_doc_upload_input">
            <input type="file" ref={fileInputRef} multiple />
          </div>
          <div className="user_index_check_upload">
            <input
              type="text"
              value={indexName}
              onChange={(e) => setIndexName(e.target.value)}
              placeholder="Enter index name"
            />
            <button onClick={handleCheckIndex}>Check</button>
            <button onClick={handleUseIndex}>Use</button>
            <button onClick={handleUserDocUpload}>Upload</button>
            <button onClick={handleDeleteIndex}>Delete</button>
            {userIndexResponse && <div>{userIndexResponse}</div>}
          </div>
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
          <div className="domain-list">
            <h3>Document IDs:</h3>
            {documents.slice(0, numDocs).map((doc, index) => (
              <div key={index} className="document-name">
                {doc}
              </div>
            ))}
          </div>
        </div>
        <div className="right-half">
          <div className="predefined-list-container">
            <select onChange={handleListSelect}>
              <option value="list0">Select a keyword list</option>
              <option value="list1">Keyword List 1</option>
              <option value="list2">Keyword List 2</option>
              {userUploadedKeywordList.length > 0 && (
                <option value="list3">User Uploaded Keyword List</option>
              )}
            </select>
            <button onClick={handleViewClick}>View</button>
            <button onClick={handleAddAllClick}>Add</button>
            <button onClick={handleTemplateDownload}>Download Template</button>
            <input type="file" accept=".xlsx" onChange={handleFileUpload} />
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
          <div className="word-doc-excel">
            <button onClick={() => handleExcelGenerate()}>
              Generate Table
            </button>
            <button onClick={handleResultDownload}>Download Result</button>
            <Modal
              isOpen={excelModalIsOpen}
              onRequestClose={() => setExcelModalIsOpen(false)}
            >
              <div>
                <button onClick={() => setExcelModalIsOpen(false)}>
                  Close
                </button>
                <DataGrid columns={gridData.columns} rows={gridData.rows} />
              </div>
            </Modal>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
