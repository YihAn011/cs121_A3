import os
import json
import nltk
import sys
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('punkt')

stemmer = PorterStemmer()

def goThroughAllFiles(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))  
    return json_files


def readFiles(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file) 
            html_content = data.get("content", "")  
            return normalAndImportant(html_content)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return "", ""  
    except Exception as e:
        print(f"Error reading file: {e}")
        return "", ""


def normalAndImportant(html):
    soup = BeautifulSoup(html, "lxml")

  
    normal_text = soup.get_text(separator=" ")

   
    important_tags = ["b", "strong", "h1", "h2", "h3", "title"]
    important_text = " ".join(tag.get_text(separator=" ") for tag in soup.find_all(important_tags))

    return normal_text, important_text


def tokenAndStem(text):
    tokens = word_tokenize(text.lower())  
    return [stemmer.stem(token) for token in tokens if token.isalnum()]  


def build_inverted_index(files):
    inverted_index = defaultdict(lambda: defaultdict(int)) 
    total_documents = len(files)

    for file in files:
        normal_text, important_text = readFiles(file)  

       
        tokens = tokenAndStem(normal_text)
        for token in tokens:
            inverted_index[token][file] += 1  

        
        important_tokens = tokenAndStem(important_text)
        for token in important_tokens:
            inverted_index[token][file] += 2  

    return inverted_index, total_documents


def makeFile(index, total_docs, filename="inverted_index.json"):
    index_data = {
        "total_documents": total_docs,
        "unique_tokens": len(index),
        "index": index
    }

    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(index_data, f, indent=4)


def getSize(filename):
    return os.path.getsize(filename) / 1024  


def main():
    if len(sys.argv) != 2:
        print("ERROR: Wrong number of arguments")
        sys.exit(1)
    
    directory = sys.argv[1]
    files = goThroughAllFiles(directory)  
    if not files:
        print("No JSON files in dir")
        sys.exit(1)

    index, total_docs = build_inverted_index(files) 
    makeFile(index, total_docs)  

   
    index_size = getSize("inverted_index.json")

    
    print(f"Index built successfully!")
    print(f"Indexed directory: {directory}")
    print(f"Number of indexed documents: {total_docs}")
    print(f"Unique tokens: {len(index)}")
    print(f"Total index size on disk: {index_size:.2f} KB")

if __name__ == "__main__":
    main()
