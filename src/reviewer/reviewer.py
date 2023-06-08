import os

import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
)


def review(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chat = ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo", request_timeout=600)
    messages = [
      SystemMessage(content="日本語で回答して。"),
      HumanMessage(content=text),
    ]
    response = chat(messages)
    return response.content