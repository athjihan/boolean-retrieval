import os
from typing import List, Dict, Set
from pyserini.search.lucene import LuceneSearcher
from pyserini.index import LuceneIndexReader

class BooleanRetrieval:
    def __init__(self, index_dir: str = "lucene_index"):
        self.index_dir = index_dir
        self.searcher = None
        self.index_reader = None
        self.inverted_index = {}
        self.documents = {}
        self.initialize_searcher()
        self.build_inverted_index()
    
    def initialize_searcher(self):
        if not os.path.exists(self.index_dir):
            raise FileNotFoundError(f"Index directory not found: {self.index_dir}")
        
        try:
            self.searcher = LuceneSearcher(self.index_dir)
            self.index_reader = LuceneIndexReader(self.index_dir)
            print("✓ Boolean retrieval system initialized")
            print(f"📁 Index: {self.index_dir}")
            print(f"📄 Documents available: {self.index_reader.stats()['documents']}")
        except Exception as e:
            raise Exception(f"Failed to initialize searcher: {e}")
    
    def build_inverted_index(self):
        print("Building inverted index...")
        total_docs = self.index_reader.stats()['documents']
        
        for internal_docid in range(total_docs):
            try:
                # Get document ID
                collection_docid = self.index_reader.convert_internal_docid_to_collection_docid(internal_docid)
                
                # Get document
                doc = self.index_reader.doc(collection_docid)
                if doc:
                    doc_content = doc.contents()
                    # Ensure doc_content is not None
                    if doc_content is None:
                        doc_content = ""
                    self.documents[collection_docid] = doc_content
                    
                    # Get document vector (terms and frequencies)
                    doc_vector = self.index_reader.get_document_vector(collection_docid)
                    if doc_vector:
                        for term in doc_vector.keys():
                            if term not in self.inverted_index:
                                self.inverted_index[term] = set()
                            self.inverted_index[term].add(collection_docid)
                else:
                    # Handle case where document is None
                    print(f"Warning: Document {collection_docid} returned None")
                    self.documents[collection_docid] = ""
                
            except Exception as e:
                print(f"Error processing document {internal_docid}: {e}")
        
        print(f"✓ Inverted index built with {len(self.inverted_index)} unique terms")
        print(f"✓ Documents loaded: {len(self.documents)}")
        print(f"✓ Inverted index built with {len(self.inverted_index)} unique terms")
    
    def search_boolean(self, query: str, max_results: int = 100) -> List[str]:
        """
        Perform Boolean search using manual inverted index
        """
        try:
            # Clean and parse query
            query = query.strip()
            if not query:
                return []
            
            # Parse Boolean query
            result_set = self._parse_boolean_query(query)
            
            # Convert set to sorted list
            results = sorted(list(result_set))[:max_results]
            return results
            
        except Exception as e:
            print(f"Error in Boolean search: {e}")
            return []
    
    def _parse_boolean_query(self, query: str) -> Set[str]:
        """
        Parse and execute Boolean query
        """
        query = query.lower().strip()
        
        # Handle different Boolean operators
        if " and not " in query:
            return self._handle_and_not(query)
        elif " and " in query:
            return self._handle_and(query)
        elif " or " in query:
            return self._handle_or(query)
        elif " not " in query:
            return self._handle_not(query)
        else:
            # Single term query
            return self._get_documents_for_term(query)
    
    def _handle_and(self, query: str) -> Set[str]:
        """Handle AND queries"""
        terms = [term.strip() for term in query.split(" and ")]
        
        if not terms:
            return set()
        
        # Start with documents containing the first term
        result_set = self._get_documents_for_term(terms[0])
        
        # Intersect with documents containing other terms
        for term in terms[1:]:
            term_docs = self._get_documents_for_term(term)
            result_set = result_set.intersection(term_docs)
        
        return result_set
    
    def _handle_or(self, query: str) -> Set[str]:
        """Handle OR queries"""
        terms = [term.strip() for term in query.split(" or ")]
        
        result_set = set()
        
        # Union all documents containing any of the terms
        for term in terms:
            term_docs = self._get_documents_for_term(term)
            result_set = result_set.union(term_docs)
        
        return result_set
    
    def _handle_not(self, query: str) -> Set[str]:
        """Handle NOT queries (term1 NOT term2)"""
        parts = query.split(" not ")
        if len(parts) != 2:
            return set()
        
        positive_term = parts[0].strip()
        negative_term = parts[1].strip()
        
        positive_docs = self._get_documents_for_term(positive_term)
        negative_docs = self._get_documents_for_term(negative_term)
        
        # Documents with positive term but not negative term
        return positive_docs - negative_docs
    
    def _handle_and_not(self, query: str) -> Set[str]:
        """Handle AND NOT queries"""
        parts = query.split(" and not ")
        if len(parts) != 2:
            return set()
        
        # Handle multiple terms before AND NOT
        left_part = parts[0].strip()
        negative_term = parts[1].strip()
        
        # Get documents matching the left part
        if " and " in left_part:
            positive_docs = self._handle_and(left_part)
        else:
            positive_docs = self._get_documents_for_term(left_part)
        
        # Get documents to exclude
        negative_docs = self._get_documents_for_term(negative_term)
        
        # Return positive documents minus negative documents
        return positive_docs - negative_docs
    
    def _get_documents_for_term(self, term: str) -> Set[str]:
        """
        Get all documents containing a specific term
        """
        term = term.strip().lower()
        if term in self.inverted_index:
            return self.inverted_index[term].copy()
        return set()
    
    def run_test_queries(self) -> List[Dict]:
        """
        Run a set of test queries and return results
        """
        test_queries = [
            "dog AND cat",
            "dog OR cat", 
            "dog AND NOT cat",
            "(bm25 OR tf-idf) AND retrieval",
        ]
        
        print("=" * 50)
        print("BOOLEAN RETRIEVAL")
        print("=" * 50)
        
        query_results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            
            # Perform search
            results = self.search_boolean(query)
            
            print(f"Matching documents: {results}")
            print(f"Total matches: {len(results)}")
            
            query_results.append({
                'query': query,
                'results': results
            })
        
        return query_results

if __name__ == "__main__":
    # Initialize the Boolean Retrieval system with the correct index directory
    # Assuming the index is located at 'indexes/lucene-index-boolean-retrieval'
    try:
        br_system = BooleanRetrieval(index_dir="indexes/lucene-index-boolean-retrieval")
        br_system.run_test_queries()
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the index directory is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
