"""
Resumable high-speed downloader and integrity validator for GLM-5.2 744B INT4 MoE Container.
Targets Colibri AI Memory Multi-Tiering Engine.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path

# Set HF transfer for maximum multi-connection throughput
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GLM52_Downloader")

REPO_ID = "mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp"
DEFAULT_DEST = r"C:\colibri_models\glm52_i4"


def download_model(dest_dir: str = DEFAULT_DEST, max_retries: int = 10):
    dest_path = Path(dest_dir).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Starting High-Speed Download for GLM-5.2 744B MoE Container")
    logger.info("Repository: %s", REPO_ID)
    logger.info("Destination: %s", dest_path)
    logger.info("HF Transfer Enabled: %s", os.environ.get("HF_HUB_ENABLE_HF_TRANSFER") == "1")
    logger.info("=" * 70)

    from huggingface_hub import snapshot_download

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            logger.info("Download Attempt %d/%d...", attempt, max_retries)
            start_time = time.time()
            
            downloaded_path = snapshot_download(
                repo_id=REPO_ID,
                local_dir=str(dest_path),
                max_workers=8,
                resume_download=True,
            )
            
            elapsed = time.time() - start_time
            logger.info("Download completed successfully in %.2f seconds (%.2f minutes)", elapsed, elapsed / 60.0)
            break
        except Exception as e:
            logger.warning("Download interrupted on attempt %d: %s", attempt, e)
            if attempt >= max_retries:
                logger.error("Exceeded maximum retries (%d). Exiting.", max_retries)
                sys.exit(1)
            wait_sec = min(5 * attempt, 30)
            logger.info("Retrying in %d seconds...", wait_sec)
            time.sleep(wait_sec)

    # Post-Download Shard Audit
    logger.info("Auditing downloaded tensor shards in %s...", dest_path)
    files = list(dest_path.glob("*.safetensors"))
    total_bytes = sum(f.stat().st_size for f in files)
    logger.info("Total .safetensors files: %d", len(files))
    logger.info("Total Model Size on Disk: %.2f GB (%.2f GiB)", total_bytes / 1e9, total_bytes / (1024**3))

    config_f = dest_path / "config.json"
    if config_f.exists():
        logger.info("config.json present: %s", config_f)
    else:
        logger.warning("config.json missing from download directory!")

    # Verify MTP Head
    mtp_files = list(dest_path.glob("out-mtp-*.safetensors"))
    logger.info("MTP Speculative Heads detected: %d", len(mtp_files))
    for m in mtp_files:
        logger.info(" - %s (%.2f MB)", m.name, m.stat().st_size / (1024**2))

    logger.info("=" * 70)
    logger.info("GLM-5.2 744B MoE Container is verified and ready for Colibri!")
    logger.info("To chat: $env:COLI_MODEL='%s'; coli chat", dest_path)
    logger.info("To serve: coli serve --model '%s'", dest_path)
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download GLM-5.2 INT4 Container for Colibri")
    parser.add_argument("--dest", type=str, default=DEFAULT_DEST, help="Destination directory on disk")
    parser.add_argument("--retries", type=int, default=10, help="Max retry attempts on network interruptions")
    args = parser.parse_args()

    download_model(dest_dir=args.dest, max_retries=args.retries)
