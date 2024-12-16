import React, { useState } from "react";
import axios from "axios";

const UploadFile = ({ onResults }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file or folder.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setIsUploading(true);
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      onResults(response.data);
    } catch (error) {
      alert(
        `Error uploading file: ${
          error.response?.data?.error || "Unknown error"
        }`
      );
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <h3>Upload a Zip File for Analysis</h3>
      <div style={{ display: "inline" }}>
        <label
          htmlFor="file-upload"
          style={{
            fontSize: "18px",
            display: "inline-block",
            borderRadius: "100px",
            padding: "8px 16px",
            backgroundColor: "#007bff",
            fontWeight: "bold",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Choose File
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".zip"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <span style={{ marginLeft: "10px", fontSize: "18px" }}>
          {selectedFile ? selectedFile.name : "No file chosen"}
        </span>
      </div>
      <button
        onClick={handleUpload}
        disabled={isUploading}
        style={{
          fontSize: "18px",
          fontWeight: "bold",
          marginLeft: "50px",
          padding: "8px 16px",
          border: "none",
          backgroundColor: "#007bff",
          borderRadius: "100px",
          color: "#fff",
          cursor: "pointer",
        }}
      >
        {isUploading ? "Uploading..." : "Upload and Analyze"}
      </button>
    </div>
  );
};

export default UploadFile;
