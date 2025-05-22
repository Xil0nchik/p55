import os
import requests
from dotenv import load_dotenv
from prettytable import PrettyTable

AREA_MOSCOW = 1
PERIOD_DAYS = 7
SUPERJOB_TOWN_ID = 4
VACANCIES_PER_PAGE = 100

PROGRAMMING_LANGUAGES = [
    "Python", "Java", "JavaScript", "Ruby", "PHP",
    "C++", "C#", "C", "Go", "1C"
]


def calculate_average_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)
    return 0


def fetch_hh_vacancies(language, page=0, headers=None):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": f"Программист {language}",
        "area": AREA_MOSCOW,
        "period": PERIOD_DAYS,
        "page": page,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def fetch_superjob_vacancies(language, page=0, headers=None):
    url = "https://api.superjob.ru/2.0/vacancies/"
    params = {
        "keyword": f"Программист {language}",
        "town": SUPERJOB_TOWN_ID,
        "count": VACANCIES_PER_PAGE,
        "page": page,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def process_hh_vacancies(language, headers):
    total_found = 0
    salaries = []
    page = 0

    while True:
        vacancies_response = fetch_hh_vacancies(language, page, headers)
        vacancies = vacancies_response.get("items", [])
        total_found = vacancies_response.get("found", 0)

        for vacancy in vacancies:
            salary = vacancy.get("salary")
            if salary and salary.get("currency") == "RUR":
                avg_salary = calculate_average_salary(salary.get("from"), salary.get("to"))
                if avg_salary:
                    salaries.append(avg_salary)

        if page >= vacancies_response.get("pages", 0) - 1:
            break
        page += 1

    return {
        "found": total_found,
        "processed": len(salaries),
        "average_salary": int(sum(salaries) / len(salaries)) if salaries else 0,
    }


def process_superjob_vacancies(language, headers):
    total_found = 0
    salaries = []
    page = 0

    while True:
        vacancies_response = fetch_superjob_vacancies(language, page, headers)
        vacancies = vacancies_response.get("objects", [])
        total_found = vacancies_response.get("total", 0)

        for vacancy in vacancies:
            if vacancy.get("currency") == "rub":
                avg_salary = calculate_average_salary(
                    vacancy.get("payment_from"), vacancy.get("payment_to")
                )
                if avg_salary:
                    salaries.append(avg_salary)

        if not vacancies_response.get("more", False):
            break
        page += 1

    return {
        "found": total_found,
        "processed": len(salaries),
        "average_salary": int(sum(salaries) / len(salaries)) if salaries else 0,
    }


def print_vacancies_table(stats_by_language, platform_name):
    table = PrettyTable()
    table.field_names = ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]

    for language, stats in sorted(stats_by_language.items()):
        table.add_row([
            language,
            stats["found"],
            stats["processed"],
            stats["average_salary"]
        ])

    print(f"\n{platform_name} Moscow")
    print(table)


def main():
    load_dotenv()

    hh_user_agent = os.getenv("HH_USER_AGENT", "MyApp/1.0")
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")

    if not superjob_api_key:
        raise RuntimeError("Не указан API-ключ для SuperJob в переменной окружения SUPERJOB_API_KEY")

    headers_hh = {"User-Agent": hh_user_agent}
    headers_superjob = {
        "X-Api-App-Id": superjob_api_key,
        "User-Agent": hh_user_agent,
    }

    hh_stats = {}
    superjob_stats = {}

    for language in PROGRAMMING_LANGUAGES:
        hh_stats[language] = process_hh_vacancies(language, headers_hh)
        superjob_stats[language] = process_superjob_vacancies(language, headers_superjob)

    print_vacancies_table(hh_stats, "HeadHunter")
    print_vacancies_table(superjob_stats, "SuperJob")


if __name__ == "__main__":
    main()
