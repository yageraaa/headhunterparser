CREATE TABLE vacancies (
    hh_id VARCHAR(255) PRIMARY KEY,
    name TEXT,
    area_name TEXT,
    employer TEXT, -- добавляем поле для компании-работодателя
    salary_from NUMERIC,
    salary_to NUMERIC,
    salary_currency TEXT,
    experience TEXT,
    schedule TEXT,
    url TEXT
);