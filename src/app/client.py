import json
import os

import streamlit as st
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from fill_fields_LLM import fill_fields_LLM
from input_processing import (
    approve_user_question,
    clarify_question,
    extract_doc,
    find_documents,
)
from schema import create_schema
from utils import check_schema_existance

load_dotenv()

APP_URL = os.getenv("APP_URL")
doc_path = os.getenv("DOCUMENTS_PATH")





# ===============================================================
# СТРАНИЦЫ
# 1 - Описание
# 2 - Чат
# 3 - Заполнение данных в документе
# 4 - Загрузка собственного документа
# ===============================================================

chat_prompt = "Отвечай на вопросы пользователя"
if "step" not in st.session_state:
    st.session_state.step = 1
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": SystemMessage(content=chat_prompt)}
    ]
if "conversation_status" not in st.session_state:
    st.session_state.conversation_status = "base"
if "previous_prompt" not in st.session_state:
    st.session_state.previous_prompt = ""
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "form_data" not in st.session_state:
    st.session_state.form_data = {}


# if "model" not in st.session_state:
#     st.session_state.model = None
def fill_docs():
    st.session_state.selected_doc = selected_doc
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": AIMessage(content=f"Вы выбрали: {selected_doc}"),
        }
    )


if st.session_state.step == 1:
    st.title("Заполнение документов с GigaChat")
    st.markdown('Мой телеграм: [@winst_y](https://t.me/winst_y)')
    st.markdown('Репозиторий с кодом проекта: [Git](https://github.com/WinsttonC/LLM-docs-filling)')

    if st.button("Заполнить свой документ"):
        st.session_state.step = 2
        st.rerun()
    description()
    # st.markdown(description)

elif st.session_state.step == 2:
    st.header("Заполнение документов")
    st.markdown("""
                Чтобы заполнить документ, напишите в чат.
                Если документа нет в базе, его можно добавить, используя 
                кнопку ниже.
                """)

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"].content)

    if st.session_state.conversation_status == "doc_filled":
        selected_doc = st.session_state.selected_doc
        file_path = f"{doc_path}/user_docs/{selected_doc}.docx"
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            file_data = file.read()
        with st.chat_message("assistant"):
            answer_doc = """Документ заполнен. Вы можете скачать его ниже.
                    Могу ли я еще чем-то помочь?"""
            st.markdown(answer_doc)
            st.download_button(
                label="Скачать файл",
                data=file_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        ### ОЧИСТКА ДАННЫХ СЕССИИ
        st.session_state.conversation_status = "base"
        st.session_state.selected_doc = ""
        st.session_state.form_data = {}
    if st.session_state.conversation_status == "add_document":
        st.session_state.step = 4
        st.rerun()

        st.session_state.conversation_status = "base"
    if st.session_state.conversation_status == "choosing_doc":
        with st.chat_message("assistant"):
            st.write(f"Найдено документов: {len(st.session_state.relevant_docs)-1}")
            # st.session_state.relevant_docs
            selected_doc = st.selectbox(
                "Выберите документ", st.session_state.relevant_docs, index=None
            )
        st.session_state.selected_doc = selected_doc
        # st.rerun()
        if st.session_state.selected_doc is not None:
            a = "Вы выбрали: " + st.session_state.selected_doc
            st.session_state.messages.append(
                {"role": "assistant", "content": AIMessage(content=a)}
            )
            st.session_state.conversation_status = "doc_selected"
            st.rerun()

    if st.session_state.conversation_status == "next":
        st.session_state.conversation_status = "base"
        st.session_state.step = 3
        st.rerun()
    if st.session_state.conversation_status == "doc_selected":
        if st.session_state.selected_doc == "Нет моего документа":
            st.session_state.conversation_status = "add_document"
            st.rerun()

        print("================")
        m = st.chat_message("assistant")
        if m.button("Заполнить документ"):
            st.session_state.conversation_status = "base"
            if not check_schema_existance(st.session_state.selected_doc):
                with st.spinner("Шаблон документа не найден. Генерируем шаблон..."):
                    create_schema(st.session_state.selected_doc)
            st.session_state.step = 3
            st.rerun()
        if m.button("Выбрать другой"):
            st.session_state.conversation_status = "base"
            choose_new_doc = "Ввведите название документа, который вы хотите заполнить"
            st.session_state.messages.append(
                {"role": "assistant", "content": AIMessage(content=choose_new_doc)}
            )
            # st.rerun()

    if prompt := st.chat_input("Что нужно сделать"):
        print(f"=== ПРОМПТ ===\n{prompt}")
        st.session_state.messages.append(
            {"role": "user", "content": HumanMessage(content=prompt)}
        )

        with st.chat_message("user"):
            st.markdown(prompt)
        if st.session_state.conversation_status == "clarify_question":
            previous_prompt = st.session_state.previous_prompt
            prompt = f"Вопрос: {previous_prompt}\nУточнение:\n{prompt}"
            st.session_state.conversation_status = "base"

        if st.session_state.conversation_status == "base":
            input_status = approve_user_question(prompt)
            if input_status == "да":
                with st.chat_message("assistant"):
                    with st.spinner("Идет поиск документов..."):
                        doc_name = extract_doc(prompt)
                        relevant_docs = find_documents(doc_name)
                    st.session_state.conversation_status = "choosing_doc"
                    relevant_docs.append("Нет моего документа")
                    st.session_state.relevant_docs = relevant_docs
                    st.rerun()

            else:
                st.session_state.conversation_status = "clarify_question"
                with st.chat_message("assistant"):
                    q = clarify_question(prompt)
                    st.session_state.previous_prompt = prompt
                    st.session_state.conversation_status = "clarify_question"
                    print("q")
                    print(q)
                    st.write(q)
                st.session_state.messages.append(
                    {"role": "assistant", "content": AIMessage(content=q)}
                )

            # selected_doc = relevant_docs[0]
            # st.session_state.selected_doc = relevant_docs[0]
            # if not check_schema_existance(selected_doc):  # TODO:
            #     create_schema(selected_doc)
            # st.session_state.step = 3
            # st.rerun()

    if st.sidebar.button("Вернуться к описанию"):
        st.session_state.step = 1
        st.rerun()
    if st.sidebar.button("Добавить документ"):
        st.session_state.step = 4
        st.rerun()


elif st.session_state.step == 3:
    selected_doc = st.session_state.selected_doc
    with open(
        f"{doc_path}/doc_schemas/{selected_doc}.json", "r", encoding="utf-8"
    ) as f:
        schema = json.load(f)

    st.header("Заполнение документа")
    st.markdown(f"""
                **Выбран документ:**\n
                {st.session_state.selected_doc} \n
                **Описание**:\n
                {schema['description']} \n\n
                **В документе нужно заполнить следующие поля:**
                """)

    st.session_state.form_data = {}

    with st.form("my_form"):
        fields = schema["fields"]

        field_names = [field for field in fields]
        questions = [fields[field]["question"] for field in fields]

        for i in range(len(field_names)):
            a = st.text_input(questions[i], key=f"text_input_{i}")
            st.write("\n")
            # st.write(f'{fields[i]}: {a}')
            # value = st.text_input(f'Текст {elem}', key=f'text_input_{elem}')
            # # Сохранение значений в словаре session_state

            st.session_state.form_data[field_names[i]] = a

        submitted = st.form_submit_button("Заполнить")
        if submitted:
            form_data = st.session_state.form_data
            st.write(form_data)
            with st.spinner("Заполняю документ. Пожалуйста, подождите."):
                fill_fields_LLM(selected_doc, form_data)

            st.session_state.conversation_status = "doc_filled"
            st.session_state.step = 2
            st.rerun()


elif st.session_state.step == 4:
    st.write("Вы можете добавить документ в базу данных.")
    uploaded_file = st.file_uploader("Загрузите .docx файл", type="docx")
    folder = f"{doc_path}/raw_docs"

    ### Добавить предобработку
    # 2. Сгенерировать схему
    # 4. Использовать название из схемы для сохранения документа

    if uploaded_file is not None:
        # Сохраните файл в указанную папку
        doc_name = os.path.splitext(uploaded_file.name)[0]
        with open(f"{folder}/{doc_name}.docx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Ищем пропущенные значения в документе..."):
            print(1)
            # if not check_doc_existance(doc_name):
            #     process_doc(doc_name, new_doc=True)
        with st.spinner("Создаем шаблон..."):
            print(2)
            # create_schema(doc_name, new_doc=True)
        st.success("Документ сохранен в базу данных.")

    if st.button("Вернуться в чат"):
        st.session_state.conversation_status = "base"
        st.session_state.relevant_docs = None
        st.session_state.step = 2
        st.rerun()
