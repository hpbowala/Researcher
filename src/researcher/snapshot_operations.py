"""Operations for polling and downloading BrightData snapshots."""

import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def poll_snapshot_status(
    snapshot_id: str, max_attempts: int = 60, delay: int = 5
) -> bool:
    """Poll the snapshot status until it's ready or failed.

    Args:
        snapshot_id: The ID of the snapshot to check.
        max_attempts: Maximum number of polling attempts.
        delay: Delay in seconds between attempts.

    Returns:
        True if snapshot is ready, False otherwise.
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    for _ in range(max_attempts):
        try:
            print(f"Checking snapshot progress... (attempt {_ + 1} of {max_attempts})")
            response = requests.get(progress_url, headers=headers, timeout=30)
            response.raise_for_status()  # raise an exception if the request is not successful

            progress_data = response.json()
            status = progress_data.get("status")
            if status == "ready":
                print(f"✅ Snapshot {snapshot_id} is ready")
                return True
            elif status == "failed":
                print(f"❌ Snapshot {snapshot_id} has an error")
                return False
            elif status == "running":
                print(f"🔄 Snapshot {snapshot_id} is running")
                time.sleep(delay)
            else:
                print(f"ℹ️ Snapshot {snapshot_id} has an unknown status: {status}")
                time.sleep(delay)
        except Exception as e:
            print(f"❌ Error checking snapshot status: {e}")
            time.sleep(delay)

    print(f"❌ Timeout waiting for snapshot {snapshot_id} to be ready")
    return False


def download_snapshot(
    snapshot_id: str, res_format: str = "json"
) -> Optional[List[Dict[Any, Any]]]:
    """Download a snapshot from the BrightData API.

    Args:
        snapshot_id: The ID of the snapshot to download.
        res_format: The format of the response (default: "json").

    Returns:
        The snapshot data as a list of dictionaries, or None if download fails.
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    download_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={res_format}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(download_url, headers=headers, timeout=120)
        response.raise_for_status()  # raise an exception if the request is not successful

        data = response.json()
        print(
            f"🎉 Successfully downloaded {len(data) if isinstance(data, list) else 1} items"
        )
        return data
    except Exception as e:
        print(f"Error downloading snapshot: {e}")
        return None
