import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any
from openai import OpenAI
from shared import Message
from botpy.ext.cog_yaml import read

class AgentServer:
    def __init__(self, config_path="config.yaml"):
        config = read(os.path.join(os.path.dirname(__file__), "..", config_path))

        self.port = 8765
        self.history: Dict[str, List[Dict]] = {}
        self.client = OpenAI(
            api_key=config["ai"]["api_key"],
            base_url=config["ai"]["base_url"]
        )
        self.model = config["ai"]["model"]
        self.system_prompt = """你是王昌阳"""

    async def handle_message(self, message: Message) -> str:
        if message.msg_type == "reset":
            if message.session_id in self.history:
                del self.history[message.session_id]
            return "对话历史已清空，让我们重新开始吧！"

        if message.msg_type == "status":
            history_count = len(self.history.get(message.session_id, []))
            return json.dumps({
                "active_sessions": len(self.history),
                "history_length": history_count,
                "model": self.model
            })

        # 普通聊天消息
        if message.session_id not in self.history:
            self.history[message.session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]

        history = self.history[message.session_id]
        if len(history) > 11:
            history = history[:1] + history[-10:]

        history.append({"role": "user", "content": message.content})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=0.7,
                max_tokens=500
            )

            ai_reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": ai_reply})
            return ai_reply

        except Exception:
            return "抱歉，AI服务暂时不可用，请稍后再试。"

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client,
            'localhost',
            self.port
        )
        print(f"Agent服务启动在端口 {self.port}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        while True:
            try:
                data = await reader.read(1024)
                if not data:
                    break

                message = Message.from_json(data.decode())
                response = await self.handle_message(message)

                writer.write(response.encode())
                await writer.drain()

            except Exception as e:
                print(f"处理客户端错误: {e}")
                break

        writer.close()

if __name__ == "__main__":
    server = AgentServer()
    asyncio.run(server.start_server())