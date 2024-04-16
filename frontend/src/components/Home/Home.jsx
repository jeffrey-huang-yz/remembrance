import React, { useState } from 'react'
import './Home.scss'
import { useEffect } from 'react'

const Home = () => {
    const [update, setUpdate] = useState(false)
    useEffect(() => {
        axios.put('/update-photos')
            .then(response => {
                console.log('Data received:', response.data);   
                //Set update status to true to remove blur effect and loading text
                setUpdate(true)
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []); 



  return (
    <div className={`home ${update ? 'update-complete' : 'update-incomplete'}`}>
            {update ? (
                <div className="content">
                    {/* Text to display when update is complete */}
                    <h1>Update Complete!</h1>
                    <p>Your photos have been updated.</p>
                    
                </div>
            ) : (
                <div className="blur-background">
                    
                </div>
            )}
            <div className='ocean'>
                <div className='wave'></div>
                <div className='wave'></div>
            </div>
        </div>
    );
}

export default Home