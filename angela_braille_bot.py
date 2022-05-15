import os
import sqlite3
import tempfile
from pathlib import Path

import telebot  # type: ignore

from website_recognizer import process_photo

bot = telebot.TeleBot(os.environ["token"])

# Connect database
os.chdir("../database")
db_connector = sqlite3.connect("Braille")
db_cursor = db_connector.cursor()


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "\n".join((r"Привет\! Я робот Анжела\!",
                                     r"Я умею распознавать текст Брайля по фотографии\, "
                                     r"используя программу И\. Оводова "
                                     r"[Angelina Braille Reader](http://angelina-reader.ru/)\. "
                                     r"Отправьте мне фото\, и я дам ответ\.")), parse_mode="MarkdownV2")

    with open(Path("doc") / "angelina-example/jane_eyre_p0011.marked.jpg", "rb") as img:
        bot.send_photo(message.chat.id, img, caption="Вот пример")
    bot.send_message(message.chat.id, "Больше примеров входных данных "
                                      "[на диске](https://csspbstu-my.sharepoint.com/:f:/g/"
                                      "personal/zuev_va_edu_spbstu_ru/Egj-vMvAMj5JtmX35kTYz"
                                      "n0BYSkJyw7BfL96AKa0i1BhMw?e=CVZMbm)",
                     parse_mode="MarkdownV2")


@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.send_message(message.chat.id, "начинаю распознавание...")
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        tmp_root = Path("tmp")
        tmp_root.mkdir(exist_ok=True)
        tmp_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        img_input_filename = tmp_dir / "input.jpg"

        with open(img_input_filename, "wb") as new_file:
            new_file.write(downloaded_file)

        img_out_filename, text_recognized = process_photo(input_filename=img_input_filename)

        with open(img_out_filename, "rb") as img:
            bot.send_photo(message.chat.id, img)
            bot.send_message(message.chat.id, text=text_recognized)

    except Exception as e:
        bot.send_message(message.chat.id, "извините, произошла ошибка")
        print(e)


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            pass
