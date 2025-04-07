// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import TicketsPage from './pages/TicketsPage';
import CreateTicketPage from './pages/CreateTicketPage'; // <-- Import CreateTicketPage
import TicketDetailPage from './pages/TicketDetailPage';
import './App.css';

// ... (keep isAuthenticated and ProtectedRoute functions as before) ...
const isAuthenticated = () => { return localStorage.getItem('accessToken') !== null; };
const ProtectedRoute = ({ children }) => { if (!isAuthenticated()) { return <Navigate to="/login" replace />; } return children; };


function App() {
  return (
    <Router>
      <div className="App">
        <h1>Ticketing System</h1>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={ <ProtectedRoute> <TicketsPage /> </ProtectedRoute> }
          />
          <Route
            path="/create-ticket"
            element={ <ProtectedRoute> <CreateTicketPage /> </ProtectedRoute> }
          />
          {/* --- <<< ADD ROUTE FOR TICKET DETAIL BELOW >>> --- */}
          <Route
            path="/tickets/:ticketId" // Use :ticketId as a URL parameter
            element={
              <ProtectedRoute> {/* Protect this route */}
                <TicketDetailPage />
              </ProtectedRoute>
            }
          />
          {/* --- <<< END OF ADDED ROUTE >>> --- */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;