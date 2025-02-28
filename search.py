# from flask import Flask, request, jsonify, render_template
# import os
# import json
# import math
# import nltk
# import re
# import requests
# from urllib.parse import urlparse
# from collections import defaultdict
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
# from urllib.parse import urlparse, urlunparse

# nltk.download('punkt')

# stemmer = PorterStemmer()

# app = Flask(__name__)  



# def normalize_url(url):
    
#     parsed = urlparse(url)
    
    
#     path = re.sub(r"index\.(html|php)$", "", parsed.path, flags=re.IGNORECASE)

#     path = re.sub(r"\.php$", "", path, flags=re.IGNORECASE)
    
#     normalized_url = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, ""))

#     return normalized_url



# def check_http_status(url):
#     try:
#         response = requests.get(url, allow_redirects=True, timeout=5)
        
        
#         if response.status_code < 400:
#             return response.url  
        
#         return None  
#     except requests.RequestException:
#         return None  


# def is_valid_webpage(url):
#     parsed = urlparse(url)
#     if re.search(
#         r"\.(css|js|bmp|gif|jpe?g|ico"
#         r"|png|tiff?|mid|mp2|mp3|mp4"
#         r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
#         r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
#         r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
#         r"|epub|dll|cnf|tgz|sha1"
#         r"|thmx|mso|arff|rtf|jar|csv"
#         r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib|img|apk|war|txt|lif|ff|sift|narrowPeak)$",
#         parsed.path.lower()):
#         return False

#     blocked_keywords = ["aiml","syllabus","paper","dataset","quotation","pdf", "book", "bibs", "bibtex", "dblp", "citation", "bib", "pubs", "sheet", "public_data", "~dechter/courses/" ,"publications"]
#     if any(kw in url.lower() for kw in blocked_keywords):
#         return False
    
#     return True

# def load_inverted_index(filename="inverted_index.json"):
#     try:
#         with open(filename, 'r', encoding="utf-8") as f:
#             index_data = json.load(f)
#             return index_data["index"], index_data["total_documents"]
#     except FileNotFoundError:
#         return None, 0

# def tokenAndStem(text):
#     tokens = word_tokenize(text.lower())  
#     return [stemmer.stem(token) for token in tokens if token.isalnum()]  

# def boolean_and_search(query_terms, index):
#     doc_sets = []
#     for term in query_terms:
#         if term in index:
#             doc_sets.append(set(index[term].keys()))
#         else:
#             return set()
#     return set.intersection(*doc_sets) if doc_sets else set()

# def boolean_or_search(query_terms, index):
#     doc_sets = set()
#     for term in query_terms:
#         if term in index:
#             doc_sets.update(index[term].keys())
#     return doc_sets

# # def compute_tf_idf(query_terms, index, total_docs):
# #     doc_scores = defaultdict(float)
# #     for term in query_terms:
# #         if term in index:
# #             df = len(index[term])
# #             idf = math.log((total_docs + 1) / (df + 1))
# #             for doc, tf in index[term].items():
# #                 doc_scores[doc] += tf * idf
# #     return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

# def compute_tf_idf(query_terms, index, total_docs, relevant_docs):
#     """
#     计算 TF-IDF 评分，仅针对 boolean AND 过滤后的文档
#     """
#     doc_scores = defaultdict(float)

#     for term in query_terms:
#         if term in index:
#             df = len(index[term])  # 该词出现在多少个文档中
#             idf = math.log((total_docs + 1) / (df + 1)) + 1  # 避免 IDF = 0，加 1 平滑

#             for doc in relevant_docs:  # 只计算 `AND` 过滤后的文档
#                 if doc in index[term]:  # 该文档包含该查询词
#                     tf = index[term][doc]  # 该词在文档中的频率
#                     tf_weighted = 1 + math.log(tf) if tf > 0 else 0  # 计算 TF，log 归一化
#                     doc_scores[doc] += tf_weighted * idf  # 计算 TF-IDF 评分

#     return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)



# def get_url_from_json(file_path):
#     try:
#         with open(file_path, 'r', encoding="utf-8") as file:
#             data = json.load(file)
#             return data.get("url", file_path)
#     except Exception:
#         return file_path

# @app.route('/')
# def index():
#     return render_template('index.html') 

# @app.route('/search', methods=['POST'])
# def search():
#     query = request.json.get('query', '').strip()
#     if not query:
#         return jsonify({"error": "Empty query"}), 400

#     index, total_docs = load_inverted_index()
#     if not index:
#         return jsonify({"error": "Index not found"}), 500

#     query_terms = tokenAndStem(query)
    
    
#     relevant_docs = boolean_and_search(query_terms, index)
#     # if not relevant_docs:
#     #     relevant_docs = boolean_or_search(query_terms, index)
#     if not relevant_docs:  
#         return jsonify([])
    
#     ranked_results = compute_tf_idf(query_terms, index, total_docs, relevant_docs)


#     unique_urls = set()
#     valid_results = []

#     for doc, score in ranked_results:
#         url = get_url_from_json(doc)
#         normalized_url = normalize_url(url) 
        
#         # if normalized_url not in unique_urls and is_valid_webpage(url) and check_http_status(url):
#         #     unique_urls.add(normalized_url)
#         #     valid_results.append({"url": url, "score": round(score, 4)})
#         final_url = check_http_status(url)  # 获取最终 URL

#         if final_url and is_valid_webpage(final_url):
#             normalized_url = normalize_url(final_url)  # 规范化最终 URL
            
#             if normalized_url not in unique_urls:
#                 unique_urls.add(normalized_url)
#                 valid_results.append({"url": final_url, "score": round(score, 4)})


#         if len(valid_results) >= 5:  
#             break

#     return jsonify(valid_results)


# if __name__ == '__main__':
#     app.run(debug=True)  
from flask import Flask, request, jsonify, render_template
import json
import math
import nltk
import re
import time
import requests
from urllib.parse import urlparse, urlunparse
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from functools import lru_cache

nltk.download('punkt')

stemmer = PorterStemmer()
app = Flask(__name__)

# **✅ Load Index Once at Startup**
print("Loading inverted index...")
index, total_docs = None, 0

def load_inverted_index(filename="inverted_index.json"):
    global index, total_docs
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            index_data = json.load(f)
            index, total_docs = index_data["index"], index_data["total_documents"]
            print(f"✅ Loaded {len(index)} terms from inverted index.")
    except FileNotFoundError:
        index, total_docs = None, 0

load_inverted_index()  # Load once at startup

# **✅ Optimized URL Normalization**
def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower().rstrip("/")
    path = re.sub(r"index\.(html|php)$", "", path, flags=re.IGNORECASE)
    path = re.sub(r"\.php$", "", path, flags=re.IGNORECASE)
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, ""))

# **✅ Cached URL Checker to Avoid Network Requests**
url_status_cache = {}

@lru_cache(maxsize=5000)
def check_http_status(url):
    if url in url_status_cache:
        return url_status_cache[url]
    
    try:
        response = requests.head(url, allow_redirects=True, timeout=2)  # Use HEAD request instead of GET
        if response.status_code < 400:
            url_status_cache[url] = response.url
            return response.url
    except requests.RequestException:
        pass
    
    url_status_cache[url] = None
    return None

# **✅ Reduce Unnecessary HTTP Requests**
def is_valid_webpage(url):
    parsed = urlparse(url)
    if re.search(
        r"\.(css|js|bmp|gif|jpe?g|ico"
        r"|png|tiff?|mid|mp2|mp3|mp4"
        r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
        r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        r"|epub|dll|cnf|tgz|sha1"
        r"|thmx|mso|arff|rtf|jar|csv"
        r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib|img|apk|war|txt|lif|ff|sift|narrowPeak)$",
        parsed.path.lower()):
        return False

    blocked_keywords = ["aiml","syllabus","paper","dataset","quotation","pdf", "book", "bibs", "bibtex", "dblp", "citation", "bib", "pubs", "sheet", "public_data", "~dechter/courses/" ,"publications"]
    if any(kw in url.lower() for kw in blocked_keywords):
        return False
    
    return True

# **✅ Optimized Query Processing**
def tokenAndStem(text):
    return [stemmer.stem(token) for token in word_tokenize(text.lower()) if token.isalnum()]

# **✅ Faster Boolean Search**
def boolean_and_search(query_terms):
    if not query_terms or index is None:
        return set()

    doc_sets = [set(index[term].keys()) for term in query_terms if term in index]
    return set.intersection(*doc_sets) if doc_sets else set()

# **✅ Precompute IDF Values**
idf_cache = {}

def compute_tf_idf(query_terms, relevant_docs):
    doc_scores = defaultdict(float)

    for term in query_terms:
        if term not in index:
            continue

        if term not in idf_cache:
            df = len(index[term])
            idf_cache[term] = math.log((total_docs + 1) / (df + 1)) + 1  # Smoothed IDF
        idf = idf_cache[term]

        for doc in relevant_docs:
            if doc in index[term]:
                tf = index[term][doc]
                tf_weighted = 1 + math.log(tf) if tf > 0 else 0
                doc_scores[doc] += tf_weighted * idf

    return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

# **✅ Faster URL Lookup**
def get_url_from_json(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return json.load(file).get("url", file_path)
    except Exception:
        return file_path

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    start_time = time.time()
    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    if index is None:
        return jsonify({"error": "Index not found"}), 500

    query_terms = tokenAndStem(query)
    
    # **✅ Faster Boolean Search**
    relevant_docs = boolean_and_search(query_terms)
    if not relevant_docs:
        return jsonify([])

    # **✅ Faster Ranking**
    ranked_results = compute_tf_idf(query_terms, relevant_docs)

    unique_urls = set()
    valid_results = []

    for doc, score in ranked_results:
        url = get_url_from_json(doc)
        final_url = check_http_status(url)  # Cached status check

        if final_url and is_valid_webpage(final_url):
            normalized_url = normalize_url(final_url)
            if normalized_url not in unique_urls:
                unique_urls.add(normalized_url)
                valid_results.append({"url": final_url, "score": round(score, 4)})

        if len(valid_results) >= 5:
            break
    elapsed_time = (time.time() - start_time) * 1000
    print(f"🔍 Search completed in {elapsed_time:.2f} ms")
    return jsonify(valid_results)

if __name__ == '__main__':
    app.run(debug=True)
