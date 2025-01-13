from abc import abstractmethod
from pydantic import ConfigDict, BaseModel
from ftts.config import Config
from ftts.data import Speech, SpeechList
from typing import Any, List, Union
import torch
from ftts.utils.base import IOMixin
from loguru import logger
from pathlib import Path


class BaseComponent(IOMixin, BaseModel):
    """A component is a module that can set tag on audio data"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)
    name: str | None = None
    description: str | None = None
    input_tags: List[str] | None = None
    output_tags: List[str] | None = None

    @abstractmethod
    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        raise NotImplementedError

    @abstractmethod
    def setup(self, **kwargs) -> None:
        raise NotImplementedError

    def get_config(self) -> Config:
        raise NotImplementedError

    def load(self, save_dir: str):
        raise NotImplementedError

    def save(self, save_dir: str):
        raise NotImplementedError

    def log_component_error(self, context: str = ""):
        logger.error(
            f"Component {self.name} error, context: {context}",
        )

    def ensure_dir_exists(self, dir: str | Path) -> Path:
        """Ensure the directory exists, if not, create it.

        Args:
            dir (str | Path): the directory path.

        Returns:
            Path: the directory path, as Path object.
        """
        dir = Path(dir)
        if not dir.exists():
            dir.mkdir(parents=True)
        return dir

    def assert_dir_exists(self, dir: str | Path) -> Path:
        """Assert the directory exists. If not, raise an error.

        Args:
            dir (str | Path): the directory path.

        Returns:
            Path: the directory path, as Path object.
        """
        dir = Path(dir)
        assert dir.exists(), f"Directory {dir} not exists."
        return dir

    def choose_device(self, device: str | None = None) -> torch.device:
        """Choose the device to run the model.

        Args:
            device (str | None): the device to run the model. Defaults to None.

        Returns:
            torch.device: the device to run the model.
        """
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        return device

    def _to_speeches(
        self,
        input: Union[str, List[str], Any, Speech, SpeechList[Speech]],
    ) -> SpeechList[Speech]:
        if isinstance(input, str):
            return SpeechList([Speech(text=input)])
        elif isinstance(input, list):
            if all(isinstance(i, str) for i in input):
                return SpeechList([Speech(text=i) for i in input])
            elif all(isinstance(i, Speech) for i in input):
                return SpeechList(input)
            else:
                raise ValueError("input type error")
        elif isinstance(input, Speech):
            return SpeechList([input])
        elif isinstance(input, SpeechList):
            return input
        else:
            raise ValueError("input type error")

    def __ror__(
        self,
        input: Union[str, List[str], Speech, SpeechList[Speech]],
    ) -> SpeechList[Speech]:
        """组件之间的同步连接符号 `|` 实现"""
        speeches = self._to_speeches(input)
        try:
            speeches = self.predict(speeches)
        except Exception as e:
            for speech in speeches:
                speech: Speech
                speech.is_bad = True
                speech.bad_reason = str(e.with_traceback(e.__traceback__))
                speech.bad_component = self.name
                self.log_component_error(context=str(e))
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                current_gpu_index = torch.cuda.current_device()
                available_memory = torch.cuda.get_device_properties(
                    current_gpu_index
                ).total_memory / (1024**3)
                used_memory = torch.cuda.memory_allocated(current_gpu_index) / (1024**3)
                free_memory = available_memory - used_memory
                if free_memory <= 0:
                    raise MemoryError("Out of GPU memory.")
        return speeches
