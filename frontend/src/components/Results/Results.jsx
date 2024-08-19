import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import PhotoCard from '../PhotoCard/PhotoCard';

const Results = () => {
  const location = useLocation();
  const file = location.state.photo;
  const [similarImages, setSimilarImages] = useState([]);

  useEffect(() => {
    const formData = new FormData();
    formData.append('file', file);

    axios.get('http://localhost:5000/find-similar-images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: true,
    })
    .then(response => {
      console.log('Data received:', response.data);
      setSimilarImages(response.data.similar_images);
    })
    .catch(error => {
      console.log('Error:', error.response);
    });
  }, [file]);

  return (
    <div>
      <h2>Selected Files</h2>
      <PhotoCard file={file} />
      <h2>Similar Images</h2>
      {similarImages.map((image, index) => (
        <img key={index} src={image} alt={`Similar Image ${index}`} />
      ))}
    </div>
  );
};

export default Results;
