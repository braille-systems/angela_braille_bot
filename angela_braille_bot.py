import os
import sys
from pathlib import Path
from subprocess import Popen

import telebot

bot = telebot.TeleBot(os.environ["token"])


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "\n".join(("Привет\! Я робот Анжела\!",
                                     "Скоро я смогу распознавать текст Брайля по фотографии\, "
                                     "используя программу И\. Оводова "
                                     "[Angelina Braille Reader](http://angelina-reader.ru/)\. "
                                     "Пока что я умею распознавать *плитки Брайля*\. "
                                     "Отправьте мне фото\, и я дам ответ\.")), parse_mode="MarkdownV2")

    bot.send_message(message.chat.id, "Вот пример:")
    with open(Path("doc") / "recognition-example.jpg", "rb") as img:
        bot.send_photo(message.chat.id, img)


@bot.message_handler(content_types=['photo'])
def photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    img_input_filename = "image.jpg"

    with open(tmp_dir / img_input_filename, "wb") as new_file:
        new_file.write(downloaded_file)

    Popen([sys.executable, "tiles-recognition/src/main.py", "-vv", tmp_dir]).wait()

    out_path = Path("out")
    with open(out_path / "result-text.txt", encoding="utf8") as out_txt:
        bot.reply_to(message, "\n".join(out_txt.readlines()))

    with open(Path("out") / "result-image.png", "rb") as img:
        bot.send_photo(message.chat.id, img)


if __name__ == "__main__":
    bot.polling(none_stop=True)
