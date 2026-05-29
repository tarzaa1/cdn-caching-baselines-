"""
Thin wrappers around the MOG API.

MOG API endpoints used:
  GET  /videos                           — list all videos with popularity + storage metadata
  POST /files/move                       — move a file between hot and cold storage
  POST /files/purge                      — purge all chunks of a file from an edge cache (server-side wildcard)
  GET  /files/copy?region=&file=&byte_start=&byte_end=  — copy one chunk into an edge cache
"""

import logging
import requests
import config

log = logging.getLogger(__name__)

_session = requests.Session()

def get_all_videos() -> list[dict]:
    videos: list[dict] = []
    page = 1

    while True:
        resp = _session.get(
            f"{config.MOG_API_BASE}/videos",
            params={"page": page},
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("data")

        if not batch:
            break

        videos.extend(batch)
        page += 1

    log.info("Fetched %d videos from MOG API.", len(videos))
    return videos

def move_file(source: str, destination: str, file_key: str):
    log.info("Moving %s: %s → %s", file_key, source, destination)
    resp = _session.post(
        f"{config.MOG_API_BASE}/files/move",
        json={"source": source, "destination": destination, "file": file_key},
        timeout=30,
    )
    resp.raise_for_status()


def purge_file(region: str, file_key: str):
    log.info("Purging %s from %s", file_key, region)
    resp = _session.post(
        f"{config.MOG_API_BASE}/files/purge",
        json={"region": region, "file": file_key},
        timeout=30,
    )
    resp.raise_for_status()

def warm_file(region: str, file_key: str):
    log.info("Warming %s at %s (%d chunks)", file_key, region, config.WARM_CHUNKS)
    for i in range(config.WARM_CHUNKS):
        byte_start = i * config.SLICE_SIZE
        byte_end = (i + 1) * config.SLICE_SIZE - 1
        resp = _session.get(
            f"{config.MOG_API_BASE}/files/copy",
            params={
                "region": region,
                "file": file_key,
                "byte_start": byte_start,
                "byte_end": byte_end,
            },
            timeout=60,
        )
        resp.raise_for_status()

def regional_views(video: dict, region: str) -> int:
    """Return the per-region view count for *region* from a VideoResult object."""
    for node in video.get("edgeNodes", []):
        if node["region"] == region:
            return node.get("views", 0)
    return 0

def is_cached(video: dict, region: str) -> bool:
    """Return whether *video* is cached at the edge node in *region*."""
    for node in video.get("edgeNodes", []):
        if node["region"] == region:
            return node.get("isCached", False)
    return False
