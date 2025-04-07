// frontend/src/pages/TicketDetailPage.jsx
import React, { useState, useEffect, useCallback } from 'react'; // <-- Import useCallback
import { useParams, Link, useNavigate } from 'react-router-dom';
// Import all needed API functions
import { getTicketById, getCommentsForTicket, addCommentForTicket, deleteTicketById } from '../services/api';

function TicketDetailPage() {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]); // State for comments
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for the new comment form
  const [newComment, setNewComment] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);
  const [commentError, setCommentError] = useState('');

  // State for delete operation
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  // Use useCallback for the fetch function used in useEffect
  const fetchTicketAndComments = useCallback(async () => {
    // Reset states on new fetch attempt
    setLoading(true);
    setError(null);
    setTicket(null); // Clear previous ticket data
    setComments([]); // Clear previous comments

    try {
      console.log(`Workspaceing ticket and comments for ID: ${ticketId}`);
      // Fetch ticket and comments (could run in parallel with Promise.all if preferred)
      const fetchedTicket = await getTicketById(ticketId);
      setTicket(fetchedTicket);

      const fetchedComments = await getCommentsForTicket(ticketId);
      setComments(fetchedComments);

    } catch (err) {
      console.error(`Failed to fetch data for ticket ${ticketId}:`, err);
      setError(err.message || `Failed to load data for ticket ${ticketId}.`);
      // Optional: Redirect if 404 or 403?
    } finally {
      setLoading(false);
    }
  }, [ticketId]); // Dependency: re-fetch if ticketId changes

  useEffect(() => {
    if (ticketId) {
      fetchTicketAndComments();
    } else {
      setError("No ticket ID provided.");
      setLoading(false);
    }
  }, [ticketId, fetchTicketAndComments]); // Include fetchTicketAndComments in dependency array

  // Handler for submitting a new comment
  const handleCommentSubmit = async (event) => {
    event.preventDefault();
    if (!newComment.trim()) {
      setCommentError('Comment cannot be empty.');
      return;
    }
    setCommentLoading(true);
    setCommentError('');

    try {
      const addedComment = await addCommentForTicket(ticketId, { content: newComment });
      // Add the new comment to the *top* of the list for immediate feedback
      setComments(prevComments => [addedComment, ...prevComments]);
      setNewComment(''); // Clear the input field
      console.log('Comment added:', addedComment);
    } catch (err) {
      console.error('Failed to add comment:', err);
      setCommentError(err.message || 'Failed to submit comment.');
    } finally {
      setCommentLoading(false);
    }
  };

    // --- <<< ADD DELETE HANDLER BELOW >>> ---
    const handleDelete = async () => {
        // Simple confirmation dialog
        if (!window.confirm('Are you sure you want to delete this ticket? This action cannot be undone.')) {
          return; // Abort if user clicks Cancel
        }
    
        setDeleteLoading(true);
        setDeleteError('');
    
        try {
          await deleteTicketById(ticketId);
          console.log(`Ticket ${ticketId} deleted successfully.`);
          alert('Ticket deleted successfully!');
          navigate('/'); // Redirect to ticket list after successful deletion
        } catch (err) {
          console.error('Failed to delete ticket:', err);
          setDeleteError(err.message || 'Failed to delete ticket.');
        } finally {
          setDeleteLoading(false);
        }
      };
      // --- <<< END OF DELETE HANDLER >>> ---

 // Render logic
 if (loading) return <p>Loading ticket details...</p>;
 if (error) return <p style={{ color: 'red' }}>Error loading ticket data: {error}</p>;
 if (!ticket) return <p>Ticket data not available.</p>;

 return (
   <div>
     {/* --- Ticket Details Section (Existing) --- */}
     <h2>Ticket Details (ID: {ticket.id})</h2>
     {/* ... p tags for details ... */}
      <p><strong>Title:</strong> {ticket.title}</p> <p><strong>Description:</strong> {ticket.description}</p> <p><strong>Status:</strong> {ticket.status}</p> <p><strong>Priority:</strong> {ticket.priority}</p> <p><strong>Created By (ID):</strong> {ticket.creator_id}</p> <p><strong>Assigned To (ID):</strong> {ticket.technician_id ?? 'None'}</p> <p><strong>Created At:</strong> {new Date(ticket.date_creation).toLocaleString()}</p> <p><strong>Last Updated:</strong> {new Date(ticket.date_mise_a_jour).toLocaleString()}</p>

     {/* Display Delete Error if any */}
     {deleteError && <p style={{ color: 'red', marginTop:'1em' }}>Delete Error: {deleteError}</p>}

     {/* --- <<< ADD DELETE BUTTON BELOW >>> --- */}
     <button
       onClick={handleDelete}
       disabled={deleteLoading}
       style={{ backgroundColor: 'red', color: 'white', marginLeft: '10px' }}
     >
       {deleteLoading ? 'Deleting...' : 'Delete Ticket'}
     </button>
     {/* --- <<< END OF ADDED BUTTON >>> --- */}

     <hr />
     {/* --- Comments Section (Existing) --- */}
     <h3>Comments</h3>
     {/* Add Comment Form */}
     <form onSubmit={handleCommentSubmit} style={{ marginBottom: '1em' }}>
        {/* ... textarea, error, button ... */}
        <div> <label htmlFor="newComment">Add Comment:</label> <br /> <textarea id="newComment" value={newComment} onChange={(e) => setNewComment(e.target.value)} rows={3} required disabled={commentLoading} style={{ width: '80%', maxWidth: '500px' }} /> </div> {commentError && <p style={{ color: 'red' }}>{commentError}</p>} <button type="submit" disabled={commentLoading}> {commentLoading ? 'Submitting...' : 'Submit Comment'} </button>
     </form>
     {/* Display Existing Comments */}
     {/* ... comment list logic ... */}
      {comments.length > 0 ? ( <ul style={{ listStyle: 'none', padding: 0 }}> {comments.map((comment) => ( <li key={comment.id} style={{ borderBottom: '1px solid #eee', marginBottom: '0.5em', paddingBottom: '0.5em' }}> <p>{comment.content}</p> <small> By User ID: {comment.creator_id} on {new Date(comment.date_creation).toLocaleString()} </small> </li> ))} </ul> ) : ( <p>No comments yet.</p> )}

     <hr />
     {/* Back Link (Existing) */}
     <Link to="/">
        <button>Back to Ticket List</button>
     </Link>
   </div>
 );
}

export default TicketDetailPage;