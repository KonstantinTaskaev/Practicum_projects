#!/usr/bin/env python
# coding: utf-8

# # Исследовательский анализ данных в Python и проверка гипотез.
# - Автор:Таскаев Константин
# - Дата: 30.06.2025
# - ссылка на дашборд по первой части проекта: https://datalens.yandex/1opjgckjxe9wm

# ## Цели и задачи проекта
# 
# Провести исследовательский анализ данных в Python, чтобы выявить инсайты об изменении пользовательских предпочтений и популярности событий осенью 2024 года, а также проверить гипотезы о разнице в поведении пользователей с мобильными и стационарными устройствами.
# 

# ## Описание данных
# В нашем распоряжении данные о бронировании билетов на сервисе Яндекс Афиша за период с 1 июня по 30 октября 2024 года в виде двух датасетов:
# Первый датасет `final_tickets_orders_df.csv` включает информацию обо всех заказах билетов, совершённых с двух типов устройств — мобильных и стационарных. 
# Датасет содержит такие поля:
# - `order_id` — уникальный идентификатор заказа.
# - `user_id` — уникальный идентификатор пользователя.
# - `created_dt_msk` — дата создания заказа (московское время).
# - `created_ts_msk` — дата и время создания заказа (московское время).
# - `event_id` — идентификатор мероприятия из таблицы events.
# - `cinema_circuit` — сеть кинотеатров. Если не применимо, то здесь будет значение 'нет'.
# - `age_limit` — возрастное ограничение мероприятия.
# - `currency_code` — валюта оплаты, например rub для российских рублей.
# - `device_type_canonical` — тип устройства, с которого был оформлен заказ, например mobile для мобильных устройств, desktop для стационарных.
# - `revenue` — выручка от заказа.
# - `service_name` — название билетного оператора.
# - `tickets_count` — количество купленных билетов.
# - `total` — общая сумма заказа.
# - В данные также был добавлен столбец `days_since_prev` с количеством дней с предыдущей покупки для каждого пользователя. Если покупки не было, то данные содержат пропуск.
# 
# Второй датасет `final_tickets_events_df` содержит информацию о событиях, включая город и регион события, а также информацию о площадке проведения мероприятия. Из данных исключили фильмы, ведь, как было видно на дашборде, событий такого типа не так много. Датасет содержит такие поля:
# - `event_id` — уникальный идентификатор мероприятия.
# - `event_name` — название мероприятия. Аналог поля event_name_code из исходной базы данных.
# - `event_type_description` — описание типа мероприятия.
# - `event_type_main` — основной тип мероприятия: театральная постановка, концерт и так далее.
# - `organizers` — организаторы мероприятия.
# - `region_name` — название региона.
# - `city_name` — название города.
# - `venue_id` — уникальный идентификатор площадки.
# - `venue_name` — название площадки.
# - `venue_address` — адрес площадки.
# 
# Анализ данных в предыдущей части проекта показал, что выручка от заказов представлена в двух валютах — российских рублях и казахстанских тенге. Для удобства решения было бы корректно привести данные к одной валюте, например к российским рублям. Для этого в нашем распоряжении датасет `final_tickets_tenge_df.csv` с информацией о курсе тенге к российскому рублю за 2024 год. Значения в рублях представлено для 100 тенге. Датасет содержит такие поля:
# - `nominal` — номинал (100 тенге).
# - `data` — дата.
# - `curs` — курс тенге к рублю.
# - `cdx` — обозначение валюты (kzt).
# Используем эти данные для конвертации валюты.

# ## Содержимое проекта
# Проведем исследовательский анализ данных, чтобы дать ответы на вопросы коллег. В ходе проекта будем работать с категориями событий, рассчитывать среднюю выручку с заказа и продажи одного билета в рублях, а также изучать распределение значений по категориям и периодам времени.

# ## План
# - Шаг 1. Загрузка данных и знакомство с ними
# - Шаг 2. Предобработка данных и подготовка их к исследованию
# - Шаг 3. Исследовательский анализ данных:
#   - Анализ распределения заказов по сегментам и их сезонные изменения
#   - Осенняя активность пользователей
#   - Популярные события и партнёры
# - Шаг 4. Статистический анализ данных
# - Шаг 5. Общий вывод и рекомендации
# 

# ## 1. Загрузка данных и знакомство с ними
# 
# Загрузим данные трех датасетов:

# In[1]:


# Импортируем библиотеки:
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import levene
from scipy.stats import mannwhitneyu


# In[2]:


#Сформируем датафреймы:
final_tickets_orders_df = pd.read_csv('/datasets/final_tickets_orders_df.csv')
final_tickets_events_df = pd.read_csv('/datasets/final_tickets_events_df.csv')
final_tickets_tenge_df = pd.read_csv('/datasets/final_tickets_tenge_df.csv')


# <div class="alert alert-info">
# <h2> Комментарий студента <a class="tocSkip"> </h2>
# 
# Благодарю за советы! Не помню, чтобы в спринте затрагивалась эта тема, а ведь это действительно важно знать заранее, чтобы уже на реальной работе быть готовым к ошибкам при выгрузке данных
# </div>

# In[3]:


#Отобразим первые 5 строк для знакомства с данными:
display(final_tickets_orders_df.head())
display(final_tickets_events_df.head())
display(final_tickets_tenge_df.head())


# In[4]:


#Проведем базовый анализ структуры данных датафрейма:
final_tickets_orders_df.info()
final_tickets_events_df.info()
final_tickets_tenge_df.info()


# - все данные соответствуют описанию;
# - отсутствуют пропуски во всех столбцах, кроме столбца `days_since_prev` из датафрейма `final_tickets_orders_df` однако, как следует из описания - этот столбец содержит количество дней с предыдущей покупки для каждого пользователя. Если покупки не было, то данные содержат пропуск;
# - столбцы `created_dt_msk` и `created_ts_msk` из датафрейма `final_tickets_orders_df` содержат информацию с датами. Их следует привезти к типу datetime64.

# In[5]:


#Приведем столбцы с датами к типу datetime
final_tickets_orders_df['created_dt_msk'] = pd.to_datetime(final_tickets_orders_df['created_dt_msk'])
final_tickets_orders_df['created_ts_msk'] = pd.to_datetime(final_tickets_orders_df['created_ts_msk'])
final_tickets_tenge_df['data'] = pd.to_datetime(final_tickets_tenge_df['data'])
#Проверим результат
final_tickets_orders_df.info()
final_tickets_tenge_df.info()


# - Окончательно убедимся, что в данных нет пропусков (кроме в столбца `days_since_prev`):

# In[6]:


print(final_tickets_orders_df.isnull().sum())
print(final_tickets_events_df.isnull().sum())
print(final_tickets_tenge_df.isnull().sum())


# - Пропуски содержатся только в столбце `days_since_prev`

# - Изучим столбцы с категориями

# In[7]:


# Объединяем датафреймы
merged_df = final_tickets_orders_df.merge(final_tickets_events_df, on='event_id', how='left')

# Соединяем данные о курсе с основным датафреймом
merged_df = merged_df.merge(final_tickets_tenge_df[['data', 'curs']], left_on='created_dt_msk', right_on='data', how='left')
# Конвертируем kzt в рубли
merged_df['revenue_rub'] = merged_df.apply(lambda row: row['revenue'] * row['curs'] / 100 if row['currency_code'] == 'kzt' else row['revenue'], axis=1)
display(merged_df)


# - Проверим уникальные значения в столбцах с категориями:

# In[8]:


unique_values_1 = merged_df['device_type_canonical'].unique()
print(unique_values_1)
unique_values_2 = merged_df['cinema_circuit'].unique()
print(unique_values_2)
unique_values_3 = merged_df['age_limit'].unique()
print(unique_values_3)
unique_values_4 = merged_df['currency_code'].unique()
print(unique_values_4)
unique_values_5 = merged_df['service_name'].unique()
print(unique_values_5)
unique_values_6 = merged_df['event_type_description'].unique()
print(unique_values_6)
unique_values_7 = merged_df['event_type_main'].unique()
print(unique_values_7)
unique_values_7 = merged_df['region_name'].unique()
print(unique_values_7)


# - 'cinema_circuit' - содержит значение "нет", которое, вероятно, можно интерпретировать, как отсутствие данных, которые закрыли заглушкой.
# - 'event_type_description' - содержит значение "событие", которое, вероятно, можно интерпретировать, как отсутствие данных, которые закрыли заглушкой.
# - 'event_type_main' и 'region_name' - содержит пропуск "nan"

# In[9]:


#Проверяем количество пропусков в столбцах 'event_type_main' и 'region_name'
print(merged_df[['event_type_main', 'region_name']].isna().sum())


# In[10]:


#Удалим обнаруженные пропуски
merged_df = merged_df.dropna(subset=['event_type_main', 'region_name'])
#Проверяем наличие пропусков после удаления:
print(merged_df.isna().sum())


# - Пропуски удалены. Остались пропуски только в столбце days_since_prev, которые мы не будем трогать, т.к. их наличие - оправдано.

# ### Изучим количественные значения по ключевым столбцам - `revenue` и `tickets_count`.
# - Начнем с распределения. Поскольку у нас в датафрейме две валюты - разделим датафреймы на отдельные по значению rub и kzt для корректного анализа распределения:

# In[11]:


df_rub = merged_df[merged_df['currency_code'] == 'rub']
df_kzt = merged_df[merged_df['currency_code'] == 'kzt']


# - Посмотрим на статистические показатели df_rub['revenue']

# In[12]:


df_rub['revenue'].describe()


# Промежуточный вывод:
# - Средняя выручка (mean): 548.01. Это значение показывает среднее значение выручки по всем заказам.
# - Стандартное отклонение (std): 871.75. Высокое стандартное отклонение указывает на то, что значения выручки сильно варьируются относительно среднего значения.
# - Минимальное значение (min): -90.76. Отрицательное значение может указывать на ошибку в данных или на возвраты средств.
# - Максимальное значение (max): 81 174.54. Это крайне высокое значение может быть выбросом и требует дополнительного анализа.

# In[13]:


#Проверим отрицательные значения:
df_rub_sub_zero = df_rub[df_rub['revenue'] <0 ]
display(df_rub_sub_zero.head())


# - В датафрейме действительно есть отрицательные значения. Вероятно, это связано с возвратами денежных средств.

# - Проанализируем выбросы. Начнем с поиска 99-го процентиля:

# In[14]:


ninety_ninth_percentile_rub = df_rub['revenue'].quantile(0.99)
print(ninety_ninth_percentile_rub)


# In[15]:


#Найдем все значения выше 99-го процентиля:
pd.set_option('display.max_columns', None)
more_then_ninety_ninth_percentile = df_rub[df_rub['revenue'] > 2570.8]
display(more_then_ninety_ninth_percentile.head())


# - Вероятно, чем выше общая стоимость заказа, тем больше выручка. Это оправдывает наличие высоких значений выручки.

# - Посмотрим на статистические показатели df_kzt['revenue']

# In[16]:


df_kzt['revenue'].describe()


# Промежуточный вывод:
# - Стандартное отклонение: 4 916.75, что указывает на значительный разброс выручки вокруг среднего значения.
# - Максимальное значение (max): 26 425.86. Это высокое значение может быть выбросом и требует дополнительного анализа.

# In[17]:


ninety_ninth_percentile_kzt = df_kzt['revenue'].quantile(0.99)
print(ninety_ninth_percentile_kzt)


# In[18]:


more_then_ninety_ninth_percentile_kzt = df_kzt[df_kzt['revenue'] > 17617.24]
display(more_then_ninety_ninth_percentile_kzt.head())


# - Вывод, как и по df_rub - чем выше общая стоимость заказа, тем больше выручка. Это оправдывает наличие высоких значений выручки.

# - Проведем аналогичный анализ по столбцу `tickets_count`

# In[19]:


df_rub['tickets_count'].describe()


# Промежуточные выводы:
# - Стандартное отклонение: 1.17, что указывает на относительно небольшой разброс количества билетов вокруг среднего значения.
# - Максимальное количество билетов в одном заказе: 57, что является значительным отклонением от среднего значения и может указывать на наличие выбросов в данных.

# In[20]:


ninety_ninth_percentile_tickets_rub = df_rub['tickets_count'].quantile(0.99)
print(ninety_ninth_percentile_tickets_rub)


# In[21]:


more_then_ninety_ninth_percentile_tickets_rub  = df_rub[df_rub['tickets_count'] > 6]
display(more_then_ninety_ninth_percentile_tickets_rub.head())


# - Предполагаю, что наличие заказов с большим количеством билетов также возможно, т.к. не исключено, что билеты покупала целая организация на своих сотрудников.

# In[22]:


df_kzt['tickets_count'].describe()


# В этом случае данные распределены равномерно: стандартное отклонение не высокое, среднее значение примерно равно медиане и максимальное значение недалеко от 75-го процентиля.

# - Построим гистограммы распределения значений и диаграммы размаха отдельно для rub и kzt - начнем со столбца `revenue`

# In[23]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 5))

# Строим гистограмму с помощью pandas через plot(kind='hist')
df_rub['revenue'].plot(
                kind='hist', # Тип графика - гистограмма
                bins=50, # Устанавливаем количество корзин - всего 50
                alpha=0.75,
                edgecolor='black',
                rot=0, # Градус вращения подписи по оси Х
)

# Настраиваем оформление графика
plt.title('Распределение значений выручки в rub')
plt.xlabel('Выручка')
plt.ylabel('Частота')
# Добавляем сетку графика
plt.grid()

# Выводим график
plt.show()


# In[24]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 3))

# Строим диаграмму размаха значений в столбце revenue
df_rub.boxplot(column='revenue', vert=False)

# Добавляем заголовок и метки оси
plt.title('Распределение значений выручки в rub')
plt.xlabel('Выручка')

# Выводим график
plt.show()


# Данные с широким разбросом и «хвостом» в правой части гистограммы. Такие высокие значения можно отнести к выбросам. Однако сами значения, не выглядят ошибкой, и такое значение выручки вполне реально (например, если некие организации заказывают билеты на всех своих сотрудников, либо компании, которые проводят корпоративные мероприятия для предприятий, получают деньги от заказчика и берет на себя закупку билетов на то или иное мероприятие). 

# In[25]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 5))

# Строим гистограмму с помощью pandas через plot(kind='hist')
df_kzt['revenue'].plot(
                kind='hist', # Тип графика - гистограмма
                bins=50, # Устанавливаем количество корзин - всего 50
                alpha=0.75,
                edgecolor='black',
                rot=0, # Градус вращения подписи по оси Х
)

# Настраиваем оформление графика
plt.title('Распределение значений выручки в kzt')
plt.xlabel('Выручка')
plt.ylabel('Частота')
# Добавляем сетку графика
plt.grid()

# Выводим график
plt.show()


# In[26]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 3))

# Строим диаграмму размаха значений в столбце revenue
df_kzt.boxplot(column='revenue', vert=False)

# Добавляем заголовок и метки оси
plt.title('Распределение значений выручки в kzt')
plt.xlabel('Выручка')

# Выводим график
plt.show()


# - По kzt данные распределены более равномерно, но также с хвостом в правой части гистограммы. Выбросов не так много(но и в этом случае, я не считаю, что это выбросы по той же логике, что и по заказам в рублях по графикам выше), но и заказов в тенге значительно меньше, относительно заказов в рублях.

# - Теперь сделаем те же графики для столбца `tickets_count`

# In[27]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 5))

# Подсчитываем количество билетов в каждой категории
ticket_counts = df_rub['tickets_count'].value_counts().sort_index()

# Строим график
plt.bar(ticket_counts.index, ticket_counts.values, edgecolor='black')

# Настраиваем оформление графика
plt.title('Распределение значений количества билетов в rub')
plt.xlabel('Количество билетов')
plt.ylabel('Частота')
plt.grid()

# Выводим график
plt.show()


# In[28]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 3))

# Строим диаграмму размаха значений в столбце revenue
df_rub.boxplot(column='tickets_count', vert=False)

# Добавляем заголовок и метки оси
plt.title('Распределение значений количества билетов в rub')
plt.xlabel('Количество билетов')

# Выводим график
plt.show()


# - по столбцу `tickets_count` данные содержат выбросы в правой части диаграммы размаха. Такие высокие значения можно отнести к выбросам, однако сами значения - не выглядят ошибкой, и такое значение выручки вполне реально (например, если некие организации заказывают билеты на всех своих сотрудников, либо компании, которые проводят корпоративные мероприятия для предприятий, получают деньги от заказчика и берет на себя закупку билетов на то или иное мероприятие). 

# In[29]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 5))

# Строим гистограмму с помощью pandas через plot(kind='hist')
df_kzt['tickets_count'].plot(
                kind='hist', # Тип графика - гистограмма
                bins=50, # Устанавливаем количество корзин - всего 50
                alpha=0.75,
                edgecolor='black',
                rot=0, # Градус вращения подписи по оси Х
)

# Настраиваем оформление графика
plt.title('Распределение значений количества в kzt')
plt.xlabel('Количество билетов')
plt.ylabel('Частота')
# Добавляем сетку графика
plt.grid()

# Выводим график
plt.show()


# In[30]:


# Создаём контейнер графика matplotlib и задаём его размер
plt.figure(figsize=(15, 3))

# Строим диаграмму размаха значений в столбце revenue
df_kzt.boxplot(column='tickets_count', vert=False)

# Добавляем заголовок и метки оси
plt.title('Распределение значений количества билетов в kzt')
plt.xlabel('Количество билетов')

# Выводим график
plt.show()


# - Графики по количеству билетов по заказам в тенге напоминают нормальное распределение значений

# ### Вывод по распределению значений:
# - С одной стороны, я не считаю данные за пределами 99-го процентиля выбросами, т.к. такие крупные заказы действительно могут быть. Но поскольку такие высокие значения могут исказить общий анализ данных - принимаю решение от них избавиться.

# In[31]:


df_rub = df_rub[(df_rub['revenue'] <= ninety_ninth_percentile_rub) & (df_rub['revenue'] > 0) & (df_rub['tickets_count'] <= ninety_ninth_percentile_tickets_rub) & (df_rub['tickets_count'] > 0)]
df_kzt= df_kzt[(df_kzt['revenue'] <= ninety_ninth_percentile_kzt) & (df_kzt['revenue'] > 0) & (df_kzt['tickets_count'] > 0)]
final_df = pd.concat([df_rub, df_kzt], ignore_index=True)
display(final_df.head())


# ### Проверка наличия дубликатов

# In[32]:


#Проверим наличие явных дубликатов
duplicates = final_df[final_df.duplicated(keep=False)]
print(duplicates)


# - Явных дубликатов не обнаружено

# In[33]:


#Проверим наличие неявных дубликатов по всем признакам, кроме order_id
columns_to_check = final_df.columns.drop('order_id')
special_duplicates = final_df[final_df.duplicated(subset=columns_to_check, keep=False)]
print(special_duplicates.shape[0])
display(special_duplicates.head())


# - Обнаружено 56 неявных дубликатов. Удалим их:

# In[34]:


final_df = final_df.drop_duplicates(subset=columns_to_check, keep='first')
# Проверим результат удаления:
columns_to_check = final_df.columns.drop('order_id')
special_duplicates = final_df[final_df.duplicated(subset=columns_to_check, keep=False)]
print(special_duplicates.shape[0])
display(special_duplicates.head())


# - Удаление прошло успешно. Еще раз ознакомимся с типами данных в итоговом датафрейме

# In[35]:


final_df.info()


# - Снизим разрядность количественных данных:

# In[36]:


# Список столбцов, которые нужно преобразовать
columns_to_convert = ['order_id', 'event_id', 'age_limit', 'city_id', 'tickets_count', 'venue_id']

# Применяем преобразование ко всем выбранным столбцам
final_df[columns_to_convert] = final_df[columns_to_convert].apply(pd.to_numeric, downcast='integer')
final_df.info()


# - Создадим несколько новых столбцов:
#   - one_ticket_revenue_rub — рассчитаем выручку с продажи одного билета на мероприятие.
#   - month — выделим месяц оформления заказа в отдельный столбец.
#   - season — создадим столбец с информацией о сезонности, включая такие категории, как: 'лето', 'осень', 'зима', 'весна'.

# In[37]:


#Вычисляем выручку с одного билета по меропиятию
final_df['one_ticket_revenue_rub'] = final_df['revenue_rub'] / final_df['tickets_count']
display(final_df.head())


# In[38]:


#Создаем столбец с месяцем, вытягивая месяц из даты в столбце created_dt_msk
final_df['month'] = final_df['created_dt_msk'].dt.month
final_df['month'] = pd.to_numeric(final_df['month'], downcast='integer')
display(final_df.head())


# In[39]:


#Сформируем функцию для формирования категорий по месяцам
def determine_season(month):
    if month in [12, 1, 2]:
        return 'зима'
    elif month in [3, 4, 5]:
        return 'весна'
    elif month in [6, 7, 8]:
        return 'лето'
    else:
        return 'осень'

final_df['season'] = final_df['created_dt_msk'].dt.month.apply(determine_season)
display(final_df.head())


# In[40]:


#Посмотрим на итоговый датафрейм
final_df.info()


# ### Вывод после предобработки данных
# - Объединили датафреймы в один
# - Удалили выбросы, оставив данные по значениям в столбцах revenue и tickets_count больше 0 по 99й процентиль
# - Удалили дубликаты
# - Оптимизировали типы данных и уменьшили разрядность количественных значений
# - Создали несколько новых столбцов:
#   - revenue_rub - сконвертировали валюту из тенге в рубли и оставили значения, которые изначально были в рублях
#   - one_ticket_revenue_rub - выручка с одного билета по мероприятиям
#   - month - месяц оформления заказа
#   - season - сезон оформления заказа
# - После всех фильтраций оставили 281700 строк.

# ## Исследовательский анализ данных

# ## Анализ распределения заказов по сегментам и их сезонные изменения

# ### Изучим изменение пользовательской активности в связи с сезонностью. 

# - Для каждого месяца найдем количество заказов и визуализируем результаты.

# In[41]:


grouped = final_df.groupby('month').agg({'order_id': 'count'}, ascending = False).reset_index()
display(grouped)


# In[42]:


plt.figure(figsize=(15, 5))  # Размер фигуры
plt.bar(grouped['month'], grouped['order_id'])
plt.title('Количество заказов по месяцам')
plt.xlabel('Месяц')
plt.ylabel('Количество заказов')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# - Как видим - количество заказов увеличивается с каждым месяцем

# - Для осеннего и летнего периодов сравним распределение заказов билетов по разным категориям: тип мероприятия, тип устройства, категория мероприятия по возрастному рейтингу.

# In[43]:


final_df_summer = final_df[final_df['season'] == 'лето']
grouped_by_event_type_summer = final_df_summer.groupby('event_type_main').agg({'order_id': 'count'}) / final_df_summer['order_id'].count() 
grouped_by_event_type_summer.sort_values(by='event_type_main', ascending=True, inplace=True)
display(grouped_by_event_type_summer)


# In[44]:


final_df_autumn = final_df[final_df['season'] == 'осень']
grouped_by_event_type_autumn = final_df_autumn.groupby('event_type_main').agg({'order_id': 'count'}) / final_df_autumn['order_id'].count()
grouped_by_event_type_autumn.sort_values(by='event_type_main', ascending=True, inplace=True)
display(grouped_by_event_type_autumn)


# In[45]:


grouped_by_device_type_summer = final_df_summer.groupby('device_type_canonical').agg({'order_id': 'count'}) / final_df_summer['order_id'].count()
grouped_by_device_type_summer.sort_values(by='order_id', ascending=True, inplace=True)
grouped_by_device_type_summer.sort_values(by='device_type_canonical', ascending=True, inplace=True)
display(grouped_by_device_type_summer)


# In[46]:


grouped_by_device_type_autumn = final_df_autumn.groupby('device_type_canonical').agg({'order_id': 'count'}) / final_df_autumn['order_id'].count() 
grouped_by_device_type_autumn.sort_values(by='order_id', ascending=True, inplace=True)
grouped_by_device_type_autumn.sort_values(by='device_type_canonical', ascending=True, inplace=True)
display(grouped_by_device_type_autumn)


# In[47]:


grouped_by_age_limit_summer = final_df_summer.groupby('age_limit').agg({'order_id': 'count'}) / final_df_summer['order_id'].count() 
grouped_by_age_limit_summer.sort_values(by='order_id', ascending=True, inplace=True)
grouped_by_age_limit_summer.sort_values(by='age_limit', ascending=True, inplace=True)
display(grouped_by_age_limit_summer)


# In[48]:


grouped_by_age_limit_autumn = final_df_autumn.groupby('age_limit').agg({'order_id': 'count'}) / final_df_autumn['order_id'].count() 
grouped_by_age_limit_autumn.sort_values(by='order_id', ascending=True, inplace=True)
grouped_by_age_limit_autumn.sort_values(by='age_limit', ascending=True, inplace=True)
display(grouped_by_age_limit_autumn)


# - Построим визуализации

# In[49]:


# Построение столбчатой диаграммы
plt.figure(figsize=(15, 5))  # Размер фигуры
ax = plt.gca()  # Получаем текущий axes

# Ширина столбцов
bar_width = 0.2
# Получаем все уникальные типы событий т.к. летом и осенью было разное количество событий - для корректного сравнения нам нужно, чтобы присутсвовало одинаковое количество строк в каждом датафрейме
all_events = grouped_by_event_type_summer.index.union(grouped_by_event_type_autumn.index)

# Заполняем пропущенные значения нулями
grouped_by_event_type_summer = grouped_by_event_type_summer.reindex(all_events, fill_value=0)
display(grouped_by_event_type_summer)
grouped_by_event_type_autumn = grouped_by_event_type_autumn.reindex(all_events, fill_value=0)
display(grouped_by_event_type_autumn)
data_to_plot = pd.concat([grouped_by_event_type_summer, grouped_by_event_type_autumn], keys=['Лето', 'Осень'])


# Рисуем столбцы для летнего периода
data_to_plot.loc['Лето'].plot(kind='bar', color='orange', ax=ax, label='Лето', width=bar_width, position=0)

# Рисуем столбцы для осеннего периода
data_to_plot.loc['Осень'].plot(kind='bar', color='skyblue', ax=ax, label='Осень', width=bar_width, position=1)

plt.title('Сравнение распределения заказов летом и осенью')
plt.xlabel('Тип события')
plt.ylabel('Доля заказов')
plt.legend(title='Сезон')
# После построения графиков
plt.legend(handles=[mpatches.Patch(color='orange', label='Лето'), mpatches.Patch(color='skyblue', label='Осень')], title='Сезон')

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# In[50]:


# Построение столбчатой диаграммы
plt.figure(figsize=(15, 5))  # Размер фигуры
ax = plt.gca()  # Получаем текущий axes

# Ширина столбцов
bar_width = 0.2
data_to_plot = pd.concat([grouped_by_device_type_summer, grouped_by_device_type_autumn], keys=['Лето', 'Осень'])


# Рисуем столбцы для летнего периода
data_to_plot.loc['Лето'].plot(kind='bar', color='orange', ax=ax, label='Лето', width=bar_width, position=0)

# Рисуем столбцы для осеннего периода
data_to_plot.loc['Осень'].plot(kind='bar', color='skyblue', ax=ax, label='Осень', width=bar_width, position=1)

plt.title('Сравнение распределения заказов по типу устройства')
plt.xlabel('Тип устройства')
plt.ylabel('Доля заказов')
plt.legend(title='Сезон')
# После построения графиков
plt.legend(handles=[mpatches.Patch(color='orange', label='Лето'), mpatches.Patch(color='skyblue', label='Осень')], title='Сезон')

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# In[51]:


# Построение столбчатой диаграммы
plt.figure(figsize=(15, 5))  # Размер фигуры
ax = plt.gca()  # Получаем текущий axes

# Ширина столбцов
bar_width = 0.2
data_to_plot = pd.concat([grouped_by_age_limit_summer, grouped_by_age_limit_autumn], keys=['Лето', 'Осень'])


# Рисуем столбцы для летнего периода
data_to_plot.loc['Лето'].plot(kind='bar', color='orange', ax=ax, label='Лето', width=bar_width, position=0)

# Рисуем столбцы для осеннего периода
data_to_plot.loc['Осень'].plot(kind='bar', color='skyblue', ax=ax, label='Осень', width=bar_width, position=1)

plt.title('Сравнение распределения заказов по возрасту пользователей')
plt.xlabel('Возраст пользователя')
plt.ylabel('Доля заказов')
plt.legend(title='Сезон')
# После построения графиков
plt.legend(handles=[mpatches.Patch(color='orange', label='Лето'), mpatches.Patch(color='skyblue', label='Осень')], title='Сезон')

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# ### Изучим изменение выручки с продажи одного билета в зависимости от типа мероприятия летом и осенью.

# In[52]:


#Считаем среднюю выручку с одного билета летом в зависимости от мероприятия:
grouped_by_event_type_summer_revenue_per_ticket = final_df_summer.groupby('event_type_main').agg({'revenue_rub': 'sum', 'tickets_count':'sum'})
grouped_by_event_type_summer_revenue_per_ticket = grouped_by_event_type_summer_revenue_per_ticket['revenue_rub']/grouped_by_event_type_summer_revenue_per_ticket['tickets_count']
display(grouped_by_event_type_summer_revenue_per_ticket)


# In[53]:


#Считаем среднюю выручку с одного билета осенью в зависимости от мероприятия:
grouped_by_event_type_autumn_revenue_per_ticket = final_df_autumn.groupby('event_type_main').agg({'revenue_rub': 'sum', 'tickets_count':'sum'})
grouped_by_event_type_autumn_revenue_per_ticket = grouped_by_event_type_autumn_revenue_per_ticket['revenue_rub']/grouped_by_event_type_autumn_revenue_per_ticket['tickets_count']
display(grouped_by_event_type_autumn_revenue_per_ticket)


# - Объединим датафреймы и посчитаем относительную разницу в выручке с одного билета летом и осенью

# In[54]:


#Выделим уникальные значения из обоих датафреймов
all_events_revenue_per_ticket_by_season = grouped_by_event_type_summer_revenue_per_ticket.index.union(grouped_by_event_type_autumn_revenue_per_ticket)
# Заполняем пропущенные значения в отдельных датафреймах нулями
grouped_by_event_type_summer_revenue_per_ticket = grouped_by_event_type_summer_revenue_per_ticket.reindex(all_events, fill_value=0)
display(grouped_by_event_type_summer_revenue_per_ticket)
grouped_by_event_type_autumn_revenue_per_ticket = grouped_by_event_type_autumn_revenue_per_ticket.reindex(all_events, fill_value=0)
display(grouped_by_event_type_autumn_revenue_per_ticket)
# Объединяем получившиеся датафреймы
revenue_per_ticket_by_season = pd.concat([grouped_by_event_type_summer_revenue_per_ticket, grouped_by_event_type_autumn_revenue_per_ticket], axis=1, keys=['Лето', 'Осень'])
# Посчитаем относительную разницу в выручке с одного билета летом и осенью
revenue_per_ticket_by_season['delta_between_season'] = revenue_per_ticket_by_season.apply(lambda x: 100 if x['Лето'] == 0 else round(((x['Осень'] / x['Лето']) * 100 - 100), 2), axis=1)
display(revenue_per_ticket_by_season)


# - Визуализируем полученные результаты

# In[55]:


plt.figure(figsize=(15, 5))
ax = revenue_per_ticket_by_season['delta_between_season'].plot(kind='bar')

# Задаем цвета для столбцов с положительными и отрицательными значенниями
colors = ['green' if val > 0 else 'red' for val in revenue_per_ticket_by_season['delta_between_season']]
for bar, color in zip(ax.containers[0], colors):
    bar.set_color(color)

plt.title('Изменение выручки с одного билета осенью относительно лета')
plt.xlabel('Тип мероприятия')
plt.ylabel('Относительное изменение (%)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()




# ### Общие выводы по двум предыдущим пунктам:
# - Выделим наиболее отличающиеся значения по выделенным группам между сезонами лето/осень с наибольшими объемами:
#   - Тип мероприятия:
#      - Концерты - летом количество концертов выше, чем осенью - доля заказов 0.44 летом против 0.37 осенью
#      - Театры - осенью количество спектаклей выше, чем осенью - доля заказов 0.25 осенью против 0.21 летом
#      - Также есть разница по типу "другое", но его не будем брать в расчет, т.к. нет понимания, что конкретно подразумевается под "другое", т.к. это, вероятно, заглушка, которая закрывает те строки, по которым нет информации по типу события.
#   - Тип устройства - значения по обоим типам (компьютер и телефон) между сезонами примерно равны.
#   - Возраст пользователя:
#     - 18 и 16 лет - летом 18-ти и 16-ти летние пользователи размещают больше заказов, чем осенью:
#       - 18 - летом 0.14, осенью 0.10
#       - 16 - летом 0.28, осенью 0.26
#     - Также высокая разница по группе "0", но эту группу не будем брать в расчет, т.к. вероятно, что это заглушка, которая закрывает те строки, по которым нет информации по возрасту пользователя, а 0 лет явно не может быть.
# - По 2-м из 7-ти мероприятий наблюдается положительная динамика в размере средней выручки за один билет, а именно: выставки и стендап. По остальным мероприятиям видим снижение средней выручки за билет.

# <div class="alert alert-success">
# <h2> Комментарий ревьюера <a class="tocSkip"> </h2>
# 
# <b>Все отлично!👍:</b> Динамика и структура заказов, а также изменения выручки изучены.

# ## Осенняя активность пользователей

# ### Проанализируем динамику изменений по дням для:
# - общего числа заказов;
# - количества активных пользователей DAU;
# - среднего числа заказов на одного пользователя;
# - средней стоимости одного билета.

# In[56]:


final_df_autumn['date'] = final_df_autumn['created_dt_msk']

# Группируем данные по дате и вычисляем нужные нам значения
final_df_autumn_per_days = final_df_autumn.groupby('date').agg({'order_id': 'count', 'user_id': 'nunique', 'revenue_rub':'sum', 'tickets_count':'sum'})

# Вычисляем среднее количество заказов на одного пользователя
final_df_autumn_per_days['avg_count_orders_by_user'] = final_df_autumn_per_days['order_id'] / final_df_autumn_per_days['user_id']
final_df_autumn_per_days['avg_one_ticket_revenue'] = final_df_autumn_per_days['revenue_rub'] / final_df_autumn_per_days['tickets_count']
final_df_autumn_per_days['revenue_rub'] = final_df_autumn_per_days['revenue_rub'].round(2)
display(final_df_autumn_per_days)


# - Построим линейные графики для отображения динамики по дням по каждому полученному значению

# In[57]:


final_df_autumn_per_days = final_df_autumn_per_days.reset_index()
plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='order_id', x='date')
plt.title('Динамика общего количества заказов по дням')
plt.xlabel('День')
plt.ylabel('Количество заказов')
plt.grid()
plt.show()


# In[58]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='user_id', x='date')
plt.title('Динамика общего количества уникальных пользователей по дням')
plt.xlabel('День')
plt.ylabel('Количество пользователей')
plt.grid()
plt.show()


# In[59]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='revenue_rub', x='date')
plt.title('Динамика общей выручки по дням')
plt.xlabel('День')
plt.ylabel('Выручка (руб)')
plt.grid()
plt.show()


# In[60]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='tickets_count', x='date')
plt.title('Динамика общего количества билетов по дням')
plt.xlabel('День')
plt.ylabel('Количество билетов')
plt.grid()
plt.show() 


# In[61]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='avg_one_ticket_revenue', x='date')
plt.title('Динамика средней выручки за один билет по дням')
plt.xlabel('День')
plt.ylabel('Средняя выручка за один билет')
plt.grid()
plt.show() 


# In[62]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_days.plot(kind='line', y='avg_count_orders_by_user', x='date')
plt.title('Динамика среднего количества заказов на одного пользователя по дням')
plt.xlabel('День')
plt.ylabel('Среднее количество заказов')
plt.grid()
plt.show()  


# ### Изучим недельную цикличность. Выделим день недели и сравните пользовательскую активность в будни и выходные.

# In[63]:


final_df_autumn['day_of_week'] = final_df_autumn['created_dt_msk'].dt.day_name() 
# Переименуем названия дня недели на русский язык:
# Создаём словарь для переименования
day_names_map = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}

# Применяем переименование
final_df_autumn['day_of_week'] = final_df_autumn['day_of_week'].map(day_names_map)
# Отсортируем данные с понедельника по воскресенье:
day_order = {
    'Понедельник': 1,
    'Вторник': 2,
    'Среда': 3,
    'Четверг': 4,
    'Пятница': 5,
    'Суббота': 6,
    'Воскресенье': 7
}

# Сортируем датафрейм по столбцу 'day_of_week' с использованием словаря
final_df_autumn = final_df_autumn.sort_values(by='day_of_week', key=lambda x: x.map(day_order))
# Добавим столбец с типом дня недели (будни, выходные)
final_df_autumn['day_type'] = final_df_autumn['day_of_week'].apply(lambda x: 'выходные' if x in ['Суббота', 'Воскресенье'] else 'будни')

# Группируем данные по дате и вычисляем нужные нам значения
final_df_autumn_per_day_of_week = final_df_autumn.groupby('day_type').agg({'order_id': 'count', 'user_id': 'nunique', 'revenue_rub':'sum', 'tickets_count':'sum'})

# Вычисляем среднее количество заказов на одного пользователя и среднюю выручку с одного билета
final_df_autumn_per_day_of_week['avg_count_orders_by_user'] = final_df_autumn_per_day_of_week['order_id'] / final_df_autumn_per_day_of_week['user_id']
final_df_autumn_per_day_of_week['avg_one_ticket_revenue'] = final_df_autumn_per_day_of_week['revenue_rub'] / final_df_autumn_per_day_of_week['tickets_count']
final_df_autumn_per_day_of_week = final_df_autumn_per_day_of_week.reset_index()
display(final_df_autumn_per_day_of_week)


# - Построим визуализации для сравнения каждого значения по типу дня недели(будни/выходные)

# In[64]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='order_id')
plt.title(f'Сравнение общего количества заказов по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Количество заказов')
plt.grid(axis='y')
plt.show()


# In[65]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='user_id')
plt.title(f'Сравнение общего количества уникальных пользователей по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Количество пользователей')
plt.grid(axis='y')
plt.show()


# In[66]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='revenue_rub')
plt.title(f'Сравнение общего объема выручка по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Выручка')
plt.grid(axis='y')
plt.show()


# In[67]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='tickets_count')
plt.title(f'Сравнение общего количества билетов по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Количество билетов')
plt.grid(axis='y')
plt.show()


# In[68]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='avg_count_orders_by_user')
plt.title(f'Сравнение среднего количества заказов на одного пользователя по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Количество заказов')
plt.grid(axis='y')
plt.show()


# In[69]:


plt.figure(figsize=(15, 5))
final_df_autumn_per_day_of_week.plot(kind='bar', x='day_type', y='avg_one_ticket_revenue')
plt.title(f'Сравнение средней выручки с одного билета по типу дня недели')
plt.xlabel('Тип дня недели')
plt.ylabel('Средняя выручка с билета')
plt.grid(axis='y')
plt.show()


# ### Общие выводы по двум предыдущим пунктам:
# - Анализ динамики по дням:
#    - Общее количество заказов, количество уникальных пользователей, общая выручка, общее кол-во билетов - в целом, эти показатели растут;
#    - По некоторым показателям наблюдаются значительные скачки в начале каждого месяца:
#      - общее кол-во билетов - в начале каждого месяца резкие повышения и сразу же понижения, после чего следует постепенный рост;
#      - средняя выручка с одного билета - резкие понижения в начале месяца, затем значение возвращается в более стабильное
#      - среднее кол-во заказов на одного пользователя - в сентябре почти не превышает трех заказов, а в октябре периодически поднимается до 4х заказов. В начале месяца резкие повышения
#    - Вероятно, в начале месяца действуют акции и глубокие скидки для пользователей, в связи с чем и наблюдается резкое повышение покупки билетов, количества заказов на одного пользователя и понижение выручки (вероятно, как раз за счет скидок: больше скидка = меньше выручка).
# - Анализ активности пользователей по типу дня недели:
#   - Почти по всем показателям выходит, что в будние дни пользователи более активны. В выходные дни только выручка с билета выше, но и заказов меньше, чем в будние дни

# ## Популярные события и партнёры

# ### Посмотрим, как события распределены по регионам и партнёрам. Это позволит выделить ключевые регионы и партнёров, которые вносят наибольший вклад в выручку.

# - Для каждого региона посчитаем уникальное количество мероприятий и общее число заказов. 
# - Для каждого билетного партнёра посчитаем общее число уникальных мероприятий, обработанных заказов и суммарную выручку с заказов билетов.
# - Также расчитаем доли вышеперечисленных метрик от общего объема.

# In[70]:


final_df_autumn_regions = final_df_autumn.groupby('region_name').agg({'event_id':'nunique', 'order_id':'count'})
final_df_autumn_regions = final_df_autumn_regions.sort_values(by = 'event_id', ascending = False)
final_df_autumn_regions['part_of_events'] = final_df_autumn_regions['event_id'] / final_df_autumn_regions['event_id'].sum()
final_df_autumn_regions['part_of_orders'] = final_df_autumn_regions['order_id'] / final_df_autumn_regions['order_id'].sum()
display(final_df_autumn_regions.head())


# In[71]:


final_df_autumn_partners = final_df_autumn.groupby('service_name').agg({'event_id':'nunique', 'order_id':'count', 'revenue_rub':'sum'})
final_df_autumn_partners = final_df_autumn_partners.sort_values(by = 'revenue_rub', ascending = False)
final_df_autumn_partners['part_of_events'] = final_df_autumn_partners['event_id'] / final_df_autumn_partners['event_id'].sum()
final_df_autumn_partners['part_of_orders'] = final_df_autumn_partners['order_id'] / final_df_autumn_partners['order_id'].sum()
final_df_autumn_partners['part_of_revenue'] = (final_df_autumn_partners['revenue_rub'] / final_df_autumn_partners['revenue_rub'].sum()).round(4)
final_df_autumn_partners['revenue_rub'] = final_df_autumn_partners['revenue_rub'].round(2)
display(final_df_autumn_partners)


# - Построим графики распределения по ключевым показателям

# In[72]:


# Сортируем данные по количеству мероприятий в порядке убывания
sorted_regions = final_df_autumn_regions.sort_values(by='event_id', ascending=False)

# Выбираем топ-10 регионов
top_regions = sorted_regions.head(10)

# Строим график
plt.figure(figsize=(15, 5))
plt.bar(top_regions.index, top_regions['event_id'])
plt.title('Топ регионов по уникальному количеству мероприятий')
plt.xlabel('Регион')
plt.ylabel('Количество мероприятий')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--')
plt.show()


# In[73]:


# Сортируем данные по выручке в порядке убывания
sorted_partners = final_df_autumn_partners.sort_values(by='revenue_rub', ascending=False)

# Выбираем топ-10 партнёров
top_partners = sorted_partners.head(10)

# Строим график
plt.figure(figsize=(15, 5))
plt.bar(top_partners.index, top_partners['revenue_rub'])
plt.title('Топ партнёров по общей выручке')
plt.xlabel('Партнёр')
plt.ylabel('Выручка')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--')
plt.show()


# ### Вывод по топам:
# - Среди регионов можно выделить топ-2 по количеству уникальных мероприятий:
#   - 1 - Каменевский регион - 3893 уникальных мероприятия;
#   - 2 - Североярская область - 2594 уникальных меропиятия.
# - Среди партнеров можно выделить топ-6 по объему выручки(взял именно этот параметр, т.к. выручка - ключевой показатель):
#   - 1 - Билеты без проблем - 12 106 370;
#   - 2 - Мой билет - 10 833 720;
#   - 3 - Облачко - 10 611 050;
#   - 4 - Лови билет! - 10 381 140;
#   - 5 - Весь в билетах - 9 350 394;
#   - 6 - Билеты в руки - 7 610 798.
#   
# 

# ## Статистический анализ данных. Проверим несколько гипотез относительно активности пользователей мобильных и стационарных устройств

# ### Гипотеза 1: Среднее количество заказов на одного пользователя мобильного приложения выше по сравнению с пользователями стационарных устройств.

# In[74]:


# Разделим датафрейм на две группы по типу устройств
group_a = final_df_autumn[final_df_autumn['device_type_canonical'] == 'mobile']
group_b = final_df_autumn[final_df_autumn['device_type_canonical'] == 'desktop']

# Находим уникальные идентификаторы пользователей в каждой группе
group_a_unique_user_id = group_a['user_id'].unique()
group_b_unique_user_id = group_b['user_id'].unique()

# Определяем пересечение пользователей
intersection_users = set(group_a_unique_user_id) & set(group_b_unique_user_id)
print(intersection_users)


# In[75]:


# Удаляем пересекающихся пользователей из исходных датафреймов
group_a_without_intersection = group_a[~group_a['user_id'].isin(intersection_users)]
group_b_without_intersection = group_b[~group_b['user_id'].isin(intersection_users)]
# Проверяем пересечение пользователей
intersection_users_after_removal = set(group_a_without_intersection['user_id']) & set(group_b_without_intersection['user_id'])
print(intersection_users_after_removal)


# - Пересечения удалены

# In[76]:


# Подсчитываем количество заказов для каждого пользователя
orders_per_user_mobile = group_a_without_intersection.groupby('user_id').agg({'order_id':'count'})
orders_per_user_desktop = group_b_without_intersection.groupby('user_id').agg({'order_id':'count'})

# Вычисляем среднее количество заказов
average_orders_mobile = orders_per_user_mobile['order_id'].mean()
average_orders_desktop = orders_per_user_desktop['order_id'].mean()

print(f"Среднее количество заказов на одного пользователя мобильного приложения: {average_orders_mobile}")
print(f"Среднее количество заказов на одного пользователя стационарного устройства: {average_orders_desktop}")


# - Проверим объем выборок:

# In[77]:


gr_a = orders_per_user_mobile['order_id'].count()
print(f"Размер выборки группы А: {gr_a}")
gr_b = orders_per_user_desktop['order_id'].count()
print(f"Размер выборки группы А: {gr_b}")


# - Размеры выборок сильно отличаются. Построим график для наглядности:

# In[78]:


# Объёмы выборок
sizes = [gr_a, gr_b]

# Метки для диаграмм
labels = ['Mobile', 'Desktop']

# Построение круговой диаграммы
plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Чтобы диаграмма была круглой
plt.title("Распределение объёма выборок")
plt.show()


# - Проверим распределение в выборах:

# #### Проверка гипотезы
# 
# Гипотеза звучит так: среднее количество заказов на одного пользователя мобильного приложения выше по сравнению с пользователями стационарных устройств. Попробуем статистически это доказать, используя одностороннюю проверку гипотезы с двумя выборками:
# 
# - Нулевая гипотеза H₀: Среднее количество заказов на одного пользователя мобильного приложения не выше по сравнению с пользователями стационарных устройств.
# 
# - Альтернативная гипотеза H₁: Среднее количество заказов на одного пользователя мобильного приложения выше по сравнению с пользователями стационарных устройств.

# - Проведем тест Манна-Уитни в связи с наличием выборов

# In[79]:


# Выполнение теста Манна — Уитни
alpha = 0.05
stat, p_value = mannwhitneyu(orders_per_user_mobile, orders_per_user_desktop, alternative='greater')
if p_value > alpha:
    print(f'p-value теста Манна — Уитни = {round(float(p_value), 2)}')
    print('Нулевая гипотеза находит подтверждение! Среднее количество заказов на одного пользователя мобильного приложения не выше по сравнению с пользователями стационарных устройств')
else:
    print(f'p-value теста Манна — Уитни = {round(float(p_value), 2)}')
    print('Нулевая гипотеза не находит подтверждения! Среднее количество заказов на одного пользователя мобильного приложения выше по сравнению с пользователями стационарных устройств, и это различие статистически значимо')


# ### Гипотеза 2: Среднее время между заказами пользователей мобильных приложений выше по сравнению с пользователями стационарных устройств.

# In[80]:


# Подсчитываем количество заказов для каждого пользователя
group_a_time = group_a_without_intersection['days_since_prev'].reset_index()
group_b_time = group_b_without_intersection['days_since_prev'].reset_index()
# Удалим пропуски из столбца days_since_prev
group_a_time = group_a_time.dropna() 
group_b_time = group_b_time.dropna()
# Вычисляем среднее время между заказами
average_days_since_prev_mobile = group_a_time['days_since_prev'].mean()
average_days_since_prev_desktop = group_b_time['days_since_prev'].mean()
print(f"Среднее время между заказами для мобильных устройств: {average_days_since_prev_mobile} дней")
print(f"Среднее время между заказами для стационарных устройств: {average_days_since_prev_desktop} дней")


# - Проверим размеры выборок

# In[81]:


gr_a_time = group_a_time['days_since_prev'].count()
print(f"Размер выборки группы А: {gr_a_time}")
gr_b_time = group_b_time['days_since_prev'].count()
print(f"Размер выборки группы А: {gr_b_time}")


# - И снова, как и в случае с предыдущей гипотезой - размеры выборок сильно отличаются. Построим график для наглядности:

# In[82]:


# Объёмы выборок
sizes = [gr_a_time, gr_b_time]  

# Метки для диаграмм
labels = ['Mobile', 'Desktop']

# Построение круговой диаграммы
plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Чтобы диаграмма была круглой
plt.title("Распределение объёма выборок")
plt.show()


# - Проверим распределение в выборах:

# #### Проверка гипотезы
# 
# Гипотеза звучит так: среднее время между заказами пользователей мобильных приложений выше по сравнению с пользователями стационарных устройств. Попробуем статистически это доказать, используя одностороннюю проверку гипотезы с двумя выборками:
# 
# - Нулевая гипотеза H₀: Среднее время между заказами пользователей мобильных приложений не выше по сравнению с пользователями стационарных устройств.
# 
# - Альтернативная гипотеза H₁: Среднее время между заказами пользователей мобильных приложений выше по сравнению с пользователями стационарных устройств.

# - Проведем тест Манна-Уитни в связи с наличием выборов

# In[83]:


# Проводим тест Манна-Уитни
alpha = 0.05
stat, p_value = mannwhitneyu(group_a_time['days_since_prev'], group_b_time['days_since_prev'], alternative='greater')

if p_value > alpha:
    print(f'p-value теста Манна — Уитни = {round(p_value, 2)}')
    print('Нулевая гипотеза находит подтверждение! Среднее количество заказов на одного пользователя мобильного приложения не выше по сравнению с пользователями стационарных устройств.')
else:
    print(f'p-value теста Манна — Уитни = {round(p_value, 2)}')
    print('Нулевая гипотеза не находит подтверждения! Среднее время между заказами пользователей мобильных приложений выше по сравнению с пользователями стационарных устройств, и это различие статистически значимо.')
 


# # Общие выводы и рекомендации
# 

# ### Исследовали данные о бронировании билетов на сервисе Яндекс Афиша за период с 1 июня по 30 октября 2024 года:
#   - провели предобработку данных, а именно: удалили часть пропусков; отчистили датафрейм от дубликатов; оптимизировали типы данных с понижением разрядности; обнаружили и устранили выбросы; дополнили датафрейм несколькими столбцами для дальнейшего исследовательского анализа; 
#   - провели исследовательский анализ данных: распределения заказов по сегментам и их сезонные изменения; осенняя активность пользователей; популярные события и партнёры;
#   - проверили гипотезы заказчика путем А/Б тестов.

# ### Основные результаты анализа: 
# - наиболее востребованые мероприятия (посчитали в виде долей от общего числа мероприятий):
#   - Концерты - доля заказов 0.44 летом, 0.37 осенью
#   - Театры - доля заказов 0.25 осенью, 0.21 летом
# - осенью популярность повысилась у следующих мероприятий:
#   - театр - летом доля заказов 0.20, осенью 0.25
#   - спорт - летом доля заказов 0.02, осенью 0.11
# - самое заметное повышение стоимости среднего чека осенью наблюдается по категории мероприятий "стендап" (повышение на 6.25%)
# - самая высокая активность пользователей выпадает на начало сентября и октября. Вероятно, в эти даты организаторы запускают акции и скидки, т.к. кол-во проданных билетов увеличивается, но и также резко падает выручка, что говорит о глубоких скидках. Далее видим повышение притока новых пользователей в течение всего времени наблюдения, что говорит о том, что акции/скидки, вероятно, влияют на привлечение (как и должно быть запланировано организаторами);
# - среди регионов и партнёров существуют явные лидеры по числу заказов и выручке с продажи билетов:
#   - среди регионов можно выделить топ-2 по количеству уникальных мероприятий:
#     - 1 - Каменевский регион - 3893 уникальных мероприятия;
#     - 2 - Североярская область - 2594 уникальных меропиятия.
#   - среди партнеров можно выделить топ-6 по объему выручки(взял именно этот параметр, т.к. выручка - ключевой показатель):
#     - 1 - Билеты без проблем - 12 106 370;
#     - 2 - Мой билет - 10 833 720;
#     - 3 - Облачко - 10 611 050;
#     - 4 - Лови билет! - 10 381 140;
#     - 5 - Весь в билетах - 9 350 394;
#     - 6 - Билеты в руки - 7 610 798.
# - по результату проверки двух гипотез, в обоих случаях нулевые гипотезы были отвергнуты в пользу альтернативных, а именно:
#   - Среднее количество заказов на одного пользователя мобильного приложения выше по сравнению с пользователями стационарных устройств, и это различие статистически значимо
#   - Среднее время между заказами пользователей мобильных приложений выше по сравнению с пользователями стационарных устройств, и это различие статистически значимо.

# ### На основе проведённого анализа можно дать следующие рекомендации и обратить внимание на ключевые аспекты:
# - Анализ популярности мероприятий:
#   - необходимо рассмотреть, с чем связано повышение популярности концертов и театров. Возможно, стоит планировать маркетинговые кампании и расписание мероприятий с учётом этих тенденций, а также проверить, применима ли та же логика к другим меропиятиям, дабы увеличить и их популярность;
# - Акции и скидки:
#   - судя по графикам - рост притока новых покупателей увеличивается, а это значит, что способы привлечения новых клиентов работают и их можно применять и дальше.
#   - проверить, можно ли оптимизировать акции и скидки так, чтобы не было столь серьезного падения средней выручки за билет.
# - Региональные различия:
#   - Каменевский регион и Североярская область являются топовыми регионами по количеству мероприятий. Логично предположить, что спрос в этих регионах довольно высок и можно вложить ресурсы на развитие рынка именно в данных регионах.
#   - не стоит забывать и про регионы с более низкими показателями, чем вышеперечисленные топ-2, но не в момент сезонности, как указано в предыстории задачи. Лучше уделить этому время уже после новогодних праздников. 
# - Сотрудничество с партнёрами:
#   - оцените эффективность сотрудничества с топовыми партнёрами по объёму выручки. Какие спообы применимы к ним, чтобы стимулировать их продолжать проявлять высокую активность по продаже билетов. Рассмотреть, какие типы мероприятий можно раскрутить с помощью топовых партнеров;
# - Использование данных о поведении пользователей:
#   - тесты показали, что с мобильного приложения формируется больше заказов на одного пользователя, чем со стационарного устройства, но в то же время и время между заказами с мобильных приложений выше. Нужно проверить техническую часть приложения: на каких этапах у пользователей могут возникать задержки/баги и т.п. и устранить их. Также стимулировать пользователей возвращаться в приложение чаще, например, с помощью акций, индивидуальных предложений на основе предпочтений пользователей.

# In[ ]:




