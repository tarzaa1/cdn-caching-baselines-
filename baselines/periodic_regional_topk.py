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
    log.info("Periodic regional top-%d refresh", config.TOP_K)

    videos = api_client.get_all_videos()

    all_top_k_keys: set[str] = set()

    for region in config.REGIONS:
        ranked = sorted(
            videos,
            key=lambda v, r=region: api_client.regional_views(v, r),
            reverse=True,
        )
        top_k = ranked[: config.TOP_K]
        top_k_keys = {v["key"] for v in top_k}
        all_top_k_keys |= top_k_keys

        log.info(
            "[%s] Top-%d by regional views: %s",
            region,
            config.TOP_K,
            [v["key"] for v in top_k],
        )

        for video in top_k:
            api_client.warm_file(region, video["key"])

        for video in videos:
            if video["key"] not in top_k_keys:
                if api_client.is_cached(video, region):
                    api_client.purge_file(region, video["key"])

    for video in videos:
        if video["key"] in all_top_k_keys and video["storage"]["name"] != "hot":
            api_client.move_file(video["storage"]["name"], "hot", video["key"])

    log.info(
        "Refresh complete. %d unique videos across all regional top-K sets. "
        "Next run in %d s.",
        len(all_top_k_keys),
        config.PERIOD_SECONDS,
    )


def main() -> None:
    log.info(
        "Baseline 4: Periodic regional top-%d (every %d s)",
        config.TOP_K,
        config.PERIOD_SECONDS,
    )

    run_once()

    schedule.every(config.PERIOD_SECONDS).seconds.do(run_once)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
