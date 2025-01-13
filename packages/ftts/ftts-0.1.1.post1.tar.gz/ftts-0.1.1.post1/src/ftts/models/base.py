from abc import abstractmethod
from ftts.config import Config
from ftts.utils.base import CheckpointMixin, IOMixin
from typing import Dict
from typing_extensions import Self
from pathlib import Path
from pydantic import ConfigDict


class Model(CheckpointMixin, IOMixin):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True
    )

    def get_config(self) -> Config:
        raise NotImplementedError

    def load(self, save_dir: str | Path, **kwargs) -> Self:
        raise NotImplementedError

    def save(self, save_dir: str | Path, **kwargs) -> None:
        raise NotImplementedError

    def from_checkpoint(self, checkpoint_dir: str | Path, **kwargs) -> Self:
        raise NotImplementedError


class CachedModel(Model):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True
    )

    cache: Dict = {}

    @abstractmethod
    def reset(self):
        raise NotImplementedError
