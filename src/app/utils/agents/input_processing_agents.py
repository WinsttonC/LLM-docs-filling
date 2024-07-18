import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from .prompts.input_prompts import approve_prompt, clarify_prompt, extract_doc_prompt, user_intent_prompt

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False
)

doc_path = os.getenv("DOCUMENTS_PATH")

def answer_is_correct(answer):
    if answer.lower() == 'да' or answer.lower() == 'нет':
        return True
    else:
        return False

def want_to_fill_document(question):
    input_text = f"Вопрос пользователя::\n{question}\n\nОтвет:\n"
    messages = [SystemMessage(content=user_intent_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)
    answer = res.content
    
    if answer_is_correct(answer):
        if answer.lower() == 'да':
            return True
        else:
            return False
    else:
        return 'Answer error'


def approve_user_question(question):
    input_text = f"Запрос пользователя:\n{question}\nОтвет:"
    messages = [SystemMessage(content=approve_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)
    answer = res.content.lower()

    return answer


def clarify_question(question):
    input_text = f"Запрос пользователя:\n{question}\nОтвет:"
    messages = [SystemMessage(content=clarify_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)
    answer = res.content

    return answer


def extract_doc(question):
    input_text = f"Запрос пользователя:\n{question}\nОтвет:"
    messages = [SystemMessage(content=extract_doc_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)
    answer = res.content

    return answer



