import sqlite3
from sqlite3 import Cursor, Connection


def selector_settings(user_id: int, database_cursor: Cursor):
    """Return user settings information"""
    database_cursor.execute("SELECT * FROM Settings WHERE user_id = ?",
                            (user_id,))
    return database_cursor.fetchall()


def selector_recognition_info(user_id: int, database_cursor: Cursor):
    """Returns user recognition settings information"""
    database_cursor.execute("SELECT * FROM Recognition_information WHERE user_id = ?",
                            (user_id,))
    return database_cursor.fetchall()


def update_settings(database_cursor: Cursor, connector: Connection,
                    user_id: int, email: str = None,
                    password: str = None, include_in_data: bool = True):
    """Update user settings"""
    database_cursor.execute(
        "UPDATE Settings "
        "SET email = ?, password = ?, include_in_data = ? "
        "WHERE user_id == ?",
        (email,
         password,
         include_in_data,
         user_id)
    )
    connector.commit()


def update_recognition_info(database_cursor: Cursor, connector: Connection,
                            user_id: int, auto_orientate: bool = True,
                            language: str = "Ru", recognize_both: bool = True):
    """Update user recognition information"""
    database_cursor.execute(
        "UPDATE Recognition_information "
        "SET auto_orientate = ?, language = ?, recognize_both = ? "
        "WHERE user_id == ? ",
        (auto_orientate,
         language,
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
    try:
        database_cursor.execute(
            "INSERT INTO Recognition_information (user_id)"
            "VALUES (?)",
            (user_id,)
        )
    except sqlite3.IntegrityError:
        pass

    connector.commit()
