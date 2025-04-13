import React from 'react';

const ConnectCoinbase = () => {
  const handleConnect = () => {
    // Redirect the user to your backend's Coinbase OAuth connection endpoint.
    // Ensure that this endpoint (e.g., /coinbase/connect/) is configured in your Django URLs.
    window.location.href = 'http://localhost:8000/coinbase/connect/';
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '2rem' }}>
      <h2>Connect Your Coinbase Wallet</h2>
      <p>Click the button below to connect your Coinbase wallet for live trading.</p>
      <button 
        onClick={handleConnect}
        style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#1976d2',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '1rem',
          cursor: 'pointer'
        }}
      >
        Connect Coinbase
      </button>
    </div>
  );
};

export default ConnectCoinbase;
