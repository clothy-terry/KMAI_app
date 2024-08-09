#pip install spacy
#python -m spacy download en_core_web_sm

import spacy
from spacy.matcher import PhraseMatcher

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

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
                    if keyword in keyword_context:
                        keyword_context[keyword].append(sentence.text)
                    else:
                        keyword_context[keyword] = [sentence.text]
    # find nearby words of key phrase
    else:
        matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        # store the sequence of token/key phrase/pattern to a Doc object for efficient find
        key_phrase = [nlp.make_doc(keyword) for keyword in keywords]
        matcher.add("KeywordMatcher", key_phrase)

        matches = matcher(doc)
        for match_id, start, end in matches:
            keyword = doc[start:end].text
            context_start = max(0, start - window_size)
            context_end = min(len(doc), end + window_size)
            context = doc[context_start:context_end].text
            if keyword in keyword_context:
                keyword_context[keyword].append(context)
            else:
                keyword_context[keyword] = [context]
    return keyword_context


def test_find_keyword_context():
    text = "The quick brown fox jumps over the lazy dog. The dog was not amused."
    keywords = ["fox jumps", "dog was", "not amused", 'lazy']
    window_size = 3

    keyword_context = find_keyword_context(text, keywords, window_size)

    for keyword, contexts in keyword_context.items():
        print(f"\nKeyword: {keyword}")
        for context_words in contexts:
            print(f"Context words: {(context_words)}")

if __name__ == '__main__':
    test_find_keyword_context()






