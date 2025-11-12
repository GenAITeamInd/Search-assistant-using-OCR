import React from "react";

export default function MatchResult({ result, uploadedPreview }) {
  if (!result) return null;
  const top = result.matched_item || {};
  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <h3>Match</h3>
      <div className="row">
        <div>
          <h4>Uploaded</h4>
          {uploadedPreview && <img src={uploadedPreview} alt="uploaded" className="thumb" />}
        </div>
        <div>
          <h4>Repository</h4>
          {top.ref_image_url && (
            <img src={top.ref_image_url} alt="repo" className="thumb" />
          )}
          <p><b>Item:</b> {top.item_number || "N/A"}</p>
          <p><b>Similarity:</b> {top.similarity ? (top.similarity*100).toFixed(1) : "N/A"}%</p>
          {top.details && (
            <div style={{ marginTop: 8 }}>
              <div><b>Description:</b> {top.details.description}</div>
              <div><b>Quantity:</b> {top.details.quantity}</div>
              <div><b>Site:</b> {top.details.site}</div>
              <div><b>Batch:</b> {top.details.batch}</div>
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 12 }}>
        <h4>OCR Candidates</h4>
        <ul>
          {(result.ocr_candidates || []).map((c, i) => (
            <li key={i}>{c.text} ({Math.round((c.confidence||0)*100)}%)</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
