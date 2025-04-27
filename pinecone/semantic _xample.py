import os
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from pinecone_datasets import load_dataset
from sentence_transformers import SentenceTransformer
import torch

# Pinecone API Key und Umgebungsvariablen
if not os.environ.get("PINECONE_API_KEY"):
    # Hier müsstest du eine Methode einfügen, um den API-Key zu authentifizieren.
    # Beispiel:
    # from getpass import getpass
    # os.environ["PINECONE_API_KEY"] = getpass("Gib deinen Pinecone API Key ein: ")
    pass

# Pinecone Initialisierung
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = 'semantic-search-fast'

# Index erstellen, falls nicht vorhanden
if not pc.has_index(name=index_name):
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='dotproduct',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

# Index-Client initialisieren
index = pc.Index(name=index_name)

# Daten laden und vorbereiten
dataset = load_dataset('quora_all-MiniLM-L6-bm25')
dataset.documents.drop(['metadata'], axis=1, inplace=True)
dataset.documents.rename(columns={'blob': 'metadata'}, inplace=True)
dataset.documents.drop(['sparse_values'], axis=1, inplace=True)
dataset.documents.drop(dataset.documents.index[320_000:], inplace=True)
dataset.documents.drop(dataset.documents.index[:240_000], inplace=True)

# Daten in den Index einfügen
batch_size = 100
for start in tqdm(range(0, len(dataset.documents), batch_size), "Upserting records batch"):
    batch = dataset.documents.iloc[start:start + batch_size].to_dict(orient="records")
    index.upsert(vectors=batch)

# SentenceTransformer-Modell laden
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

# Funktion zum Finden ähnlicher Fragen
def find_similar_questions(question):
    xq = model.encode(question).tolist()
    return index.query(vector=xq, top_k=5, include_metadata=True)

# Funktion zum Ausgeben der Ergebnisse
def print_query_results(results):
    for result in results['matches']:
        print(f"{round(result['score'], 2)}: {result['metadata']['text']}")

# Beispielabfrage
question = "Welche Stadt hat die höchste Einwohnerzahl der Welt?"
results = find_similar_questions(question)
print_query_results(results)

# Index löschen (optional)
# pc.delete_index(name=index_name)