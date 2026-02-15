import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'botpy'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import botpy
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from shared import Message

class BotClient:
    def __init__(self, agent_host="localhost", agent_port=8765):
        self.agent_host = agent_host
        self.agent_port = agent_port
        self.reader = None
        self.writer = None

    async def connect_to_agent(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.agent_host, self.agent_port
        )

    async def send_to_agent(self, message: Message) -> str:
        if not self.writer:
            await self.connect_to_agent()

        try:
            self.writer.write(message.to_json().encode())
            await self.writer.drain()

            response = await self.reader.read(1024)
            return response.decode()
        except Exception as e:
            print(f"发送到Agent失败: {e}")
            return "AI服务连接失败"

class QQBot(BotClient, botpy.Client):
    def __init__(self, config_path="config.yaml"):
        config = read(os.path.join(os.path.dirname(__file__), "..", config_path))
        BotClient.__init__(self)
        botpy.Client.__init__(self, intents=botpy.Intents(public_messages=True))
        self.config = config

    async def on_ready(self):
        print(f"QQ机器人 「{self.robot.name}」 已启动!")
        await self.connect_to_agent()

    async def on_group_at_message_create(self, message: GroupMessage):
        content = message.content.replace(f"<@!{self.robot.id}>", "").strip()
        session_id = message.group_openid

        # 判断消息类型
        msg_type = "chat"
        if content.lower() in ["清空对话", "重置对话", "清除历史"]:
            msg_type = "reset"
        elif "系统状态" in content.lower() or "status" in content.lower():
            msg_type = "status"

        # 发送请求到Agent服务
        msg = Message(session_id=session_id, content=content, msg_type=msg_type)
        response = await self.send_to_agent(msg)

        # 格式化回复
        if msg_type == "status":
            try:
                import json
                data = json.loads(response)
                response = f"🤖 机器人状态\n正在服务 {data['active_sessions']} 个会话\n当前会话历史: {data['history_length']} 条\n使用模型: {data['model']}"
            except:
                response = "状态查询失败"
        elif msg_type == "chat" and not response.startswith("对话历史"):
            response = f"🤖 小数: {response}"

        # 发送回复到QQ
        await message._api.post_group_message(
            group_openid=session_id,
            msg_type=0,
            msg_id=message.id,
            content=response
        )

if __name__ == "__main__":
    bot = QQBot()
    bot.run(appid=bot.config["appid"], secret=bot.config["secret"])