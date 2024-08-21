# KM Search Engine(Backend)

This project is an AI-powered search engine for knowledge management. It uses Flask for the backend, and leverages Dense and Sparse Retrievers for information retrieval.

## Author Information

- **Name**: Terry Liu
- **Affiliation**: Linde Inc
- **Supervisors**: Mushtaq Ahmed, Jeff Barr
- **Release Date**: 8/21/2024

## Project Structure

The project consists of several components:

- `Backend.py`: This is the main Flask application file. It sets up the API endpoint for search and handles the search logic.
- `local_model`: This folder contains the SBERT model configuration.It is static.
- `Index_files`: This folder contains the index of documents on knowledge management site, used for performing similarity matches between user queries and documents. They are static.
- `retriv`: This folder contains wrapped classes that provide the functionality of the AI-powered search engine. It stores the model inferencing code.
- `test_backend_api.py`: This script tests the backend API.
- `test_model_inference.py`: This script tests the model inference.
- `all_collected_text.json`: all collected text from Knowledge Management Site Content, preprocessed in json format to be feed in models

## Getting Started
1. Ensure that you have Python>=3.8 installed on your machine.
2. cd into (..\backend) to install:
pip install Flask
pip install flask-cors
pip install retriv
pip install spacy
python -m spacy download en_core_web_sm
pip install Werkzeug
3. Run the Flask application using the command `python Backend.py`.

## Testing

You can test the backend API and the model inference using the provided test scripts. Run `python test_backend.py` and `python test_model_inference.py` to execute the tests.