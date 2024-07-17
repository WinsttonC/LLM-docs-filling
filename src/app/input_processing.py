import os

from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage

from chat import chat
from chroma import Chroma
from utils import hash_filename

load_dotenv()

embedding_name = "text-embedding-3-large"
collection_name = "embedding_name"
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("BASE_URL_OPENAI_API")
doc_path = os.getenv("DOCUMENTS_PATH")

folder_path = f"{doc_path}/documents"

embedding_model = embedding_functions.OpenAIEmbeddingFunction(
    model_name=embedding_name,
    api_key=api_key,
    api_base=api_base,
)

approve_prompt = """
Ты юрист. Твоя задача - решить, можно ли точно
определить тип юридического документа по 
запросу пользователя.
Отвечай только: да/нужно уточнить

Пример 1
Запрос пользователя:
Заполни доверенность на сына.

Ответ:
нужно уточнить

Пример 2
Запрос пользователя:
Я хочу заполнить ОСАГО

Ответ:
да
"""

clarify_prompt = """
Ты - профессиональный юрист.
По запросу пользователя нельзя однозначно определить,
какой тип документа ему необходимо заполнить.
Твоя задача - задачать уточняющий вопрос пользователю,
используя его изначальный вопрос.
Будь вежлив.

Пример 1:
Вопрос пользователя:
Заполни доверенность на сына.

Ответ:
Подскажите, подалуйта, какой именно тип доверенности нужно заполнить?
"""

extract_doc_prompt = """
Ты - юрист. Твоя задача - определять по 
запросу пользователей, какой юридический документ
им больше всего подходит.
Отвечай только названием документа.

Пример 1
Пример 1
Запрос пользователя:
Заполни доверенность управление автомобилем на сына.

Ответ:
Доверенность на управление транспортным средством.

Пример 2
Запрос пользователя:
Я хочу заполнить ОСАГО

Ответ:
Договор страхования ОСАГО
"""


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


def find_documents(question):
    client = Chroma(f"{doc_path}/vect_docs", embedding_model, collection_name)

    docs = client.get_relevant_docs(question)
    docs = [
        doc
        for doc, distance in zip(docs["documents"][0], docs["distances"][0])
        if distance < 0.8  # TODO
    ]

    return docs


def add_documents_to_vectorstore(doc_name):
    client = Chroma(f"{doc_path}/vect_docs", embedding_model, collection_name)

    document_titles = [doc_name]

    data_dict = {
        "docs": document_titles,
        "ids": [hash_filename(f) for f in document_titles],
    }

    client.add_docs(data_dict)
