import React, { useEffect, useState } from 'react';
import { Router, Route, redirect } from 'react-router-dom';
import { lazy } from 'react';
import LoginPage from './components/LoginPage/LoginPage';
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
    //useEffect(() => {
    //  // Check if user is logged in by making an API request to the backend
    //  fetch('/check_login')
    //    .then(response => {
    //      if (response.ok) {
    //        setIsLoggedIn(true);
    //      }
    //    });
    //}, []);

  //const handleLogin = () => {
  //  // Redirect user to backend for Google OAuth login
  //  window.location.href = '/login';
  //};

  return ( 
    /*<Router>
      <div>
        <Route exact path="/">
  
          {isLoggedIn ? redirect("/home") : <LoginPage />} 
        </Route>
        <Route path="/home">
         
        </Route>
      </div>
    </Router> */
    <div>
      <LoginPage />
    </div>
  );
};

export default App;
