# -*- coding: utf-8 -*-
"""philosophy_bot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S1g1hqLZ7sZtq3tQ8Pxadj9yC1fPI9Wr?usp=sharing

# Installing dependencies
"""

!pip install -q pandas sentence-transformers chromadb requests gradio

"""# Importing the required libraries"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import requests
import os

"""# Setting OpenRouter API Key"""

os.environ["OPENROUTER_API_KEY"] = "YOUR-API-KEY-HERE"

"""# Loading the dataset from Google Drive"""

from google.colab import drive
drive.mount('/content/drive')
file_path = '/content/drive/My Drive/philosophy_data.csv'
df = pd.read_csv(file_path)
df = df.dropna(subset=['sentence_str']).reset_index(drop=True)
df['original_publication_date'] = df['original_publication_date'].astype(int)

"""# Sentence encoding"""

sentences = df['sentence_str'].tolist()
model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(sentences, batch_size=32, show_progress_bar=True)

"""# Seting up ChromaDB"""

client = chromadb.Client()
try:
    collection = client.get_collection("philosophy")
except:
    collection = client.create_collection("philosophy")

"""# Addding text to ChromaDB in batches"""

if len(collection.get()['ids']) == 0:
    ids = [f"philo_{i}" for i in range(len(sentences))]
    metadatas = df[['author','school','original_publication_date']].to_dict(orient='records')
    batch_size = 5000
    for start in range(0, len(sentences), batch_size):
        end = min(start + batch_size, len(sentences))
        collection.add(
            documents=sentences[start:end],
            embeddings=vectors[start:end].tolist(),
            ids=ids[start:end],
            metadatas=metadatas[start:end]
        )
        print(f"Added records {start} to {end}")

"""# Retrieve function"""

def retrieve_quotes(question: str, top_k: int = 3):
    q_vec = model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=q_vec,
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    return list(zip(results['documents'][0], results['metadatas'][0]))

"""# LLM call via OpenRouter

"""

def ask_llm(question: str, top_k: int = 3) -> str:
    ctx = retrieve_quotes(question, top_k=top_k)
    quotes_text = "\n\n".join(
        f"{m['author']} ({m['school']}): “{d}”" for d, m in ctx
    )

    messages = [
        {"role": "system", "content": "You are a learned philosophy assistant. Quote relevant passages with author and school, then explain clearly."},
        {"role": "user", "content": f"Here are some passages:\n\n{quotes_text}\n\nQUESTION: {question}\n\nAnswer based on those passages."}
    ]

    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {"model": "mistralai/mistral-7b-instruct", "messages": messages}

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    try:
        response.raise_for_status()
        data = response.json()
        print("Response from LLM:", data)
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("ERROR:", e)
        print("Full response text:", response.text)
        return "Sorry, an error occurred while contacting the AI."

"""# Test call"""

for doc, meta in retrieve_quotes("Body without organs", top_k=7):
    print(f"{meta['author']} ({meta['school']}): {doc}")

#@title { vertical-output: true}
print(ask_llm("What is body without organs?"))
