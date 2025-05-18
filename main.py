import os
import requests
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()

AREA_MOSCOW = 1
PERIOD_DAYS = 7
SUPERJOB_TOWN_ID = 4
VACANCIES_PER_PAGE = 100

SUPERJOB_API_KEY = os.getenv("SUPERJOB_API_KEY")
HH_USER_AGENT = os.getenv("HH_USER_AGENT", "MyApp/1.0")

HEADERS_HH = {"User-Agent": HH_USER_AGENT}
HEADERS_SUPERJOB = {
    "X-Api-App-Id": SUPERJOB_API_KEY,
    "User-Agent": HH_USER_AGENT,
}

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

def get_hh_vacancies(language, page=0):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": f"Программист {language}",
        "area": AREA_MOSCOW,
        "period": PERIOD_DAYS,
        "page": page,
    }
    try:
        response = requests.get(url, headers=HEADERS_HH, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching HH data for {language}: {e}")
        return None

def get_superjob_vacancies(language, page=0):
    url = "https://api.superjob.ru/2.0/vacancies/"
    params = {
        "keyword": f"Программист {language}",
        "town": SUPERJOB_TOWN_ID,
        "count": VACANCIES_PER_PAGE,
        "page": page,
    }
    try:
        response = requests.get(url, headers=HEADERS_SUPERJOB, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching SuperJob data for {language}: {e}")
        return None

def process_hh_vacancies(language):
    total_vacancies = 0
    salaries = []
    page = 0
    while True:
        data = get_hh_vacancies(language, page)
        if not data or "items" not in data:
            break
        vacancies = data["items"]
        total_vacancies = data.get("found", 0)
        for vacancy in vacancies:
            salary_info = vacancy.get("salary")
            if salary_info and salary_info.get("currency") == "RUR":
                avg_salary = calculate_average_salary(salary_info.get("from"), salary_info.get("to"))
                if avg_salary > 0:
                    salaries.append(avg_salary)
        if page >= data.get("pages", 0) - 1:
            break
        page += 1
    return {
        "vacancies_found": total_vacancies,
        "vacancies_processed": len(salaries),
        "average_salary": int(sum(salaries) / len(salaries)) if salaries else 0,
    }

def process_superjob_vacancies(language):
    total_vacancies = 0
    salaries = []
    page = 0
    while True:
        data = get_superjob_vacancies(language, page)
        if not data or "objects" not in data:
            break
        vacancies = data["objects"]
        total_vacancies = data.get("total", 0)
        for vacancy in vacancies:
            payment_from = vacancy.get("payment_from")
            payment_to = vacancy.get("payment_to")
            currency = vacancy.get("currency")
            if currency == "rub":
                avg_salary = calculate_average_salary(payment_from, payment_to)
                if avg_salary > 0:
                    salaries.append(avg_salary)
        if not data.get("more", False):
            break
        page += 1
    return {
        "vacancies_found": total_vacancies,
        "vacancies_processed": len(salaries),
        "average_salary": int(sum(salaries) / len(salaries)) if salaries else 0,
    }

def print_vacancies_table(stats, platform_name):
    table = PrettyTable()
    table.field_names = ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    for language, data in sorted(stats.items()):
        table.add_row([language.lower(), data["vacancies_found"], data["vacancies_processed"], data["average_salary"]])
    print(f"+{platform_name} Moscow+{'-' * 18}+{'-' * 20}+{'-' * 21}+{'-' * 18}+")
    print(table)

def main():
    hh_stats = {}
    superjob_stats = {}

    for language in PROGRAMMING_LANGUAGES:
        hh_stats[language] = process_hh_vacancies(language)
        superjob_stats[language] = process_superjob_vacancies(language)

    print_vacancies_table(hh_stats, "HeadHunter")
    print_vacancies_table(superjob_stats, "SuperJob")

if __name__ == "__main__":
    main()
