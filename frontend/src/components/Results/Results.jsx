import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const Results = () => {
  const location = useLocation();
  const [previewImage, setPreviewImage] = useState(null);
  const file = location.state.photo;

  const getBase64Representation = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);

      if (file instanceof Blob) {
        reader.readAsDataURL(file);
      } else {
        reject(new Error('File must be a Blob or File object'));
      }
    });

  const handlePreview = async (file) => {
    try {
      if (!file.url && !file.preview) {
        const base64Data = await getBase64Representation(file);
        setPreviewImage(base64Data);
      }
    } catch (error) {
      console.error('Error reading file:', error.message);
    }
  };

  useEffect(() => {
    handlePreview(file);
  }, [file]);

  return (
    <div>
      <h2>Selected Files</h2>
      <img style={{ width: '100%' }} src={previewImage} alt="Preview" />
    </div>
  );
};

export default Results;
