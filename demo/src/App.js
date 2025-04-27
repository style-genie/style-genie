import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  async function searchItemsWithPinecone() {
    if (!query) {
      setResults([]);
      return;
    }
    //mode: 'no-cors',
    try {
      const response = await fetch('http://localhost:1500/search', {
        method: 'POST',
        
        headers: {
          'Content-Type': 'application/json',
          
        },
        body: JSON.stringify({
          query: query,
        }),
      })
      .then(function(response) {         
        print(response)             // first then()
        if(response.ok)
        {
          console.log(response)
          const data =  response.json();
          console.log(data);
          setResults(data.matches);
        }
  
        throw new Error('Something went wrong.');
    })  
    .then(function(text) {                          // second then()
      console.log('Request successful', text);  
    })  
    .catch(function(error) {                        // catch
      console.log('Request failed', error);
    });

      // if (!response.ok) {
      //   console.log(response)
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }
      // else{
      //   console.log(response);
      //   console.log(response.json());
      // }


    } catch (error) {
      console.error('Error:', error);
      setResults([{ error: 'Error loading data or performing search.' }]);
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Pinecone Search</p>
        <input
          type="text"
          id="searchInput"
          placeholder="Enter search query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={searchItemsWithPinecone}>Search</button>
      </header>
      <div id="results">
        {results.map((match, index) => (
          <div key={index} className="result-item">
            <p><strong>Score: {match.score}</strong></p>
            <p>ID: {match.id}</p>
            {match.metadata && Object.entries(match.metadata).map(([key, value]) => (
              <p key={key}>{key}: {value}</p>
            ))}
            {match.error && <p>Error: {match.error}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
