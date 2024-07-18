import os
import warnings

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from .prompts.field_prompts import extraction_prompt

load_dotenv()
warnings.filterwarnings("ignore")


GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False, model="GigaChat-Pro"
)  # model='GigaChat-Pro'


def find_fields(prompt):
    """
    Заменяет пропуски в строке на шаблон
    вида [[Описание пропуска]].

    Parameters
    ----------
    prompt : str
        Строка документа с пропусками + (опц. контекст).
    Returns
    ---------
    answer : str
        Строка с размеченными пропусками.
    """
    messages = [SystemMessage(content=extraction_prompt)]
    messages.append(HumanMessage(content=prompt))
    res = chat(messages)
    answer = res.content

    return answer
