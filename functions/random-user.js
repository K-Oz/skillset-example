exports.handler = async (event, context) => {
  try {
    const response = await fetch('https://randomuser.me/api');
    const data = await response.text();
    
    return {
      statusCode: 200,
      body: data
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch random user data' })
    };
  }
};