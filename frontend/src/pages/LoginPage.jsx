// frontend/src/pages/LoginPage.jsx

import React, { useState } from 'react';
import { loginUser } from '../services/api';
import { useNavigate } from 'react-router-dom'; // <-- Import useNavigate hook

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // <-- Get the navigate function

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    // console.log('Attempting login with:', { email, password }); // Optional log

    try {
      const tokenData = await loginUser(email, password);
      console.log('Login successful! Token Data:', tokenData);

      if (tokenData.access_token) {
        localStorage.setItem('accessToken', tokenData.access_token);
        // --- Use navigate to redirect ---
        navigate('/'); // <-- Redirect to the main page route ("/")
      } else {
        setError('Login successful, but no token received.');
      }

    } catch (err) {
      console.error('Login failed:', err);
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  // --- JSX for the form remains the same ---
  return (
    // ... (keep existing JSX) ...
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
         {/* ... email input ... */}
         {/* ... password input ... */}
         {/* ... error paragraph ... */}
         {/* ... button ... */}
         <div> <label htmlFor="email">Email:</label> <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading} /> </div> <div> <label htmlFor="password">Password:</label> <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading} /> </div> {error && <p style={{ color: 'red' }}>{error}</p>} <button type="submit" disabled={loading}> {loading ? 'Logging in...' : 'Login'} </button>
      </form>
    </div>
  );
}

export default LoginPage;