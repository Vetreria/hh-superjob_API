import requests
from statistics import mean
import os
import dotenv
from terminaltables import AsciiTable
from itertools import count


def predict_rub_salary(from_sal, to_sal):
    if to_sal and from_sal:
        return (from_sal + to_sal) / 2
    elif to_sal:
        return to_sal * 0.8
    elif from_sal:
        return from_sal * 1.2


def prepare_hh(lang, popular_langs):
    found_count, result_items = fetch_hh(lang)
    salary_result = get_hh_salary(result_items)
    salary_avg, processed_vac = calc_salary(salary_result)
    popular_langs[lang] = {
        "vacancies_found": found_count,
        "vacancies_processed": processed_vac,
        "average_salary": round(salary_avg, 2)
        }
    return popular_langs


def prepare_sj(sj_key, lang, popular_langs):
    found_count, result_items = fetch_superjob(sj_key, lang)
    salary_result = get_sj_salary(result_items)
    salary_avg, processed_vac = calc_salary(salary_result)
    popular_langs[lang] = {
        "vacancies_found": found_count,
        "vacancies_processed": processed_vac,
        "average_salary": round(salary_avg, 2)
        }
    return popular_langs


def get_hh_salary(result_items):
    salary_result = []
    for item in result_items:
        salary_item = item["salary"]
        if salary_item:
            from_sal = salary_item["from"]
            to_sal = salary_item["to"]
            currency_sal = salary_item["currency"]
            if currency_sal == "RUR":
                salary_result.append(predict_rub_salary(from_sal, to_sal))
    return salary_result


def calc_salary(salary_result):
    processed_vac = len(salary_result)
    if len(salary_result):
        salary_avg = mean(salary_result)
    else:
        salary_avg = 0
    return salary_avg, processed_vac


def fetch_hh(lang):
    result_items = []
    page_count = count(start=0, step=1)
    for page in page_count:
        headers = {
            "User-Agent": "api-test-agent' 'https://api.hh.ru/vacancies'"
        }
        params = {
            "clusters": "true",
            "text": f"программист {lang}",
            "area": 1,
            "period": 30,
            "page": page,
            "per_page": 20,
        }
        response = requests.get(
            "https://api.hh.ru/vacancies", headers=headers, params=params
        )
        response.raise_for_status()
        result = response.json()
        found_count = result["found"]
        result_items = result_items + result["items"]
        if page == result["pages"] - 1:
            break
    return found_count, result_items


def print_table(popular_langs, title):
    table_data = [
        (
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        )
    ]
    for lang in popular_langs:
        lang_list = (
            lang,
            popular_langs[lang]["vacancies_found"],
            popular_langs[lang]["vacancies_processed"],
            popular_langs[lang]["average_salary"],
        )
        table_data.append(lang_list)
    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[3] = "right"
    print(table_instance.table)
    print()


def fetch_superjob(sj_key, lang):
    headers = {"X-Api-App-Id": sj_key}
    page_count = count(start=0, step=10)
    result_items = []
    for page in page_count:
        params = {
            "town": "Москва",
            "keywords[0][srws]": "1",
            "keywords[0][skwc]": "and",
            "keywords[0][keys]": lang,
            "catalogues": [48],
            "count": 5,
            "page": page,
        }
        response = requests.get(
            "https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params
        )
        response.raise_for_status()
        result = response.json()
        result_items = result_items + result["objects"]
        found_count = result["total"]
        if not result["more"]:
            break
    return found_count, result_items


def get_sj_salary(result_items):
    salary_result = []
    for object in result_items:
        from_sal = object["payment_from"]
        to_sal = object["payment_to"]
        currency_sal = object["currency"]
        salary_item = predict_rub_salary(from_sal, to_sal)
        if currency_sal == "rub":
            if salary_item:
                salary_result.append(salary_item)
    return salary_result


def main():
    dotenv.load_dotenv()

    langs = [
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "CSS",
        "C#",
        "C",
        "Go",
        "Shell",
        "Objective-C",
        "Scala",
        "Swift",
        "TypeScript",
    ]
    sj_key = os.environ["SJ_KEY"]
    popular_langs_sj = {}
    popular_langs_hh = {}
    for lang in langs:
        prepare_sj(sj_key, lang, popular_langs = popular_langs_sj)
        prepare_hh(lang, popular_langs = popular_langs_hh)
    print_table(popular_langs = popular_langs_sj, title= "SuperJob Moscow")
    print_table(popular_langs = popular_langs_hh, title= "Hh Moscow")


if __name__ == "__main__":
    main()
