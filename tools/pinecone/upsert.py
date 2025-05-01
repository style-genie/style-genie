import json
from pinecone import Pinecone 
import os
from tqdm import tqdm

# Load data from pinecone_data.json
try:
    with open('pinecone_data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: pinecone_data.json not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Invalid JSON format in pinecone_data.json.")
    exit()

# Initialize Pinecone (replace with your API key and environment)
try:
    pc = Pinecone(api_key="pcsk_...")
    host = "https://sg-va8ozeb.svc.aped-4627-b74a.pinecone.io"  # Replace with your index name
    index = pc.Index(host=host)
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    exit()

# Prepare data for upsert (assuming data is a list of dictionaries)
batch_size = 100
if isinstance(data, list):
    for start in tqdm(range(0, len(data), batch_size), desc="Upserting records batch"):
        batch = data[start:start + batch_size]
        vectors = []
        for item in batch:
            if isinstance(item, dict):
                vector_id = str(item.get('id'))  # Use 'id' as the vector ID
                text = item.get('description') # Use description as text
                vector_values = item.get('values') # Assuming the vector is already calculated
                metadata = {k: v for k, v in item.items() if k not in ['id', 'description', 'values']} # Store all other fields as metadata
                vectors.append({'values': "", "id": vector_id, 'text': text})

                    # if isinstance(vector_values, list):
                        # try:
                            # vector_values = [float(x) for x in vector_values] # Convert vector values to float
                        # except ValueError:
                            # print(f"Error: Invalid vector values for item with id {vector_id}.  Ensure vector values are numbers.")
                    # else:
                        # print(f"Warning: 'values' field for item with id {vector_id} is not a list.")
            # else:
                # print("Warning: Skipping non-dictionary item in data.")

        # Upsert to Pinecone
        if vectors:
            try:
                index.upsert_records("",vectors)
                print(f"Successfully upserted {len(vectors)} vectors to Pinecone index '{host}'")
            except Exception as e:
                print(f"Error upserting to Pinecone: {e}")
else:
    print("Error: Data in pinecone_data.json is not a list.")
    exit()
