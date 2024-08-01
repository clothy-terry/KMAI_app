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




