import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Bots from './components/Bots';
import NewBot from './components/NewBot';
import ConnectCoinbase from './components/ConnectCoinbase';

const App = () => {
  return (
    <Router>
      <div>
        <nav style={{ padding: '1rem', background: '#1976d2', color: 'white' }}>
          <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem', margin: 0, padding: 0 }}>
            <li>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
            </li>
            <li>
              <Link to="/bots" style={{ color: 'white', textDecoration: 'none' }}>Bots</Link>
            </li>
            <li>
              <Link to="/new-bot" style={{ color: 'white', textDecoration: 'none' }}>New Bot</Link>
            </li>
            <li>
              <Link to="/connect-coinbase" style={{ color: 'white', textDecoration: 'none' }}>Connect Coinbase</Link>
            </li>
          </ul>
        </nav>
        <div style={{ padding: '1rem' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bots" element={<Bots />} />
            <Route path="/new-bot" element={<NewBot />} />
            <Route path="/connect-coinbase" element={<ConnectCoinbase />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;