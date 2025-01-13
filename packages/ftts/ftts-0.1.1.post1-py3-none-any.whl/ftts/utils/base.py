from ftts.config import Config
from abc import ABC, abstractmethod
from pathlib import Path
from .prepare_model import download, DEFAULT_CACHE_DIR
from typing import Literal


class IOMixin(ABC):
    @abstractmethod
    def save(self, save_dir: str):
        raise NotImplementedError

    @abstractmethod
    def load(self, save_dir: str):
        raise NotImplementedError

    @abstractmethod
    def get_config(self) -> Config:
        raise NotImplementedError


class CheckpointMixin(ABC):
    cache_dir: str | Path = DEFAULT_CACHE_DIR
    checkpoint: str | None = None
    endpoint: Literal["modelscope", "huggingface", "hf-mirror"] = "hf-mirror"

    @abstractmethod
    def from_checkpoint(self, checkpoint_dir: str, **kwargs):
        raise NotImplementedError

    def download_checkpoint(self, revision: str = None) -> Path:
        if self.checkpoint is None:
            raise ValueError("checkpoint is None")
        checkpoint_dir = self.cache_dir / self.checkpoint
        if not checkpoint_dir.exists():
            download(
                repo_id=self.checkpoint,
                revision=revision,
                cache_dir=self.cache_dir,
                endpoint=self.endpoint,
            )
        return checkpoint_dir

    @property
    def checkpoint_dir(self) -> Path | None:
        if self.checkpoint is None:
            return None
        return self.cache_dir / self.checkpoint

    @property
    def default_checkpoint_dir(self) -> Path:
        return self.cache_dir / self.checkpoint


def clear_cache(cache_dir: str | Path = DEFAULT_CACHE_DIR):
    """清空缓存目录

    Args:
        cache_dir (str | Path, optional): 缓存目录. Defaults to DEFAULT_CACHE_DIR = Path.home() / ".cache" / "fasr" / "checkpoints".
    """
    cache_dir = Path(cache_dir)
    if cache_dir.exists():
        for item in cache_dir.iterdir():
            if item.is_dir():
                for sub_item in item.iterdir():
                    sub_item.unlink()
                item.rmdir()
            else:
                item.unlink()
    else:
        cache_dir.mkdir(parents=True)
    return cache_dir
