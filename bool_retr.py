import os
from typing import List, Dict, Set
from pyserini.search.lucene import LuceneSearcher
from pyserini.index import LuceneIndexReader
from pyserini.analysis import Analyzer, get_lucene_analyzer

class BooleanRetrieval:
    def __init__(self, index_dir: str = "lucene_index"):
        self.index_dir = index_dir
        self.searcher = None
        self.index_reader = None
        self.inverted_index = {}
        self.documents = {}
        self.stemmer_analyzer = self._initialize_stemmer_analyzer()
        self.initialize_searcher()
        self.build_inverted_index()
    
    def _initialize_stemmer_analyzer(self):
        lucene_analyzer_for_stemming = get_lucene_analyzer(stemmer='porter')
        return Analyzer(lucene_analyzer_for_stemming)

    def initialize_searcher(self):
        if not os.path.exists(self.index_dir):
            raise FileNotFoundError(f"Index directory not found: {self.index_dir}")
        
        try:
            self.searcher = LuceneSearcher(self.index_dir)
            self.index_reader = LuceneIndexReader(self.index_dir)
        except Exception as e:
            raise Exception(f"Failed to initialize searcher: {e}")

    # mapping words to document IDs that contain them
    def build_inverted_index(self):
        total_docs = self.index_reader.stats()['documents']
        
        for internal_docid in range(total_docs):
            try:
                # get document ID
                collection_docid = self.index_reader.convert_internal_docid_to_collection_docid(internal_docid)
                
                # get document
                doc = self.index_reader.doc(collection_docid)
                if doc:
                    doc_content = doc.contents()
                    if doc_content is None:
                        doc_content = ""
                    self.documents[collection_docid] = doc_content
                    
                    # get document vector (terms and frequencies)
                    doc_vector = self.index_reader.get_document_vector(collection_docid)
                    if doc_vector:
                        for term in doc_vector.keys():
                            if term not in self.inverted_index:
                                self.inverted_index[term] = set()
                            self.inverted_index[term].add(collection_docid)
                else:
                    print(f"Warning: Document {collection_docid} returned None")
                    self.documents[collection_docid] = ""
                
            except Exception as e:
                print(f"Error processing document {internal_docid}: {e}")

    def search_boolean(self, query: str, max_results: int = 100) -> List[str]:
        try:
            print(f"Performing boolean search for query: '{query}'")
            # clean and parse query
            query = query.strip()
            if not query:
                return []
            
            # parse Boolean query
            result_set = self._parse_boolean_query(query)
            
            # convert set to sorted list, sorting numerically by extracting the number from the docid
            results = sorted(list(result_set), key=lambda x: int(x[1:]))[:max_results]
            return results
            
        except Exception as e:
            print(f"Error in Boolean search: {e}")
            return []
    
    def _parse_boolean_query(self, query: str) -> Set[str]:
        query = query.lower().strip()
        
        # handle different Boolean operators
        if " and not " in query:
            return self._handle_and_not(query)
        elif " and " in query:
            return self._handle_and(query)
        elif " or " in query:
            return self._handle_or(query)
        elif " not " in query:
            return self._handle_not(query)
        else:
            # single term query
            return self._get_documents_for_term(query)
    
    def _handle_and(self, query: str) -> Set[str]:
        terms = [term.strip() for term in query.split(" and ")]
        
        if not terms:
            return set()
        
        # start with documents containing the first term
        result_set = self._get_documents_for_term(terms[0])
        
        # intersect with documents containing other terms
        for term in terms[1:]:
            term_docs = self._get_documents_for_term(term)
            result_set = result_set.intersection(term_docs)
        
        return result_set
    
    def _handle_or(self, query: str) -> Set[str]:
        terms = [term.strip() for term in query.split(" or ")]
        
        result_set = set()
        
        # union all documents containing any of the terms
        for term in terms:
            term_docs = self._get_documents_for_term(term)
            result_set = result_set.union(term_docs)
        
        return result_set
    
    def _handle_not(self, query: str) -> Set[str]:
        parts = query.split(" not ")
        if len(parts) != 2:
            return set()
        
        positive_term = parts[0].strip()
        negative_term = parts[1].strip()
        
        positive_docs = self._get_documents_for_term(positive_term)
        negative_docs = self._get_documents_for_term(negative_term)
        
        # documents with positive term but not negative term
        return positive_docs - negative_docs
    
    def _handle_and_not(self, query: str) -> Set[str]:
        parts = query.split(" and not ")
        if len(parts) != 2:
            return set()
        
        # handle multiple terms before AND NOT
        left_part = parts[0].strip()
        negative_term = parts[1].strip()
        
        if " and " in left_part:
            positive_docs = self._handle_and(left_part)
        else:
            positive_docs = self._get_documents_for_term(left_part)
        
        negative_docs = self._get_documents_for_term(negative_term)
        
        return positive_docs - negative_docs

    # get all documents containing a specific term
    def _get_documents_for_term(self, term: str) -> Set[str]:
        term = term.strip().lower()
        
        # apply stemming to the query term
        analyzed_result = self.stemmer_analyzer.analyze(term)
        stemmed_term = analyzed_result[0] if analyzed_result else term

        if stemmed_term in self.inverted_index:
            return self.inverted_index[stemmed_term].copy()
        return set()
    
    def run_queries(self) -> List[Dict]:
        queries = [
            "dog AND cat",
            "dog OR cat", 
            "dog AND NOT cat",
            "(bm25 OR tf-idf) AND retrieval",
            "neural AND NOT (bm25 OR tf-idf)",
            "retrieval OR rarity"
        ]
        
        print("=" * 50)
        print("BOOLEAN RETRIEVAL")
        print("=" * 50)
        
        query_results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}: {query}")
            
            # perform search
            results = self.search_boolean(query)
            
            print(f"Matching documents: {results}")
            print(f"Total matches: {len(results)}")
            
            query_results.append({
                'query': query,
                'results': results
            })
        
        return query_results


if __name__ == "__main__":
    try:
        br_system = BooleanRetrieval(index_dir="indexes/lucene-index-boolean-retrieval")
        br_system.run_queries()
        print("=" * 50)
        print("\n📚 Boolean retrieval queries completed ✓")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the index directory is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
