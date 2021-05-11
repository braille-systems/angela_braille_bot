import os

import telebot

bot = telebot.TeleBot(os.environ["token"])


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "\n".join(("Hello\! I'm the Angela Braille Reader bot\!",
                                     "Currently I'm under development\. When I'm complete "
                                     "I will do Braille character recognition from photo "
                                     "using I\. Ovodov's [Angelina Braille Reader](http://angelina-reader.ru/) "
                                     "as a backend\.")), parse_mode="MarkdownV2")


if __name__ == "__main__":
    bot.polling(none_stop=True)
