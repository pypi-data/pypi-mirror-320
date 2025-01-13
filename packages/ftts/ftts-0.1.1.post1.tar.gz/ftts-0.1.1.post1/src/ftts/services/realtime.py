from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ftts import SpeechPipeline
from ftts.data import Speech, Speaker
from ftts.preprocessors import StreamSentenceSplitter
from typing import Literal
from loguru import logger
import uvicorn
import traceback
from pydantic import BaseModel, Field
import time
from urllib.parse import parse_qs
from pathlib import Path
import torch
import numpy as np
from io import BytesIO
from pydub import AudioSegment
import lameenc
from torchaudio.io import StreamWriter


class TextChunk(BaseModel):
    text: str
    is_last: bool = False


class InferParams(BaseModel):
    refine_text: bool = False
    speaker: Speaker | None = None
    speed: int = Field(5, ge=1, le=9)


class Waveform(BaseModel):
    data: str
    sample_rate: int = 24000


class SpeechChunk(BaseModel):
    waveform: Waveform | None = None
    speaker: str | None = None


class TTSResponse(BaseModel):
    code: Literal[0, -1] = 0
    msg: str = "success"
    data: SpeechChunk | None = None
    is_last: bool = False


def serve_realtime_chattts(
    host: str = "0.0.0.0",
    port: int = 27000,
    model: str = "stream_chattts_v2",
    checkpoint_dir: str | None = None,
    compile: bool = False,
    device: Literal["cuda", "cpu"] | None = None,
    use_vllm: bool = False,
    gpu_memory_utilization: float = 0.5,
    debug: bool = False,
):
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Starting server at {host}:{port}")
    if checkpoint_dir:
        logger.info(f"Loading model from {checkpoint_dir}")
    chattts = SpeechPipeline().add_pipe(
        "stream_synthesiser",
        checkpoint_dir=checkpoint_dir,
        compile=compile,
        device=device,
        model=model,
        use_vllm=use_vllm,
        gpu_memory_utilization=gpu_memory_utilization,
    )
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    default_male_speaker_file = (
        Path(__file__).parent.parent / "asset" / "speakers" / "male.json"
    )
    default_male_speaker = Speaker().load_json(default_male_speaker_file)
    default_female_speaker_file = (
        Path(__file__).parent.parent / "asset" / "speakers" / "female.json"
    )
    default_female_speaker = Speaker().load_json(default_female_speaker_file)

    @app.websocket("/tts/realtime")
    async def stream_chattts(websocket: WebSocket):
        await websocket.accept()
        logger.info("Connection established")

        query_params = parse_qs(websocket.scope["query_string"].decode("utf-8"))

        audio_format = query_params.get("format", ["pcm"])[0]
        if audio_format not in ["pcm", "mp3", "wav"]:
            await websocket.send_json(
                TTSResponse(
                    code=-1, msg=f"Unsupported audio format: {audio_format}"
                ).model_dump()
            )
            await websocket.close()
            return

        speaker_type = query_params.get("speaker", ["male"])[0]
        if speaker_type == "male":
            speaker = default_male_speaker
        else:
            speaker = default_female_speaker
        speed = query_params.get("speed", [5])[0]
        refine_text = query_params.get("refine_text", [False])[0]
        try:
            infer_params = InferParams(
                refine_text=refine_text,
                speaker=speaker,
                speed=speed,
            )
        except Exception as e:
            logger.error(f"Invalid request: {e}")
            await websocket.send_json(
                TTSResponse(code=-1, msg=f"Invalid request: {e}").model_dump()
            )
            await websocket.close()
            return

        chattts.set_pipe("stream_synthesiser", **infer_params.model_dump())
        logger.info(f"Received request: {infer_params}")

        is_last_chunk = False
        stream_sentence_splitter = StreamSentenceSplitter()
        first_response_time = None
        i = 0
        try:
            while not is_last_chunk:
                data = await websocket.receive_json()
                try:
                    text_chunk = TextChunk(**data)
                except KeyError as e:
                    logger.error(f"Missing key in data: {e}")
                    await websocket.send_json(
                        TTSResponse(
                            code=-1, msg=f"Missing key in data: {e}"
                        ).model_dump()
                    )
                    continue
                except Exception as e:
                    logger.error(f"Invalid data format: {e}")
                    await websocket.send_json(
                        TTSResponse(
                            code=-1, msg=f"Invalid data format: {e}"
                        ).model_dump()
                    )
                    continue
                is_last_chunk = text_chunk.is_last
                sentences = stream_sentence_splitter.process_text(
                    text=text_chunk.text, is_last=text_chunk.is_last
                )
                if len(sentences) > 0:
                    for sentence in sentences:
                        start = time.perf_counter()
                        logger.info(f"synthesizing: {sentence}")
                        speech: Speech = chattts(sentence)
                        if audio_format == "mp3":
                            encoder = lameenc.Encoder()
                            encoder.set_bit_rate(64)
                            encoder.set_in_sample_rate(24000)
                            encoder.set_channels(1)
                            encoder.set_quality(7)
                        for data in speech.stream():
                            if not first_response_time:
                                first_response_time = round(
                                    time.perf_counter() - start, 3
                                )
                                logger.info(
                                    f"first response delay: {first_response_time} seconds"
                                )
                            data = np.clip(data, -1, 1)
                            int16_data = (data * 32767).astype(np.int16).tobytes()
                            if audio_format == "pcm":
                                await websocket.send_bytes(int16_data)
                                logger.info(f"sent {len(int16_data)} bytes")
                            elif audio_format == "wav":
                                audio = AudioSegment(
                                    int16_data,
                                    sample_width=2,
                                    frame_rate=24000,
                                    channels=1,
                                )
                                if debug:
                                    audio.export(f"{i}.wav", format="wav")
                                    i += 1
                                wav_io = BytesIO()
                                audio.export(wav_io, format="wav")
                                wav_io.seek(0)
                                await websocket.send_bytes(wav_io.read())
                                logger.info(f"sent {len(int16_data)} bytes")
                            elif audio_format == "mp3":
                                mp3_chunk = encoder.encode(int16_data)
                                if mp3_chunk:
                                    await websocket.send_bytes(mp3_chunk)
                                    logger.info(f"sent {len(mp3_chunk)} bytes")
                        if audio_format == "mp3":
                            mp3_chunk = encoder.flush()
                            if mp3_chunk:
                                await websocket.send_bytes(mp3_chunk)
                        end = time.perf_counter()
                        synthesis_time = round(end - start, 2)
                        logger.info(
                            f"synthesized {speech.duration} seconds speech in {synthesis_time} seconds"
                        )
            logger.info("All text received and synthesized")

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(
                f"Unexpected error: {e}\nCall stack:\n{traceback.format_exc()}"
            )
            await websocket.close()
        finally:
            await websocket.close()

    async def synthesise_mp3_stream(text: str, chattts: SpeechPipeline) -> BytesIO:
        speech = chattts(text)
        buffer = BytesIO()
        s = StreamWriter(dst=buffer)
        s.add_audio_stream(sample_rate=24000, num_channels=1, encoder="libmp3lame", encoder_format="s16p")
        with s.open():
            for data in speech.stream():
                int16_tensor = torch.from_numpy((data * 32767).astype(np.int16))
                s.write_audio_chunk(int16_tensor)
        return buffer
        



    uvicorn.run(app, host=host, port=port, ws_max_queue=1)
