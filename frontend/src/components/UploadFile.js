import React, { useState } from "react";
import axios from "axios";

const UploadFile = ({ onResults }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false); // State for showing upload progress

  // Handle file selection
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file.");
      return;
    }

    // Validate file extension
    if (!selectedFile.name.endsWith(".zip")) {
      alert("Please upload a .zip file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setIsUploading(true);
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Pass results to the parent component
      onResults(response.data);
    //   alert("File uploaded and analyzed successfully!");
    } catch (error) {
      alert(
        `Error uploading file: ${error.response?.data?.error || "Unknown error"}`
      );
      console.error("Upload Error:", error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <h3>Upload a Zip File for Analysis</h3>
      <input type="file" accept=".zip" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={isUploading}>
        {isUploading ? "Uploading..." : "Upload and Analyze"}
      </button>
    </div>
  );
};

export default UploadFile;
