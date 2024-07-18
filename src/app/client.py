import json
import os

import streamlit as st
from utils.agents.input_processing_agents import (
    approve_user_question,
    clarify_question,
    extract_doc,
)
from utils.chroma import find_documents
from config import description
from dotenv import load_dotenv
from utils.fill_document import fill_fields_LLM
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from utils.schema import check_doc_existance, check_schema_existance, create_schema
from utils.process_fields import create_fields_template

load_dotenv()

APP_URL = os.getenv("APP_URL")
doc_path = os.getenv("DOCUMENTS_PATH")

# ===============================================================
# СТРАНИЦЫ
# 1 - Описание
# 2 - Чат
# 3 - Заполнение данных в документе
# 4 - Загрузка собственного документа
# 5 - Загрузка обработанного шаблона
# ===============================================================



chat_prompt = "Старайся максимально точно ответить на вопрос пользователя:"
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
if "clarification_steps" not in st.session_state:
    st.session_state.clarification_steps = 0

if st.session_state.step == 1:
    st.title("Заполнение документов с GigaChat")

    if st.button("Перейти в чат"):
        st.session_state.step = 2
        st.rerun()
    description()

elif st.session_state.step == 2:
    st.header("Заполнение документов")
    st.markdown("""
                Чтобы заполнить документ, напишите в чат.
                Поиск возвращает только подходящие под запрос документы,
                если документа нет в базе, его можно добавить, используя 
                кнопку на боковой панели.
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
        if len(st.session_state.relevant_docs) == 1:
            with st.chat_message("assistant"):
                st.write(f"Документов по вашему запросу не найдено. Вы можете добавить шаблон документа самостоятельно")
                # st.session_state.relevant_docs
                if st.button('Добавить документ', key='0 docs'):
                    st.session_state.relevant_docs = []
                    st.session_state.conversation_status = 'base'
                    st.session_state.step = 4
                    st.rerun()
        else:
            with st.chat_message("assistant"):
                st.write(f"Найдено документов: {len(st.session_state.relevant_docs)-1}")
                # st.session_state.relevant_docs
                selected_doc = st.selectbox(
                    "Выберите документ", st.session_state.relevant_docs, index=None
                )
            st.session_state.selected_doc = selected_doc

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
        st.session_state.messages.append(
            {"role": "user", "content": HumanMessage(content=prompt)}
        )

        with st.chat_message("user"):
            st.markdown(prompt)
        if st.session_state.conversation_status == "clarify_question":
            st.session_state.clarification_steps += 1
            previous_prompt = st.session_state.previous_prompt
            prompt = f"Вопрос: {previous_prompt}\nУточнение:\n{prompt}"
            st.session_state.conversation_status = "base"

        if st.session_state.conversation_status == "base":
            input_status = approve_user_question(prompt)
            if input_status == "да" or st.session_state.clarification_steps > 1:
                st.session_state.clarification_steps = 0
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
                    st.write(q)
                st.session_state.messages.append(
                    {"role": "assistant", "content": AIMessage(content=q)}
                )         

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
            # st.write(form_data)
            with st.spinner("Заполняю документ. Пожалуйста, подождите."):
                fill_fields_LLM(selected_doc, form_data)

            st.session_state.conversation_status = "doc_filled"
            st.session_state.step = 2
            st.rerun()
    
    if st.sidebar.button("Вернуться к описанию"):
        st.session_state.selected_doc = None
        st.session_state.step = 1
        st.rerun()
    if st.sidebar.button("Вернуться в чат"):
        st.session_state.selected_doc = None
        st.session_state.step = 2
        st.rerun()


elif st.session_state.step == 4:
    st.write("Вы можете добавить документ в базу данных.")
    uploaded_file = st.file_uploader("Загрузите .docx файл", type="docx")
    folder = f"{doc_path}/raw_docs"

    if uploaded_file is not None:
        # Сохраните файл в указанную папку
        doc_name = os.path.splitext(uploaded_file.name)[0]
        with open(f"{folder}/{doc_name}.docx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Ищем пропущенные значения в документе..."):
            if not check_doc_existance(doc_name):
                create_fields_template(doc_name, new_doc=True)
        with st.spinner("Создаем шаблон..."):
            new_doc_name = create_schema(doc_name, new_doc=True)
        st.success("Документ сохранен в базу данных.")
        st.session_state.generated_template = new_doc_name
        
        st.session_state.step = 5
        st.rerun()



    if st.button("Вернуться в чат"):
        st.session_state.conversation_status = "base"
        st.session_state.relevant_docs = []
        st.session_state.step = 2
        st.rerun()


elif st.session_state.step == 5:
    doc_name = st.session_state.generated_template
    file_path = f"{doc_path}/documents/{doc_name}.docx"
    schema_path = f"{doc_path}/doc_schemas/{doc_name}.json"
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        file_data = file.read()

    with open(schema_path, "r", encoding='utf-8') as file:
        schema = json.load(file)

    description = schema['description']
    
    st.markdown(f""" ## {doc_name}
    **Описание:**\n
    {description} \n
    """)

    st.download_button(
            label="Скачать шаблон документа",
            data=file_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    

    if st.button("Вернуться в чат", key='step 5 chat'):
        st.session_state.generated_template = None
        st.session_state.conversation_status = "base"
        st.session_state.step = 2
        st.rerun()
    if st.button("Вернуться к описанию", key='step 5 desc'):
        st.session_state.generated_template = None
        st.session_state.conversation_status = "base"
        st.session_state.step = 1
        st.rerun()
