from flask import Flask, request, jsonify
from flask_cors import CORS
from retriv import DenseRetriever
from retriv import SparseRetriever

app = Flask(__name__)
CORS(app)

dr = DenseRetriever.load("new-index")
sr = SparseRetriever.load("sparse_index(1)_June_20_2024")

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    
    # Check if the query is empty
    if not query:
        return jsonify({'error': 'Query must not be empty'}), 400

    dr_results = dr.search(
        query=query,  # What to search for
        return_docs=True,  
        cutoff=5, 
    )
    sr_results, top_docs_for_terms = sr.search(
        query=query,    
        return_docs=True,
        cutoff=5,
    )
    results = dr_results + sr_results
    doc_ids = [result['id'] for result in results]
    if sr_results == []:
        return jsonify({'error': 'No keyword found, results are based on semantic search', 'doc_ids':doc_ids}), 400
    response = {
        'doc_ids': doc_ids,
        'top_docs_for_terms': top_docs_for_terms
    }
    return jsonify(response)

import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

nltk.download('punkt')
nltk.download('stopwords')

@app.route('/keyword_frequency', methods=['POST'])
def keyword_frequency():
    data = request.get_json()
    keywords = data.get('keywords')
    doc_ids = data.get('doc_ids')

    # Load the document dictionary from the JSON file
    with open('all_collected_text.json', 'r') as f:
        doc_dict = json.load(f)

    # Filter the documents based on the provided IDs
    doc_dict = [doc for doc in doc_dict if doc['id'] in doc_ids]

    result_dict = {}

    for doc in doc_dict:
        id = doc['id']
        text = doc['text']
        result_dict[id] = {}

        # Convert the document text to lower case and splits into words and punctuation
        doc_words = word_tokenize(text.lower())

        # Remove punctuation and stopwords
        stop_words = set(stopwords.words('english'))
        doc_words = [word for word in doc_words if word not in string.punctuation and word not in stop_words]

        # Iterate over each word in the query
        for word in keywords:
            # Count the number of times the word appears in the document
            word_count = doc_words.count(word.lower())

            # Add the count to the result dictionary
            result_dict[id][word] = word_count

    return jsonify(result_dict)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
