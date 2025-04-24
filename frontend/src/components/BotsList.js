// src/components/BotsList.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

export default function BotsList() {
  const [bots, setBots] = useState([]);
  useEffect(() => {
    axios.get('/api/bots/')
      .then(res => setBots(res.data))
      .catch(console.error);
  }, []);
  return (
    <div>
      <h1 className="text-3xl font-semibold mb-4">Your Bots</h1>
      <ul className="space-y-2">
        {bots.map(bot => (
          <li key={bot.id}>
            <Link
              to={`/bots/${bot.id}`}
              className="block p-4 bg-white rounded shadow hover:shadow-lg transition"
            >
              <h2 className="text-xl font-medium">{bot.bot_name}</h2>
              <p className="text-gray-500">{bot.description}</p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
