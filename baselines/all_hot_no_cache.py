"""
Baseline 1 — All-hot, no cache.

Ensures a clean starting state for experiments:
  1. Any video not already on hot storage is moved there.
  2. Every video is purged from every edge node's nginx cache.

Run once before starting an experiment.
"""

import logging
import sys

import api_client
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def run() -> None:
    log.info("Baseline 1: All-hot, no cache")

    videos = api_client.get_all_videos()

    cold_videos = [v for v in videos if v["storage"]["name"] != "hot"]
    if cold_videos:
        log.info("Moving %d video(s) from cold to hot.", len(cold_videos))
        for video in cold_videos:
            api_client.move_file("cold", "hot", video["key"])
    else:
        log.info("All videos already on hot storage.")

    log.info("Purging cached videos from all regions.")
    for video in videos:
        for region in config.REGIONS:
            if api_client.is_cached(video, region):
                api_client.purge_file(region, video["key"])

    log.info("Done. All videos are on hot storage; all edge caches are empty.")


if __name__ == "__main__":
    run()
