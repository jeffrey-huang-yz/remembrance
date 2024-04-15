import React from 'react'
import './Home.scss'
import { useEffect } from 'react'

const Home = () => {

    useEffect(() => {
        axios.put('/update-photos')
            .then(response => {
                console.log('Data received:', response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []); 



  return (
    <div className='ocean'>
        <div className='wave'></div>
        <div className='wave'></div>
    </div>
  )
}

export default Home