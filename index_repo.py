from utils import ensure_index
if __name__ == "__main__":
    ensure_index(repo_dir="repo_images", index_path="index.npz", repository_json="repository.json")
    print("Index built/refreshed.")