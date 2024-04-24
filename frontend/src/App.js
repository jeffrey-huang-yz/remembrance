import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Routes, Route, Switch } from 'react-router-dom';
import { redirect } from 'react-router';
import LoginPage from './components/LoginPage/LoginPage';
import Home from './components/Home/Home';
import Results from './components/Results/Results';
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
    useEffect(() => {
      // Check if user is logged in by making an API request to the backend
      fetch('http://localhost:5000/check-login', {
          credentials: 'include' // Include cookies in the request
      })
      .then(response => {
          if (response.ok) {
              setIsLoggedIn(true);
          }
      });
    }, []);


  const handleLogin = () => {
    // Redirect user to backend for Google OAuth login
    window.location.href = '/login';
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} exact />
        <Route path="/home" element={<Home />} exact/>
        <Route path='results' element={<Results />} exact/>
      </Routes>
    </Router>
  );
};

export default App
