// src/components/Dashboard.jsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, Grid } from '@mui/material';

export default function Dashboard() {
  const [bots, setBots] = useState([]);

  // Fetch bots on mount
  useEffect(() => {
    axios.get('http://localhost:8000/api/bots/')
      .then(response => {
        setBots(response.data);
      })
      .catch(error => {
        console.error('Error fetching bots:', error);
      });
  }, []);

  // Load TradingView script & instantiate widget
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      new window.TradingView.widget({
        width: '100%',
        height: 400,
        symbol: 'BINANCE:BTCUSDT',
        interval: 'D',
        timezone: 'Etc/UTC',
        theme: 'light',
        style: '1',
        locale: 'en',
        toolbar_bg: '#f1f3f6',
        enable_publishing: false,
        hide_side_toolbar: false,
        allow_symbol_change: true,
        container_id: 'tradingview_btcusdt'
      });
    };
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" gutterBottom>
      </Typography>

      {/* TradingView widget at the top */}
      <div id="tradingview_btcusdt" style={{ width: '100%', height: 400, marginBottom: 24 }} />

      <Grid container spacing={2}>
        {bots.map(bot => (
          <Grid item xs={12} sm={6} md={4} key={bot.id}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6">{bot.bot_name}</Typography>
                <Typography variant="subtitle2" color="text.secondary">
                  Type: {bot.trade_type}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Created: {new Date(bot.created_at).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}
