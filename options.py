import os
import sqlite3


class Options:

    def __init__(self, api_key=None, **kwargs):
        self.__data_src = ""
        self.__api_url = ""
        if not api_key:
            self.__api_key = os.environ.get('TILT_API_KEY')
        self.__api_key = api_key

    @property
    def data_src(self):
        return self.__data_src

    @property
    def api_url(self):
        return self.__data_src

    def validate_program(self, program_name):
        conn = sqlite3.Connection("~/tilt/tilt.db")
        cur = conn.cursor()
        return cur.execute('SELECT program_id FROM programs WHERE name = ?', program_name).fetchone()
