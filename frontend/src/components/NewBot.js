import React, { useState } from 'react';
import axios from 'axios';
import { Typography, TextField, Button, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, FormGroup, Card, CardContent, Box } from '@mui/material';

function NewBot() {
  const [botName, setBotName] = useState('');
  const [description, setDescription] = useState('');
  const [tradeType, setTradeType] = useState('live');
  const [customizations, setCustomizations] = useState({
    x_api: { crypto: false, general: false, sentiment: false },
    ask_news: false
  });

  const toggleXAPIOption = (option) => {
    setCustomizations(prevState => ({
      ...prevState,
      x_api: {
        ...prevState.x_api,
        [option]: !prevState.x_api[option]
      }
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      bot_name: botName,
      description,
      trade_type: tradeType,
      customizations: customizations
    };
    axios.post('http://localhost:5000/api/bots', payload, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'your_api_key_here'
      }
    })
    .then(response => console.log(response.data))
    .catch(error => console.error("Error creating bot:", error));    
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          Create New Bot
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField 
            label="Bot Name" 
            variant="outlined" 
            value={botName} 
            onChange={(e) => setBotName(e.target.value)}
            required 
          />
          <TextField 
            label="Description" 
            variant="outlined" 
            multiline 
            rows={3} 
            value={description} 
            onChange={(e) => setDescription(e.target.value)}
          />
          <FormControl fullWidth>
            <InputLabel id="trade-type-label">Trade Type</InputLabel>
            <Select
              labelId="trade-type-label"
              value={tradeType}
              label="Trade Type"
              onChange={(e) => setTradeType(e.target.value)}
            >
              <MenuItem value="live">Live Trading</MenuItem>
              <MenuItem value="backtesting">Backtesting</MenuItem>
            </Select>
          </FormControl>
          <Typography variant="h6">Integrate X API</Typography>
          <FormGroup row>
            <FormControlLabel
              control={
                <Checkbox 
                  checked={customizations.x_api.crypto} 
                  onChange={() => toggleXAPIOption('crypto')} 
                />
              }
              label="Crypto News"
            />
            <FormControlLabel
              control={
                <Checkbox 
                  checked={customizations.x_api.general} 
                  onChange={() => toggleXAPIOption('general')} 
                />
              }
              label="General News"
            />
            <FormControlLabel
              control={
                <Checkbox 
                  checked={customizations.x_api.sentiment} 
                  onChange={() => toggleXAPIOption('sentiment')} 
                />
              }
              label="Sentiment Analysis"
            />
          </FormGroup>
          <Button variant="contained" color="primary" type="submit">
            Create Bot
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}

export default NewBot;
