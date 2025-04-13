import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, List, ListItem, ListItemText, Paper } from '@mui/material';

function Bots() {
  const [bots, setBots] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/bots')
      .then(response => {
        setBots(response.data);
      })
      .catch(error => {
        console.error("Error fetching bots:", error);
      });
  }, []);

  return (
    <Paper sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Existing Bots
      </Typography>
      <List>
        {bots.map(bot => (
          <ListItem key={bot.id} divider>
            <ListItemText
              primary={bot.bot_name}
              secondary={`Trade Type: ${bot.trade_type} | Created: ${new Date(bot.created_at).toLocaleString()}`}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}

export default Bots;
