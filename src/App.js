import React, { useState } from "react";
import axios from "axios";
import UploadForm from "./components/UploadForm";
import MatchResult from "./components/MatchResult";
import SimilarGrid from "./components/SimilarGrid";

export default function App() {
  const [result, setResult] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/v1/match_item",   // ✅ Direct backend URL
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
      setPreview(URL.createObjectURL(file));
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Error uploading file. Check backend is running on port 8000.");
    }
  };

  return (
    <div className="container">
      <h2>Visual Search Assistant</h2>
      <UploadForm onUpload={handleUpload} />
      <MatchResult result={result} uploadedPreview={preview} />
      <SimilarGrid items={result?.similar_images || []} />
    </div>
  );
}
