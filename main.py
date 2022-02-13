import requests
from statistics import mean
import os
import dotenv
from terminaltables import AsciiTable


def predict_rub_salary(salary_item):
    from_sal = salary_item["from"]
    to_sal = salary_item["to"]
    currency_sal = salary_item["currency"]
    if currency_sal == "RUR":
        if to_sal is not None and from_sal is not None:
            return (from_sal + to_sal) / 2
        elif to_sal is None and from_sal is not None:
            return from_sal * 1.2
        elif to_sal is not None and from_sal is None:
            return to_sal * 0.8
    else:
        return None


def predict_rub_salary_for_superJob(from_sal, to_sal, currency_sal):
    if currency_sal == "rub":
        if to_sal != 0 and from_sal != 0:
            return (from_sal + to_sal) / 2
        elif to_sal == 0 and from_sal != 0:
            return from_sal * 1.2
        elif to_sal != 0 and from_sal == 0:
            return to_sal * 0.8
    else:
        return None


def get_request(lang, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    }
    response = requests.get(
        f"https://api.hh.ru/vacancies?clusters=true&text=NAME:программист {lang}&area=1&period=30&page={page}&per_page=100",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def get_vacancies(langs):
    popular_langs = {}
    for lang in langs:
        result_items = []
        page = 0
        pages = 0
        salary_result = []
        while page <= pages:
            result = get_request(lang, page)
            pages = result["pages"] - 1
            page += 1
            found_count = result["found"]
            popular_langs[lang] = {"vacancies_found": found_count}
            result_items = result_items + result["items"]
        for item in result_items:
            salary_item = item["salary"]
            if salary_item is not None:
                if predict_rub_salary(salary_item) is not None:
                    salary_result.append(predict_rub_salary(salary_item))
        popular_langs[lang].update({"vacancies_processed": len(salary_result)})
        if len(salary_result):
            salary_avg = mean(salary_result)
            popular_langs[lang].update({"average_salary": round(salary_avg, 2)})
        else:
            popular_langs[lang].update({"average_salary": "нет данных"})
    title = "Hh Moscow"
    make_table(popular_langs, title)


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


def superjob_rquest(sj_key, langs):
    popular_langs = {}
    headers = {"X-Api-App-Id": sj_key}
    for lang in langs:
        salary_result = []
        page_result = 0
        more_result = True
        result_items = []
        while more_result == True:
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
            result_objects = result["objects"]
            page_result += 1
            more_result = result["more"]
            popular_langs[lang] = {"vacancies_found": result["total"]}
            result_items = result_items + result["objects"]
        for object in result_objects:
            from_sal = object["payment_from"]
            to_sal = object["payment_to"]
            currency_sal = object["currency"]
            salary_item = predict_rub_salary_for_superJob(
                from_sal, to_sal, currency_sal
            )
            if salary_item is not None:
                salary_result.append(salary_item)
        popular_langs[lang].update({"vacancies_processed": len(salary_result)})
        if len(salary_result):
            salary_avg = mean(salary_result)
            popular_langs[lang].update({"average_salary": round(salary_avg, 2)})
        else:
            popular_langs[lang].update({"average_salary": "нет данных"})
            popular_langs[lang].update({"vacancies_processed": len(salary_result)})
    title = "SuperJob Moscow"
    make_table(popular_langs, title)


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
    get_vacancies(langs)
    superjob_rquest(sj_key, langs)


if __name__ == "__main__":
    main()
