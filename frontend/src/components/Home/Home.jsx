import React, { useState } from 'react'
import './Home.scss'
import { useEffect } from 'react'
import axios from 'axios'
import { Button, Card } from 'antd';
import DragAndDrop from '../DragAndDrop/DragAndDrop';
import useFileSelection from '../../hooks/useFileSelection';
import Spline from '@splinetool/react-spline';
import { useNavigate } from 'react-router-dom'; 

const Home = () => {
    const [selectedFiles, addFile, removeFile] = useFileSelection();
    const [update, setUpdate] = useState(true);
    const navigate = useNavigate();
    
    useEffect(() => {
        axios.get('http://localhost:5000/update-photos', {
            withCredentials: true  // Set to true to send cookies
        })
        .then(response => {
            console.log('Data received:', response.data);   
            // Set update status to true to remove blur effect and loading text
            setUpdate(true);
        })
        .catch(error => {
            if (error.response) {
                console.error('Server Error:', error.response.data);
                console.error('Status Code:', error.response.status);
            } else if (error.request) {
                console.error('Network Error:', error.request);
            } else {
                console.error('Error:', error.message);
            }
        });
    }, []);

    const handleSubmit = () => {
        console.log('Selected Files:', selectedFiles);
        const file = selectedFiles[0];
        
        navigate('/results', {state: {photo: file} });
    };



    return (
        <div className={`home ${update ? 'update-complete' : 'update-incomplete'}`}>
        {update ? (
            <div className="content">
                <h1 className='title'>Remembrance</h1>
                
                <Card
                    className='submit-card'
                    style={{ margin: 'auto', width: '50%' }}
                    actions={[<Button className='submit' onClick={handleSubmit}>Submit</Button>]}
                >
                    
                    <DragAndDrop addFile={addFile} removeFile={removeFile} />
                </Card>         
                <div>
                        
                <Spline scene="https://prod.spline.design/1HlDZLOg5jr4KS4W/scene.splinecode" />
                

            </div>
            </div>
            
        ) : (
            <div>
                <h1 className='loading animate-flicker'>Processing Your Google Photos</h1>
                <div className="blur-background">
                    <div className='ocean'>
                        <div className='wave'></div>
                        <div className='wave'></div>
                    </div>
                </div>
            </div>
        )}
        </div>
    );                                              
}

export default Home