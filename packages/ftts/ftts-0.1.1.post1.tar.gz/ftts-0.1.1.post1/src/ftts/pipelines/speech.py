from pydantic import validate_call, ConfigDict, Field, model_validator, BaseModel
from ftts.components import TextNormalizer
from ftts.components.base import BaseComponent
from ftts.data import SpeechList, Speech, SpeechQueue
from ftts.config import registry, Config
from ftts.utils.base import IOMixin
from typing import List
from typing_extensions import Self
from collections import OrderedDict
from loguru import logger
from queue import Queue, Empty
from pathlib import Path
import time
import threading


def run_component(
    component: BaseComponent, speeches: SpeechList[Speech]
) -> SpeechList[Speech]:
    """Run a component to process the speech data

    Args:
        component (BaseComponent): the component to process the speech data
        speeches (SpeechList[Speech]): the speech data

    Returns:
        SpeechList[Speech]: the processed speech data
    """
    start = time.perf_counter()
    speeches = speeches | component
    end = time.perf_counter()
    spent = end - start
    for speech in speeches:
        speech: Speech
        if speech.spent_time is None:
            speech.spent_time = {}
        if speech.spent_time.get(component.name) is None:
            speech.spent_time[component.name] = spent
        else:
            speech.spent_time[component.name] += spent
        speech.spent_time[component.name] = round(speech.spent_time[component.name], 3)
    return speeches


@registry.pipes.register("thread_pipe")
class Pipe(IOMixin, BaseModel):
    """Pipe is a component in the pipeline that can process the audio data in parallel"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    component: BaseComponent | None = Field(
        None, description="the component to process the audio"
    )
    verbose: bool = Field(False, description="whether to print detailed logs")
    input_queue: SpeechQueue | None = None
    output_queue: SpeechQueue | None = None
    batch_timeout: float = Field(0.01, description="dynamic batch timeout", ge=0)
    batch_size: int | None = Field(1, description="dynamic batch size", ge=1)
    is_last: bool = Field(True, description="whether it is the last component")
    stop_event: threading.Event | None = Field(None, description="stop event")
    thread: threading.Thread | None = Field(default=None, description="thread object")

    @model_validator(mode="after")
    def validate_stop_event(self):
        if self.stop_event is None:
            self.stop_event = threading.Event()
        return self

    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        """Predict the audio data"""
        return run_component(component=self.component, speeches=speeches)

    def run_loop(self):
        while not self.stop_event.is_set():
            batch = self.dynamic_batch()
            if len(batch) == 0:
                continue
            speeches = SpeechList([speech for speech, response_queue in batch])
            start = time.perf_counter()
            _ = self.predict(speeches=speeches)
            end = time.perf_counter()
            _spent = round(end - start, 2)
            if self.is_last or self.output_queue is None:
                for speech, response_queue in batch:
                    response_queue: Queue
                    response_queue.put(speech)
            else:
                for item in batch:
                    self.output_queue.put(item)
                    self.input_queue.task_done()

    def dynamic_batch(self):
        entered_at = time.monotonic()
        end_time = entered_at + self.batch_timeout
        batch = []
        if self.batch_size is None:
            batch_size = 1e6
        else:
            batch_size = self.batch_size
        while time.monotonic() < end_time and len(batch) < batch_size:
            try:
                audio, response_queue = self.input_queue.get(timeout=self.batch_timeout)
                batch.append((audio, response_queue))
            except Exception:
                break
        return batch

    def start(self):
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.daemon = True
        self.thread.name = self.component.name
        self.thread.start()

    def get_config(self) -> Config:
        data = {
            "pipe": {
                "@pipes": "thread_pipe",
                "batch_timeout": self.batch_timeout,
                "batch_size": self.batch_size,
            }
        }
        config = Config(data=data)
        return config

    def save(self, save_dir: str):
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        config = self.get_config()
        config.to_disk(save_dir / "config.cfg")
        self.component.save(save_dir / "component")

    def load(self, save_dir: str):
        save_dir = Path(save_dir)
        config = Config().from_disk(save_dir / "config.cfg")
        pipe = registry.resolve(config)["pipe"]
        self.batch_size = pipe.batch_size
        self.batch_timeout = pipe.batch_timeout
        component_dir = save_dir / "component"
        component_config = Config().from_disk(component_dir / "config.cfg")
        component: BaseComponent = registry.resolve(component_config)["component"]
        self.component = component.load(component_dir)
        return self

    @property
    def name(self) -> str | None:
        if self.component is None:
            return None
        return self.component.name

    @property
    def input_tags(self) -> List[str]:
        if self.component is None:
            return []
        return self.component.input_tags

    @property
    def output_tags(self) -> List[str]:
        if self.component is None:
            return []
        return self.component.output_tags


@registry.pipelines.register("speech_pipeline")
class SpeechPipeline(IOMixin, BaseModel):
    """Audio Pipeline start with a loader component which can load the audio data from the disk or other sources.
    Args:
        loader (BaseComponent | Literal["v1", "v2"], optional): the loader component. Defaults to AudioLoaderV1.
        pipes (OrderedDict[str, Pipe] | None, optional): the components in the pipeline. Defaults to None.
        request_queue (AudioQueue | None, optional): the request queue. Defaults to None.
    """

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    pipes: OrderedDict[str, Pipe] | None = Field(
        default=None, description="the components in the pipeline"
    )
    request_queue: SpeechQueue | None = Field(
        default=None, description="the request queue"
    )
    remove_erhua: bool = Field(
        False, description="Remove erhua (儿化) in Mandarin Chinese"
    )
    enable_0_to_9: bool = Field(False, description="Enable 0 to 9 in Mandarin Chinese")
    normalizer: TextNormalizer | None = Field(
        None, description="the normalizer component"
    )

    @model_validator(mode="after")
    def validate_pipes(self):
        if self.pipes is None:
            self.pipes = OrderedDict()
        if self.request_queue is None:
            self.request_queue = SpeechQueue()
        if self.normalizer is None:
            self.normalizer = TextNormalizer(
                remove_erhua=self.remove_erhua,
                enable_0_to_9=self.enable_0_to_9,
            )
            self.normalizer.setup()
        return self

    @validate_call
    def __call__(
        self,
        input: str | Speech | Path,
        verbose: bool = False,
        clear: bool = False,
        timeout: float | None = None,
    ) -> Speech:
        return self.run(input, verbose=verbose, clear=clear, timeout=timeout)[0]

    @validate_call
    def run(
        self,
        input: str | Speech | List[str] | SpeechList,
        timeout: float | None = None,
        verbose: bool = False,
        clear: bool = False,
    ) -> SpeechList[Speech]:
        """Run the pipeline

        Args:
            input (str | Speech | List[str] | SpeechList): the input speech data.
            timeout (float | None, optional): the timeout of the response queue. Defaults to None.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            clear (bool, optional): whether to clear the audio data after processing. Defaults to False.

        Returns:
            SpeechList[Speech]: the processed Speech data
        """
        start = time.perf_counter()
        for _, pipe in self.pipes.items():
            pipe.verbose = verbose
        response_queue = Queue()
        speeches = self.normalizer._to_speeches(input=input)
        for speech in speeches:
            if speech.is_bad:
                response_queue.put(speech)
        speeches = run_component(component=self.normalizer, speeches=speeches)
        if len(self.pipes) == 0:
            for speech in speeches:
                response_queue.put(speech)
        else:
            for speech in speeches:
                self.request_queue.put((speech, response_queue))

        results = SpeechList()
        while True:
            if len(speeches) == len(results):
                break
            try:
                speech: Speech = response_queue.get(timeout=timeout)
                results.append(speech)
                response_queue.task_done()
            except Empty:
                logger.error("response queue timeout")
                for speech in speeches:
                    if not speech.is_bad:
                        speech.is_bad = True
                        speech.bad_reason = "response queue timeout"
                break
        end = time.perf_counter()
        spent = max(round(end - start, 2), 1e-5)
        logger.info(f"pipeline spent {spent} seconds")
        return speeches

    @validate_call
    def add_pipe(
        self,
        component: str | BaseComponent,
        batch_timeout: float = 0.01,
        batch_size: int | None = 1,
        queue_duration: int = 600,
        verbose: bool = False,
        **config,
    ) -> Self:
        """Add a component to the pipeline

        Args:
            component (str | BaseComponent): the component to add to the pipeline.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            batch_size (int | None, optional): dynamic batch size. Defaults to 1.
            queue_duration (int, optional): duration of the queue. Defaults to 600.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            **config: the parameters of the component.
        """
        if isinstance(component, str):
            if component == "normalizer":
                raise ValueError("normalizer component is reserved")
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = SpeechQueue(maxsize=queue_duration)
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
                input_queue=input_queue,
                verbose=verbose,
                **config,
            )
            pipe.start()
            self.pipes[pipe.name] = pipe
            return self
        elif isinstance(component, BaseComponent):
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = SpeechQueue(maxsize=queue_duration)
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
                input_queue=input_queue,
                verbose=verbose,
                **config,
            )
            pipe.start()
            self.pipes[component.name] = pipe
            return self

    @validate_call
    def get_pipe(self, name: str) -> Pipe | None:
        """Get a component from the pipeline

        Args:
            name (str): the name of the component registered in the registry.

        Returns:
            Pipe | None: the component object in the pipeline or None
        """
        return self.pipes.get(name, None)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def _init_pipe(
        self,
        component: str | BaseComponent,
        verbose: bool = False,
        is_last: bool = True,
        input_queue: SpeechQueue = None,
        output_queue: SpeechQueue = None,
        batch_timeout: float = 0.01,
        batch_size: int | None = None,
        **config,
    ) -> Pipe:
        """Initialize a component in the pipeline

        Args:
            component (str | BaseComponent): the component to add to the pipeline. It can be the name of the component registered in the registry or the component object.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            is_last (bool, optional): whether it is the last component. Defaults to True.
            input_queue (AudioQueue, optional): the input queue of the component. Defaults to None.
            output_queue (AudioQueue, optional): the output queue of the component. Defaults to None.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            batch_size (int | None, optional): dynamic batch size. Defaults to None.

        Returns:
            Pipe: the component object in the pipeline
        """
        if isinstance(component, str):
            _component: BaseComponent = registry.components.get(component)()
            _component = _component.setup(**config)
            pipe = Pipe(
                component=_component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
            )
            return pipe
        elif isinstance(component, BaseComponent):
            pipe = Pipe(
                component=component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
            )
            return pipe

    @validate_call
    def remove_pipe(self, name: str) -> Self:
        """Remove a component from the pipeline

        Args:
            name (str): the name of the component.

        Returns:
            Pipeline: the pipeline object
        """
        pipe: Pipe = self.pipes[name]
        if len(self.pipes) == 1:
            self._del_pipe(name)
            return self
        elif pipe.is_last:
            pre_pipe = self.pipes[self.pipe_names[-2]]
            pre_pipe.is_last = True
            pre_pipe.output_queue = None
            self._del_pipe(name)
            return self
        else:
            for i, pipe_name in enumerate(self.pipe_names):
                if pipe_name == name:
                    if i == 0:
                        next_pipe = self.pipes[self.pipe_names[i + 1]]
                        next_pipe.input_queue = self.request_queue
                        self._del_pipe(name)
                        return self
                    else:
                        pre_pipe = self.pipes[self.pipe_names[i - 1]]
                        next_pipe = self.pipes[self.pipe_names[i + 1]]
                        next_pipe.input_queue = pre_pipe.output_queue
                        self._del_pipe(name)
                        return self

    @validate_call
    def set_pipe(
        self,
        name: str,
        batch_size: int = 1,
        batch_timeout: float = 0.01,
        **config,
    ) -> Self:
        """Set the dynamic batch size and batch timeout of a component

        Args:
            name (str): the name of the pipe
            batch_size (int, optional): dynamic batch size. Defaults to 1.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            **config: the parameters of the component.

        Returns:
            Pipeline: the pipeline object
        """
        self.pipes[name].batch_size = batch_size
        self.pipes[name].batch_timeout = batch_timeout
        if config:
            for key, value in config.items():
                if hasattr(self.pipes[name].component, key):
                    setattr(self.pipes[name].component, key, value)
        return self

    def get_config(self) -> Config:
        """Get the configuration of the pipeline

        Returns:
            Config: the configuration of the pipeline
        """
        data = {
            "pipeline": {
                "@pipelines": "speech_pipeline",
                "remove_interjections": self.remove_interjections,
                "remove_erhua": self.remove_erhua,
                "traditional_to_simple": self.traditional_to_simple,
                "remove_puncts": self.remove_puncts,
                "full_to_half": self.full_to_half,
                "tag_oov": self.tag_oov,
                "pipes": {},
            }
        }
        for name, pipe in self.pipes.items():
            data["pipeline"]["pipes"][name] = pipe.get_config()["pipe"]
        config = Config(data=data)
        return config

    @validate_call
    def save(self, save_dir: str | Path) -> None:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            import shutil

            shutil.rmtree(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
        config = self.get_config()
        config.to_disk(save_dir / "config.cfg")
        try:
            for name, pipe in self.pipes.items():
                pipe.save(save_dir=save_dir / name)
        except Exception as e:
            import shutil

            shutil.rmtree(save_dir)
            raise e

    @validate_call
    def load(self, save_dir: str | Path) -> Self:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            raise FileNotFoundError(f"{save_dir} not found")
        config = Config().from_disk(save_dir / "config.cfg")
        pipeline = registry.resolve(config)["pipeline"]
        self.loader = pipeline.loader
        for name, pipe in pipeline.pipes.items():
            pipe: Pipe = pipe.load(save_dir / name)
            self.add_pipe(
                component=pipe.component,
                batch_timeout=pipe.batch_timeout,
                batch_size=pipe.batch_size,
            )
        return self

    @property
    def pipe_names(self) -> List[Pipe]:
        """Get the names of the components in the pipeline"""
        names = []
        for _, pipe in self.pipes.items():
            names.append(pipe.name)
        return names

    @property
    def pipe_registry_names(self) -> List[str]:
        """Get the names of the components in the pipeline from the registry

        Returns:
            List[str]: the names of the components in the pipeline
        """
        names = list(self.pipes.keys())
        return names

    def _del_pipe(self, name: str):
        """delete a component from the pipeline"""
        pipe: Pipe = self.pipes[name]
        pipe.stop_event.set()
        pipe.thread.join()
        del self.pipes[name]

    def __del__(self):
        """terminate all threads when delete the object"""
        for name in self.pipe_names:
            pipe = self.pipes[name]
            if pipe.stop_event is not None:
                pipe.stop_event.set()
            if pipe.thread is not None:
                pipe.thread.join()

    def __str__(self) -> str:
        s = "text -> normalizer -> "
        for name in self.pipe_names:
            s += f"{name} -> "
        return s + "speech"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.pipes)
