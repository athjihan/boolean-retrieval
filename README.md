# Boolean Retrieval System 📚

This project implements a basic Boolean retrieval system using `Pyserini` and `Lucene` for indexing and searching. It allows users to preprocess a collection of documents, build an inverted index, and perform Boolean queries (AND, OR, NOT, AND NOT) to retrieve relevant documents.

## Features ✨

*   **Document Preprocessing:** Utilizes Pyserini's Lucene analyzer for tokenization and stemming of documents.
*   **Lucene Indexing:** Indexes preprocessed documents into a Lucene index using Pyserini's Anserini indexer.
*   **Boolean Search:** Supports complex Boolean queries with `AND`, `OR`, `NOT`, and `AND NOT` operators.
*   **Inverted Index Construction:** Builds a manual inverted index from the Lucene index for efficient Boolean operations.
*   **Test Queries:** Includes a set of predefined test queries to demonstrate functionality.

## Installation 💻

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/athjihan/boolean-retrieval.git
    cd boolean-retrieval
    ```

2.  **Install dependencies:**
    ```bash
    pip install pyserini
    ```
    *(Note: Pyserini requires Java 11 or higher to be installed and configured in your PATH.)*

## Usage 🚀

Follow these steps to preprocess documents, build the index, and run the Boolean retrieval system:

1.  **Preprocess Documents:**
    Run the `preprocess.py` script to preprocess the sample documents and generate `corpus/docs.jsonl`.
    ```bash
    python preprocess.py
    ```

2.  **Build Lucene Index:**
    Run the `indexing.py` script to build the Lucene index from the preprocessed documents. The index will be stored in the `indexes/lucene-index-boolean-retrieval` directory.
    ```bash
    python indexing.py
    ```

3.  **Run Boolean Retrieval System:**
    Execute the `bool_retr.py` script to initialize the Boolean retrieval system and run predefined test queries.
    ```bash
    python bool_retr.py
    ```

## Dependencies 📦

*   `pyserini`: A Python toolkit for reproducible information retrieval research with sparse and dense representations.
