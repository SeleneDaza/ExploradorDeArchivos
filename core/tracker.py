import os
import hashlib
import time
import pickle
from pathlib import Path
from typing import List, Dict, Optional

# Simple in-memory cache: key -> (timestamp, result)
_cache = {}
CACHE_TTL = 60 * 5  # 5 minutes

# disk cache
CACHE_DIR = Path.home() / ".explorador_cache"
CACHE_FILE = CACHE_DIR / "tracker_cache.pickle"


def _load_cache():
    global _cache
    try:
        if CACHE_FILE.exists():
            with CACHE_FILE.open("rb") as f:
                _cache = pickle.load(f)
    except Exception:
        _cache = {}


def _save_cache():
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("wb") as f:
            pickle.dump(_cache, f)
    except Exception:
        pass


# load persisted cache on import
_load_cache()


def _file_info(path: Path) -> Dict:
    st = path.stat()
    return {
        "path": str(path),
        "size": st.st_size,
        "mtime": st.st_mtime,
    }


def compute_hash(path: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(target_path: str, roots: Optional[List[str]] = None) -> List[Dict]:
    target = Path(target_path)
    if not target.exists() or not target.is_file():
        return []

    key = ("dup", str(target.resolve()))
    now = time.time()
    if key in _cache:
        ts, val = _cache[key]
        if now - ts < CACHE_TTL:
            return val

    target_size = target.stat().st_size
    target_hash = compute_hash(str(target))

    if roots is None:
        # default to user's home folder
        roots = [str(Path.home())]

    results = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                try:
                    fpath = Path(dirpath) / fname
                    # skip the same file
                    if fpath.resolve() == target.resolve():
                        continue
                    if not fpath.is_file():
                        continue
                    if fpath.stat().st_size != target_size:
                        continue
                    # compute hash
                    try:
                        h = compute_hash(str(fpath))
                    except Exception:
                        continue
                    if h == target_hash:
                        results.append(_file_info(fpath))
                except Exception:
                    continue

    # include target as original at top
    final = [
        {
            "path": str(target),
            "size": target_size,
            "mtime": target.stat().st_mtime,
            "is_original": True,
        }
    ]
    for r in results:
        r["is_original"] = False
        final.append(r)

    _cache[key] = (now, final)
    _save_cache()
    return final


def is_text_file(path: str) -> bool:
    # rudimentary check: try opening as text
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1024)
        return True
    except Exception:
        return False


def find_references(target_path: str, roots: Optional[List[str]] = None, max_files: Optional[int] = None) -> List[Dict]:
    target = Path(target_path)
    if not target.exists() or not target.is_file():
        return []

    key = ("ref", str(target.resolve()))
    now = time.time()
    if key in _cache:
        ts, val = _cache[key]
        if now - ts < CACHE_TTL:
            return val

    needle_basename = target.name
    needle_full = str(target.resolve())

    if roots is None:
        roots = [str(Path.home())]

    results = []
    files_scanned = 0
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                fpath = Path(dirpath) / fname
                try:
                    if not fpath.is_file():
                        continue
                    # optional limit
                    files_scanned += 1
                    if max_files and files_scanned > max_files:
                        break
                    if not is_text_file(str(fpath)):
                        continue
                    try:
                        with open(str(fpath), "r", encoding="utf-8", errors="ignore") as fh:
                            for i, line in enumerate(fh, start=1):
                                if needle_basename in line or needle_full in line:
                                    results.append({
                                        "path": str(fpath),
                                        "line": i,
                                        "excerpt": line.strip(),
                                    })
                                    break
                    except Exception:
                        continue
                except Exception:
                    continue
            else:
                continue
            break

    _cache[key] = (now, results)
    _save_cache()
    return results


def clear_cache():
    _cache.clear()
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    # quick local test
    import sys
    t = sys.argv[1]
    print("hash:", compute_hash(t))
    print("dups:", find_duplicates(t, roots=[str(Path.home())]))
    print("refs:", find_references(t, roots=[str(Path.home())], max_files=1000))
