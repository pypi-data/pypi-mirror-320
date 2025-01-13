import torch.nn as nn
from typing import Optional
import torch
from ftts.layers.gfsq import GFSQ
from ftts.layers.feature_extractor import MelSpectrogramFeatures
import math
import yaml
import vocos
from vocos.feature_extractors import EncodecFeatures
from vocos.pretrained import instantiate_class
from pathlib import Path


vocos_models = {}


class Vocos(vocos.Vocos):
    def __init__(self, checkpoint_dir: str, name: str = "mel", device: str = "cpu"):
        self.name = name
        self.device = device
        assert name in ["encodec", "mel"]
        key = f"{name}-{device}"
        if key not in vocos_models:
            model = self.from_checkpoint(checkpoint_dir)
            vocos_models[key] = model.to(device)
        model = vocos_models[key]
        super().__init__(model.feature_extractor, model.backbone, model.head)
        if name == "encodec":
            self.feature_extractor.encodec.eval()
            self.bandwidths = self.feature_extractor.bandwidths
        self.feature_dim = self.backbone.input_channels
        # encodec: T => T * upsample_rate
        # mel: T => (T - 1) * upsample_rate
        self.upsample_rate = self.head.istft.hop_length

    def get_encodec_codes(self, audio: torch.Tensor, bandwidth_id: int = -1):
        assert self.name == "encodec"
        bandwidth = self.bandwidths[bandwidth_id]
        self.feature_extractor.encodec.set_target_bandwidth(bandwidth)
        return self.feature_extractor.get_encodec_codes(audio)

    def extra_features(self, audio: torch.Tensor, bandwidth_id: int = -1):
        if self.name == "encodec":
            codes = self.get_encodec_codes(audio, bandwidth_id)
            return self.codes_to_features(codes)
        return self.feature_extractor(audio)

    def decode(self, features: torch.Tensor, bandwidth_id: int = -1):
        if self.name == "encodec":
            if bandwidth_id < 0:
                bandwidth_id += len(self.bandwidths)
            assert 0 <= bandwidth_id < len(self.bandwidths)
            bandwidth_id = torch.tensor([bandwidth_id]).to(self.device)
            return super().decode(features, bandwidth_id=bandwidth_id)
        return super().decode(features)

    def decode_codes(self, codes: torch.Tensor, bandwidth_id: int = -1):
        assert self.name == "encodec"
        features = self.codes_to_features(codes)
        return self.decode(features, bandwidth_id)

    def from_checkpoint(self, checkpoint_dir: str | Path, **kwargs):
        checkpoint_dir = Path(checkpoint_dir)
        config_path = checkpoint_dir / "config.yaml"
        model_path = checkpoint_dir / "pytorch_model.bin"
        model = self.init_model(config_path)
        state_dict = torch.load(model_path, map_location="cpu", weights_only=True)
        if isinstance(model.feature_extractor, EncodecFeatures):
            encodec_parameters = {
                "feature_extractor.encodec." + key: value
                for key, value in model.feature_extractor.encodec.state_dict().items()
            }
            state_dict.update(encodec_parameters)
        model.load_state_dict(state_dict)
        model.eval()
        return model

    def init_model(self, config_path: str) -> "Vocos":
        """
        Class method to create a new Vocos model instance from hyperparameters stored in a yaml configuration file.
        """
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        feature_extractor = instantiate_class(args=(), init=config["feature_extractor"])
        backbone = instantiate_class(args=(), init=config["backbone"])
        head = instantiate_class(args=(), init=config["head"])
        model = vocos.Vocos(
            feature_extractor=feature_extractor, backbone=backbone, head=head
        )
        return model


class StreamingVocos(Vocos):
    def __init__(
        self,
        checkpoint_dir: str | Path,
        name: str = "mel",
        device: str = "cpu",
        bandwidth_id: int = -1,
        chunk_size_ms: int = 300,
        padding_ms: int = None,
    ):
        super().__init__(name=name, device=device, checkpoint_dir=checkpoint_dir)
        self.device = device
        self.bandwidth_id = bandwidth_id
        self.chunk_size = int(chunk_size_ms / 1000 * 24000 / self.upsample_rate)
        # 8 * 3 * self.upsample_rate / 24000 * 1000
        padding_ms = padding_ms or self.upsample_rate
        self.padding = int(padding_ms / 1000 * 24000 / self.upsample_rate)

        self.cur_idx = -1
        self.caches_shape = (1, self.feature_dim, self.chunk_size + 2 * self.padding)
        self.caches = torch.zeros(self.caches_shape).to(self.device)

    def reset(self):
        self.cur_idx = -1
        self.caches = torch.zeros(self.caches_shape).to(self.device)

    def get_size(self):
        """
        Method to get the length of unprocessed codes or features.
        """
        effective_size = self.cur_idx + 1 - self.padding
        if effective_size <= 0:
            return 0
        return effective_size % self.chunk_size or self.chunk_size

    def decode_caches(self):
        cur_size = self.get_size()
        if cur_size == 0:
            return torch.empty(1, 0).to(self.device)
        audio = self.decode(self.caches, self.bandwidth_id)
        audio = audio[:, self.padding * self.upsample_rate :]
        audio = audio[:, (self.chunk_size - cur_size) * self.upsample_rate :]
        self.reset()
        return audio

    def streaming_decode(self, features: torch.Tensor, is_last: bool = False):
        """
        Method to streaming decode audio waveform from already calculated features.
        The features is passed through the backbone and the head to reconstruct the audio output.

        Args:
            features (Tensor): The input tensor of features of shape (B, C, L), where B is the batch size,
                               C denotes the feature dimension, and L is the sequence length.
            is_last (bool): Whether the input features is the last frame.

        Returns:
            Tensor: The output tensor representing the reconstructed audio waveform of shape (B, T).
        """
        for idx, feature in enumerate(torch.unbind(features, dim=2)):
            self.caches = torch.roll(self.caches, shifts=-1, dims=2)
            self.caches[:, :, -1] = feature
            self.cur_idx += 1
            is_last_feature = is_last and idx == features.shape[2] - 1
            cur_size = self.get_size()
            if cur_size != self.chunk_size and not is_last_feature:
                continue
            audio = self.decode(self.caches, self.bandwidth_id)
            audio = audio[:, self.padding * self.upsample_rate :]
            if cur_size != self.chunk_size:
                audio = audio[:, (self.chunk_size - cur_size) * self.upsample_rate :]
            if not is_last_feature:
                audio = audio[:, : self.chunk_size * self.upsample_rate]
            else:
                self.reset()
            yield audio

    def streaming_decode_codes(self, codes: torch.Tensor, is_last: bool = False):
        assert self.name == "encodec"
        features = self.codes_to_features(codes)
        for audio in self.streaming_decode(features, is_last=is_last):
            yield audio

    def test_streaming_decode(self, wav_path: str):
        import torchaudio

        audio, sr = torchaudio.load(wav_path)
        if audio.size(0) > 1:
            audio = audio.mean(dim=0, keepdim=True)
        audio = audio.to(self.device)
        audio = torchaudio.functional.resample(audio, orig_freq=sr, new_freq=24000)

        audio_hat = []
        if self.name == "encodec":
            codes = self.get_encodec_codes(audio)
            audio = self.decode_codes(codes)
            for code in torch.unbind(codes, dim=2):
                audio_hat += self.streaming_decode_codes(code[:, :, None])
        else:
            features = self.feature_extractor(audio)
            audio = self.decode(features)
            for feature in torch.unbind(features, dim=2):
                audio_hat += self.streaming_decode(feature[:, :, None])
        audio_hat.append(self.decode_caches())
        audio_hat = torch.cat(audio_hat, dim=1)
        similarity = torch.cosine_similarity(audio, audio_hat).mean()
        print(audio.shape[1], audio_hat.shape[1], similarity)


class ConvNeXtBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        intermediate_dim: int,
        kernel: int,
        dilation: int,
        layer_scale_init_value: float = 1e-6,
    ):
        # ConvNeXt Block copied from Vocos.
        super().__init__()
        self.dwconv = nn.Conv1d(
            dim,
            dim,
            kernel_size=kernel,
            padding=dilation * (kernel // 2),
            dilation=dilation,
            groups=dim,
        )  # depthwise conv
        self.norm = nn.LayerNorm(dim, eps=1e-6)
        self.pwconv1 = nn.Linear(
            dim, intermediate_dim
        )  # pointwise/1x1 convs, implemented with linear layers
        self.act = nn.GELU()
        self.pwconv2 = nn.Linear(intermediate_dim, dim)
        self.gamma = nn.Parameter(
            layer_scale_init_value * torch.ones(dim), requires_grad=True
        )

    def forward(self, x: torch.Tensor, cond=None) -> torch.Tensor:
        residual = x
        y = self.dwconv(x)
        y.transpose_(1, 2)  # (B, C, T) -> (B, T, C)
        x = self.norm(y)
        y = self.pwconv1(x)
        x = self.act(y)
        y = self.pwconv2(x)
        if self.gamma is not None:
            y *= self.gamma
        y.transpose_(1, 2)  # (B, T, C) -> (B, C, T)
        x = y + residual
        return x


class DVAEDecoder(nn.Module):
    def __init__(
        self,
        idim: int,
        odim: int,
        n_layer=12,
        bn_dim=64,
        hidden=256,
        kernel=7,
        dilation=2,
        up=False,
    ):
        # DVAEDecoder Block modified from ChatTTS.
        super().__init__()
        self.up = up
        self.conv_in = nn.Sequential(
            nn.Conv1d(idim, bn_dim, 3, 1, 1),
            nn.GELU(),
            nn.Conv1d(bn_dim, hidden, 3, 1, 1),
        )
        self.decoder_block = nn.ModuleList(
            [
                ConvNeXtBlock(hidden, hidden * 4, kernel, dilation)
                for _ in range(n_layer)
            ]
        )
        self.conv_out = nn.Conv1d(hidden, odim, kernel_size=1, bias=False)

    def forward(self, x: torch.Tensor, conditioning=None) -> torch.Tensor:
        # B, C, T
        y = self.conv_in(x)
        for f in self.decoder_block:
            y = f(y, conditioning)
        x = self.conv_out(y)
        return x


class DVAE(nn.Module):
    def __init__(
        self,
        decoder_config: dict,
        encoder_config: Optional[dict] = None,
        vq_config: Optional[dict] = None,
        dim=512,
    ):
        # DVAE Block modified from ChatTTS.
        super().__init__()
        coef = torch.rand(100)
        self.register_buffer("coef", coef.unsqueeze(0).unsqueeze_(2))

        # encoder
        self.downsample_conv = nn.Sequential(
            nn.Conv1d(100, dim, 3, 1, 1),
            nn.GELU(),
            nn.Conv1d(dim, dim, 4, 2, 1),
            nn.GELU(),
        )
        self.preprocessor_mel = MelSpectrogramFeatures()
        self.encoder: Optional[DVAEDecoder] = DVAEDecoder(**encoder_config)

        # decoder
        self.decoder = DVAEDecoder(**decoder_config)
        self.out_conv = nn.Conv1d(dim, 100, 3, 1, 1, bias=False)
        self.vq_layer = GFSQ(**vq_config)

    def forward(self, inp: torch.Tensor, mode: str = "decode") -> torch.Tensor:
        assert mode in ["encode", "decode"]
        if mode == "encode":
            mel = self.preprocessor_mel(inp) / self.coef.view(100, 1)
            x = self.downsample_conv(mel).unsqueeze_(0)
            x = self.encoder(x)
            ind = self.vq_layer(x)
            return ind

        vq_feats = self.vq_layer._embed(inp)
        vq_feats = (
            vq_feats.view(
                (vq_feats.size(0), 2, vq_feats.size(1) // 2, vq_feats.size(2))
            )
            .permute(0, 2, 3, 1)
            .flatten(2)
        )
        return self.out_conv(self.decoder(x=vq_feats)) * self.coef


dvae_models = {}


class StreamingDVAE:
    def __init__(
        self,
        checkpoint_dir: str,
        device: str = "cpu",
        chunk_size_ms: int = None,
        padding_ms: int = 40,
        vocos_chunk_size_ms: int = 300,
        vocos_padding_ms: int = None,
    ):
        self.device = device
        key = f"{checkpoint_dir}-{device}"
        if key not in dvae_models:
            config = yaml.safe_load(open(f"{checkpoint_dir}/config.yaml"))
            weights_path = f"{checkpoint_dir}/pytorch_model.bin"
            weights = torch.load(weights_path, weights_only=True, mmap=True)
            model = DVAE(config["decoder"], config["encoder"], config["vq"])
            model.load_state_dict(weights)
            dvae_models[key] = (model.to(device), len(config["vq"]["levels"]))
        self.dvae, self.num_quantizers = dvae_models[key]

        self.vocos = StreamingVocos(
            checkpoint_dir=f"{checkpoint_dir}/vocos-mel-24k",
            device=self.device,
            chunk_size_ms=vocos_chunk_size_ms,
            padding_ms=vocos_padding_ms,
        )
        if chunk_size_ms is None:
            chunk_size = self.vocos.chunk_size + self.vocos.padding
        else:
            chunk_size = chunk_size_ms / 10
        self.chunk_size = int(math.ceil(chunk_size / 2))
        self.padding = int(padding_ms / 10 / 2)

        self.cur_idx = -1
        self.caches_shape = (1, self.num_quantizers, self.chunk_size + 2 * self.padding)
        self.caches = torch.zeros(self.caches_shape, dtype=torch.long).to(self.device)

    def reset(self):
        self.cur_idx = -1
        self.caches = torch.zeros(self.caches_shape, dtype=torch.long).to(self.device)

    def extract_features(self, audio: torch.Tensor):
        return self.vocos.feature_extractor(audio)

    def encode(self, audio: torch.Tensor):
        return self.dvae(audio, mode="encode")

    def decode(self, codes: torch.Tensor, to_mel: bool = False):
        mel = self.dvae(codes, mode="decode")
        return mel if to_mel else self.vocos.decode(mel)

    def get_size(self):
        """
        Method to get the length of unprocessed codes or features.
        """
        effective_size = self.cur_idx + 1 - self.padding
        if effective_size <= 0:
            return 0
        return effective_size % self.chunk_size or self.chunk_size

    def decode_caches(self, to_mel: bool = False):
        cur_size = self.get_size()
        if cur_size == 0:
            if to_mel:
                return torch.empty(1, self.num_quantizers, 0).to(self.device)
            return self.vocos.decode_caches()
        mel = self.decode(self.caches, to_mel=True)
        mel = mel[:, :, self.padding * 2 :]
        mel = mel[:, :, (self.chunk_size - cur_size) * 2 :]
        self.reset()
        if to_mel:
            return mel
        audios = list(self.vocos.streaming_decode(mel, is_last=True))
        return torch.cat(audios, dim=1)

    def streaming_decode(self, codes: torch.Tensor, to_mel=False, is_last=False):
        for idx, code in enumerate(torch.unbind(codes, dim=2)):
            self.caches = torch.roll(self.caches, shifts=-1, dims=2)
            self.caches[:, :, -1] = code
            self.cur_idx += 1
            is_last_code = is_last and idx == codes.shape[2] - 1
            cur_size = self.get_size()
            if cur_size != self.chunk_size and not is_last_code:
                continue
            mel = self.decode(self.caches, to_mel=True)
            mel = mel[:, :, self.padding * 2 :]
            if cur_size != self.chunk_size:
                mel = mel[:, :, (self.chunk_size - cur_size) * 2 :]
            if not is_last_code:
                mel = mel[:, :, : self.chunk_size * 2]
            else:
                self.reset()
            if to_mel:
                yield mel
            else:
                for audio in self.vocos.streaming_decode(mel, is_last):
                    yield audio

    def test_streaming_decode(self, wav_path: str):
        import torchaudio

        audio, sr = torchaudio.load(wav_path)
        if audio.size(0) > 1:
            audio = audio.mean(dim=0, keepdim=True)
        audio = audio.to(self.device)
        audio = torchaudio.functional.resample(audio, orig_freq=sr, new_freq=24000)
        mel = self.extract_features(audio)
        codes = self.encode(audio[0])

        mel_hat = []
        for code in torch.unbind(codes, dim=2):
            mel_hat += self.streaming_decode(code[:, :, None], to_mel=True)
        mel_hat.append(self.decode_caches(to_mel=True))
        mel_hat = torch.cat(mel_hat, dim=2)
        t = min(mel.shape[2], mel_hat.shape[2])
        similarity = torch.cosine_similarity(mel[:, :, :t], mel_hat).mean()
        print(mel.shape[2], mel_hat.shape[2], similarity)
