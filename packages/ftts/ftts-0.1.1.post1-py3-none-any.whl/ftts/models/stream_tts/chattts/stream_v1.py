import torch
from ftts.data import Speaker, Waveform, StreamWaveform
from ftts.models.stream_tts.base import StreamTTSModel
from ftts.models.stream_tts.chattts.chat import Chat
from pathlib import Path
from typing import List, Optional
from typing_extensions import Self
from ftts.config import registry
from dataclasses import dataclass
from loguru import logger


@dataclass(repr=False, eq=False)
class RefineTextParams:
    prompt: str = ""
    top_P: float = 0.7
    top_K: int = 20
    temperature: float = 0.7
    repetition_penalty: float = 1.0
    max_new_token: int = 384
    min_new_token: int = 0
    show_tqdm: bool = True
    ensure_non_empty: bool = True
    manual_seed: Optional[int] = None


@dataclass(repr=False, eq=False)
class InferCodeParams(RefineTextParams):
    prompt: str = "[speed_5]"
    spk_emb: Optional[str] = None
    spk_smp: Optional[str] = None
    txt_smp: Optional[str] = None
    temperature: float = 0.3
    repetition_penalty: float = 1.05
    max_new_token: int = 2048
    stream_batch: int = 24
    stream_speed: int = 12000
    pass_first_n_batches: int = 2


@registry.stream_tts_models.register("stream_chattts_v1")
class StreamChatTTSV1(StreamTTSModel):
    checkpoint: str = "2Noise/ChatTTS"

    model: Chat | None = None

    def synthesize_waveform_stream(
        self, text: str, speaker: Speaker | None = None, **kwargs
    ) -> List[Waveform]:
        assert self.model is not None, "Model is not loaded"
        skip_refine_text = kwargs.get("skip_refine_text", True)
        if not skip_refine_text:
            oral = kwargs.get("oral", 7)
            laugh = kwargs.get("laugh", 0)
            stop = kwargs.get("stop", 0)
            params_refine_text = RefineTextParams(
                prompt=f"[oral_{oral}][laugh_{laugh}][break_{stop}]"
            )
            text = self.refine_text(text, params_refine_text)
            text = text.replace("[Ebreak]", "")
            logger.info("Refined text:", text)
        else:
            if not skip_refine_text and "break" not in text:
                text += "[uv_break]"  # prevent the last word from breaking the sound
            else:
                text += "[uv_break]"

        speed = kwargs.get("speed", 5)
        if speaker is None:
            speaker = self.get_random_speaker()
        params_infer_code = InferCodeParams(
            prompt=f"[speed_{speed}]",
            spk_emb=speaker.id,
        )
        data = self.model.infer(
            text=text,
            skip_refine_text=True,
            params_infer_code=params_infer_code,
            stream=True,
        )
        waveform = StreamWaveform(stream=data, sample_rate=24000)
        return waveform

    def refine_text(self, text: str, params: RefineTextParams) -> str:
        return self.model.infer(
            text=text, refine_text_only=True, params_refine_text=params
        )[0]

    def get_random_speaker(self) -> Speaker:
        assert self.model is not None, "Model is not loaded"
        random_spk_id = self.model.sample_random_speaker()
        return Speaker(id=random_spk_id)

    def reset(self):
        pass

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        compile: bool = False,
        use_vllm: bool = False,
        gpu_memory_utilization: float = 0.5,
        **kwargs,
    ) -> Self:
        self._load_model(
            checkpoint_dir=checkpoint_dir,
            device=device,
            compile=compile,
            use_vllm=use_vllm,
            gpu_memory_utilization=gpu_memory_utilization,
        )
        return self

    def _load_model(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        compile: bool = False,
        use_vllm: bool = False,
        gpu_memory_utilization: float = 0.5,
    ) -> None:
        if not checkpoint_dir:
            checkpoint_dir = self.checkpoint_dir / "asset"
            self.download_checkpoint()
        else:
            checkpoint_dir = Path(checkpoint_dir)
            if not checkpoint_dir.exists():
                raise FileNotFoundError(
                    f"Checkpoint directory {checkpoint_dir} does not exist"
                )
        self.model = Chat()
        vocos_ckpt_path = checkpoint_dir / "Vocos.safetensors"
        dvae_ckpt_path = checkpoint_dir / "DVAE.safetensors"
        gpt_ckpt_path = checkpoint_dir / "gpt"
        embed_path = checkpoint_dir / "Embed.safetensors"
        decoker_path = checkpoint_dir / "Decoder.safetensors"
        tokenizer_path = checkpoint_dir / "tokenizer"
        if device is None:
            device = "cpu" if not torch.cuda.is_available() else "cuda"
        self.model._load(
            vocos_ckpt_path=vocos_ckpt_path,
            dvae_ckpt_path=dvae_ckpt_path,
            gpt_ckpt_path=gpt_ckpt_path,
            decoder_ckpt_path=decoker_path,
            embed_path=embed_path,
            tokenizer_path=tokenizer_path,
            device=device,
            compile=compile,
            use_vllm=use_vllm,
            gpu_memory_utilization=gpu_memory_utilization,
        )
