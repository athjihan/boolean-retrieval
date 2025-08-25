import os
import subprocess

# Define the path to the corpus and the index directory
corpus_path = 'corpus'
index_path = 'indexes/lucene-index-boolean-retrieval'

# Ensure the index directory exists
os.makedirs(index_path, exist_ok=True)

# Command to index the corpus using Pyserini's Anserini indexer
# We need to specify the collection, input path, index path, and other options.
# Pyserini's `index` command is a wrapper around Anserini's indexing capabilities.
# The command structure is typically:
# python -m pyserini.index -collection JsonCollection -generator Default
# -threads 1 -input <corpus_path> -index <index_path>
# -storePositions -storeDocvectors -storeRaw -stemmer porter

command = [
    "python", "-m", "pyserini.index.lucene",
    "-collection", "JsonCollection",
    "-generator", "DefaultLuceneDocumentGenerator",
    "-threads", "1",
    "-input", corpus_path,
    "-index", index_path,
    "-storePositions",
    "-storeDocvectors",
    "-storeRaw",
    "--stemmer", "porter"
]

print(f"Starting indexing process for corpus: {corpus_path}")
print(f"Index will be stored at: {index_path}")
print(f"Executing command: {' '.join(command)}")

try:
    # Execute the command
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print("Indexing completed successfully!")
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
except subprocess.CalledProcessError as e:
    print(f"Error during indexing: {e}")
    print("STDOUT:")
    print(e.stdout)
    print("STDERR:")
    print(e.stderr)
except FileNotFoundError:
    print("Error: 'python' command not found. Ensure Python is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
