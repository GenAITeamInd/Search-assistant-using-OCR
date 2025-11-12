from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os, re

from utils import (
    save_upload,
    run_ocr_optional,
    extract_item_numbers_from_ocr,
    compute_embedding,
    brute_force_search,
    ensure_index,
    load_repo_metadata
)

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR / "repo_images"
UPLOADS_DIR = BASE_DIR / "uploads"
INDEX_PATH = BASE_DIR / "index.npz"
REPOSITORY_JSON = BASE_DIR / "repository.json"

app = FastAPI(title="Visual Search Assistant (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/repo", StaticFiles(directory=str(REPO_DIR)), name="repo")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

ensure_index(repo_dir=str(REPO_DIR), index_path=str(INDEX_PATH), repository_json=str(REPOSITORY_JSON))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/match_item")
async def match_item(file: UploadFile = File(...)):
    saved_path, saved_name = save_upload(file, dest_dir=str(UPLOADS_DIR))
    ocr_results = run_ocr_optional(saved_path)
    candidates = extract_item_numbers_from_ocr(ocr_results)
    emb = compute_embedding(saved_path)
    results = brute_force_search(emb, index_path=str(INDEX_PATH), top_k=9)
    repo_meta = load_repo_metadata(str(REPOSITORY_JSON))
    top = results[0] if results else None
    top_item_number = top[1].get("item_number") if top else None
    matched_details = repo_meta.get(top_item_number, {}) if top_item_number else {}
    response = {
        "uploaded_image_name": saved_name,
        "uploaded_image_url": f"/uploads/{saved_name}",
        "ocr_candidates": candidates,
        "matched_item": {
            "item_number": top_item_number,
            "details": matched_details,
            "similarity": float(top[0]) if top else None,
            "ref_image_url": f"/repo/{top[1].get('image_name')}" if top else None
        },
        "similar_images": [
            {
                "item_number": meta.get("item_number"),
                "image_name": meta.get("image_name"),
                "image_url": f"/repo/{meta.get('image_name')}",
                "similarity": float(score)
            }
            for score, meta in results[1:]
        ]
    }
    return JSONResponse(response)
