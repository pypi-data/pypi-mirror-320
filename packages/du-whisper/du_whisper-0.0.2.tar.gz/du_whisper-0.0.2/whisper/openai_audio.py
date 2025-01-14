# -*- coding: utf-8 -*-
# openai 相关操作
import io
import os
import math

import soundfile as sf
from openai import AsyncOpenAI

from loguru import logger

from schemas import OutData, InData


class AsyncOpenaiWhisper:
    """使用 OpenAI 的 Whisper API 进行音频转录。"""

    def __init__(self, sid, data: InData):
        self.sid = sid
        self.start = 0
        self.to = data.to
        self.audio_data = data.data
        self.client = AsyncOpenAI()  # 使用异步客户端
        self.model = "whisper-1"
        self.original_language = data.original
        self.response_format = "verbose_json"
        self.temperature = 0

    def write_audio_data(self) -> io.BytesIO:
        """将音频数据写入缓冲区"""
        buffer = io.BytesIO()
        buffer.name = f"{self.sid}.wav"
        sf.write(buffer, self.audio_data, samplerate=16000, format='WAV', subtype='PCM_16')
        buffer.seek(0)  # 将缓冲区的位置重置为开头
        self.start += math.ceil(len(self.audio_data) / 16000)  # 四舍五入到整秒
        return buffer

    async def transcribe(self) -> str:
        """使用 openai 转录"""
        buffer = self.write_audio_data()
        params = {
            "model": self.model,
            "file": buffer,
            "response_format": self.response_format,
            "temperature": self.temperature,
            # "timestamp_granularities": ["word", "segment"]
        }
        transcript = await self.client.audio.translations.create(**params)
        logger.debug(f"已处理 OpenAI 转录 {self.start} 秒")
        return transcript.text

    async def translate_text(self, text) -> str:
        """使用openai 翻译"""
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"You are a helpful assistant that translates text into {self.to}."},
                {"role": "user", "content": text},
                {"role": "assistant", "content": ""}
            ]
        )
        translation = response.choices[0].message.content.strip()
        return translation

    async def get_results(self) -> OutData:
        """获取结果"""
        text = await self.transcribe()
        if self.to and text:
            transl_text = await self.translate_text(text)
        else:
            transl_text = None
        return OutData(data=text, transl=transl_text, sid=self.sid)
