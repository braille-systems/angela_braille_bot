import sqlite3
from sqlite3 import Cursor, Connection
from typing import Optional

from website_recognizer import RecognitionParams, Lang, lang_inv_map

db_name = "Braille"


def selector_settings(user_id: int, database_cursor: Cursor):
    """Return user settings information"""
    database_cursor.execute("SELECT * FROM Settings WHERE user_id = ?",
                            (user_id,))
    return database_cursor.fetchall()


def selector_recognition_info(user_id: int, database_cursor: Cursor) -> Optional[RecognitionParams]:
    """Returns user recognition settings information"""
    database_cursor.execute("SELECT * FROM Recognition_information WHERE user_id = ?",
                            (user_id,))
    result = database_cursor.fetchall()
    if not len(result):  # empty result
        return None

    settings = selector_settings(user_id=user_id, database_cursor=database_cursor)

    return RecognitionParams(
        has_public_confirm=settings[0][3],
        lang=lang_inv_map[result[0][2]],
        two_sides=result[0][3],
        auto_orient=result[0][1]
    )


def update_settings(database_cursor: Cursor, connector: Connection,
                    user_id: int, email: str = None,
                    password: str = None, include_in_data: bool = False,
                    force_null_update: bool = False):
    """Update user settings"""
    database_cursor.execute(
        "UPDATE Settings "
        "SET include_in_data = ? "
        "WHERE user_id == ?",
        (include_in_data,
         user_id)
    )
    if email or force_null_update:
        database_cursor.execute(
            "UPDATE Settings "
            "SET email = ?, password = ?"
            "WHERE user_id == ?",
            (email,
             password,
             user_id)
        )
    connector.commit()


def update_recognition_info(database_cursor: Cursor, connector: Connection,
                            user_id: int, auto_orientate: bool = True,
                            language: Lang = Lang.ru, recognize_both: bool = True):
    """Update user recognition information"""
    database_cursor.execute(
        "UPDATE Recognition_information "
        "SET auto_orientate = ?, language = ?, recognize_both = ? "
        "WHERE user_id == ? ",
        (auto_orientate,
         str(language),
         recognize_both,
         user_id)
    )
    connector.commit()


def insert_new_user(database_cursor: Cursor, connector: Connection,
                    user_id: int):
    """Insert new user in db with default values"""
    try:
        database_cursor.execute(
            "INSERT INTO Settings (user_id)"
            "VALUES (?)",
            (user_id,)
        )
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print("something went wrong")
        print(e)
    try:
        database_cursor.execute(
            "INSERT INTO Recognition_information (user_id)"
            "VALUES (?)",
            (user_id,)
        )
    except sqlite3.IntegrityError:
        pass

    connector.commit()
