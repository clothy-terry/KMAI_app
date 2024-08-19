# AI-powered Search Engine Project

This project aims to enhance information retreival(IR) in Linde's knowledge management system. We built a semantic search algorithm and a keyword search algorithm. The semantic search engine(Dense_retrieve) utilizes the SBERT(Sentence-BERT) model to compute vector representations of queries and documents to determine relevance scores. The keyword-based search engine(Spare_retreiver) ranks a set of documents based on the query terms appearing in each document.

## Author Information

- **Name**: Terry Liu
- **Affiliation**: Linde Inc
- **Supervisors**: Mushtaq Ahmed, Jeff Barr
- **Release Date**: 6/12/2024

## Project Structure

This project has several directories and files:

- `local_model`: This folder stores our fine-tuned Sentence-BERT (SBERT) model.

- `other`: This folder contains other Python scripts that are not directly relevant to the project.

- `small_doc_samples`: This folder contains a small portion of the dataset for testing purposes.

- `text_mining`: This folder contains scripts for text mining and data cleaning.

- `all_collected_text.json`: all collected text, preprocessed in json format to be feed in models

- `dense_indexing.py` & `dense_search.py`: semantic search engine

- `sparse_indexing.py` & `sparse_search/py`: keyword-based search engine

## Getting Started

These instructions will guide you on how to run the code on your local machine.

### Prerequisites

Ensure that you have Python>=3.8 installed on your machine.

### Installation

1. Navigate to the `search_engine` folder in your terminal.
2. Install the necessary package by typing and entering: `pip install retriv`.

### Running the Code

To test the semantic search engine:
1. Type and enter: `python dense_indexing.py`.
2. Type and enter: `python dense_search.py`.

To test the keyword search engine:
1. Type and enter: `python sparse_indexing.py`.
2. Type and enter: `python sparse_search.py`.

## Usage

After running the respective search scripts, you can enter your query to test the search engines.

Example user query input:
L-0246
- Mostly Keyword: "Cold treatment processes discussed in this memorandum"
- A few keywords: "The role of temperature in metal assembly processes"
- No keywords: "The application of low temperatures in industrial manufacturing processes"

HydrogenPortal / AustraliaEnergy2023.pdf
- Mostly Keyword: "Australia's Climate Change Act 2022", "Australia's Powering Australia Plan"
- A few keywords: "Australia's efforts in reducing methane emissions","The impact of the Capacity Investment Scheme on Australia's power system"
- No keywords: "The significance of Australia's Powering Australia Plan in achieving clean electricity sources"

## Features

### Dense Retriever (Semantic Search)

The dense retriever handles keyword matches and can handle user queries with minimal or no keywords at all. It utilizes the SBERT model to compute vector representations of queries and documents to determine relevance scores. The documents are transformed into low-dimensional vectors, each capturing more abstract meaning rather than specific words. The vector is dense as its elements are non-zero.

#### Data preprocessing of Dense_retriever
Handle by the AutoTokenizer from the Hugging Face Transformers library, within the SBERT model itself.The tokenization process is designed to prepare the text data in a way that’s suitable for the model. However, this doesn’t include some of the preprocessing steps you might see in traditional NLP, such as lowercasing, stopword removal, or stemming. These steps are often not necessary when working with models like BERT, as they are designed to understand the semantic meaning of text and can handle variations in case, word forms, etc.

SBERT model preprocessing the text by the following steps:

1. Tokenization: The sentence is split into individual words or tokens using the WordPiece tokenizer. WordPiece tokenization is a technique that breaks a word into smaller sub-words to handle out-of-vocabulary (OOV) words.
2. Adding Special Tokens: BERT adds special tokens to the input. It adds [CLS] (classification) token at the beginning of each sentence, which is used as an aggregate representation for classification tasks. It also adds [SEP] (separation) token at the end of each sentence to help the model distinguish between different sentences.
3. Position Embedding: BERT adds positional embeddings to each token to indicate its position in the sentence.
4. Masking: In order to understand the context of a word based on the words around it, SBERT randomly masks some of the words in the sentence and tries to predict them based on the context provided by the non-masked words.

#### Dense_Retriever Algorithm
After tokenization, the tokenized sentences are converted into word embeddings by pre-trained BERT(Bidirectional Encoder Representations from Transformers) model, which are vectors representing each word in the sentence. These embeddings are then passed through the transformer layers of the SBERT model, which compute the output vectors for each word.The final output vector is calculated by pooling the outputs of all the words in the sentence.

Once the SBERT model calculates the final output vectors for the query and each document, the similarity between the query and each document is computed by taking the dot product between the query vector and the document vector. This dot product value is viewed as a measure of the similarity between the two vectors. The dot product assumes that similar vectors will have high dot products and dissimilar vectors will have low dot products.

### Sparse Search Engine (Keyword-based Search)

The sparse search engine is ideal for tasks involving exact keyword match. It ranks a set of documents based on the query terms appearing in each document. 

#### Data preprocessing of Sparse_retriever
Sparse Retriever preprocess the data to feed in BM25 model by traditional NLP methods:

1. Tokenization: This is the process of breaking down the text into individual words or tokens. This is a crucial step as BM25 operates at the token level.
2. Normalization: This usually involves converting all text to lower case so that the algorithm treats words like “Hello” and “hello” as the same token. It may also involve other tasks such as removing punctuation, converting numbers to their word equivalents, etc.
3. Stop Word Removal: Stop words are common words like “is”, “the”, “and”, etc., that do not carry much meaningful information. Removing these can help reduce the dimensionality of the data and focus on the important words.
4. Stemming: This is the process of reducing inflected (or sometimes derived) words to their word stem or root form. For example, “jumps”, “jumping”, and “jumped” would all be reduced to “jump”. This helps in treating different forms of the same word as one token.

#### Sparse_retriever Algorithm
The Sparse Retriever uses the BM25 algorithm to compute a relevance score between a query and a document. The algorithm consists of three main parts: term frequency, inverse document frequency, and document length normalization.

In the term frequency part, the frequency of each query term in the document is calculated. The inverse document frequency part calculates the frequency of each query term in the entire corpus of documents. The document length normalization part scales the document score based on its length.

After these three parts are calculated, the BM25 algorithm computes a similarity score between the query and the document. This score is represented by a vector with one element for each unique term in the query, with the value being the score for that term.

### Hybrid Retriever
The Hybrid Retriever leverages both lexical and semantic matching, is composed of three integral components: the Sparse Retriever, the Dense Retriever, and the Merger. The Merger plays a crucial role in fusing the results from the Sparse and Dense Retrievers to generate a comprehensive set of hybrid results. This design ensures an unbiased approach towards any specific type of search engine and relevant results for wider range of user query. Furthermore, its customizable weight configuration allows for a personalized search experience tailored to the user’s specific needs.

#### hybrid_retriever Algorithm(Merger)
Consider a scenario where the keyword search excels in finding relevant results for a user query, while the semantic search falls short. In our initial design, we selected the top 5 results from both the keyword and semantic searches. However, this approach could potentially overlook good results from the keyword search that are significantly more relevant than the top 5 results from a less effective semantic search.

Recognizing this limitation, it becomes evident that a method to compare and rank results from these two distinct searches is necessary. This is where the Merger shines. It employs a normalization technique to provide a fair comparison of scores from the two different searches, leading to a more equitable ranking of documents. This innovative approach ensures that no relevant document is overlooked, thereby enhancing the overall effectiveness of our Hybrid Retriever.

First normalize the similarity scores from dense_retriever and sparese_retriever, base on Min-Max normalization by default, it combines the normalized scores of the retrieval runs using a weighted sum. The results are then sorted by descending score and ascending document ID. Finally, the method applies a cutoff to limit the number of results returned for each query.

#### Results normalization
Min-Max Normalization: This method scales the scores to the range [0, 1] by subtracting the minimum score and dividing by the range of the scores. Normalization transforms the scores from different search engines to the same scale, making them directly comparable.
normalized_score = (score - min_score) / (max_score - min_score)

#### Customized Weight
The weights are either all equal (if self.params is None) or specified by self.params["weights"]. 
Customization example:
    merger = Merger()
    merger.params = {"weights": [0.7, 0.3]} 
    # Please note that the weights should sum up to 1, and number of weights should be 2
    hr.merger = merger