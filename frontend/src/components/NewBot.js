// src/components/NewBot.jsx

import React, { useState } from 'react';
import axios from 'axios';
import {
  Typography,
  Button,
  Card,
  CardContent,
  Box,
  CircularProgress,
  Link,
  TextField,
  Grid
} from '@mui/material';

export default function NewBot() {
  const [isDeploying, setIsDeploying] = useState(false);
  const [isDeployed, setIsDeployed] = useState(false);
  const [dashUrl, setDashUrl] = useState('');

  // Dummy option states
  const [buyThreshold, setBuyThreshold] = useState(80);
  const [sellThreshold, setSellThreshold] = useState(50);
  const [initialBudget, setInitialBudget] = useState(1000);
  const [orderValue, setOrderValue] = useState(100);
  const [tradeInterval, setTradeInterval] = useState(30);

  const deployBot = () => {
    setIsDeploying(true);
    setIsDeployed(false);

    axios.post('http://localhost:8000/api/run-trading-bot/', {}, {
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
      const url = response.data.dash_url || 'http://localhost:8050';
      setDashUrl(url);
      setIsDeploying(false);
      setIsDeployed(true);
    })
    .catch(error => {
      console.error("Error deploying trading bot:", error);
      alert("Error deploying trading bot. Check the console for details.");
      setIsDeploying(false);
    });
  };

  const openDashApp = () => {
    window.open(dashUrl, '_blank');
  };

  return (
    <Card>
      <CardContent sx={{ maxWidth: 600, margin: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          Trading Bot Deployment
        </Typography>

        {/* Option fields (dummy) */}
        <Box component="form" noValidate sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Buy Threshold"
                type="number"
                value={buyThreshold}
                onChange={e => setBuyThreshold(Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Sell Threshold"
                type="number"
                value={sellThreshold}
                onChange={e => setSellThreshold(Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Initial Budget (USDT)"
                type="number"
                value={initialBudget}
                onChange={e => setInitialBudget(Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Order Value (USDT)"
                type="number"
                value={orderValue}
                onChange={e => setOrderValue(Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Trade Interval (s)"
                type="number"
                value={tradeInterval}
                onChange={e => setTradeInterval(Number(e.target.value))}
              />
            </Grid>
          </Grid>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {!isDeployed ? (
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={deployBot}
              disabled={isDeploying}
              sx={{ mb: 2 }}
            >
              {isDeploying ? 'Deploying...' : 'Deploy Trading Bot'}
            </Button>
          ) : (
            <Button
              variant="contained"
              color="success"
              size="large"
              onClick={openDashApp}
              sx={{ mb: 2 }}
            >
              View Trading Bot Dashboard
            </Button>
          )}

          {isDeploying && (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <CircularProgress size={24} sx={{ mb: 1 }} />
              <Typography variant="body2" color="textSecondary">
                Starting trading bot and preparing visualization...
              </Typography>
            </Box>
          )}

          {isDeployed && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body1" color="success.main" sx={{ mb: 1 }}>
                Trading bot successfully deployed!
              </Typography>
              <Typography variant="body2">
                It may take a few moments for the dashboard to be ready.
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                If the dashboard doesn't open, please try again in a few seconds or visit:
              </Typography>
              <Link href={dashUrl} target="_blank" rel="noopener">
                {dashUrl}
              </Link>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
