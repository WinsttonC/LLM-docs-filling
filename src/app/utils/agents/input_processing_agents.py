import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from prompts import approve_prompt, clarify_prompt, extract_doc_prompt

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False, streaming=True
)

 ==============================
doc_path = os.getenv("DOCUMENTS_PATH")
def check_doc_existance(doc_name):
    file_path = f"{doc_path}/documents/{doc_name}.docx"
    if os.path.exists(file_path):
        return True
    else:
        return False


def check_schema_existance(doc_name):
    file_path = f"{doc_path}/doc_schemas/{doc_name}.json"
    # file_path = f'doc_schemas/{doc_name}'
    if os.path.exists(file_path):
        return True
    else:
        return False

===========================



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



