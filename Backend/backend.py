from flask import Flask, request, jsonify
from flask_cors import CORS
from retriv import DenseRetriever
from retriv import SparseRetriever
from retriv import Merger
from retriv import HybridRetriever

app = Flask(__name__)
CORS(app)

dr = DenseRetriever.load("new-index")
sr = SparseRetriever.load("sparse_index(1)_June_20_2024")
hr = HybridRetriever.load("index2")


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

@app.route('/v2/search', methods=['POST'])
def search_V2():
    data = request.get_json()
    query = data.get('query')
    
    # Check if the query is empty
    if not query:
        return jsonify({'error': 'Query must not be empty'}), 400
    
    merger = Merger()
    merger.params = {"weights": [0.7, 0.3]}  # Set the weights for the two retrieval runs
    hr.merger = merger
    results, top_docs_for_terms = hr.search(
            query='nitrogen hydrogen',  # What to search for
            return_docs=True, 
            cutoff=10, 
        )
    
    doc_ids = [result['id'] for result in results]
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

#pip install spacy
#python -m spacy download en_core_web_sm

import spacy
from spacy.matcher import PhraseMatcher
# Load spaCy model
nlp = spacy.load('en_core_web_sm')

@app.route('/keyword_context', methods=['POST'])
# input: 'doc_ids', 'keywords', 'window_size'
# output: doct[keyowrd][]
def keyword_context():
    data = request.get_json()
    doc_ids = data.get('doc_ids')
    keywords = data.get('keywords')
    window_size = data.get('window_size')

    # Load the document dictionary from the JSON file
    with open('all_collected_text.json', 'r') as f:
        doc_dict = json.load(f)

    # Filter the documents based on the provided IDs
    doc_dict = [doc for doc in doc_dict if doc['id'] in doc_ids]
    # Function to find sentence or nearby words for each keyword
    def find_keyword_context(doc_text, keywords, window_size=None):
        # split the each doc text into sentences -> doc.sents
        doc = nlp(doc_text)
        keyword_context = {}
        # find sentence
        if window_size is None:
            for sentence in doc.sents:
                for keyword in keywords:
                    if keyword in sentence.text.lower():
                        sentence_words = [token.text.lower() for token in sentence]
                        # if keyword exist in return dict
                        if keyword in keyword_context:
                            keyword_context[keyword].append(sentence.text)
                        else:
                            keyword_context[keyword] = [sentence.text]
        # find nearby words of key phrase
        else:
            pass

        return keyword_context
    res_doc_keyword_dict = {}
    for doc in doc_dict:
        doc_text = doc['text']
        doc_id = doc['id']
        keyword_sent_dict = find_keyword_context(doc_text, keywords, window_size)
        res_doc_keyword_dict[doc_id] = keyword_sent_dict
        
    return jsonify(res_doc_keyword_dict)

# save user doc to {index_name} folder, extract text to {index_name}.jsonl, build hr index
from werkzeug.utils import secure_filename
import os
from retriv import HybridRetriever
from text_mining import process_documents
@app.route('/extract_and_build_index', methods=['POST'])
def extract_and_build_index_route():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    # start saving the docs
    files = request.files.getlist('files')
    index_name = request.form.get('index_name')
    directory = f'{index_name}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file in files:
        # If the user does not select a file, the browser might
        # submit an empty file without a filename.
        # if os doesn't work, just store docs at the frontend
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            # may have restrictions on the maximum size of the file system, 
            # or may not persist files when the application is restarted
            file.save(os.path.join(directory, filename))

    #start extracting text json from user_doc folder
    print('start collecting text')
    output_json_file = f"{index_name}.jsonl"
    collected_text, skipped_files = process_documents(directory, output_json_file)

    # start building index
    hr = HybridRetriever(
        index_name= index_name,# specify a index name
        sr_model="bm25",
        min_df=1,
        tokenizer="whitespace",
        stemmer="english",
        stopwords="english",
        do_lowercasing=True,
        do_ampersand_normalization=True,
        do_special_chars_normalization=True,
        do_acronyms_normalization=True,
        do_punctuation_removal=True,
        dr_model="local_model",
        normalize=True,
        max_length=128,
        use_ann=False,
    )
    hr = hr.index_file(
        path=output_json_file, # specify text json path
        embeddings_path=None, 
        use_gpu=False,  
        batch_size=512,  
        show_progress=True, 
        callback=lambda doc: {"id": doc["id"], "text": doc["text"]}
    )
    if skipped_files == []:
        return jsonify({'message':'Uploaded!'})
    else:
        return jsonify({'message':f'Failed to process some docs:{skipped_files}'})

@app.route('/check_index/<index_name>', methods=['GET'])
def check_index(index_name):
    directory = os.path.join('index_files', 'collections', index_name)
    if os.path.exists(directory):
        return jsonify({'message': f'Available!'})
    else:
        return jsonify({'message': f'Not available...Please upload'})

import shutil

@app.route('/delete_index/<index_name>', methods=['DELETE'])
def delete_index(index_name):
    directory = os.path.join('index_files', 'collections', index_name)
    jsonl_file = f'{index_name}.jsonl'
    if os.path.exists(jsonl_file) and os.path.exists(directory):
        os.remove(jsonl_file)
        shutil.rmtree(directory)
        return jsonify({'message': f'"{index_name}" has been deleted.'})
    else:
        return jsonify({'message': f'Documents set not exist'})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
