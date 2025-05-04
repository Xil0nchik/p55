import requests
from itertools import count
from terminaltables import AsciiTable
import os


def predict_rub_salary(salary):
    if salary and salary["currency"] == "RUR":
        if salary["from"] and salary["to"]:
            return int((salary["from"] + salary["to"]) / 2)
        elif salary["from"]:
            return int(salary["from"] * 1.2)
        elif salary["to"]:
            return int(salary["to"] * 0.8)
    return None


def predict_rub_salary_for_superjob(vacancy):
    payment_from = vacancy.get("payment_from")
    payment_to = vacancy.get("payment_to")
    currency = vacancy.get("currency")
    if currency != "rub":
        return None
    if payment_from and payment_to:
        return int((payment_from + payment_to) / 2)
    elif payment_from:
        return int(payment_from * 1.2)
    elif payment_to:
        return int(payment_to * 0.8)
    return None


def get_statistic_hh(languages):
    vacancies_summary = {}
    for language in languages:
        total_salary = []
        vacancies_found = 0
        for page in count(0):
            payload = {
                "text": f"Программист {language}",
                "area": "1",
                "period": "7",
                "page": page,
            }
            try:
                response = requests.get("https://api.hh.ru/vacancies", params=payload)
                response.raise_for_status()
                data = response.json()
                if page == 0:
                    vacancies_found = data.get("found", 0)
                if page >= data.get("pages", 0) - 1 or not data.get("items"):
                    break
                for vacancy in data["items"]:
                    salary = predict_rub_salary(vacancy.get("salary"))
                    if salary:
                        total_salary.append(salary)
            except requests.RequestException as e:
                print(f"Error fetching HH data for {language}: {e}")
                break
        average_salary = (
            int(sum(total_salary) / len(total_salary)) if total_salary else 0
        )
        vacancies_summary[language.lower()] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(total_salary),
            "average_salary": average_salary,
        }
    return vacancies_summary


def get_superjob_stats(languages):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": os.getenv(
            "SUPERJOB_API_KEY",
            "keysuperjob",
        )
    }
    stats = {}
    for language in languages:
        salaries = []
        vacancies_processed = 0
        vacancies_found = 0
        for page in count(start=0):
            params = {
                "count": 100,
                "page": page,
                "keyword": f"Программист {language}",
                "town": 4,  # Moscow
            }
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if page == 0:
                    vacancies_found = data.get("total", 0)
                for vacancy in data.get("objects", []):
                    salary = predict_rub_salary_for_superjob(vacancy)
                    if salary:
                        salaries.append(salary)
                        vacancies_processed += 1
                if not data.get("more"):
                    break
            except requests.RequestException as e:
                print(f"Error fetching SuperJob data for {language}: {e}")
                break
        average_salary = int(sum(salaries) / len(salaries)) if salaries else 0
        stats[language.lower()] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }
    return stats


def print_stats_table(stats, platform="SuperJob"):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]
    for lang, data in sorted(stats.items()):
        table_data.append(
            [
                lang,
                str(data["vacancies_found"]),
                str(data["vacancies_processed"]),
                str(data["average_salary"]),
            ]
        )
    table = AsciiTable(table_data, f"{platform} Moscow")
    return table.table


if __name__ == "__main__":
    languages = [
        "Python",
        "Java",
        "JavaScript",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
        "1C",
    ]
    hh_stats = get_statistic_hh(languages)
    sj_stats = get_superjob_stats(languages)
    print(print_stats_table(hh_stats, platform="HeadHunter"))
    print(print_stats_table(sj_stats, platform="SuperJob"))
