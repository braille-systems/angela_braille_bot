import os
import sys
from pathlib import Path
from subprocess import Popen

import telebot

bot = telebot.TeleBot(os.environ["token"])


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "\n".join(("Hello\! I'm the Angela Braille Reader bot\!",
                                     "Currently I'm under development\. When I'm complete "
                                     "I will do Braille character recognition from photo "
                                     "using I\. Ovodov's [Angelina Braille Reader](http://angelina-reader.ru/) "
                                     "as a backend\.")), parse_mode="MarkdownV2")


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

    with open(Path("out") / "result-image.png", "rb") as img:
        bot.send_photo(message.chat.id, img)


if __name__ == "__main__":
    bot.polling(none_stop=True)
