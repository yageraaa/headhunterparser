import telebot
from telebot import types
import psycopg2
import time
from collections import defaultdict

TOKEN = 'НЕ ЗАБУДЬТЕ ВСТАВИТЬ ТОКЕН'
bot = telebot.TeleBot(TOKEN)

DB_CONFIG = {
    'dbname': 'job_vacancies',
    'user': 'postgres',
    'password': 'postgres1234',
    'host': 'localhost',
    'port': '9999'
}

user_states = {}
def get_vacancies(query, params):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query, params)
    vacancies = cur.fetchall()
    cur.close()
    conn.close()
    print("Fetched vacancies:", vacancies)
    return vacancies

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 "Приветствую, для более удобного взаимодействия с ботом, ознакомьтесь с командами.\n\n"
                 "Для поиска введите название вакансии в поле ввода текста.\nИспользуйте /filters для настройки "
                 "фильтров.\nИспользуйте /stop для остановки отправки вакансий, а для возобновления /resume.\n\n"
                 "*Для более удобного управления ботом используйте меню команд (три горизонтальные полоски слева от "
                 "поля ввода текста).*",
                 parse_mode='Markdown')

user_filters = {}

def set_city_filter(user_id, city):
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['city'] = city
def set_salary_filter(user_id, salary_from, salary_to):
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['salary_from'] = salary_from
    user_filters[user_id]['salary_to'] = salary_to

def set_schedule_filter(user_id, schedule):
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['schedule'] = schedule


def set_filter(user_id, filter_name, *values):
    if user_id not in user_filters:
        user_filters[user_id] = {}
    if len(values) == 1:
        user_filters[user_id][filter_name] = values[0]
    else:
        user_filters[user_id][filter_name] = values

@bot.message_handler(commands=['filters'])
def vacancy_filters(message):
    markup = types.InlineKeyboardMarkup()
    itembtn1 = types.InlineKeyboardButton('По городу', callback_data='filter_city')
    itembtn2 = types.InlineKeyboardButton('По зарплате', callback_data='filter_salary')
    itembtn3 = types.InlineKeyboardButton('По графику', callback_data='filter_schedule')
    markup.add(itembtn1)
    markup.add(itembtn2)
    markup.add(itembtn3)
    user_states[message.chat.id] = False
    bot.send_message(message.chat.id, "Выберите фильтр:", reply_markup=markup)

@bot.message_handler(commands=['resetfilters'])
def reset_filters(message):
    user_id = message.chat.id
    reset_user_filters(user_id)
    bot.send_message(user_id, "Все ваши фильтры были сброшены. Вы можете установить новые фильтры или начать поиск "
                              "вакансий без фильтров.")
def reset_user_filters(user_id):
    if user_id in user_filters:
        del user_filters[user_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('filter_'))
def handle_filters(call):
    # Получаем ID пользователя из коллбэка
    user_id = call.message.chat.id

    if call.data == 'filter_city':
        msg = bot.send_message(call.message.chat.id, "Введите город:")
        bot.register_next_step_handler(msg, set_city)
    elif call.data == 'filter_salary':
        msg = bot.send_message(user_id,
                               "Укажите интересующую зарплату в формате: МИН-МАКС (60000-120000)")
        bot.register_next_step_handler(msg, set_salary, user_id)
    elif call.data == 'filter_schedule':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Полный день', callback_data='schedule_full')
        button2 = types.InlineKeyboardButton('Гибкий график', callback_data='schedule_flexible')
        button3 = types.InlineKeyboardButton('Удаленная работа', callback_data='schedule_remote')
        markup.add(button1)
        markup.add(button2)
        markup.add(button3)
        bot.send_message(call.message.chat.id, "Выберите график работы:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_'))
def handle_schedule(call):
    user_id = call.message.chat.id
    schedule = ''
    if call.data == 'schedule_full':
        schedule = 'Полный день'
    elif call.data == 'schedule_flexible':
        schedule = 'Гибкий график'
    elif call.data == 'schedule_remote':
        schedule = 'Удаленная работa'

    set_schedule(user_id, schedule)
    try:
        bot.send_message(user_id, f"Фильтр по графику работы установлен: {schedule}.\nУстановите ещё один фильтр "
                                  f"используя,"
                                      f"/filters или начните поиск, написав интересующее имя вакансии в поиск")
    except Exception as e:
        print(f"Failed to send message with error: {e}")
    bot.answer_callback_query(call.id)


def set_schedule(user_id, schedule_text):
    set_schedule_filter(user_id, schedule_text)
def set_city(message):
    user_id = message.chat.id
    city = message.text
    set_city_filter(user_id, city)
    bot.send_message(user_id, f"Фильтр по городу установлен: {city}.\nУстановите ещё один фильтр, используя"
                                      f" /filters или начните поиск, написав интересующее имя вакансии в поиск")
def set_salary(message, user_id):
    text = message.text.lower()
    salary_range = text.replace('от', '').replace('до', '').strip().split('-')

    salary_from = None
    salary_to = None

    if 'от' in text and 'до' in text:
        salary_from = int(salary_range[0].strip())
        salary_to = int(salary_range[1].strip())
    elif 'от' in text:
        salary_parts = salary_range[0].strip().split()
        salary_from = int(salary_parts[0])
    elif 'до' in text:
        salary_parts = salary_range[0].strip().split()
        salary_to = int(salary_parts[0])
    elif len(salary_range) == 2:
        salary_from = int(salary_range[0].strip())
        salary_to = int(salary_range[1].strip())
    elif len(salary_range) == 1 and salary_range[0].isdigit():
        salary_from = int(salary_range[0].strip())
    else:
        bot.send_message(user_id, "Пожалуйста, укажите зарплату корректно.")
        return

    set_salary_filter(user_id, salary_from, salary_to)
    response_text = ("Фильтр по зарплате установлен.\nУстановите ещё один фильтр, используя /filters или начните поиск,"
                     "написав интересующее имя вакансии в поиск")
    if salary_from:
        response_text += f" От {salary_from}."
    if salary_to:
        response_text += f" До {salary_to}."
    bot.send_message(user_id, response_text)


@bot.message_handler(commands=['stop'])
def stop_sending(message):
    user_states[message.chat.id] = False
    bot.reply_to(message, "Отправка вакансий остановлена. Используйте команду /resume для возобновления.")

@bot.message_handler(commands=['resume'])
def resume_sending(message):
    user_states[message.chat.id] = True
    bot.reply_to(message, "Возобновление отправки вакансий. Пожалуйста, повторите ваш поиск.")
def generate_markdown_vacancy_message(vacancy):
    if len(vacancy) < 9:
            raise ValueError("Expected 9 values from the query result, got less. Received: {}".format(vacancy))
    name, salary_from, salary_to, salary_currency, employer, area_name, url, schedule, experience = vacancy

    salary = "не указано"
    if salary_from and salary_to:
        salary = f"от {salary_from} до {salary_to}"
    elif salary_from:
        salary = f"от {salary_from}"
    elif salary_to:
        salary = f"до {salary_to}"
    if salary_currency:
        salary += f" {salary_currency}"

    schedule_info = schedule if schedule else "не указан"
    experience_info = experience if experience else "не требуется или не указан"

    return f"*{name}*\nЗарплата: {salary}\nРаботодатель: {employer}\nГород: {area_name}\nГрафик работы: {schedule_info}\nОпыт: {experience_info}\nСсылка на вакансию: {url}"
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    search_text = message.text
    user_id = message.chat.id
    words = search_text.split()
    filters = user_filters.get(user_id, {})

    user_states[user_id] = True

    query_parts = [
        "SELECT name, salary_from, salary_to, salary_currency, employer, area_name, url, schedule, experience",
        "FROM vacancies",
    ]
    query_conditions = ["name ILIKE %s" for word in words]
    query_parts.append("WHERE " + " AND ".join(query_conditions))

    params = ["%{}%".format(word.lower()) for word in words]

    if 'city' in filters:
        query_parts.append("AND area_name = %s")
        params.append(filters['city'])
    if 'salary_from' in filters:
        query_parts.append("AND salary_from >= %s")
        params.append(filters['salary_from'])
    if 'salary_to' in filters:
        query_parts.append("AND salary_to <= %s")
        params.append(filters['salary_to'])
    if 'schedule' in filters:
        query_parts.append("AND schedule = %s")
        params.append(filters['schedule'])

    full_query = " ".join(query_parts)
    vacancies = get_vacancies(full_query, tuple(params))

    if vacancies:
        salary_info = defaultdict(list)
        target_currencies = ['RUR', 'USD', 'KZT', 'BYR', 'UZS', 'KGS', 'EUR', 'TZS']
        for v in vacancies:
            if v[3] in target_currencies:
                salary_from = v[1] if v[1] is not None else v[2]
                salary_to = v[2] if v[2] is not None else v[1]
                salary_info[v[3]].append((salary_from, salary_to))

        salary_message = f"Найдено вакансий: {len(vacancies)}\n"
        for currency, salaries in salary_info.items():
            min_salary = min(s[0] for s in salaries)
            max_salary = max(s[1] for s in salaries)
            avg_salary = int(sum((s[0] + s[1]) / 2 for s in salaries) / len(salaries))
            salary_message += (f"Для {currency}: минимальная: {min_salary}, максимальная: {max_salary}, "
                               f"средняя: {avg_salary}\n")

        bot.send_message(user_id, salary_message)

        for vacancy in vacancies:
            if user_states.get(user_id, True):
                try:
                    bot.send_message(user_id, generate_markdown_vacancy_message(vacancy), parse_mode='Markdown')
                    time.sleep(1)
                except telebot.apihelper.ApiTelegramException as e:
                    if e.error_code == 429:
                        wait_time = e.result_json['parameters']['retry_after']
                        print(f"Слишком много запросов. Повторная отправка через {wait_time} секунд.")
                        time.sleep(wait_time)
                        bot.send_message(user_id, generate_markdown_vacancy_message(vacancy), parse_mode='Markdown')
            else:
                break
    else:
        bot.send_message(user_id, "По вашему запросу вакансии не найдены.")

bot.polling()
