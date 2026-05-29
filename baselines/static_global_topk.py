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
    log.info("Baseline 2: Static global top-%d", config.TOP_K)

    videos = api_client.get_all_videos()

    ranked = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)
    top_k = ranked[: config.TOP_K]
    top_k_keys = {v["key"] for v in top_k}

    log.info(
        "Top-%d videos by global views: %s",
        config.TOP_K,
        [v["key"] for v in top_k],
    )

    for video in top_k:
        if video["storage"]["name"] != "hot":
            api_client.move_file(video["storage"]["name"], "hot", video["key"])

    for video in top_k:
        for region in config.REGIONS:
            api_client.warm_file(region, video["key"])

    non_top_k = [v for v in videos if v["key"] not in top_k_keys]
    log.info("Purging %d non-top-K videos from all edges.", len(non_top_k))
    for video in non_top_k:
        for region in config.REGIONS:
            if api_client.is_cached(video, region):
                api_client.purge_file(region, video["key"])

    log.info("Done. Top-%d videos pre-warmed at all edges.", config.TOP_K)


if __name__ == "__main__":
    run()
