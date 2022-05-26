"""
1. Послать POST-запрос по адресу https://angelina-reader.ru/upload_photo/ с html-формой, в которой указать следующие поля:
file: наше фото
has_public_confirm: False
lang: RU
2. Будет возвращена HTML-страница, в которой можно где-то в javascript-коде найти некий длинный ID
(строка типа url: "/result_test/_88514a1791fe4b92a9ba8d83eda205d7/"),
который нам понадобится для получения результата.
3. Нужно проверять URL https://angelina-reader.ru/result_test/ID, например,
 https://angelina-reader.ru/result_test/_88514a1791fe4b92a9ba8d83eda205d7/
Эта страница возвращает текст с одним словом: True или False.
4. Когда на предыдущем шаге получаем True, можно отправиться на страницу https://angelina-reader.ru/result/ID,
где уже будет HTML, из которого можно вытянуть распознанный текст и URL фото-результата.

"""
from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from bs4 import BeautifulSoup
from pathlib import Path

import shutil
import requests
import re
import time

base_url = "https://angelina-reader.ru"


class Lang(Enum):
    ru = "RU",
    en = "EN",
    greek = "GR",
    lv = "LV",
    uzc = "UZ",
    uzl = "UZL",
    polski = "PL"

    def __str__(self):
        return self.value[0]


lang_inv_map = {item.value[0]: item for item in Lang}


@dataclass
class RecognitionParams:  # TODO to separate file (e.g. params.py), create a parent class for recognition/bot params
    has_public_confirm: bool
    lang: Lang
    two_sides: bool
    auto_orient: bool

    receive_txt: bool
    receive_img: bool
    receive_msg: bool

    has_public_confirm_key = "has_public_confirm"
    lang_key = "lang"
    two_sides_key = "process_2_sides"
    auto_orient_key = "find_orientation"
    receive_txt_key = "receive_txt"
    receive_msg_key = "receive_msg"
    receive_img_key = "receive_img"

    def get_data_dict(self):
        return {self.has_public_confirm_key: str(bool(self.has_public_confirm)),
                self.lang_key: self.lang.value[0],
                self.two_sides_key: str(bool(self.two_sides)),
                self.auto_orient_key: str(bool(self.auto_orient)),
                self.receive_txt_key: str(bool(self.receive_txt)),
                self.receive_img_key: str(bool(self.receive_img)),
                self.receive_msg_key: str(bool(self.receive_msg))}

    true_false_selector = {True: "Да", False: "Нет"}
    lang_selector = {
        Lang.ru: "Русский",
        Lang.en: "Английский",
        Lang.lv: "Латвийский",
        Lang.greek: "Греческий",
        Lang.uzc: "Узбекский (Кириллица)",
        Lang.uzl: "Узбекский (Латиница)",
        Lang.polski: "Польский"
    }

    options = {
        lang_key: "Язык",
        auto_orient_key: "Автоориентация",
        two_sides_key: "Обе стороны",
        has_public_confirm_key: "Публичное использование фото",

        receive_txt_key: "Получать текстовый файл с результатом",
        receive_img_key: "Получать изображение с результатом",
        receive_msg_key: "Получать сообщение с результатом"
    }

    emoji = {
        lang_key: "🈳",
        auto_orient_key: "🔄",
        two_sides_key: "📄",
        has_public_confirm_key: "🌐",
        receive_txt_key: "📋",
        receive_img_key: "🖼️",
        receive_msg_key: "💬"
    }

    def get_selector(self) -> dict:
        return {
            self.lang_key: [self.lang_selector, self.lang],
            self.auto_orient_key: [self.true_false_selector, self.auto_orient],
            self.two_sides_key: [self.true_false_selector, self.two_sides],
            self.has_public_confirm_key: [self.true_false_selector, self.has_public_confirm],
            self.receive_txt_key: [self.true_false_selector, self.receive_txt],
            self.receive_img_key: [self.true_false_selector, self.receive_img],
            self.receive_msg_key: [self.true_false_selector, self.receive_msg]
        }

    def __repr__(self):
        selector = (f"{RecognitionParams.emoji[k]} {RecognitionParams.options[k]}: {v[0][v[1]]}"
                    for k, v in self.get_selector().items())
        return "Настройки:\n" + "\n".join(selector)


def post_form(filename: Path, params: RecognitionParams) -> str:
    files = {"file": open(file=str(filename), mode="rb")}
    data = params.get_data_dict()
    print(data)
    url = base_url + "/upload_photo/"
    r = requests.post(url=url, files=files, data=data)

    id_match = re.search(r"url: \"/result_test/(.*)/\"", r.text)
    groups = id_match.groups()  # type: ignore
    if len(groups) != 1:
        raise RuntimeError("unable to find the job ID in the returned web page")
    return id_match.groups()[0]  # type: ignore


def result_ready(id: str) -> bool:
    url = f"{base_url}/result_test/{id}/"
    result = requests.get(url=url)
    return True if result.text == "True" else False


def retrieve_text(id: str) -> str:
    result_url = f"{base_url}/result/{id}"
    r = requests.get(result_url)
    soup = BeautifulSoup(r.text.replace("/br", "br"), "lxml")
    text_tag = soup.find("div", attrs={"class": "read-card__text"}).find("tt")

    for br_tag in text_tag.findAll("br"):
        br_tag.replace_with("\n")

    # remove repetitive newlines
    text = re.sub("\n+", "\n", text_tag.text)

    nonBreakSpace = u"\xa0"
    return re.sub(nonBreakSpace, " ", text)  # replace non-breaking spaces with normal


def get_result(id: str, out_filename: Path) -> str:
    id_no_underscore = id[1:]  # remove underscore
    img_url = f"{base_url}/static/data/results/{id_no_underscore}.marked.jpg"
    img_response = requests.get(img_url, stream=True)
    if img_response.status_code != 200:
        raise RuntimeError(f"unable to get result for ID {id}")
    with open(str(out_filename), "wb") as fout:
        shutil.copyfileobj(img_response.raw, fout)
    del img_response

    return retrieve_text(id)


def process_photo(input_filename: Path, params: RecognitionParams) -> Tuple[Path, str]:
    job_id = post_form(input_filename, params)
    print(job_id)  # TODO log instead of print
    while not result_ready(job_id):
        time.sleep(.5)

    out_filename = input_filename.parent / (input_filename.stem + ".marked.jpg")
    text = get_result(id=job_id, out_filename=out_filename)
    return out_filename, text


def main():
    data_path = Path("data/jane_eyre_p0011.jpg")
    job_id = post_form(data_path, RecognitionParams(has_public_confirm=False, lang=Lang.en,
                                                    two_sides=False, auto_orient=False))
    while not result_ready(job_id):
        time.sleep(.5)

    out_path = (data_path.parent / "tmp") / (data_path.stem + ".marked.jpg")
    out_path.parent.mkdir(exist_ok=True)
    text = get_result(id=job_id, out_filename=out_path)
    print(text)


if __name__ == "__main__":
    main()
