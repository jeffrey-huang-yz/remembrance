import React, { useEffect } from 'react';
import './LoginPage.scss';

const SplitText = ({ target }) => {
  useEffect(() => {
    function splitTextIntoSpans(target) {
      let elements = document.querySelectorAll(target);
      elements.forEach((element) => {
        element.classList.add('split-text');
        let text = element.innerText;
        let splitText = text
          .split(" ")
          .map(function (word) {
            let char = word.split('').map(char => {
              return `<span class="split-char">${char}</span>`;
            }).join('');
            return `<div class="split-word">${char}&nbsp;</div>`;
          }).join('');

        element.innerHTML = splitText;
      });
    }

    splitTextIntoSpans(target);
  }, [target]);

  return null; // This component doesn't render anything visible
};

const LoginPage = () => {
  const handleLogin = (event) => {
    console.log('clicked login')
    event.preventDefault(); 
  };

  return (
    <div className='background'>
      <div className="bubble-text title-text">Remembrance</div>
      <SplitText target=".bubble-text" /> {/* Include the SplitText component */}
      <div className="login-container">
        <h2>remembrance.</h2>
        <p><b>remembrance</b> is a tool designed to help you correlate an uploaded photo with photos you have previously uploaded onto Google photos. 
        This website aims to create nostalgia and let you appreciate the past. 
        </p>
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
