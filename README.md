# Salary Parser: Анализ вакансий программистов (HeadHunter и SuperJob)

Этот проект собирает и анализирует зарплаты программистов в Москве, используя API сайтов HeadHunter и SuperJob. Данные выводятся в виде таблиц в терминале и в виде HTML-страницы, соответствующей стандартам W3C.

## Возможности

* Поддержка популярных языков программирования (Python, Java, JavaScript, C++, и др.)
* Получение количества найденных вакансий, обработанных и средней зарплаты
* Отдельный сбор статистики с HeadHunter и SuperJob
* Обработка всех страниц вакансий
* Генерация HTML-отчёта, валидного по стандартам W3C

## Пример вывода (консоль)

```
+------------------------+-------------------+----------------------+------------------+
| Язык программирования   | Вакансий найдено  | Вакансий обработано  | Средняя зарплата |
+------------------------+-------------------+----------------------+------------------+
| python                 | 1320              | 850                  | 180000           |
| java                   | 1100              | 790                  | 170000           |
+------------------------+-------------------+----------------------+------------------+
```

## Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Xil0nchik/p55
cd p55
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Установите переменные окружения:

### Переменные окружения

Перед запуском убедитесь, что заданы следующие переменные окружения:

| Переменная         | Обязательная | Значение по умолчанию | Назначение                                                                                                 |
| ------------------ | ------------ | --------------------- | ---------------------------------------------------------------------------------------------------------- |
| `SUPERJOB_API_KEY` | Да           | `keysuperjob`         | API-ключ для доступа к SuperJob. Без реального ключа может вернуть тестовые данные.                        |
| `HH_USER_AGENT`    | Нет          | `MyApp/1.0`           | Идентификатор приложения при обращении к API HeadHunter и SuperJob. Используется в заголовке `User-Agent`. |

#### Установка переменных в Linux/macOS:

```bash
export SUPERJOB_API_KEY=ваш_секретный_ключ
export HH_USER_AGENT="MySalaryParser/1.0"
```

#### Установка переменных в Windows (PowerShell):

```powershell
$env:SUPERJOB_API_KEY="ваш_секретный_ключ"
$env:HH_USER_AGENT="MySalaryParser/1.0"
```

4. Запустите скрипт:

```bash
python main.py
```

## Зависимости

* `requests`
* `python-dotenv`
* `prettytable`

## Как это работает

| Функция                             | Назначение                                   |
| ----------------------------------- | -------------------------------------------- |
| `predict_rub_salary()`              | Нормализация зарплат с HeadHunter            |
| `predict_rub_salary_for_superjob()` | Нормализация зарплат с SuperJob              |
| `get_statistic_hh()`                | Получение и анализ вакансий с HeadHunter     |
| `get_superjob_stats()`              | Получение и анализ вакансий с SuperJob       |
| `print_stats_table()`               | Вывод статистики в таблице в консоли (ASCII) |
| `generate_html()`                   | Генерация валидного HTML-отчёта              |

## Лицензия

Проект распространяется под лицензией MIT.
