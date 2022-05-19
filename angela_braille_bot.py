import os
import sqlite3
import tempfile
from functools import partial
from pathlib import Path
from typing import Tuple

import telebot  # type: ignore

from website_recognizer import process_photo, RecognitionParams
from database.db_worker import db_name, insert_new_user, update_recognition_info, selector_recognition_info
from database.db_worker import update_settings

bot = telebot.TeleBot(os.environ["token"])

# Connect database
os.chdir("database")


def print_info(message: telebot.types.Message) -> None:
    bot.reply_to(message, "\n".join((r"Привет\! Я робот Анжела\!",
                                     r"Я умею распознавать текст Брайля по фотографии\, "
                                     r"используя программу И\. Оводова "
                                     r"[Angelina Braille Reader](http://angelina-reader.ru/)\. "
                                     r"Отправьте мне фото\, и я дам ответ\.")), parse_mode="MarkdownV2")

    with open(Path("..") / "doc/angelina-example/jane_eyre_p0011.marked.jpg", "rb") as img:
        bot.send_photo(message.chat.id, img, caption="Вот пример")
    bot.send_message(message.chat.id, "Примеры входных данных "
                                      "[на диске](https://csspbstu-my.sharepoint.com/:f:/g/personal/"
                                      "zuev_va_edu_spbstu_ru/EvFV7VaCIl5PqnKMREDnogsB8z87Qxo0ms7UGgB"
                                      "gwCdGcg?e=ZCHrDM)",
                     parse_mode="MarkdownV2")
    bot.send_message(message.chat.id,
                     "\n".join(("Также доступны команды:",
                                "/help - вызов справки",
                                "/params - настройки бота")))


@bot.message_handler(commands=["start"])
def send_welcome(message):
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()
    if selector_recognition_info(message.chat.id, db_cursor):
        bot.reply_to(message, "А Вы уже зарегистрированы в нашей базе!")
        return
    insert_new_user(database_cursor=db_cursor, connector=db_connector, user_id=message.chat.id)
    print_info(message)


@bot.message_handler(commands=["help"])
def send_help(message):
    print_info(message)


hide_settings = "hide_settings"
change_settings = "change_settings"
back_to_settings = "back_to_settings"


def create_settings_message(chat_id: int) -> Tuple[str, telebot.types.InlineKeyboardMarkup]:
    recognition_info = selector_recognition_info(chat_id, sqlite3.connect(db_name).cursor())
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Изменить настройки", callback_data=change_settings))
    keyboard.row(telebot.types.InlineKeyboardButton("Скрыть настройки", callback_data=hide_settings))
    return str(recognition_info), keyboard


@bot.message_handler(commands=["params"])
def send_settings(message: telebot.types.Message):
    settings_text, keyboard = create_settings_message(message.chat.id)
    bot.send_message(message.chat.id, text=settings_text, reply_markup=keyboard)


def add_back_row(keyboard: telebot.types.InlineKeyboardMarkup, callback_data: str) -> None:
    keyboard.row(telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data=callback_data))


def process_settings_callback(query: telebot.types.CallbackQuery) -> None:
    """
    Viewing (maybe after modifying) some parameter in bot settings
    :param query: query with data in a format <param_name>|<[optional] new_param_value> (e.g. "lang|RU" or "lang|")
    :return: None
    """
    param, selected_value = query.data.split("|")
    if param not in RecognitionParams.options.keys():
        return
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()

    # if `selected_value` is given, change the value of `param`
    prev_info = selector_recognition_info(query.message.chat.id, database_cursor=db_cursor)
    if len(selected_value):
        if selected_value in ("True", "False"):
            selected_value = 1 if selected_value == "True" else 0
        update_shorthand = partial(update_recognition_info,
                                   database_cursor=db_cursor,
                                   connector=db_connector,
                                   user_id=query.message.chat.id)
        if param == RecognitionParams.lang_key:
            update_shorthand(language=selected_value, recognize_both=prev_info.two_sides,
                             auto_orientate=prev_info.auto_orient)
        if param == RecognitionParams.two_sides_key:
            update_shorthand(recognize_both=selected_value, language=prev_info.lang,
                             auto_orientate=prev_info.auto_orient)
        if param == RecognitionParams.auto_orient_key:
            update_shorthand(auto_orientate=selected_value, recognize_both=prev_info.two_sides,
                             language=prev_info.lang)
        if param == RecognitionParams.has_public_confirm_key:
            update_settings(database_cursor=db_cursor, connector=db_connector, user_id=query.message.chat.id,
                            include_in_data=selected_value)

    # retrieve recognition settings, display the keyboard
    recognition_info = selector_recognition_info(query.message.chat.id, database_cursor=db_cursor)
    selector, option = recognition_info.get_selector()[param]
    item_keyboard = telebot.types.InlineKeyboardMarkup()
    for k, v in selector.items():
        prefix = "🔘 " if option == k else ""
        appendix = " (Выбрано)" if option == k else ""
        item_keyboard.row(telebot.types.InlineKeyboardButton(f"{prefix}{RecognitionParams.options[param]}: {v}{appendix}",
                                                             callback_data=f"{param}|{str(k)}"))
    add_back_row(item_keyboard, callback_data=change_settings)
    bot.edit_message_text(
        text=recognition_info,
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        reply_markup=item_keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(query: telebot.types.CallbackQuery) -> None:
    if query.data == hide_settings:
        bot.delete_message(query.message.chat.id, query.message.id)

    if query.data == change_settings:
        keyboard = telebot.types.InlineKeyboardMarkup()

        for k, v in RecognitionParams.options.items():
            keyboard.row(telebot.types.InlineKeyboardButton(v, callback_data=f"{k}|"))
        add_back_row(keyboard, callback_data=back_to_settings)

        bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=keyboard)

    if query.data == back_to_settings:
        params_text, params_keyboard = create_settings_message(query.message.chat.id)
        bot.edit_message_text(
            text=params_text,
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=params_keyboard
        )

    if "|" in query.data:
        process_settings_callback(query)

    bot.answer_callback_query(query.id)


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

        recognition_info = selector_recognition_info(message.chat.id, sqlite3.connect(db_name).cursor())
        img_out_filename, text_recognized = process_photo(input_filename=img_input_filename, params=recognition_info)

        with open(img_out_filename, "rb") as img:
            bot.send_photo(message.chat.id, img)
            bot.send_message(message.chat.id,
                             text=text_recognized if len(text_recognized)
                             else "Брайлевский текст на изображении не обнаружен")

        # send_settings(message) TODO add settings after each recognition (if user chooses to show them in settings)

    except Exception as e:
        bot.send_message(message.chat.id, "извините, произошла ошибка")
        print(e)


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            pass
