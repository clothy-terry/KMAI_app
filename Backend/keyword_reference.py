#pip install nltk spacy scikit-learn
#python -m spacy download en_core_web_sm

import nltk
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import string


# Download NLTK data files (run once)
nltk.download('punkt')
nltk.download('stopwords')


# Load spaCy model
nlp = spacy.load('en_core_web_sm')


# Function to extract keywords using CountVectorizer
def extract_keywords(text, num_keywords=5):
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    cv = CountVectorizer(stop_words=stop_words)
    word_count_vector = cv.fit_transform([text])
    sum_words = word_count_vector.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in cv.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in words_freq[:num_keywords]]
    return keywords


# Function to find sentence or nearby words for each keyword
def find_keyword_context(text, keywords, window_size=None):
    # split the each doc text into sentences -> doc.sents
    doc = nlp(text)
    keyword_context = {}
   
    # find sentence
    if window_size is None:
        for sentence in doc.sents:
            for keyword in keywords:
                if keyword in sentence.text.lower():
                    sentence_words = [token.text.lower() for token in sentence]
                    #sentence.text
                    # if keyword exist in return dict
                    if keyword in keyword_context:
                        keyword_context[keyword].append(sentence.text)
                    else:
                        keyword_context[keyword] = [sentence.text]
    # find context
    else:
        for token in doc:
            if token.text.lower() in keywords:
                start = max(0, token.i - window_size)
                end = min(len(doc), token.i + window_size + 1)
                context_words = [doc[i].text for i in range(start, end)]
                if token.text.lower() in keyword_context:
                    keyword_context[token.text.lower()].append(' '.join(context_words))
                else:
                    keyword_context[token.text.lower()] = [' '.join(context_words)]
   
    return keyword_context


# Example usage
text = """
Artificial Intelligence (AI) is transforming industries by enabling new solutions. Machine Learning, a subset of AI, is particularly effective for predictive analytics. Companies are investing heavily in AI research and development. The impact of AI is significant in healthcare, finance, and transportation. Natural Language Processing (NLP) is a crucial area within AI that deals with the interaction between computers and humans through language.
"""


# Customizable keywords
custom_keywords = ['ai', 'learning', 'processing', 'impact']


# Extract keywords (if needed)
# keywords = extract_keywords(text, num_keywords=5)
# print("Extracted Keywords:", keywords)


# Find context for each keyword
keyword_context = find_keyword_context(text, custom_keywords, 3)

# demo
doc = nlp(text)
print(doc)
print(doc.sents)
sentences = list(doc.sents)
print('toekns:', [token for token in sentences[0]])
print(sentences[0].text)


# Display keyword contexts
for keyword, contexts in keyword_context.items():
    print(f"\nKeyword: {keyword}")
    for context_words in contexts:
        print(f"Context words: {(context_words)}")




