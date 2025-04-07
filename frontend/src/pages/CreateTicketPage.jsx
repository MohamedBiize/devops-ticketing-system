// frontend/src/pages/CreateTicketPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTicket } from '../services/api';

// Define priority options based on backend Enum keys/values expected by API
// Ensure these values match EXACTLY what the backend Enum expects
const priorityOptions = ['Faible', 'Moyenne', 'Élevée', 'Critique'];
const defaultPriority = 'Moyenne';

function CreateTicketPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(defaultPriority);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    const ticketData = {
      title,
      description,
      priority, // Send the selected priority
    };

    console.log('Submitting ticket:', ticketData);

    try {
      const newTicket = await createTicket(ticketData);
      console.log('Ticket created successfully:', newTicket);
      alert('Ticket created successfully!');
      // Redirect to the main tickets list after successful creation
      navigate('/'); // Navigate back to the root route (TicketsPage)
    } catch (err) {
      console.error('Failed to create ticket:', err);
      setError(err.message || 'Failed to create ticket.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Create New Ticket</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title:</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="description">Description:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            disabled={loading}
            rows={5}
          />
        </div>
        <div>
          <label htmlFor="priority">Priority:</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            disabled={loading}
          >
            {priorityOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Ticket'}
        </button>
         {/* Add a button/link to go back */}
         <button type="button" onClick={() => navigate('/')} disabled={loading} style={{marginLeft: '10px'}}>
            Cancel
         </button>
      </form>
    </div>
  );
}

export default CreateTicketPage;