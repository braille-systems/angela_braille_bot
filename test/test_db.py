import os
from database.db_worker import selector_settings, selector_recognition_info, db_name
from database.db_worker import insert_new_user
from database.db_worker import update_recognition_info, update_settings
import sqlite3

from website_recognizer import Lang

os.chdir("database")


def test_selector_settings():
    # Connect database
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()

    assert selector_settings(-1, db_cursor)[0] == (-1, None, None, 1)


def test_selector_rec_info():
    # Connect database
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()
    selector_result = selector_recognition_info(-1, database_cursor=db_cursor)
    assert selector_result
    assert selector_result.two_sides == 1
    assert selector_result.auto_orient == 1
    assert selector_result.lang == Lang.ru
    assert not selector_result.has_public_confirm


def test_insert():
    # Connect database
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()

    insert_new_user(db_cursor, db_connector, -2)

    assert selector_settings(-2, db_cursor)[0] == (-2, None, None, 1)
    recognition_info = selector_recognition_info(-2, db_cursor)
    assert recognition_info
    assert recognition_info.lang == Lang.ru
    assert recognition_info.auto_orient == 1
    assert recognition_info.two_sides == 1


def test_update_settings():
    # Connect database
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()

    update_settings(db_cursor, db_connector, -1, "em-1")

    assert selector_settings(-1, db_cursor)[0] == (-1, "em-1", None, 1)
    update_settings(db_cursor, db_connector, -1)


def test_update_rec_info():
    # Connect database
    db_connector = sqlite3.connect(db_name)
    db_cursor = db_connector.cursor()

    update_recognition_info(db_cursor, db_connector, -1, auto_orientate=False)

    recognition_info = selector_recognition_info(-1, db_cursor)
    assert recognition_info
    assert recognition_info.auto_orient == 0
    assert recognition_info.two_sides == 1
    assert recognition_info.lang == Lang.ru

    update_recognition_info(db_cursor, db_connector, -1)
