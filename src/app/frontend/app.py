import os
import asyncio

import aiohttp
import pandas as pd
import requests
import streamlit as st
from config import description
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from chat import chat
from input_processing import extract_doc, clarify_question, approve_user_question
load_dotenv()

APP_URL = os.getenv("APP_URL")

# ===============================================================
# СТРАНИЦЫ
# 1 - Авторизация
# 2 - Регистрация
# 3 - Страница с информацией о пользователе
# 4 - Пополнение баланса
# 5 - Выбор модели
# 6 - Предсказание
# ===============================================================

chat_prompt = 'Отвечай на вопросы пользователя'
if "step" not in st.session_state:
    st.session_state.step = 1

if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant',
                                  'content': SystemMessage(content=chat_prompt)}]
# if "model" not in st.session_state:
#     st.session_state.model = None


if st.session_state.step == 1:
    st.title("Заполнение документов с GigaChat")
    st.header("")

    # ============= ВСТАВИТЬ ОПИСАНИЕ РЕШЕНИЯ ==================

    if st.button("Заполнить свой документ"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.header("Заполнение документов")
    st.markdown("""
                Чтобы заполнить документ, напишите в чат.
                Если документа нет в базе, его можно добавить, используя 
                кнопку ниже.
                """)


    for message in st.session_state.messages[1:]:
        with st.chat_message(message['role']):
            st.markdown(message['content'].content)

    if prompt := st.chat_input("Что нужно сделать"):
        print(f'=== ПРОМПТ ===\n{prompt}')
        st.session_state.messages.append({'role': 'user',
                                          'content': HumanMessage(content=prompt)})
        with st.chat_message("user"):
            st.markdown(prompt)

        input_status = approve_user_question(prompt)
        print('input_status')
        print(input_status)
        if input_status == 'да': 
            doc_type = extract_doc(prompt)
            print('doc_type')
            print(doc_type)
        else:
            with st.chat_message("assistant"):
                q = clarify_question(prompt)
                print('q')
                print(q)
                st.write(q)

            st.session_state.messages.append({"role": "assistant", 
                                            "content": AIMessage(content=q)})
    
    if st.sidebar.button("Вернуться к описанию"):
        st.session_state.step = 1
        st.rerun()
