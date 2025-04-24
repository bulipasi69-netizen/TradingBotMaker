// src/components/BotDetail.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import Plot from 'react-plotly.js';

export default function BotDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`/api/bots/${id}/plot-data/`)
      .then(res => setData(res.data))
      .catch(console.error);
  }, [id]);

  if (!data) return <p>Loading chart…</p>;

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-4">Bot #{id} Performance</h1>
      <Plot
        data={[
          { x: data.timestamps, y: data.prices, type: 'scatter', mode: 'lines', name: 'Price' },
          { x: data.buy_times, y: data.buy_prices, type: 'scatter', mode: 'markers', name: 'Buys', marker: { color: 'green' } },
          { x: data.sell_times, y: data.sell_prices, type: 'scatter', mode: 'markers', name: 'Sells', marker: { color: 'red' } },
        ]}
        layout={{ width: 800, height: 400, title: 'Live BTC Price & Trades' }}
      />
    </div>
  );
}
