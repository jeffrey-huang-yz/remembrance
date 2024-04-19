import { Upload } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import useFilePreview from '../../hooks/useFilePreview';

const { Dragger } = Upload;

const DragAndDrop = ({ addFile, removeFile }) => {
  const [handlePreview, previewContent] = useFilePreview();

  const beforeUploadHandler = (file) => {
    addFile(file);
    return false;
  };

  return (
    <>
      <Dragger
        multiple={true}
        onRemove={removeFile}
        showUploadList={true}
        listType="picture-card"
        beforeUpload={beforeUploadHandler}
        onPreview={handlePreview}
        accept="image/*"
        style={{color: "black", borderColor: "black"}}
      >
        <p className="ant-upload-drag-icon">
          <PlusOutlined style={{color: "black"}}/>
        </p>
        <p className="ant-upload-text">
          Click this area or drag files to upload <b>one</b> photo
        </p>
      </Dragger>
      {previewContent}
    </>
  );
};

export default DragAndDrop;
