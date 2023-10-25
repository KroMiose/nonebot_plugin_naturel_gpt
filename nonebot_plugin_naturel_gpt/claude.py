import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from typing import AsyncGenerator
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import *

class Slack_Claude_Client:
    slack_user_token: str
    claude_id: str
    channel_id: str
    slack_client: AsyncWebClient
    pre_msg: str

    def __init__(
        self,
        slack_user_token: str,
        claude_id: str,
        channel_id: str,
        pre_msg: str = "<忽略'@Claude',不说没看到也不说看到>",
    ):
        self.slack_user_token = slack_user_token
        self.claude_id = claude_id
        self.channel_id = channel_id
        self.slack_client = AsyncWebClient(token=self.slack_user_token)
        self.pre_msg = pre_msg

    def create_new_chat(self):
        return {"thread_ts": "", "msg_ts": ""}

    async def send_message(self, question: str, chat: dict):
        result = await self.slack_client.chat_postMessage(
            channel=self.channel_id,
            text=f"<@{self.claude_id}>{question}",
            thread_ts=chat["thread_ts"],
        )
        if result["ok"]:
            chat["msg_ts"] = result["ts"]
            if not chat["thread_ts"]:
                chat["thread_ts"] = result["ts"]
            return chat
        else:
            raise Exception(f"Error: {result}")

    async def get_stream_message(self, chat: dict):
        retry = 10
        detail_error = "Unknown error"
        while True:
            if retry <= 0:
                raise Exception(detail_error)
            try:
                text = await self.get_reply(chat)
                yield text
                if text.finished:
                    break
            except Exception as e:
                detail_error = str(e)
                retry -= 1

    async def get_reply(self, chat: dict):
        result = await self.slack_client.conversations_replies(
            ts=chat["thread_ts"],
            channel=self.channel_id,
            oldest=chat["msg_ts"],
        )
        for message in result.data["messages"][::-1]:
            text = message.get("text", "")
            user = message.get("user", "")
            msg_ts = float(message.get("ts", 0))
            if (
                text.rstrip("_Typing…_")
                and (not text.startswith("\n&gt; _*Please note:*"))
                and (msg_ts > float(chat["msg_ts"]))
                and user == self.claude_id
            ):
                return Text(
                    content=text.rstrip("\n\n_Typing…_"),
                    finished=bool(not text.endswith("_Typing…_")),
                )
        await asyncio.sleep(2)
        raise Exception("")

    async def ask_stream_raw(self, question: str, chat: dict):
        new_chat = await self.send_message(question, chat)
        await asyncio.sleep(3)
        last_text = None
        new_text = None
        while True:
            async for data in self.get_stream_message(new_chat):
                new_text = data.content
                finished = data.finished
                if finished and (new_text == last_text):
                    return new_text
                last_text = new_text
            await asyncio.sleep(1) 
        

class Text:
    content: str
    finished: bool

    def __init__(self, content: str, finished: bool):
        self.content = content
        self.finished = finished


# replace 'your question' with the actual string

async def get_multiple_replies_from_claude(questions: list,seg:list):
    slack_user_token = config.slack_user_token
    claude_id = config.claude_id
    channel_id = config.channel_id 
    pre_msg = "<忽略'@Claude',不说没看到也不说看到>"

    client = Slack_Claude_Client(slack_user_token, claude_id, channel_id, pre_msg)
    chat = client.create_new_chat()
    questions = ["{}".format(msg["content"]) for msg in questions]
    new_list = []
    start = 0
    for num in seg:
        new_list.append(''.join(questions[start:start+num]))
        start += num
    # Loop over each question in the questions list
# 假设 questions, chat, client 是有效和已经定义的变量
    results=[]
    for question in new_list:
            reply = await client.ask_stream_raw(question, chat)
            results.append(reply)
    return results