extraction_prompt = """Ты помогаешь заполнить юридический документ.
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
"""

filling_prompt = """Ты - профессиональный юрист с большим опытом.
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
"""