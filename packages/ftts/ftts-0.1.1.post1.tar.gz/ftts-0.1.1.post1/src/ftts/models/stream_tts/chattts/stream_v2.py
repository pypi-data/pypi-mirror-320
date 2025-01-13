from ChatTTS import model
from ftts.components.normalizer import Normalizer
from ftts.data import Speaker, StreamWaveform
from ftts.layers.dvae import StreamingDVAE
from ftts.models.stream_tts.base import StreamTTSModel
from ftts.models.stream_tts.chattts.gpt import StreamGPT
from typing import Optional
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


class Embed(model.Embed):
    def __init__(
        self,
        hidden_size,
        num_audio_tokens,
        num_text_tokens,
        num_vq,
        model_path,
        device="cpu",
    ):
        super().__init__(hidden_size, num_audio_tokens, num_text_tokens, num_vq)
        self.load_pretrained(model_path, device=device)


@registry.stream_tts_models.register("stream_chattts_v2")
class StreamChatTTSV2(StreamTTSModel):
    checkpoint: str = "Ddream-ai/ChatTTS-streaming"
    endpoint: str = "hf-mirror"

    gpt: StreamGPT | None = None
    sdvae: StreamingDVAE | None = None
    normalizer: Normalizer = Normalizer()

    def synthesize_waveform_stream(
        self,
        text: str,
        speaker: Speaker | None = None,
        speed: int = 4,
        normalize: bool = False,
        **kwargs,
    ):
        if normalize:
            text = self.normalizer.normalize(text)
        text = text.replace(":", "").replace(
            "：", ""
        )  # chattts will not generate suitable audio for these characters
        skip_refine_text = kwargs.get("skip_refine_text", True)
        if not skip_refine_text:
            oral = kwargs.get("oral", 7)
            laugh = kwargs.get("laugh", 0)
            stop = kwargs.get("stop", 6)
            params_refine_text = RefineTextParams(
                prompt=f"[oral_{oral}][laugh_{laugh}][break_{stop}]"
            )
            text = self.refine_text(text, params_refine_text)
            logger.info("Refined text: {}", text)
        else:
            text += "[uv_break]"  # prevent the last word from breaking the sound
        stream = self.generate(
            text, speaker_id=speaker.id if speaker else None, speed=speed
        )
        return StreamWaveform(stream=stream, sample_rate=24000)

    def generate(self, text: str, speaker_id: str | None = None, speed: int = 4):
        assert self.gpt is not None, "Model is not loaded"
        assert self.sdvae is not None, "Model is not loaded"
        for tokens in self.gpt.generate(text, speed=speed, spk_emb=speaker_id):
            for audio in self.sdvae.streaming_decode(tokens):
                yield audio
        yield self.sdvae.decode_caches()

    def refine_text(self, text: str, params: RefineTextParams) -> str:
        assert self.gpt is not None, "Model is not loaded"
        return self.gpt.refine_text(text, params)

    def get_random_speaker(self):
        speaker_id = self.gpt.speaker.sample_random()
        return Speaker(id=speaker_id)

    def reset(self):
        pass

    def from_checkpoint(
        self,
        checkpoint_dir: str | None = None,
        device: str = "cpu",
        compile: bool = False,
        use_vllm: bool = False,
        gpu_memory_utilization: float = 0.5,
        **kwargs,
    ):
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()

        self.gpt = StreamGPT(
            {
                "hidden_size": 768,
                "intermediate_size": 3072,
                "num_attention_heads": 12,
                "num_hidden_layers": 20,
                "use_cache": False,
                "max_position_embeddings": 4096,
                "spk_emb_dim": 192,
                "spk_KL": False,
                "num_audio_tokens": 626,
                "num_text_tokens": 21178,
                "num_vq": 4,
            },
            f"{str(checkpoint_dir)}/Embed.safetensors",
            f"{str(checkpoint_dir)}/gpt",
            f"{str(checkpoint_dir)}/tokenizer",
            device=device,
            compile=compile,
            use_vllm=use_vllm,
            gpu_memory_utilization=gpu_memory_utilization,
        )

        self.sdvae = StreamingDVAE(
            device=device, checkpoint_dir=f"{str(checkpoint_dir)}/dvae"
        )
        return self
