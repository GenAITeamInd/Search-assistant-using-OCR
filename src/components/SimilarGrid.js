import React from "react";

export default function SimilarGrid({ items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="card">
      <h3>Similar Images</h3>
      <div className="grid">
        {items.map((m, idx) => (
          <div key={idx}>
            <img src={m.image_url} alt={m.item_number || "similar"} className="small" />
            <div style={{ fontSize: 12, marginTop: 4 }}>
              <b>{m.item_number || "N/A"}</b><br/>
              {(m.similarity*100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
