from pathlib import Path
from typing import Literal


DEFAULT_CACHE_DIR = Path.home() / ".cache" / "ftts" / "checkpoints"  # 默认缓存目录


def prepare_chattts(
    cache_dir: str | Path = DEFAULT_CACHE_DIR, use_hf_mirror: bool = True
) -> None:
    """Prepare offline models for building pipeline"""
    from huggingface_hub import snapshot_download
    import os

    if use_hf_mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    repo_id = "2Noise/ChatTTS"
    cache_dir = Path(cache_dir) / repo_id
    snapshot_download(
        repo_id=repo_id,
        local_dir=cache_dir,
        local_dir_use_symlinks=False,
        ignore_patterns=["*.pt"],
    )


def prepare_stream_chattts(
    cache_dir: str | Path = DEFAULT_CACHE_DIR, use_hf_mirror: bool = True
) -> None:
    """Prepare offline models for building pipeline"""
    from huggingface_hub import snapshot_download
    import os

    if use_hf_mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    repo_id = "Ddream-ai/ChatTTS-streaming"
    cache_dir = Path(cache_dir) / repo_id
    snapshot_download(
        repo_id=repo_id,
        local_dir=cache_dir,
        local_dir_use_symlinks=False,
    )


def clear_cache(cache_dir: str | Path = DEFAULT_CACHE_DIR) -> None:
    """Clear all files in cache directory, be careful!"""
    import shutil

    if cache_dir.exists():
        shutil.rmtree(cache_dir)


def download(
    repo_id: str,
    revision: str = None,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    endpoint: Literal["modelscope", "huggingface", "hf-mirror"] = "hf-mirror",
) -> None:
    """Download model from modelscope"""
    cache_dir = Path(cache_dir)
    if endpoint == "hf-mirror":
        from huggingface_hub import snapshot_download

        _ = snapshot_download(
            repo_id=repo_id,
            local_dir=cache_dir / repo_id,
            revision=revision,
            local_dir_use_symlinks=False,
            endpoint="https://hf-mirror.com",
        )
    if endpoint == "huggingface":
        from huggingface_hub import snapshot_download

        _ = snapshot_download(
            repo_id=repo_id,
            local_dir=cache_dir / repo_id,
            revision=revision,
            local_dir_use_symlinks=False,
        )

    elif endpoint == "modelscope":
        from modelscope import snapshot_download

        _ = snapshot_download(model_id=repo_id, cache_dir=cache_dir, revision=revision)
