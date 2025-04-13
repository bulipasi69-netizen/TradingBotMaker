import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Card, CardContent, Grid } from '@mui/material';

function Dashboard() {
  const [bots, setBots] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/bots')
      .then(response => {
        setBots(response.data);
      })
      .catch(error => {
        console.error("Error fetching bots:", error);
      });
  }, []);

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" gutterBottom>
        Bot performance metrics (dummy data for now)
      </Typography>
      <Grid container spacing={2}>
        {bots.map(bot => (
          <Grid item xs={12} sm={6} md={4} key={bot.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{bot.bot_name}</Typography>
                <Typography variant="subtitle1">
                  Trade type: {bot.trade_type}
                </Typography>
                <Typography variant="body2">
                  Created at: {new Date(bot.created_at).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default Dashboard;
