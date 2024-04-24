import React from 'react';

const Results = ({ location }) => {
  const { selectedFiles } = location.state;

  return (
    <div>
      <h2>Selected Files</h2>
      {selectedFiles.map((file, index) => (
        <img key={index} src={file.preview} alt={`Image ${index}`} />
      ))}
    </div>
  );
};

export default Results;
