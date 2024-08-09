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
            # initialize shared vocab across multiple docs text
            matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
            # store the sequence of token/key phrase/pattern to a Doc object for efficient find
            key_phrase = [nlp.make_doc(keyword) for keyword in keywords]
            matcher.add("KeywordMatcher", key_phrase)
            # a list of matches, tuples(id, start_token_idx, end_token_idx)
            matches = matcher(doc)
            for match_id, start, end in matches:
                keyword = doc[start:end].text
                # expand start, end token idx to include nearby words
                context_start = max(0, start - window_size)
                context_end = min(len(doc), end + window_size)
                context = doc[context_start:context_end].text
                if keyword in keyword_context:
                    keyword_context[keyword].append(context)
                else:
                    keyword_context[keyword] = [context]

        return keyword_context
    res_doc_keyword_dict = {}
    for doc in doc_dict:
        doc_text = doc['text']
        doc_id = doc['id']
        keyword_sent_dict = find_keyword_context(doc_text, keywords, window_size)
        res_doc_keyword_dict[doc_id] = keyword_sent_dict
        
    return jsonify(res_doc_keyword_dict)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
