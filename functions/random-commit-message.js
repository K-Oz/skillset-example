const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  try {
    // For local development, we'd use the Go binary
    // In production, we'll need to make an HTTP request to an external API
    const response = await fetch('https://whatthecommit.com/index.txt');
    const data = await response.text();
    
    return {
      statusCode: 200,
      body: data
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch commit message' })
    };
  }
};