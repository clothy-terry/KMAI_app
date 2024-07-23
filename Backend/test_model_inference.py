from retriv import DenseRetriever
from retriv import SparseRetriever



dr = DenseRetriever.load("new-index")
sr = SparseRetriever.load("index_June_20_2024")

def search():
    while True:
        query = input("Enter your query (or 'quit' to stop): ")
        if query.lower() == 'quit':
            break
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
        response = {
            'doc_ids': doc_ids,
            'top_docs_for_terms': top_docs_for_terms
        }
        print(response)


if __name__ == '__main__':
    search()
