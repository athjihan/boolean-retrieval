from pyserini.analysis import Analyzer, get_lucene_analyzer
import re

lucene_analyzer_for_stemming = get_lucene_analyzer(stemmer='porter')
stemmer_analyzer = Analyzer(lucene_analyzer_for_stemming)

# list stopwords
stopwords = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
             "if", "in", "into", "is", "it", "no", "not", "of", "on", "or",
             "such", "that", "the", "their", "then", "there", "these",
             "they", "this", "to", "was", "will", "with"}

def preprocess_document(document_text):
    # 1. lowercase
    text = document_text.lower()

    # 2. remove punctuation and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text) 
    text = re.sub(r'\s+', ' ', text).strip() 

    # tokenize
    tokens = text.split()

    # 3. remove stopwords
    filtered_tokens = [word for word in tokens if word not in stopwords]

    # 4. stemming using Pyserini's Porter stemmer
    stemmed_tokens = []
    for token in filtered_tokens:
        analyzed_result = stemmer_analyzer.analyze(token)
        if analyzed_result:
            stemmed_tokens.append(analyzed_result[0])
        else:
            stemmed_tokens.append(token)

    return " ".join(stemmed_tokens)

docs = [
  ("d1",  "The cat chased a small mouse into the garden."),
  ("d2",  "A friendly dog played fetch by the river."),
  ("d3",  "BM25 is a ranking function widely used in search engines."),
  ("d4",  "Boolean retrieval uses logical operators like AND and OR."),
  ("d5",  "TF-IDF weights terms by frequency and rarity."),
  ("d6",  "Neural retrieval uses dense embeddings for semantic search."),
  ("d7",  "The dog and the cat slept on the same couch."),
  ("d8",  "The library hosts a workshop on information retrieval."),
  ("d9",  "Students implemented BM25 and compared it with TF-IDF."),
  ("d10", "The chef roasted chicken with rosemary and garlic."),
  ("d11", "A black cat crossed the old stone bridge at night."),
  ("d12", "Dogs are loyal companions during long hikes."),
  ("d13", "The dataset contains fifteen short sentences for testing."),
  ("d14", "Reranking models reorder BM25 candidates using transformers."),
  ("d15", "The dog sniffed a cat but ignored the mouse.")
]

preprocessed_documents = []
for doc_id, doc_text in docs:
    preprocessed_doc = preprocess_document(doc_text)
    preprocessed_documents.append({"id": doc_id, "contents": preprocessed_doc})

print("Preprocessed Documents:")
for doc in preprocessed_documents:
    print(doc)
