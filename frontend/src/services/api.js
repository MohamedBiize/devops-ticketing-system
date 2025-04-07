// frontend/src/services/api.js

const API_URL = 'http://localhost:8000';

// Helper function to get auth headers (existing)
const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Login function (existing)
export async function loginUser(email, password) {
  // ... (keep existing loginUser code) ...
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const response = await fetch(`${API_URL}/token`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: formData });
  const data = await response.json();
  if (!response.ok) { throw new Error(data.detail || `HTTP error! status: ${response.status}`); }
  return data;
}

// Get Tickets function (existing)
export async function getTickets() {
  // ... (keep existing getTickets code) ...
  const response = await fetch(`${API_URL}/tickets`, { method: 'GET', headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' } });
  const data = await response.json();
  if (!response.ok) { throw new Error(data.detail || `HTTP error! status: ${response.status}`); }
  return data;
}

// --- <<< ADD CREATE TICKET FUNCTION BELOW >>> ---

export async function createTicket(ticketData) {
  // ticketData should be an object like { title, description, priority }
  const response = await fetch(`${API_URL}/tickets`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(), // Include authentication token
      'Content-Type': 'application/json', // Sending JSON data
    },
    body: JSON.stringify(ticketData), // Convert ticket data object to JSON string
  });

  const data = await response.json();

  if (!response.ok) {
    // Handle errors, including potential validation errors (422) or auth errors (401/403)
    throw new Error(data.detail || `HTTP error! status: ${response.status}`);
  }
  // Returns the newly created ticket data (including id, status, etc.)
  return data;
}

// --- <<< END OF ADDED FUNCTION >>> ---
export async function getTicketById(ticketId) {
    const response = await fetch(`${API_URL}/tickets/${ticketId}`, {
      method: 'GET',
      headers: {
        ...getAuthHeaders(), // Include authentication token
        'Content-Type': 'application/json',
      },
    });
  
    const data = await response.json();
  
    if (!response.ok) {
      // Handle errors like 404 Not Found or 403 Forbidden
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }
    // Returns the specific ticket data
    return data;
  }
  export async function getCommentsForTicket(ticketId) {
    const response = await fetch(`${API_URL}/tickets/${ticketId}/comments`, {
      method: 'GET',
      headers: {
        ...getAuthHeaders(), // Include authentication token
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    if (!response.ok) {
      // Handle errors like 404 Not Found or 403 Forbidden
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }
    // Returns the list of comments for the ticket
    return data;
  }
  
  export async function addCommentForTicket(ticketId, commentData) {
    // commentData should be an object like { content: string }
    const response = await fetch(`${API_URL}/tickets/${ticketId}/comments`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(), // Include authentication token
        'Content-Type': 'application/json', // Sending JSON data
      },
      body: JSON.stringify(commentData), // Convert comment data object to JSON string
    });
  
    const data = await response.json();
  
    if (!response.ok) {
      // Handle errors, including potential validation errors (422) or auth errors (401/403)
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }
    // Returns the newly created comment data
    return data;
  }

  export async function deleteTicketById(ticketId) {
    const response = await fetch(`${API_URL}/tickets/${ticketId}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(), // Include authentication token
      },
    });
  
    // DELETE requests often return 204 No Content on success, which has no body
    // We check if the status code indicates success (200-299)
    if (!response.ok) {
      // Try to parse error detail if available (like for 403/404)
      let errorDetail = `HTTP error! status: ${response.status}`;
      try {
        const data = await response.json();
        errorDetail = data.detail || errorDetail;
      } catch (e) {
        // Ignore if response has no body or isn't JSON
      }
      throw new Error(errorDetail);
    }
    // No data to return on successful delete
    return true;
  }