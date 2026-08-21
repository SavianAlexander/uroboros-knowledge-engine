"""
High-Throughput Multi-Stream Parallel Downloader for GLM-5.2 744B MoE.
Downloads multiple 2.8 GB shards concurrently to uncap high-speed Starlink bandwidth.
"""

import os
import sys
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from huggingface_hub import HfApi, hf_hub_download, HfFolder

# Authenticate with stored user token and optimize HTTP connection pool
HF_TOKEN = HfFolder.get_token()
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("FastDownloader")

REPO_ID = "mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp"
DEST_DIR = r"C:\colibri_models\glm52_i4"
MAX_PARALLEL_SHARDS = 8  # 8 concurrent 2.8 GB shard streams


def download_single_file(filename: str, expected_size: int, dest_path: Path, max_retries: int = 5) -> bool:
    target_file = dest_path / filename
    if target_file.exists() and target_file.stat().st_size == expected_size:
        logger.info("[ALREADY COMPLETE] %s (%.2f MB)", filename, expected_size / (1024**2))
        return True

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("[STARTING] %s (%.2f MB) [Stream Active]", filename, (expected_size or 0) / (1024**2))
            t0 = time.time()
            hf_hub_download(
                repo_id=REPO_ID,
                filename=filename,
                local_dir=str(dest_path),
                force_download=False,
                token=HF_TOKEN,
            )
            elapsed = time.time() - t0
            speed_mb = ((expected_size or 0) / (1024**2)) / max(elapsed, 0.1)
            logger.info("[FINISHED] %s in %.1fs (%.2f MB/s)", filename, elapsed, speed_mb)
            return True
        except Exception as e:
            logger.warning("[RETRY %d/%d] Error downloading %s: %s", attempt, max_retries, filename, e)
            time.sleep(min(attempt * 2, 10))

    logger.error("[FAILED] Could not download %s after %d retries.", filename, max_retries)
    return False


def main():
    dest_path = Path(DEST_DIR).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Initiating High-Throughput Multi-Stream Download for GLM-5.2 MoE")
    logger.info("Repository: %s", REPO_ID)
    logger.info("Destination: %s", dest_path)
    logger.info("Parallel Shard Streams: %d", MAX_PARALLEL_SHARDS)
    logger.info("=" * 70)

    api = HfApi()
    model_info = api.model_info(REPO_ID, files_metadata=True)
    all_files = [
        (s.rfilename, getattr(s, "size", 0))
        for s in model_info.siblings
        if not s.rfilename.startswith(".git")
    ]

    total_files = len(all_files)
    total_expected_bytes = sum(size for _, size in all_files if size)
    logger.info("Total Files: %d | Total Payload: %.2f GB", total_files, total_expected_bytes / 1e9)

    # Separate metadata files from heavy shards to download metadata first
    metadata_files = [f for f in all_files if not f[0].endswith(".safetensors")]
    tensor_files = [f for f in all_files if f[0].endswith(".safetensors")]

    for filename, size in metadata_files:
        download_single_file(filename, size, dest_path)

    # Download heavy safetensors shards in parallel
    logger.info("Launching parallel thread pool with %d concurrent shard workers...", MAX_PARALLEL_SHARDS)
    start_time = time.time()
    completed_count = 0
    failed_files = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SHARDS) as executor:
        future_to_file = {
            executor.submit(download_single_file, filename, size, dest_path): filename
            for filename, size in tensor_files
        }

        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                success = future.result()
                if success:
                    completed_count += 1
                    pct = (completed_count / len(tensor_files)) * 100.0
                    logger.info("Progress: %d/%d tensor shards complete (%.1f%%)", completed_count, len(tensor_files), pct)
                else:
                    failed_files.append(filename)
            except Exception as exc:
                logger.error("Exception downloading %s: %s", filename, exc)
                failed_files.append(filename)

    total_time = time.time() - start_time
    logger.info("=" * 70)
    logger.info("Parallel Download Finished in %.2f minutes!", total_time / 60.0)
    if failed_files:
        logger.warning("The following files failed: %s", failed_files)
    else:
        logger.info("All %d shards downloaded and verified successfully!", total_files)
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
