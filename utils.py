import os, re, numpy as np
from PIL import Image
# Optional OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False

def save_upload(upload_file, dest_dir="uploads"):
    os.makedirs(dest_dir, exist_ok=True)
    name = upload_file.filename or "upload.png"
    base, ext = os.path.splitext(name)
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', base) + ext
    final = os.path.join(dest_dir, safe)
    with open(final, "wb") as f:
        f.write(upload_file.file.read())
    return final, os.path.basename(final)

def run_ocr_optional(image_path):
    if not TESSERACT_AVAILABLE:
        return []
    try:
        img = Image.open(image_path).convert("RGB")
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        out = []
        for i, txt in enumerate(data.get("text", [])):
            txt = (txt or "").strip()
            if not txt:
                continue
            try:
                conf = float(data.get("conf", [])[i])
                conf = max(0.0, min(conf, 100.0)) / 100.0
            except:
                conf = 0.0
            out.append({"text": txt, "confidence": conf})
        return out
    except Exception:
        return []

ITEM_PATTERNS = [
  r'\\bFG[-\\s_]?\\d{4,12}\\b',
  r'\\bF[Gg]\\s?\\d{4,12}\\b',
]

def extract_item_numbers_from_ocr(ocr_results):
    cands = []
    for r in ocr_results:
        t = r["text"]
        for pat in ITEM_PATTERNS:
            m = re.search(pat, t, flags=re.I)
            if m:
                cand = m.group(0).upper().replace(" ", "").replace("_", "").replace("-", "")
                cand = re.sub(r'[^A-Z0-9]', '', cand)
                if not cand.startswith("FG"):
                    continue
                cands.append({"text": cand, "confidence": r["confidence"]})
    best = {}
    for c in cands:
        key = c["text"]
        best[key] = max(best.get(key, 0), c["confidence"])
    return [{"text": k, "confidence": v} for k, v in best.items()]

def compute_embedding(image_path, bins=(8,8,8)):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    hist, _ = np.histogramdd(arr.reshape(-1,3), bins=bins, range=[(0,256),(0,256),(0,256)])
    vec = hist.flatten().astype('float32')
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def cosine_sim(a, b):
    a = np.array(a); b = np.array(b)
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na==0 or nb==0: return 0.0
    return float(np.dot(a,b) / (na*nb))

def brute_force_search(query_emb, index_path="index.npz", top_k=9):
    data = load_index(index_path)
    if data is None: return []
    embs = data["embs"]; metas = data["metas"]
    scores = []
    for meta, emb in zip(metas, embs):
        s = cosine_sim(query_emb, emb)
        scores.append((s, meta))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]

def load_index(index_path="index.npz"):
    if not os.path.exists(index_path): return None
    npz = np.load(index_path, allow_pickle=True)
    embs = npz["embs"]
    metas = list(npz["metas"].tolist())
    return {"embs": embs, "metas": metas}

def load_repo_metadata(repository_json):
    import json
    if not os.path.exists(repository_json):
        return {}
    with open(repository_json, "r") as f:
        return json.load(f)

def ensure_index(repo_dir="repo_images", index_path="index.npz", repository_json="repository.json"):
    if os.path.exists(index_path):
        return
    from pathlib import Path
    files = list(Path(repo_dir).glob("*.*"))
    embs, metas = [], []
    meta_map = {}
    if os.path.exists(repository_json):
        import json
        with open(repository_json, "r") as f:
            meta_map = json.load(f)
    for p in files:
        try:
            emb = compute_embedding(str(p))
            item_number = None
            image_name = p.name
            for k, v in meta_map.items():
                if v.get("image_name") == image_name:
                    item_number = k
                    break
            metas.append({"image_name": image_name, "item_number": item_number})
            embs.append(emb)
        except Exception:
            continue
    if len(embs)==0:
        np.savez_compressed(index_path, embs=np.zeros((0,1), dtype='float32'), metas=np.array([]))
    else:
        np.savez_compressed(index_path, embs=np.stack(embs), metas=np.array(metas, dtype=object))
