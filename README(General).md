# KM Search Engine
This project is designed to revolutionize information retrieval (IR) within Linde’s knowledge management system. It consists of two main components: a Flask Backend and a React Frontend. The Backend serves as an AI-driven search engine, specifically tailored for knowledge management, while the Frontend, built with React, provides an intuitive user interface for seamless interaction with the tool.

## Author Information

- **Name**: Terry Liu
- **Affiliation**: Linde Inc
- **Supervisors**: Mushtaq Ahmed, Jeff Barr
- **Release Date**: 6/20/2024

## Architecture Diagram

User Interface (React.js)
    |
    | HTTP Requests (POST)
    |
Flask Server (Python)
    |
    | Dense and Sparse Retrievers(SBERT Model & BM25)
    |
Knowledge Base (Static Index Files)



User Interface (React.js)
    |
    | HTTP Requests (POST)
    |
    |
    | HTTP Requests (POST)
    |
Azure Web App -hosted Flask Server (Python)
    |--- Route Handlers: Handle incoming requests and return responses.
    |--- SBERT Model: A Sentence-BERT model for semantic text similarity.
    |--- BM25: A bag-of-words retrieval function that ranks a set of documents based on the query terms 
    
    search API
    |
    1.terms appearing in each document. 2. user query embedding
    |
Knowledge Base (Static Index Files)
    |--- Document Index: Contains metadata about each document (e.g., title, author, publication date).
    |--- Inverted Index: Maps each unique word to its occurrences in the documents (for BM25).
    |--- Embedding Index: Stores SBERT embeddings of each document for semantic search.


## Frontend

The Frontend is a a user-friendly interface created with React for users to input their queries. It was bootstrapped with Create React App. It handles user interactions, manages the UI components states, and sends HTTP requests to the backend server when a user submits a query. It also displays the search results returned by the server.It is detailed in its own README.md file located in the Frontend folder.

## Backend

The backend of our application is a Flask server. It exposes an API endpoint (/search) that accepts POST requests. When the server receives a request, it retrieves the user’s query from the request body and passes it to the Dense and Sparse Retrievers. Then it returns the matching document names from result of Retrievers. It is detailed in its own README.md file located in the Backend folder.

# Dense and Sparse Retrievers

These are the core components of this search engine. They take a user’s query and return the most relevant documents from your knowledge base. The Dense Retriever uses a dense vector space model(SBERT) to find semantically similar documents, while the Sparse Retriever uses a sparse vector space model(BM25, Tf-Idf) to find documents that match the query terms.

# Knowledge Base (Index Files)
 Your knowledge base consists of a set of documents indexed for search. The static indices are stored in files (new-index and index1) that are loaded into memory when the Flask server starts. The retrievers use these indices to find the most relevant documents for a given query.
