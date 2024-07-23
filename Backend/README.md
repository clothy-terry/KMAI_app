# KM Search Engine(Backend)

This project is an AI-powered search engine for knowledge management. It uses Flask for the backend, and leverages Dense and Sparse Retrievers for information retrieval.

## Author Information

- **Name**: Terry Liu
- **Affiliation**: Linde Inc
- **Supervisors**: Mushtaq Ahmed, Jeff Barr
- **Release Date**: 6/20/2024

## Project Structure

The project consists of several components:

- `Backend.py`: This is the main Flask application file. It sets up the API endpoint for search and handles the search logic.
- `local_model`: This folder contains the SBERT model configuration.It is static.
- `Index_files`: This folder contains the index of documents on knowledge management site, used for performing similarity matches between user queries and documents. They are static.
- `retriv`: This folder contains wrapped classes that provide the functionality of the AI-powered search engine. It stores the model inferencing code.
- `test_backend_api.py`: This script tests the backend API.
- `test_model_inference.py`: This script tests the model inference.

## Getting Started

1. Clone the repository.
2. Install the required dependencies.
3. Run the Flask application using the command `python Backend.py`.

## Usage

To use the search engine, send a POST request to the `/search` endpoint with your query in the request body. The query must not be empty. The response will contain the IDs of the top documents that match the query.

## Testing

You can test the backend API and the model inference using the provided test scripts. Run `python test_backend_api.py` and `python test_model_inference.py` to execute the tests.