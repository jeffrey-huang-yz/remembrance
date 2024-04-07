import React from 'react';
import './LoginPage.scss';

const LoginPage = () => {
  const handleLogin = (event) => {
    console.log('clicked login')
    event.preventDefault(); 
    

  };

  return (
    <div className='background'>
      <h1 className="title-text">Remembrance</h1>
      <div className="login-container">
        <h2>Please Sign In</h2>
        <div className="google-sign-in-button" onClick={handleLogin}>
        <img
          src="https://developers.google.com/static/identity/images/branding_guideline_sample_dk_rd_lg.svg"
          alt="Sign in with Google"
        />
      </div>
      </div>
    </div>
  );
};

export default LoginPage;