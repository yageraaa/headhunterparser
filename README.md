# Парсер вакансий Head Hunter 




Этот проект включает в себя серию парсера и бота, работающих взаимосвязано для сбора и анализа данных с использованием Python и базы данных PostgreSQL. Проект упакован в Docker для удобства развертывания посредством docker-compose и управления зависимостями.

## Начало работы

Для использования и разработки проекта на локальном уровне необходимо выполнить следующие шаги.

### Предварительные требования

Убедитесь, что на вашей машине установлены следующие программы:
- Docker
- PostgreSQL
- Любая IDE (Pycharm,VS Code)
  
### Настройка и запуск
1. *Создание базы данных и таблицы*

Откройте `psql` на вашем компьютере. Зполните данные так, как указано в квадратных скобках и затем введите пароль, который вы указывали в мастере загрузки PostgreSQL:

```terminal
Server [localhost]: localhost
Database [postgres]: postgres
Port [9999]: 9999
Username [postgres]: postgres
Пароль пользователя postgres:
   ```
После того, как вы успешно войдёте в базу данных  `postgres`, введите данную команду для создания новой базы данных:

```SQL
CREATE DATABASE job_vacancies;
   ```
Откройте заново `psql` и повторите вход, указав в строке `Database` не `postgres`, а `job_vacancies`:

```terminal
Server [localhost]: localhost
Database [postgres]: job_vacancies
Port [9999]: 9999
Username [postgres]: postgres
Пароль пользователя postgres:
   ```
Теперь для создания таблицы осталось ввести только скрипт:

```SQL
CREATE TABLE vacancies (
    hh_id VARCHAR(255) PRIMARY KEY,
    name TEXT,
    area_name TEXT,
    employer TEXT, 
    salary_from NUMERIC,
    salary_to NUMERIC,
    salary_currency TEXT,
    experience TEXT,
    schedule TEXT,
    url TEXT
);
   ```
Готово. Наша таблица создана)
2. *Подготовка файлов*

   2.1. Для начала настройте параметры базы данных в файле `parser.py`, исходя из базы данных, которую вы создали. Ниже приведён пример конфигурации подключения:

   ```python
   DB_CONFIG = {
       'dbname': 'job_vacancies',
       'user': 'postgres',
       'password': 'postgres1234',
       'host': 'localhost'
   }
   ```
   2.2. Создайте бота в Telegram, используя https://t.me/BotFather. После создания вам должны дать уникальный токен. Вставьте данный токен в `bot_parser.py` вместо надписи в кавычках:

   ```python
   TOKEN = 'НЕ ЗАБУДЬТЕ ВСТАВИТЬ ТОКЕН'
   ```
   2.3. Скачайте необходимые библиотеки, если они ещё не установлены

   ```terminal
   pip install requests psycopg2-binary pyTelegramBotAPI unittest2 schedule pandas
   ```
   2.4 Для начала откройте файл `parser.py`. В самом низу файла найдите:
   
    ```python
   if __name__ == '__main__':
    schedule.every(3).days.at("00:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)
   ```
   И исправьте на:

    ```python
   if __name__ == '__main__':
    logging.info("Немедленный запуск функции main для тестирования.")
    main()
   ```
   Нам нужно это сделать для немедленного запуска парсинга вакансий и записи их в бд, так как по умолчанию парсинг автоматически запускается каждые три дня.

3. *Запуск*
  
   Теперь запустите файл `parser.py`. После сообщения `Данные успешно зафиксированы в базе данных` запустите `bot_parser.py` и перейдите к боту, токен которого вы указали. Нажмите на кнопку `Start` и пользуйтесь ботом на здоровье.
   Также используя программу `pgAdmin` вы можете уидеть свою таблицу и данные в ней, введя команду:

   ```SQL
   SELECT * FROM vacancies;
   ```

### Альтернативный запуск проекта с помощью Docker 🐋

Перед началом работы убедитесь, что все файлы расположены в одной папке. Вот список всех необходимых файлов:

- `parser.py` - основной файл парсера.
- `bot_parser.py` - файл бота, который интерпретирует данные.
- `test_parser.py` - тесты для парсера.
- `test_bot_parser.py` - тесты для бот-парсера.
- `Dockerfile.parser` - Dockerfile для парсера.
- `Dockerfile.bot_parser` - Dockerfile для бота-парсера.
- `Dockerfile.test_parser` - Dockerfile для тестов парсера.
- `Dockerfile.test_bot_parser` - Dockerfile для тестов бот-парсера.
- `requirements.txt` - файл с перечнем зависимостей Python.
- `docker-compose.yml` - файл для управления много-контейнерными Docker приложениями.
- `job_vacancies.csv` - CSV файл с данными о вакансиях.
- `Dockerfile.job_vacancies` - Dockerfile для обработки данных о вакансиях.

*Внесём небольше правки в файл `docker-compose.yml`. В самом низу найдите данный фргамент кода и заполните параметры базы данных соответсвенно вашим:*

```docker-compose.yml
   db:
    image: postgres:12
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    ports:
      - "5432:5432"
   ```

*Воспользуемся Docker Compose для сборки и запуска всех контейнеров*

Для начала в терминале перейдём в папку нашего проекта, используя команду `cd \путь\до\папки`. Затем воспользуемся Docker Compose для сборки и запуска всех контейнеров:

```терминал
   docker-compose up --build
   ```

После того, как появятся надписи ниже, вы можете зайти в Docker и во вкладке  `Images` увидеть ваши контейнеры. Все компоненты вашего проекта будут запущены и связаны между собой в одной сети.

 ✔ Container uchebpraktika-parser-1           Created                                                              0.0s
 
 ✔ Container uchebpraktika-db-1               Created                                                              0.0s
 
 ✔ Container uchebpraktika-bot_parser-1       Created                                                              0.0s
 
 ✔ Container uchebpraktika-test_parser-1      Created                                                              0.0s
 
 ✔ Container uchebpraktika-test_bot_parser-1  Created                                                              0.0s


## Работа с проектом

Ваш проект теперь работает и готов к использованию. Парсер автоматически соберёт данные, а бот начнёт свою работу по обработке и реагированию на события.



## Единственный и неповторимый Автор

* *Gera* - *Основной разработчик* - [Профиль](https://github.com/yageraaa)

