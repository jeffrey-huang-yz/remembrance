import React from 'react';
import { Card } from 'antd';
import { useState, useEffect } from 'react';

const PhotoCard = ({ file }) => {
    const [previewImage, setPreviewImage] = useState(null);

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
        <Card
            hoverable
            style={{ width: 240 }}
            cover={<img alt="Preview" src={file.preview || file.url} />}
        >
            <Card.Meta title={file.name || 'Untitled'} />
        </Card>
    );
};

export default PhotoCard;
