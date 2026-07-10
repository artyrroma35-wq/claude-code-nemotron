from .key_aggregator import ModelKeyPool

NVIDIA_NIM_KEYS = [
    "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",
    "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",
]

_nvidia_pool = ModelKeyPool(NVIDIA_NIM_KEYS, name="nvidia_nim", min_interval=1.0)

def get_nvidia_pool():
    return _nvidia_pool
