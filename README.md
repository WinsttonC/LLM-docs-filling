

Мой телеграм: [@winst_y](https://t.me/winst_y)

### Описание
Данная система предназначена для автоматического заполнения документов 
с использованием больших языковых моделей (LLM). 
**Основная цель системы** – упростить процесс создания и заполнения различных форм и документов, 
таких как доверенности, договоры и другие юридические документы.
В качестве основной модели при разработке использовался GigaChat Lite. 
Приложение интегрируется с GigaChat API но не зависит от него. 
При необходимости LLM может быть легко заменена на любую другую,
включая open-source модели.

### Краткая характеристика

0. Пользователь вводит запрос, например: "Хочу заполнить обязательную страховку
на автомобиль"

1. Определение необходимого документа 

1.1 Агент 1 определяет, можно ли по запросу пользователя точно понять, какой
документ следует искать в базе данных. Если запрос непонятен - задается уточняющий вопрос. 

1.2 Если в запросе содержится достаточно точное название документа - Агент 2 определяет 
по запросу название документа, после чего производится векторизация названия и поиск
ближайших в базе данных. 

Если документа в базе не найдется, пользователю будет предложено
добавить собственный документ в качестве шаблона. Для определения релевантных документов
используется порог близости векторов, рассчитанный эмпирически в процессе экспериментов. 
Если релевантные документы найдены, пользователь может выбрать один наиболее подходящий 
из списка. После чего он будет перенаправлен на страницу с заполнением пропусков. 

2. Заполнение пропусков 
2.1 Для каждого документа в базе есть шаблон с пропущенными полями, полученный на этапе
создания шаблона. В шаблоне для каждого пропуска в контексте документа Агентом 3 
сгенерирован уточняющий вопрос. В форме для заполнения выводится список полей и
уточняющий вопрос для каждого. 

2.2 После того, как пользователь заполнил все пропуски, Агент 4 обрабатывает шаблон документа
по блокам из n абзацев (выбирая только абзацы с пропусками) и заполняет пропуски данными пользователя. 

2.3 Пользователю отправляется документ с заполненными полями. 

3. Обработка документа, загруженного пользователем 

3.1 Создается шаблон документа с Агентом 5. Текст обрабатывается по блокам из нескольких абзацев.
Каждый пропуск заполняется кратким описанием в контексте, например: [[Серия паспорта заявителя]]. 

3.2 Создается JSON-схема документа
- Агент 6 генерирует краткое содержание документа по блокам, затем Агент 7 генерирует характеристику
документа по краткому содержанию частей.
- Агент 8 генерирует название документа по его характеристике.
- Агент 9 генерирует уточняющий вопрос для каждого пропуска в документе с учетом контекста. 

3.3 DOCX шаблон и JSON-схема добавляются в файлое хранилище с контролем версий (пока просто отдельные папки)
3.4 Документ и метаданные из JSON-схемы добавляются в векторное хранилище.

#### Дополнительные замечания
- Обработка текста по блокам из нескольких абзацев показала себя лучше всего в плане качества
генерации и выявления полей. В таком случае агент видит не только сам пропуск, но и контекст в котором
он находится, поэтому удается точнее задать вопрос пользователю или заполнить пропуски его данными.


### Основные компоненты системы 
В общем виде система состоит из 3 основных компонентов:

##### 1. Разметка пропусков в документе
Система анализирует предоставленный документ и извлекает 
типовые поля, такие как ФИО, дата, адрес и т.д. 
Для этого используются регулярные выражения и LLM агенты. 
При необходимости пропуски можно легко заменить или отредактировать,
так как повторное извлечение легко используется с помощью регулярных
выражений.

**Результат:** документ в исходном формате размеченными полями пропусков.

##### 2. Создание шаблона документа

**Результат:** JSON-схема документа со следущими ключами:
- Название документа
- Описание документа 5-6 предложений с основной информацией
- Поля (краткая характеристика каждого пропуска в документе)
    - Контекст (несколько слов до и после каждого поля)
    - Вопрос пользователю для уточнения данных по этому полю в контексте
- Дата последнего обновления

##### 3. Заполнение документов данными пользователя

**Результат:** заполненный данными пользователя документ в 
исходном формате, готовый к подписи.


### TO DO
В этом блоке описаны потенциальные улучшения проекта, которые 
могут повысить качество, скорость работы, стабильность 
или удобство взаимодействия.
- Уточнение правильности извлечение шаблона у пользователя с возможностью отредактировать часть полей.
- Уточнение правильности заполнения документа с возможность отредактировать свои ответы.
- Можно ускорить создание шаблонов и разметку документов за счет параллельной обработки блоков.
Распараллелить запросы можно только с платной подпиской на GigaChat или с использованием других API.

- Обработка таблиц, картинок и нечитаемых pdf документов. Так как все алгоритмы рассчитаны на 
обработку строк, нет ограничений на использование других форматов документа.
   