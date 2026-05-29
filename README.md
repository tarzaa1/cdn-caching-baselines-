# CDN Proactive Caching Baselines

Scripts for evaluating proactive cache placement strategies on a two-cluster CDN using view counts and prediction scores from the MOG API as popularity signals.

## Baselines

| Script | Description |
|---|---|
| `all_hot_no_cache.py` | Moves all videos to hot storage and purges all edge caches. Run once to establish a clean experiment baseline. |
| `static_global_topk.py` | Ranks videos by global views, pre-warms the top-K at every edge. Run once; never updated. |
| `periodic_global_topk.py` | Same as above, but re-runs on a fixed interval to track popularity changes over time. |
| `periodic_regional_topk.py` | Periodic top-K per region — each edge is warmed with the videos most popular in that region. |

## Configuration

All parameters are in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `MOG_API_BASE` | `http://10.13.14.1:30070` | MOG API endpoint |
| `TOP_K` | `10` | Number of videos to keep warmed per baseline |
| `WARM_CHUNKS` | `10` | Number of 1 MB chunks to pre-warm per video |
| `PERIOD_SECONDS` | `86400` | Re-run interval for periodic baselines (seconds) |

## Setup

```bash
cd baselines
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Clean slate before an experiment
python all_hot_no_cache.py

# Static global top-K (run once)
python static_global_topk.py

# Periodic global top-K (runs until interrupted)
python periodic_global_topk.py

# Periodic regional top-K (runs until interrupted)
python periodic_regional_topk.py
```
