// frontend/src/pages/TicketsPage.jsx
import React, { useState, useEffect } from 'react'; // <-- Import useState and useEffect
import { getTickets } from '../services/api'; // <-- Import the getTickets function
import { useNavigate, Link } from 'react-router-dom';// <-- Import useNavigate

function TicketsPage() {
  const [tickets, setTickets] = useState([]); // State to hold the list of tickets
  const [loading, setLoading] = useState(true); // State for loading indicator
  const [error, setError] = useState(null); // State for errors
  const navigate = useNavigate(); // Hook for navigation

  // Use useEffect to fetch tickets when the component mounts
  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedTickets = await getTickets();
        setTickets(fetchedTickets);
      } catch (err) {
        console.error("Failed to fetch tickets:", err);
        setError(err.message || "Failed to load tickets.");
        // If unauthorized (e.g., bad token), redirect to login
        if (err.message.includes('401') || err.message.includes('Not authenticated')) {
           // A more robust check might involve specific error codes/types
           handleLogout(); // Use logout to clear token and redirect
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []); // Empty dependency array means this runs once on mount

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    console.log('Logged out!'); // Changed alert to console.log
    navigate('/login'); // Use navigate for cleaner redirect
  };

  // --- Render Logic ---
  let content;
  if (loading) {
    content = <p>Loading tickets...</p>;
  } else if (error) {
    content = <p style={{ color: 'red' }}>Error: {error}</p>;
  } else if (tickets.length === 0) {
    content = <p>No tickets found.</p>;
  } else {
    content = (
      <ul>
        {tickets.map((ticket) => (
          // Make the list item link to the detail page
          <li key={ticket.id}>
            <Link to={`/tickets/${ticket.id}`}> {/* Link using ticket ID */}
              <strong>ID: {ticket.id} - {ticket.title}</strong>
            </Link>
            <div> {/* Keep other details */}
              Status: {ticket.status} | Priority: {ticket.priority} |
              Created: {new Date(ticket.date_creation).toLocaleString()} |
              Creator ID: {ticket.creator_id} |
              Tech ID: {ticket.technician_id ?? 'None'}
            </div>
          </li>
        ))}
      </ul>
    );
  }
  return (
    <div>
      <h2>Tickets</h2>
      <button onClick={handleLogout} style={{ marginRight: '10px' }}>Logout</button>
      {/* --- <<< ADD CREATE TICKET LINK/BUTTON BELOW >>> --- */}
      <Link to="/create-ticket">
        <button>Create New Ticket</button>
      </Link>
      {/* --- <<< END OF ADDED LINK/BUTTON >>> --- */}
      <div style={{marginTop: '1em'}}> {/* Add some space */}
         {content}
      </div>
    </div>
  );
}

export default TicketsPage;