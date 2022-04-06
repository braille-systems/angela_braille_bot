"""
1. Послать POST-запрос по адресу https://angelina-reader.ru/upload_photo/ с html-формой, в которой указать следующие поля:
file: наше фото
has_public_confirm: False
lang: RU
2. Будет возвращена HTML-страница, в которой можно где-то в javascript-коде найти некий длинный ID (строка типа url: "/result_test/_88514a1791fe4b92a9ba8d83eda205d7/",), который нам понадобится для получения результата.
3. Нужно проверять URL https://angelina-reader.ru/result_test/ID, например, https://angelina-reader.ru/result_test/_88514a1791fe4b92a9ba8d83eda205d7/
Эта страница возвращает текст с одним словом: True или False.
4. Когда на предыдущем шаге получаем True, можно отправиться на страницу https://angelina-reader.ru/result/ID, где уже будет HTML, из которого можно вытянуть распознанный текст и URL фото-результата.

"""
from pathlib import Path

import shutil
import requests
import re
import time

base_url = "https://angelina-reader.ru"


def post_form(filename: Path) -> str:
    files = {"file": open(file=str(filename), mode="rb")}
    data = {"has_public_confirm": "False", "lang": "RU", "process_2_sides": "False"}
    url = base_url + "/upload_photo/"
    r = requests.post(url=url, files=files, data=data)

    id_match = re.search(r"url: \"/result_test/(.*)/\"", r.text)
    groups = id_match.groups()
    if len(groups) != 1:
        raise RuntimeError("unable to find the job ID in the returned web page")
    return id_match.groups()[0]


def result_ready(id: str) -> bool:
    url = f"{base_url}/result_test/{id}/"
    result = requests.get(url=url)
    return True if result.text == "True" else False


def get_result(id: str, out_filename: Path) -> None:
    id_no_underscore = id[1:]  # remove underscore
    img_url = f"{base_url}/static/data/results/{id_no_underscore}.marked.jpg"
    img_response = requests.get(img_url, stream=True)
    if img_response.status_code != 200:
        raise RuntimeError(f"unable to get result for ID {id}")
    with open(str(out_filename), "wb") as fout:
        shutil.copyfileobj(img_response.raw, fout)
    del img_response


def main():
    data_path = Path("data/jane_eyre_p0011.jpg")
    job_id = post_form(data_path)
    while not result_ready(job_id):
        time.sleep(.5)

    out_path = (data_path.parent / "tmp") / (data_path.stem + ".marked.jpg")
    out_path.parent.mkdir(exist_ok=True)
    get_result(id=job_id, out_filename=out_path)


if __name__ == "__main__":
    main()
