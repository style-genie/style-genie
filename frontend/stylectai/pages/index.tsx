import React, { useState, useEffect } from 'react';
import { setCookie, getCookie } from 'cookies-next';
import UserModal from '../components/UserModal';
import SessionTest from './session_test';

const IndexPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  useEffect(() => {
    const storedSessionId = getCookie('sessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId.toString());
      setIsModalOpen(false); // Close modal if session ID exists
    }
  }, []);

  const handleModalSubmit = async (username: string, bearerToken: string) => {
    setIsModalOpen(false);

    try {
      const response = await fetch('/api/auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, bearerToken }),
      });

      if (response.ok) {
        const data = await response.json();
        const newSessionId = data.sessionId;
        setSessionId(newSessionId);
        setCookie('sessionId', newSessionId);
      } else {
        console.error('Authentication failed');
      }
    } catch (error) {
      console.error('Error during authentication:', error);
    }
  };

  return (
    <div>
      {isModalOpen && (
        <UserModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleModalSubmit}
        />
      )}
      {!isModalOpen&&sessionId ? (
        <SessionTest />
      ) : (
        <h1>Please log in to continue</h1>
      )}
    </div>
  );
};

export default IndexPage;
