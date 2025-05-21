exports.handler = async (event, context) => {
  try {
    let params = {};
    
    if (event.body) {
      try {
        params = JSON.parse(event.body);
      } catch (e) {
        // If parsing fails, use default params
      }
    }
    
    // Build the URL based on parameters
    let url = 'https://loripsum.net/api';
    
    if (params.number_of_paragraphs) {
      const num = Math.min(Math.max(1, params.number_of_paragraphs), 10);
      url += `/${num}`;
    }
    
    if (params.paragraph_length && ['short', 'medium', 'long', 'verylong'].includes(params.paragraph_length)) {
      url += `/${params.paragraph_length}`;
    }
    
    if (params.decorate) url += '/decorate';
    if (params.link) url += '/link';
    if (params.unordered_lists) url += '/ul';
    if (params.numbered_lists) url += '/ol';
    if (params.description_lists) url += '/dl';
    if (params.blockquotes) url += '/bq';
    if (params.code) url += '/code';
    if (params.headers) url += '/headers';
    if (params.all_caps) url += '/allcaps';
    if (params.prude) url += '/prude';
    
    const response = await fetch(url);
    const data = await response.text();
    
    return {
      statusCode: 200,
      body: data
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch lorem ipsum text' })
    };
  }
};