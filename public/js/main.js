/**
 * Marduk Cognitive Tokamak - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('Marduk Cognitive Tokamak interface initialized');
  
  // Smooth scrolling for navigation links
  const navLinks = document.querySelectorAll('nav a');
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Hero button action
  const startBtn = document.getElementById('start-btn');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      document.querySelector('#memory').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    });
  }
  
  // Secondary buttons - placeholder functionality
  const secondaryBtns = document.querySelectorAll('.secondary-btn');
  secondaryBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const action = this.textContent.trim();
      
      // Show a notification that these features are coming soon
      showNotification(`${action} feature coming soon!`);
    });
  });
  
  // Check API health
  checkApiHealth();
  
  // Initialize animation observers
  initAnimationObservers();
});

/**
 * Check the health of the API
 */
async function checkApiHealth() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    
    if (data.status === 'healthy') {
      console.log('API is healthy:', data);
    } else {
      console.warn('API health check returned non-healthy status:', data);
    }
  } catch (error) {
    console.error('API health check failed:', error);
  }
}

/**
 * Show a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (info, success, error)
 */
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  
  // Add to the DOM
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Remove after delay
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

/**
 * Initialize intersection observers for animations
 */
function initAnimationObservers() {
  const sections = document.querySelectorAll('.component-section');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1
  });
  
  sections.forEach(section => {
    observer.observe(section);
  });
}

/**
 * Simulate a chat with the Marduk LLM
 * @param {string} message - The user's message
 * @returns {Promise<string>} - The LLM's response
 */
async function chatWithMarduk(message) {
  try {
    const response = await fetch('/api/llm/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: message })
    });
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error chatting with Marduk LLM:', error);
    return 'I apologize, but I am currently unable to process your request.';
  }
}