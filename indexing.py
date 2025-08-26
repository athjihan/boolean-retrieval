import os
import subprocess
import shutil

# define the path to the corpus (input documents) and the index directory (output)
corpus_path = 'corpus'
index_path = 'indexes/lucene-index-boolean-retrieval'

# remove the index directory if it exists to ensure a fresh index
if os.path.exists(index_path):
    print(f"Removing existing index directory: {index_path}")
    shutil.rmtree(index_path)

# create the index directory if it doesn't exist
os.makedirs(index_path, exist_ok=True)

# command to index JSON documents from the corpus_path into a Lucene index and applying Porter stemming
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
    # execute the indexing command
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print("Indexing completed successfully!")
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

# handle errors that occur during the command execution
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
    
print("🔢 Indexing process completed ✓")
