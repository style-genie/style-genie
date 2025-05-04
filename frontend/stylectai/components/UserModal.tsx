import React, { useState } from 'react';

interface UserModalProps {
  onClose: () => void;
  onSubmit: (username: string, bearerToken: string) => void;
}

const UserModal: React.FC<UserModalProps> = ({ onClose, onSubmit }) => {
  const [username, setUsername] = useState('');
  const [bearerToken, setBearerToken] = useState('');

  const handleSubmit = () => {
    onSubmit(username, bearerToken);
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <span className="close" onClick={onClose}>&times;</span>
        <h2>Enter Username and Bearer Token</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="text"
          placeholder="Bearer Token"
          value={bearerToken}
          onChange={(e) => setBearerToken(e.target.value)}
        />
        <button onClick={handleSubmit}>Submit</button>
      </div>
    </div>
  );
};

export default UserModal;
