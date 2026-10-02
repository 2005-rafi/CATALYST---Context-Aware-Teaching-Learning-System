"""
Pre-download utility for Embedding and Cross-Encoder Reranking models.
Saves model weights locally into persistent storage for offline, zero-latency restarts.
Usage:
    python scripts/download_models.py
"""

import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from sentence_transformers import SentenceTransformer, CrossEncoder
from backend.core.config.settings import get_settings

def download_and_cache_models():
    settings = get_settings()
    
    emb_model_name = settings.EMBEDDING_MODEL
    emb_dest_path = Path(settings.local_embedding_model_path())
    
    ce_model_name = settings.CROSS_ENCODER_MODEL
    ce_dest_path = Path(settings.local_cross_encoder_path())
    
    print("=" * 65)
    print("      LOCAL MODEL PRE-DOWNLOAD & OFFLINE CACHE UTILITY")
    print("=" * 65)
    print(f"Target Cache Directory: {Path(settings.MODELS_CACHE_PATH).resolve()}")
    
    # 1. Download & Save Embedding Model
    print(f"\n[1/2] Processing Embedding Model: '{emb_model_name}'...")
    emb_dest_path.mkdir(parents=True, exist_ok=True)
    
    if (emb_dest_path / "config.json").exists() and (any(emb_dest_path.glob("*.safetensors")) or any(emb_dest_path.glob("*.bin"))):
        print(f"      Status: Model already present locally at:\n      -> {emb_dest_path}")
    else:
        print(f"      Downloading from Hugging Face Hub...")
        start_t = time.time()
        emb_model = SentenceTransformer(emb_model_name)
        emb_model.save(str(emb_dest_path))
        dur = time.time() - start_t
        print(f"      [SUCCESS] Saved to:\n      -> {emb_dest_path} (took {dur:.1f}s)")
        
    # 2. Download & Save Cross-Encoder Model
    print(f"\n[2/2] Processing Cross-Encoder Model: '{ce_model_name}'...")
    ce_dest_path.mkdir(parents=True, exist_ok=True)
    
    if (ce_dest_path / "config.json").exists() and (any(ce_dest_path.glob("*.safetensors")) or any(ce_dest_path.glob("*.bin"))):
        print(f"      Status: Model already present locally at:\n      -> {ce_dest_path}")
    else:
        print(f"      Downloading from Hugging Face Hub...")
        start_t = time.time()
        ce_model = CrossEncoder(ce_model_name)
        ce_model.save(str(ce_dest_path))
        dur = time.time() - start_t
        print(f"      [SUCCESS] Saved to:\n      -> {ce_dest_path} (took {dur:.1f}s)")
        
    print("\n" + "=" * 65)
    print("  [ALL MODELS STORED LOCALLY AND READY FOR 100% OFFLINE USE]")
    print("=" * 65)

if __name__ == "__main__":
    download_and_cache_models()
