import React from 'react';
import { Box, Typography, List, ListItem, ListItemText } from '@mui/material';

const HistoryPanel = () => {
  return (
    <Box p={2}>
      <Typography variant="h6" gutterBottom>
        Verification History
      </Typography>
      <List>
        <ListItem>
          <ListItemText 
            primary="Sample verification"
            secondary="Verified as accurate"
          />
        </ListItem>
      </List>
    </Box>
  );
};

export default HistoryPanel;
