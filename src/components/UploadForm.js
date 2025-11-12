import React, { useState } from "react";

export default function UploadForm({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!file) return alert("Choose a file");
    setLoading(true);
    try {
      await onUpload(file);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <input type="file" accept="image/*,.pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={submit} style={{ marginLeft: 8 }} disabled={loading}>
        {loading ? "Processing..." : "Upload"}
      </button>
    </div>
  );
}
