import requests
import psycopg2
import logging
import schedule
import time

#настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Подключение к бд Postgre
DB_CONFIG = {
    'dbname': 'job_vacancies',
    'user': 'postgres',
    'password': 'postgres1234',
    'host': 'localhost'
}

def fetch_vacancies(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        logging.info("Данные успешно получены с URL: %s", url)
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"Ошибка HTTP: {e}")
        return None

def save_vacancies_to_db(conn, vacancies):
    if vacancies is None:
        logging.warning("Нет данных о вакансиях для сохранения.")
        return
    cur = conn.cursor()

    for item in vacancies['items']:
        hh_id = item.get('id')
        name = item.get('name')
        area_name = item.get('area', {}).get('name')
        employer = item.get('employer', {}).get('name')
        salary_from = item.get('salary', {}).get('from') if item.get('salary') else None
        salary_to = item.get('salary', {}).get('to') if item.get('salary') else None
        salary_currency = item.get('salary', {}).get('currency') if item.get('salary') else None
        experience = item.get('experience', {}).get('name')
        schedule = item.get('schedule', {}).get('name')
        url = item.get('alternate_url')

        insert_query = """
        INSERT INTO vacancies (hh_id, name, area_name, employer, salary_from, salary_to, salary_currency, experience, schedule, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (hh_id) DO NOTHING;
        """
        cur.execute(insert_query, (hh_id, name, area_name, employer, salary_from, salary_to, salary_currency, experience, schedule, url))
        logging.info(f"Вакансия с ID {hh_id} сохранена в базу данных.")

    conn.commit()
    logging.info("Данные успешно зафиксированы в базе данных.")


def main():
    DB_CONFIG = {
        'dbname': 'job_vacancies',
        'user': 'postgres',
        'password': 'postgres1234',
        'host': 'localhost'
    }
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except TypeError as e:
        print(f"Ошибка типа: {e}")
        return

    page = 0
    while True:
        data = fetch_vacancies('https://api.hh.ru/vacancies',
                               {'text': 'Python', 'page': page, 'per_page': 20})
        if not data or not data['items']:
            break
        save_vacancies_to_db(conn, data)
        page += 1

    conn.close()
def job():
    logging.info("Запуск парсинга...")
    main()
#Парсинг вакансий и занесение в бд каждые три дня
if __name__ == '__main__':
    schedule.every(3).days.at("00:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)

#если надо будет проверить, что всё точно парсится то вот код
#if __name__ == '__main__':
    #logging.info("Немедленный запуск функции main для тестирования.")
    #main()
