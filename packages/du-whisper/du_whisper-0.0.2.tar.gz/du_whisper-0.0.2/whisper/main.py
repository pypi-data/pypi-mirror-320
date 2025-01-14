# -*- coding: utf-8 -*-
# 项目入口
import os
import argparse

import socketio
from loguru import logger
parser = argparse.ArgumentParser()

parser.add_argument("--host", type=str, default='0.0.0.0')
parser.add_argument("--port", type=int, default=43007)
parser.add_argument("--openai", type=str, default='')

args = parser.parse_args()
if args.openai:
    # 启动程序时传入 openai api key
    os.environ["OPENAI_API_KEY"] = args.openai
else:
    # 手动设置 openai api key
    os.environ["OPENAI_API_KEY"] = ''

from schemas import InData
from settings import setup_logging
from openai_audio import AsyncOpenaiWhisper




class SioServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)

        # 注册事件处理
        self.sio.on('connect', self.handle_connect)
        self.sio.on('disconnect', self.handle_disconnect)
        self.sio.on('handle_message', self.handle_message)

    async def handle_connect(self, sid, environ):
        logger.info(f"用户 {sid} 已连接")

    async def handle_disconnect(self, sid):
        logger.info(f"用户 {sid} 已断开连接")

    async def handle_message(self, sid, data: InData):
        logger.info(f"用户 {sid} 发送消息: {data['message']}")
        prc = AsyncOpenaiWhisper(sid=sid, **dict(data))
        results = await prc.transcribe()
        # 广播消息给所有用户
        await self.sio.emit('handle_message', results, to=sid)


if __name__ == '__main__':
    from uvicorn import Config, Server

    sio_app = SioServer()
    server = Server(Config(app=sio_app.app,
                           host=args.host,
                           port=args.port))
    setup_logging('INFO') # DEBUG  # 使用 loguru 异步日志代替系统日志
    server.run()  # 启动 server
