const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
require('dotenv').config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Memory API routes
app.get('/api/memory/atoms', (req, res) => {
  // In a real implementation, this would query the memory store
  res.json({ 
    message: 'Memory atom retrieval endpoint',
    status: 'Not yet implemented'
  });
});

// Bolt API routes
app.get('/api/bolt/experiments', (req, res) => {
  // In a real implementation, this would list available experiments
  res.json({ 
    message: 'Bolt experiments endpoint',
    status: 'Not yet implemented'
  });
});

// LLM API routes
app.post('/api/llm/query', (req, res) => {
  const { query } = req.body;
  // In a real implementation, this would call the LLM
  res.json({ 
    message: 'LLM query endpoint',
    query,
    response: 'This is a placeholder response from the Marduk LLM',
    status: 'Not yet implemented'
  });
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Marduk Cognitive Tokamak server running on port ${PORT}`);
  console.log(`Visit http://localhost:${PORT} to access the interface`);
});

module.exports = app; // For testing