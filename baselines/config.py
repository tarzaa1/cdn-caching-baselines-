MOG_API_BASE = "http://10.13.14.1:30070"

REGIONS = ["eu-central-1", "us-east-1", "br-southeast-1"]

# Must match nginx `slice 1m`.
SLICE_SIZE = 1024 * 1024  # bytes

WARM_CHUNKS = 10

TOP_K = 10

PERIOD_SECONDS = 86_400
