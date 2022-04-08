import os
import sys
from pathlib import Path
from subprocess import Popen

import telebot  # type: ignore
import tempfile

bot = telebot.TeleBot(os.environ["token"])


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "\n".join((r"Привет\! Я робот Анжела\!",
                                     r"Я умею распознавать текст Брайля по фотографии\, "
                                     r"используя программу И\. Оводова "
                                     r"[Angelina Braille Reader](http://angelina-reader.ru/)\. "
                                     r"Также я могу находить на картинке *плитки Брайля*\. "
                                     r"Отправьте мне фото\, и я дам ответ\.")), parse_mode="MarkdownV2")

    bot.send_message(message.chat.id, "Вот примеры:")
    for photo_file_name, caption in (("recognition-example.jpg", "Распознавание плиток"),
                                     ("angelina-example/jane_eyre_p0011.marked.jpg", "Распознавание страницы"),
                                     ("angelina-example/jane_eyre_p0011.marked.improved.jpg",
                                      "Распознавание страницы (с постобработкой)")):
        with open(Path("doc") / photo_file_name, "rb") as img:
            bot.send_photo(message.chat.id, img, caption=caption)
    bot.send_message(message.chat.id, "Больше примеров входных данных "
                                      "[на диске](https://csspbstu-my.sharepoint.com/:f:/g/"
                                      "personal/zuev_va_edu_spbstu_ru/Egj-vMvAMj5JtmX35kTYz"
                                      "n0BYSkJyw7BfL96AKa0i1BhMw?e=CVZMbm)",
                     parse_mode="MarkdownV2")


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    try:
        bot.answer_callback_query(query.id)
        bot.send_message(query.message.chat.id, "начинаю распознавание...")
        tmp_dir = Path(query.data.split("|")[1])

        if query.data.startswith("tiles"):
            Popen([sys.executable, "tiles-recognition/src/main.py", "-vv", tmp_dir]).wait()

            out_path = Path("out")
            with open(out_path / "result-text.txt", encoding="utf8") as out_txt:
                recognized_letters = [line.strip() for line in out_txt.readlines()]
                if max(map(len, recognized_letters)) == 0:
                    bot.reply_to(query.message, "Я поискала на этой картинке плитки Брайля, но не нашла.")
                    return
                bot.reply_to(query.message, "\n".join(recognized_letters))

            with open(out_path / "result-image.png", "rb") as img:
                bot.send_photo(query.message.chat.id, img)
        else:
            Popen([sys.executable, "run_local.py", tmp_dir.absolute() / "image.jpg", "-l", "EN", "-o"],
                  cwd="AngelinaReader").wait()
            for suffix, caption in (("", "без постобработки"), (".improved", "с постобработкой")):
                with open(tmp_dir / "image.marked{}.jpg".format(suffix), "rb") as img:
                    bot.send_photo(query.message.chat.id, img, caption=caption)
    except Exception:
        bot.send_message(query.message.chat.id, "извините, произошла ошибка")


@bot.message_handler(content_types=['photo'])
def photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        tmp_root = Path("tmp")
        tmp_root.mkdir(exist_ok=True)
        tmp_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        img_input_filename = "image.jpg"

        with open(tmp_dir / img_input_filename, "wb") as new_file:
            new_file.write(downloaded_file)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton("Плитки Брайля", callback_data="tiles|" + str(tmp_dir)))
        keyboard.row(telebot.types.InlineKeyboardButton("Брайлевскую страницу на английском",
                                                        callback_data="page|" + str(tmp_dir)), )
        bot.send_message(message.chat.id, "Картинка получена. Что на ней нужно распознать?", reply_markup=keyboard)
    except Exception:
        bot.send_message(message.chat.id, "извините, произошла ошибка")  # TODO reduce duplication


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            pass
