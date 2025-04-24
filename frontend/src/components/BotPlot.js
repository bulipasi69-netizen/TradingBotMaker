import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

export default function BotPlot({ botId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`/api/bots/${botId}/plot-data/`)
      .then(res => setData(res.data))
      .catch(console.error);
  }, [botId]);

  if (!data) return <div>Loading chart…</div>;

  return (
    <Plot
      data={[
        {
          x: data.times,
          y: data.prices,
          type: 'scatter',
          mode: 'lines',
          name: 'Price'
        },
        {
          x: data.buys.map(p => p.time),
          y: data.buys.map(p => p.price),
          type: 'scatter',
          mode: 'markers',
          marker: { color: 'green', size: 8 },
          name: 'Buys'
        },
        {
          x: data.sells.map(p => p.time),
          y: data.sells.map(p => p.price),
          type: 'scatter',
          mode: 'markers',
          marker: { color: 'red', size: 8 },
          name: 'Sells'
        }
      ]}
      layout={{
        title: 'Bot Performance (past 24h)',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Price (USDT)' },
        margin: { t: 40, r: 20, b: 40, l: 50 }
      }}
      style={{ width: '100%', height: '400px' }}
    />
  );
}
