import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from prompts import filling_prompt

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False, streaming=True
)

def fill_fields(prompt):
    messages = [SystemMessage(content=filling_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)
    answer = res.content
    
    return answer