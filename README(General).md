# KM Search Engine
This project is designed to revolutionize information retrieval (IR) within Linde’s knowledge management system. It consists of two main components: a Flask Backend and a React Frontend. The Backend serves as an AI-driven search engine, specifically tailored for knowledge management, while the Frontend, built with React, provides an intuitive user interface for seamless interaction with the tool.

## Author Information

- **Name**: Terry Liu
- **Affiliation**: Linde Inc
- **Supervisors**: Mushtaq Ahmed, Jeff Barr
- **Release Date**: 8/21/2024

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


## Frontend

The Frontend is a a user-friendly interface created with React. It was bootstrapped with Create React App. It handles user interactions, manages the UI components states, and sends HTTP requests to the backend server. It also displays the results returned by the server.It is detailed in its own README.md file located in the Frontend folder.

## Backend

The backend of our application is a Flask server. It exposes an API endpoints that accepts requests. 

# Dense and Sparse Retrievers

These are the core components of this search engine. They take a user’s query and return the most relevant documents from your knowledge base. The Dense Retriever uses a dense vector space model(SBERT) to find semantically similar documents, while the Sparse Retriever uses a sparse vector space model(BM25, Tf-Idf) to find documents that match the query terms.

# Knowledge Base (Index Files)
 Your knowledge base consists of a set of documents indexed for search. The static indices are stored in files that are loaded into memory when the Flask server starts. The retrievers use these indices to find the most relevant documents for a given query.
