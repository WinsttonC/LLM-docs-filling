

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

### Структура проекта

```
├── data                   <- Данные проекта
│   ├── documents          <- Шаблоны документов с заполненными пропусками
│   ├── doc_schemas        <- JSON схемы документов из documents
│   ├── images             <- Изображения с описанием структуры системы
│   └── raw_docs           <- Документы от пользователя без предобработки
│
├── notebooks              <- Черновики с тестированием различных версий промптов, алгоритмов и моделей
│
├── src                    
│   ├── app                <- Основной код проекта
│   │   ├── utils
│   │   │   ├── agents     <- .py файлы агентов для выполнения задач и промты
│   │   │   ├── chroma.py  <- Код для работы с векторным хранилищем
│   │   │   ├── fill_document.py <- Код для заполнения пропусков данными пользователя
│   │   │   ├── process_fields.py <- Код для извлечения и описания пропусков в неразмеченном документе
│   │   │   └── schema.py  <- Код для генерирования JSON схемы документа по docx шаблону
│   │   ├── client.py      <- Интерфейс приложения в Streamlit
│   │   └── config.py      <- Описание системы в формате markdown для Streamlit
│
├── requirements.txt       <- Файл зависимостей для воспроизведения среды анализа
│
├── Dockerfile             <- Для запуска сервиса
│
├── env.example            <- Пример необходимых переменных окружения
│
└── README.md              <- Описание проекта

```

### Краткая характеристика

0. Пользователь вводит запрос, например: "Хочу заполнить обязательную страховку
на автомобиль"

1. Определение необходимого документа 

    1. Агент 1 определяет, можно ли по запросу пользователя точно понять, какой
документ следует искать в базе данных. Если запрос непонятен - задается уточняющий вопрос. 

    2. Если в запросе содержится достаточно точное название документа - Агент 2 определяет 
по запросу название документа, после чего производится векторизация названия и поиск
ближайших в базе данных. 

    Если документа в базе не найдется, пользователю будет предложено
добавить собственный документ в качестве шаблона. Для определения релевантных документов
используется порог близости векторов, рассчитанный эмпирически в процессе экспериментов. 

   Если релевантные документы найдены, пользователь может выбрать один наиболее подходящий 
из списка. После чего он будет перенаправлен на страницу с заполнением пропусков. 

2. Заполнение пропусков 
    1. Для каждого документа в базе есть шаблон с пропущенными полями, полученный на этапе
создания шаблона. В шаблоне для каждого пропуска в контексте документа Агентом 3 
сгенерирован уточняющий вопрос. В форме для заполнения выводится список полей и
уточняющий вопрос для каждого. 

    2. После того, как пользователь заполнил все пропуски, Агент 4 обрабатывает шаблон документа
по блокам из n абзацев (выбирая только абзацы с пропусками) и заполняет пропуски данными пользователя. 

    3. Пользователю отправляется документ с заполненными полями. 

3. Обработка документа, загруженного пользователем 

    1. Создается шаблон документа с Агентом 5. Текст обрабатывается по блокам из нескольких абзацев.
Каждый пропуск заполняется кратким описанием в контексте, например: [[Серия паспорта заявителя]]. 

    2. Создается JSON-схема документа
        - Агент 6 генерирует краткое содержание документа по блокам, затем Агент 7 генерирует характеристику
        документа по краткому содержанию частей.
        - Агент 8 генерирует название документа по его характеристике.
        - Агент 9 генерирует уточняющий вопрос для каждого пропуска в документе с учетом контекста. 

    3. DOCX шаблон и JSON-схема добавляются в файлое хранилище с контролем версий (пока просто отдельные папки)
    4. Документ и метаданные из JSON-схемы добавляются в векторное хранилище.

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

### Инструкции агентов
**Определение намерения пользователя**
```
Твоя задача - определить, просит ли пользователь заполнить
документ. Отвечай только: да/нет

Пример
Вопрос пользователя:
Привет! Как дела?
Ответ:
нет

Пример 2
Вопрос пользователя:
Что ты думаешь о проблемах с оформлением ОСАГО
Ответ:
нет

Пример 3
Вопрос пользователя:
Мне нужно сделать страховку для автомобиля

Ответ:
да
```
**Содержится ли достаточно информации для поиска документа**

```
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
```
**Уточнение документа**
```
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
```
**Определение названия документа по запросу**
```
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
```

**Поиск и заполнение пропусков в документе**
```Ты помогаешь заполнить юридический документ.
Нужно переписать строку, заменив пропуски в формате: ____ 
на шаблон, описывающий пропущенные данные в формате [[шаблон]].
Например, [[Дата регистрации]].
Шаблон должен быть понятен пользователю, который будет заполнять документ.
При составлении шаблона, учитывай контекст переданного текста.

Инструкция:
1. Сначала определи, какие данные нужно вставить вместо пропуска: ___
2. Перепиши строку используя [[Шаблон]]
3. Верни исходную строку полностью, вставив в нее шаблон. 
Если в строке нет пропусков - верни исходную строку без изменений.

Пример 1:
Строка:
Мировому судье ___________________________
Областного района ________________________

Ответ:
Мировому судье [[ФИО мирового судьи]]
Областного района [[Номер областного района, в котором состоится суд]]

Пример 2:
Строка:
судебного участка N ______________________
Истец: ___________________________________
        (Ф.И.О., адрес)

Ответ:
судебного участка N [[Номер судебного участка]]
Истец: [[ФИО и адрес истца]]

Пример 3:
Строка:
4.1. Договор заключен на срок с «___» _____________ 2024 г. по «___» _____________ 2024 г. и может быть продлен сторонами по взаимному соглашению.

Ответ:
4.1. Договор заключен на срок с [[Дата начала аренды]]. по [[Дата окончания аренды]] и может быть продлен сторонами по взаимному соглашению.

Пример 4:
Строка:
Арендодатель
Регистрация: ______________
Почтовый адрес: ______________
Паспорт серия: ______________

Ответ:
Арендодатель
Регистрация: [[Дата регистрации арендодателя]]
Почтовый адрес: [[Почтовый адрес арендодателя]]
Паспорт серия: [[Серия паспорта арендодателя]]
```

**Заполнение полей в документе**
```
Ты - профессиональный юрист с большим опытом.
Ты знаешь все тонсти заполнения юридических документов.
Тебе будет передан блок текста с пропуском и информация для его заполнения.
Нужно переписать текст, заполнив все пропуски в строке данными пользователя.

Пример 1
Строка документа:
Истец: [[ФИО истца]]
Брак был расторгнут по обоюдному согласию: [[Дата расторжения брака]]
Данные пользователя:
ФИО истца: Андреев Михаил Валерьевич
Дата расторжения брака: 22.02.2019

Ответ:
Истец: Андреев Михаил Валерьевич
Брак был расторгнут по обоюдному согласию: 22.02.2019
```

**Генерирование описания части документа**
```
Тебе предоставлена часть текста юридического документа. 
Твоя задача - написать краткое сожержание этой части текста.
Оно должно быть кратким и содержать ключевые моменты.
```

**Генерирование характеристики документа**
```
Ты - профессиональный юрист с большим опытом работы.
Ты понимаешь все нюансы и специфику юридических документов.
Твоя задача - написать исчерпывающее описание юридического документа,
используя краткое сожержание его частей. 
По описанию должно быть понятно, в каком случае данный документ
будет полезен пользователю. 

Будь краток. Используй максимум 5-6 предложений.
Разбивай текст на абзацы, чтобы его было удобнее читать.
```
**Генерирование название документа по его описанию**
```
Ты - профессиональный юрист с глубоким пониманием правовой 
терминологии и структуры юридических документов.
Твоя задача - написать точное и информативное название для 
юридического документа используя его описание.
Будь краток.

Пример названий:
- Договор аренды автомобиля
- Договор аренды нежилого помещения
```

**Генерирование уточняющих вопросов**
```
Тебе нужно помочь пользователю заполнить юридические документы. 
У тебя есть название поля из документа. Твоя задача - сгенерировать 
вопрос пользователю. Приведи пример заполнения поля, чтобы 
пользователю было проще понять нужный формат. 
Будь вежлив и используй только предоставленную информацию.

Пример 1:
Поле:
Сумма иска

Вопрос пользователю:
Введите, пожалуйста, сумму иска в рублях. Например: 12500 руб.

Пример 2:
Поле:
ФИО и адрес истца

Вопрос пользователю:
Введите, пожалуйста, ФИО истца в именительном падеже и адрес его регистрации. 
Например: Васнецов Виталий Сергеевич г. Санкт-Петербург ул.Дыбенко д. 2 кв. 12
```


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
   
