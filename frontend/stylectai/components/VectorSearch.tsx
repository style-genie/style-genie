import React, { useState, useEffect } from 'react';

interface Result {
  score: number;
  values: any; // Adjust the type of values based on your data
}

const VectorSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiKey = "pcsk_6x3uAk_9t8PaNmdJx3kTVMJ5PENnRhQXYgdRJ4QZoQA79krQmpcXyL9XmXxWKEBxmLqXYP";
  const indexName = "sg";
  const indexHost = "sg-va8ozeb.svc.aped-4627-b74a.pinecone.io";
  const namespace = "";

  const searchItemsWithPinecone = async () => {
    setLoading(true);
    setError(null);
    setResults([]);

    const url = `https://${indexHost}/indexes/${indexName}/query`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Api-Key': apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vector: null,
          topK: 2,
          namespace: namespace,
          query: query,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);

      if (data.matches) {
        setResults(data.matches as Result[]);
      } else {
        setResults([]);
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during the search.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="search-container">
        <input
          type="text"
          id="searchInput"
          placeholder="Enter search query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={searchItemsWithPinecone} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      <div id="results">
        {results.map((result, index) => (
          <div key={index} className="result-item">
            <p><strong>Score: {result.score}</strong></p>
            <p>Value: {JSON.stringify(result.values)}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VectorSearch;
