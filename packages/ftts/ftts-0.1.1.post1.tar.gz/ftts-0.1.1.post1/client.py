from websockets.asyncio.client import connect
import numpy as np
import asyncio
from pydantic import BaseModel
import sounddevice as sd
import soundfile as sf
import time
from loguru import logger
from typing import Literal
from pydub import AudioSegment
from io import BytesIO


class TTSRequest(BaseModel):
    text: str
    is_last: bool = False


async def send_text(websocket, text: str):
    for i, s in enumerate(text):
        is_last = i == len(text) - 1
        message = TTSRequest(text=s, is_last=is_last).model_dump_json()
        await websocket.send(message=message)
        logger.info(f"sent: {message}")
        global start
        start = time.perf_counter()
        await asyncio.sleep(0.01)


async def receive_speech(websocket, format: Literal["wav", "pcm", "mp3"] = "pcm"):
    print("format", format)
    stream = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
    speech = []
    with stream:
        first_spent = None
        while True:
            try:
                data = await websocket.recv()
                if not first_spent:
                    first_spent = time.perf_counter() - start
                    logger.info(
                        f"first spent: {first_spent}, received length: {len(data)}"
                    )
                else:
                    spent = time.perf_counter() - start
                    logger.info(
                        f"response spent: {spent}, received length: {len(data)}"
                    )
                if format == "pcm":
                    waveform = np.frombuffer(data, dtype=np.int16)
                    stream.write(waveform)
                    speech.append(waveform)
                elif format == "wav":
                    waveform = np.frombuffer(data, dtype=np.int16)
                    stream.write(waveform)
                    speech.append(waveform)
                elif format == "mp3":
                    # Decode the chunk to 16-bit PCM
                    audio = AudioSegment.from_mp3(BytesIO(data))
                    waveform = np.array(
                        audio.get_array_of_samples(), dtype=np.int16
                    )
                    stream.write(waveform)
                    speech.append(waveform)

            except Exception:
                logger.info("response finished, save to output.wav")
                sf.write("output.wav", np.concatenate(speech), 24000)
                break


async def main():
    speed = "5"  # 语速 0 - 9
    refineText = "0"  # 是否口语化 0 或者 1
    speaker = "female"  # 男 或者 女
    format = "mp3"  # 输出格式
    # url = "ws://lbggateway.58corp.com/tts/realtime"
    url = "ws://localhost:27000/tts/realtime"
    url += "?speed=" + speed
    url += "&refine_text=" + refineText
    url += "&speaker=" + speaker
    url += "&format=" + format
    logger.info(f"connecting to {url}")
    async with connect(url) as websocket:
        text = "中央空调等2:回收空调品牌大金空调、格力空调、美的空调、海尔空调、志高空调、三洋空调、华宝空调、华凌空调、春兰空调、日立空调、LG空调、TCL空调、飞歌空调等等多种品牌空调。"
        text = "你好，我的电话是123456789，体重是75kg，身高是180cm，体脂率是20%。家用电器：回收电视机、回收电冰箱、回收洗衣机、回收空调"
        tasks = [send_text(websocket, text), receive_speech(websocket, format)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
