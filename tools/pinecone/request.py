from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import torch
import pinecone
from typing import List, Dict

app = FastAPI(
    title="Fashion Item Search API",
    description="API for searching fashion items using semantic search",
    version="1.0.0"
)

# Model and Pinecone Initialization
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

# Pinecone Connection
pinecone.init(api_key="pcsk_...")
index = pinecone.Index(name="sg")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    score: float
    metadata: Dict[str, str]

@app.get("/health")
async def health_check():
    """Checks if the server and the Pinecone connection are working"""
    try:
        if index_name not in pinecone.list_indexes():
            raise HTTPException(status_code=500, detail="Pinecone Index not available")
        return {"status": "healthy", "index": index_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=List[SearchResult])
async def search_items(request: SearchRequest):
    """Searches for similar fashion items"""
    try:
        # Convert query to vector
        query_vector = model.encode(request.query).tolist()
        
        # Query Pinecone
        results = index.query(
            vector=query_vector,
            top_k=request.top_k,
            include_metadata=True
        )
        
        # Format results
        formatted_results = [
            SearchResult(
                score=match.score,
                metadata=match.metadata
            )
            for match in results.matches
        ]
        
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1500)