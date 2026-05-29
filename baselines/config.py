MOG_API_BASE = "http://10.13.14.1:30070"

REGIONS = ["eu-central-1", "us-east-1", "br-southeast-1"]

# Must match nginx `slice 1m`.
SLICE_SIZE = 1024 * 1024  # bytes

# Number of chunks to pre-warm per video (first N × 1 MB of each file).
WARM_CHUNKS = 10

# -------------------------------------------------------------------
# Baseline parameters (override via environment or direct edit)
# -------------------------------------------------------------------

# Top-K for baselines 2, 3, 4.
TOP_K = 10

# Re-run interval for periodic baselines (3 and 4), in seconds.
PERIOD_SECONDS = 86_400  # 24 h
