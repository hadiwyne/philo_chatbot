# Philosophy Q&A Bot

A lightweight Question-Answering chatbot that answers philosophical questions using embedded passages from key thinkers like Plato, Aristotle, Nietzsche, and Foucault.

---

## What It Does

- Ingests and vectorizes philosophical quotes using `sentence-transformers`
- Stores and retrieves relevant quotes via `ChromaDB`
- Calls a free LLM (via OpenRouter) to generate answers based on retrieved passages

---

## Try It Live

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1S1g1hqLZ7sZtq3tQ8Pxadj9yC1fPI9Wr?usp=sharing)

---

## Tech Stack

| Component              | Tool/Library             |
|------------------------|--------------------------|
| Embedding Model        | `sentence-transformers` (MiniLM) |
| Vector Database        | `ChromaDB` (DuckDB+Parquet) |
| LLM Backend (Free API) | `OpenRouter` (Mistral, etc.) |
| Notebook Environment   | Google Colab             |

---
