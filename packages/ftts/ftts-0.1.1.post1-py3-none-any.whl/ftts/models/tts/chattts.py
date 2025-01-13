import torch
from ChatTTS import Chat
from ftts.components.normalizer import Normalizer
from ftts.data import Speaker, Waveform
from .base import TTSModel
from pathlib import Path
from typing import List
from ftts.config import registry


@registry.tts_models.register("chattts")
class ChatTTS(TTSModel):
    checkpoint: str = "2Noise/ChatTTS"

    model: Chat | None = None
    normalizer: Normalizer = Normalizer()

    def synthesize_waveform(
        self, texts: List[str], speaker: Speaker, normalize: bool = False, **kwargs
    ) -> List[Waveform]:
        assert self.model is not None, "Model is not loaded"
        if normalize:
            texts = [self.normalizer.normalize(text) for text in texts]
        texts = [self.add_uv_break(text) for text in texts]
        speed = kwargs.get("speed", 3)
        skip_refine_text = kwargs.get("skip_refine_text", True)
        params_infer_code = self.model.InferCodeParams(
            prompt=f"[speed_{speed}]",
            spk_emb=speaker.id,
        )
        data = self.model.infer(
            text=texts,
            skip_refine_text=skip_refine_text,
            params_infer_code=params_infer_code,
        )
        waveforms = [
            Waveform(data=data[i], sample_rate=24000) for i in range(len(data))
        ]
        return waveforms

    def get_random_speaker(self) -> Speaker:
        assert self.model is not None, "Model is not loaded"
        random_spk_id = self.model.sample_random_speaker()
        return Speaker(id=random_spk_id)

    def add_uv_break(self, text: str) -> str:
        """add [uv_break] to prevent the last word from breaking the sound"""
        return f"{text}[uv_break][uv_break]"

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        compile: bool = False,
        **kwargs,
    ) -> "ChatTTS":
        self._load_model(
            checkpoint_dir=checkpoint_dir, device=device, compile=compile, **kwargs
        )
        return self

    def _load_model(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        compile: bool = False,
        **kwargs,
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
            **kwargs,
        )
