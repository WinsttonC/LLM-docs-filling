import os
import warnings

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from .prompts.field_prompts import filling_prompt

warnings.filterwarnings("ignore")

load_dotenv()

GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False, streaming=True
)


def fill_fields(prompt):
    """
    Заполняет пропущенные поля вида [[Описание пропуска]]
    в строке.

    Parameters
    ----------
    prompt : str
        Строка документа с пропусками и данные пользователя.
    Returns
    ---------
    answer : str
        Заполненный блок документа.
    """

    messages = [SystemMessage(content=filling_prompt)]
    messages.append(HumanMessage(content=prompt))
    res = chat(messages)
    answer = res.content

    return answer
