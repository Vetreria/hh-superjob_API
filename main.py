import requests
from statistics import mean
import os
import dotenv
from terminaltables import AsciiTable


def predict_rub_salary(from_sal, to_sal):
    if to_sal and from_sal:
        return (from_sal + to_sal) / 2
    elif not to_sal:
        return from_sal * 1.2
    elif not from_sal:
        return to_sal * 0.8


def prepar_hh(langs):
    popular_langs = {}
    for lang in langs:
        found_count, result_items = fetch_hh(lang)
        salary_result = get_salarys_hh(result_items)
        salary_avg, processed_vac = calc_salary(salary_result)
        popular_langs[lang] = {"vacancies_found": found_count}
        popular_langs[lang].update({"vacancies_processed": processed_vac})
        popular_langs[lang].update({"average_salary": round(salary_avg, 2)})
    title = "Hh Moscow"
    make_table(popular_langs, title)

def prepar_sj(sj_key, langs):
    popular_langs = {}
    for lang in langs:
        found_count, result_items = fetch_superjob(sj_key, lang)
        salary_result = get_salarys_sj(result_items)
        salary_avg, processed_vac = calc_salary(salary_result)
        popular_langs[lang] = {"vacancies_found": found_count}
        popular_langs[lang].update({"vacancies_processed": processed_vac})
        popular_langs[lang].update({"average_salary": round(salary_avg, 2)})
    title = "SuperJob Moscow"
    make_table(popular_langs, title)


def get_salarys_hh(result_items):
    salary_result = []
    for item in result_items:
        salary_item = item["salary"]
        if salary_item:
            from_sal = salary_item["from"]
            to_sal = salary_item["to"]
            currency_sal = salary_item["currency"]
            if currency_sal == 'RUR':
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
    page = 0
    pages = 0
    while page <= pages:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        }
        params = {
                "clusters": "true",
                "text": f"программист {lang}",
                "area": 1,
                "period": 30,
                "page": page,
                "per_page": 100
            }
        response = requests.get("https://api.hh.ru/vacancies",
        headers=headers, params=params
        )
        response.raise_for_status()
        result = response.json()
        pages = result["pages"] - 1
        page += 1
        found_count = result["found"]
        result_items = result_items + result["items"]
    return found_count, result_items


def make_table(popular_langs, title):
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
    page_result = 0
    more_result = True
    result_items = []
    while more_result:
            params = {
                "town": "Москва",
                "keywords[0][srws]": "1",
                "keywords[0][skwc]": "and",
                "keywords[0][keys]": lang,
                "catalogues": [48],
                "count": 5,
                "page": page_result,
            }
            response = requests.get(
                "https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params
            )
            response.raise_for_status()
            result = response.json()
            page_result += 1
            more_result = result["more"]
            result_items = result_items + result["objects"]
            found_count =result["total"]
    return found_count, result_items


def get_salarys_sj(result_items):
    salary_result = []
    for object in result_items:
            from_sal = object["payment_from"]
            to_sal = object["payment_to"]
            currency_sal = object["currency"]
            salary_item = predict_rub_salary(from_sal, to_sal)
            if currency_sal == 'rub':
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
    prepar_hh(langs)
    prepar_sj(sj_key, langs)


if __name__ == "__main__":
    main()
