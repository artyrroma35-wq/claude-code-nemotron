
"""Smart Key Aggregator - per-model pools with auto-failover."""
from __future__ import annotations
import asyncio, time, threading, random
from typing import Any
from loguru import logger

# ============================================================
# ALL 5 NVIDIA NIM KEYS
# ============================================================
NVIDIA_KEYS = [
    "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",  # K1
    "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",  # K2
    "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",  # K3
    "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",  # K4
    "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",  # K5
]

# ============================================================
# ALL 4 MISTRAL KEYS
# ============================================================
MISTRAL_KEYS = [
    "y6wdWhaUyeBtxNgU8cb2DmFzDFy9ibrQ",
    "couItY7tR4oeQYrxraAdvjpBVqOgj1yq",
    "CAOWkkn4LMuQYh6THRfhsqTbPnfzujBO",
    "WqrqcVoGsG8u3F1Rh5DgwIKyscgN0s6R",
]

# ============================================================
# MODEL FALLBACK CHAINS
# Each model has a list of alternatives if it fails
# ============================================================
NVIDIA_MODELS = {
    # Reasoning / Complex
    "deepseek-pro": {
        "name": "deepseek-ai/deepseek-v4-pro",
        "fallbacks": ["deepseek-ai/deepseek-v4-flash", "nvidia/nemotron-3-super-120b", "meta/llama-3.3-70b-instruct"],
        "type": "reasoning",
    },
    "deepseek-flash": {
        "name": "deepseek-ai/deepseek-v4-flash",
        "fallbacks": ["meta/llama-3.3-70b-instruct", "nvidia/nemotron-3-super-120b", "deepseek-ai/deepseek-v4-pro"],
        "type": "coding",
    },
    "nemotron-super": {
        "name": "nvidia/nemotron-3-super-120b",
        "fallbacks": ["deepseek-ai/deepseek-v4-flash", "mistralai/mistral-nemotron", "meta/llama-3.3-70b-instruct"],
        "type": "agentic",
    },
    "nemotron-ultra": {
        "name": "nvidia/nemotron-3-ultra-550b-a55b",
        "fallbacks": ["nvidia/nemotron-3-super-120b", "deepseek-ai/deepseek-v4-pro", "meta/llama-3.3-70b-instruct"],
        "type": "ultra",
    },
    "llama-3.3": {
        "name": "meta/llama-3.3-70b-instruct",
        "fallbacks": ["mistralai/mistral-nemotron", "deepseek-ai/deepseek-v4-flash", "nvidia/nemotron-3-super-120b"],
        "type": "general",
    },
    "mistral-nemotron": {
        "name": "mistralai/mistral-nemotron",
        "fallbacks": ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-v4-flash", "nvidia/nemotron-3-super-120b"],
        "type": "coding",
    },
    "qwen-397b": {
        "name": "qwen/qwen3.5-397b-a79b",
        "fallbacks": ["deepseek-ai/deepseek-v4-pro", "nvidia/nemotron-3-super-120b", "meta/llama-3.3-70b-instruct"],
        "type": "science",
    },
    "minimax": {
        "name": "minimax/minimax-m2.7",
        "fallbacks": ["deepseek-ai/deepseek-v4-flash", "meta/llama-3.3-70b-instruct", "mistralai/mistral-nemotron"],
        "type": "coding",
    },
}

# ============================================================
# KEY STATE TRACKER
# ============================================================
class KeyState:
    def __init__(self, key: str, provider: str):
        self.key = key
        self.provider = provider
        self.active_requests = 0
        self.total_requests = 0
        self.failures = 0
        self.consecutive_failures = 0
        self.disabled_until = 0.0
        self.last_used = 0.0
        self.avg_response_time = 0.0
        self.sample_count = 0
        self.model_blacklist = {}  # model -> disabled_until

    @property
    def is_disabled(self) -> bool:
        return time.time() < self.disabled_until

    def record_success(self, response_time: float):
        self.active_requests -= 1
        self.consecutive_failures = 0
        self.failures = 0
        self.avg_response_time = (self.avg_response_time * self.sample_count + response_time) / (self.sample_count + 1) if self.sample_count > 0 else response_time
        self.sample_count += 1

    def record_failure(self):
        self.active_requests -= 1
        self.consecutive_failures += 1
        self.failures += 1
        if self.consecutive_failures >= 3:
            backoff = min(60 * (2 ** (self.consecutive_failures - 3)), 300)
            self.disabled_until = time.time() + backoff
            logger.warning(f"Key {self.key[:12]}... disabled for {backoff}s ({self.consecutive_failures} consecutive failures)")

    def blacklist_model(self, model: str, duration: int = 30):
        self.model_blacklist[model] = time.time() + duration

    def is_model_blacklisted(self, model: str) -> bool:
        return model in self.model_blacklist and time.time() < self.model_blacklist[model]

    def record_start(self):
        self.active_requests += 1
        self.total_requests += 1
        self.last_used = time.time()

    def score(self) -> float:
        if self.is_disabled:
            return 999999
        return self.active_requests * 100 - (time.time() - self.last_used) * 0.1

# ============================================================
# GLOBAL POOLS
# ============================================================
class KeyPool:
    def __init__(self, keys: list[str], provider: str, name: str):
        self.name = name
        self.provider = provider
        self._keys = {k: KeyState(k, provider) for k in keys}
        self._lock = asyncio.Lock()
        self._model_index = 0
        logger.info(f"Pool '{name}': {len(keys)} keys from {provider}")

    async def get_key(self, preferred_model: str | None = None) -> tuple[str, str]:
        """Get the best key AND model. Returns (key, model_name)."""
        async with self._lock:
            # Find best key
            sorted_keys = sorted(self._keys.values(), key=lambda k: k.score())
            best_key = sorted_keys[0]
            
            # Find best model that isn't blacklisted on this key
            model = preferred_model or "meta/llama-3.3-70b-instruct"
            if best_key.is_model_blacklisted(model):
                # Try fallbacks
                for info in NVIDIA_MODELS.values():
                    if info["name"] == model:
                        for fb in info["fallbacks"]:
                            if not best_key.is_model_blacklisted(fb):
                                model = fb
                                break
                        break
            
            best_key.record_start()
            return best_key.key, model

    def record_success(self, key: str, response_time: float):
        if key in self._keys: self._keys[key].record_success(response_time)

    def record_failure(self, key: str, model: str = ""):
        if key in self._keys:
            self._keys[key].record_failure()
            if model:
                self._keys[key].blacklist_model(model, 30)

    def get_stats(self) -> dict:
        total = len(self._keys)
        disabled = sum(1 for k in self._keys.values() if k.is_disabled)
        total_reqs = sum(k.total_requests for k in self._keys.values())
        return {
            "name": self.name,
            "total_keys": total,
            "disabled_keys": disabled,
            "total_requests": total_reqs,
            "keys": [{"id": k.key[:12] + "...", "active": k.active_requests, "total": k.total_requests, "failures": k.consecutive_failures, "disabled": k.is_disabled, "avg_time": f"{k.avg_response_time:.1f}s" if k.sample_count else "N/A"} for k in self._keys.values()]
        }

# Create global pools
_nvidia_pool = KeyPool(NVIDIA_KEYS, "nvidia", "nvidia")
_mistral_pool = KeyPool(MISTRAL_KEYS, "mistral", "mistral")

def get_nvidia_pool() -> KeyPool: return _nvidia_pool
def get_mistral_pool() -> KeyPool: return _mistral_pool
def get_models() -> dict: return NVIDIA_MODELS

def get_pool(name="text"):
    pools = {"text": _text_pool, "vision": _vision_pool, "ocr": _ocr_pool, "audio": _audio_pool}
    return pools.get(name, _text_pool)

