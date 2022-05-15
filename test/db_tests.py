import os
from database.db_worker import selector_settings
from database.db_worker import selector_recognition_info
from database.db_worker import insert_new_user
from database.db_worker import update_recognition_info
from database.db_worker import update_settings
import sqlite3


os.chdir("../database")


def test_selector_settings():
    # Connect database
    db_connector = sqlite3.connect("Braille")
    db_cursor = db_connector.cursor()

    assert selector_settings(-1, db_cursor)[0] == (-1, None, None, 1)


def test_selector_rec_info():
    # Connect database
    db_connector = sqlite3.connect("Braille")
    db_cursor = db_connector.cursor()

    assert selector_recognition_info(-1, db_cursor)[0] == (-1, 1, "Ru", 1)


def test_insert():
    # Connect database
    db_connector = sqlite3.connect("Braille")
    db_cursor = db_connector.cursor()

    insert_new_user(db_cursor, db_connector, -2)

    assert selector_settings(-2, db_cursor)[0] == (-2, None, None, 1)
    assert selector_recognition_info(-2, db_cursor)[0] == (-2, 1, "Ru", 1)


def test_update_settings():
    # Connect database
    db_connector = sqlite3.connect("Braille")
    db_cursor = db_connector.cursor()

    update_settings(db_cursor, db_connector, -1, "em-1")

    assert selector_settings(-1, db_cursor)[0] == (-1, "em-1", None, 1)
    update_settings(db_cursor, db_connector, -1)


def test_update_rec_info():
    # Connect database
    db_connector = sqlite3.connect("Braille")
    db_cursor = db_connector.cursor()

    update_recognition_info(db_cursor, db_connector, -1, False)

    assert selector_recognition_info(-1, db_cursor)[0] == (-1, 0, "Ru", 1)
    update_recognition_info(db_cursor, db_connector, -1)
