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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
