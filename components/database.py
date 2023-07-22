"""
Excalibur
Moduł bazy danych
by Jakub Rutkowski (chixPL) 2023
"""

import psycopg2
from functools import lru_cache
from configparser import ConfigParser
import datetime
import platform

class Database:

    def __init__(self, currentVersion, debug=False, filename='base/database.ini', section='postgresql'):
        self.debug = debug
        self.currentVersion = currentVersion
        parser = ConfigParser() #tworzenie obiektu parsera
        parser.read(filename)   #wczytanie pliku do parsera
        
        self.db_params = {} #słownik przechowujący wczytane paramatry
        
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.db_params[param[0]] = param[1]
        else:
            raise Exception('Section {0} nie znaleziony w {1}'.format(section, filename))
        
        self.log_start()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cur = self.conn.cursor()
            if(self.debug):
                with open("base/database.log", "a") as f:
                    f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} Zalogowano do DB.\n")
                    f.write(self.fetchone("SELECT version()") + "\n")
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"Błąd połączenia z bazą: {e}")
    
    def disconnect(self):
        with open("base/database.log", "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} Rozłączono z db.\n")
        self.conn.close()

    def fetchone(self, query, oneRow=False):
        try:
            self.cur.execute(query)
            if self.debug:
                self.log_success(query, "Read")
            if oneRow:
                return self.cur.fetchone()
            return self.cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as e:
            if self.debug:
                print(f"Błąd bazy danych: {e}\n w query: {query}")
                self.log_error(query, "Read", e)
            return False
          
    def fetchall(self, query):
        try:
            self.cur.execute(query)
            if self.debug:
                self.log_success(query, "ReadAll")
            return self.cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as e:
            if self.debug:
                print(f"Błąd bazy danych: {e}\n w query: {query}")
                self.log_error(query, "ReadAll", e)
            return False
    
    def execute(self, query, doReturn=False):
        try:
            self.cur.execute(query)
            self.conn.commit()
            if self.debug:
                self.log_success(query, "Write")
            if doReturn:
                return self.cur.fetchone()
            else:
                return True
        except (Exception, psycopg2.DatabaseError) as e:
            if self.debug:
                print(f"Błąd bazy danych: {e}\n w query: {query}")
                self.log_error(query, "Write", e)
            return False

    @lru_cache(maxsize=4)
    def check_connection(self):
        try:
            result = self.fetchone("SELECT COUNT(id_uzytkownika) FROM uzytkownicy")
            if result > 0:
                return True
            else:
                return False
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"Błąd bazy danych: {e}")
            if self.debug:
                self.log_error("SELECT COUNT(id_uzytkownika) FROM uzytkownicy", "CheckConnection", e)
            return False
    
    # Logi

    def log_start(self):
        with open("base/database.log", "w+") as f:
            f.write("      /| ________________\n")
            f.write("O|===|* >________________>\n")
            f.write("      \| \n")
            
            f.write(f"Uruchomiono Excalibur {datetime.datetime.now()}\n")
            f.write(f"Wersja {self.currentVersion}\n")
            f.write(f"Python {platform.python_version()}\n")
            f.write(f"System {platform.system()} {platform.release()}\n")
    
    def log_success(self, query, mode):
        with open("base/database.log", "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} {mode} : {query}\n")
    
    def log_error(self, query, mode, error):
        with open("base/database.log", "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} ERROR {mode} : {query} - {error}\n")
    