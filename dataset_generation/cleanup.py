"""
Script to clean up generated dataset files.
"""

import shutil
from pathlib import Path


def cleanup_dataset():
    """Remove all generated dataset files."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    if data_dir.exists():
        print(f"Removing {data_dir}...")
        shutil.rmtree(data_dir)
        print("✅ Cleaned up data directory")
    else:
        print("ℹ️  No data directory found - nothing to clean")
    
    # Also clean up any __pycache__ directories
    cache_dirs = list(Path(__file__).parent.rglob("__pycache__"))
    for cache_dir in cache_dirs:
        print(f"Removing {cache_dir}...")
        shutil.rmtree(cache_dir)
    
    if cache_dirs:
        print("✅ Cleaned up cache directories")
    
    print("\n✅ Cleanup complete! Ready to regenerate dataset.")


if __name__ == "__main__":
    cleanup_dataset()

