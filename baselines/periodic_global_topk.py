"""
Baseline 3 — Periodic global top-K.

Same placement logic as Baseline 2, but re-executed on a fixed interval so the
cache placement tracks changes in global popularity over time.

  Each period:
    1. Fetch all videos and rank by global view count.
    2. Move top-K to hot storage if not already there.
    3. Warm every edge with the top-K videos.
    4. Purge all other videos from every edge cache.

Parameters (edit config.py to change):
  TOP_K           — number of videos to keep warmed
  PERIOD_SECONDS  — how often to re-run (default 86 400 s = 24 h)
"""

import logging
import sys
import time

import schedule

import api_client
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def run_once() -> None:
    log.info("--- Periodic global top-%d refresh ---", config.TOP_K)

    videos = api_client.get_all_videos()

    ranked = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)
    top_k = ranked[: config.TOP_K]
    top_k_keys = {v["key"] for v in top_k}

    log.info(
        "Top-%d videos by global views: %s",
        config.TOP_K,
        [v["key"] for v in top_k],
    )

    # Ensure top-K are on hot storage.
    for video in top_k:
        if video["storage"]["name"] != "hot":
            api_client.move_file(video["storage"]["name"], "hot", video["key"])

    # Warm every edge with every top-K video.
    for video in top_k:
        for region in config.REGIONS:
            api_client.warm_file(region, video["key"])

    # Purge non-top-K from every edge.
    non_top_k = [v for v in videos if v["key"] not in top_k_keys]
    for video in non_top_k:
        for region in config.REGIONS:
            api_client.purge_file(region, video["key"])

    log.info("Refresh complete. Next run in %d s.", config.PERIOD_SECONDS)


def main() -> None:
    log.info(
        "=== Baseline 3: Periodic global top-%d (every %d s) ===",
        config.TOP_K,
        config.PERIOD_SECONDS,
    )

    run_once()  # Execute immediately on start.

    schedule.every(config.PERIOD_SECONDS).seconds.do(run_once)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
