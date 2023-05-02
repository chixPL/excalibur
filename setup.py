# Sprawdzanie requirements.txt
import pkg_resources
import sys

try:
    pkg_resources.require(open('requirements.txt', mode='r'))
except OSError:
    cont = input("Nie można sprawdzić requirements. Sprawdź czy jesteś w głównym katalogu. Jesteś pewien że requirements są zainstalowane? [T/n] ")
    if cont.lower() == 'n':
        sys.exit()
except pkg_resources.ResolutionError:
    sys.exit('Nie znaleziono wymaganych bibliotek. Uruchom pip install -r requirements.txt.')

from configparser import ConfigParser

def config(filename='base/database.ini', section='postgresql'):
    parser = ConfigParser() #tworzenie obiektu parsera
    parser.read(filename)   #wczytanie pliku do parsera
    
    db = {} #słownik przechowujący wczytane paramatry
    
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} nie znaleziony w {1}'.format(section, filename))
    
    return db

import psycopg2

# Sprawdzenie czy baza już istnieje
conn = None
try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(id_uzytkownika) FROM uzytkownicy")
    result = cur.fetchone()
    if result[0] > 0:
        sys.exit("Baza danych już istnieje. Jeśli chcesz ją zainstalować ponownie, usuń ją ręcznie.")
except (Exception, psycopg2.DatabaseError) as e:
    pass

# Instalacja

import os
import psycopg2.errors
from hashlib import md5
from getpass import getpass

print("="*50)
print("      /| ________________")
print("O|===|* >________________>")
print("      \|")
print("Excalibur - proces pierwszej instalacji")
print("by Jakub Rutkowski (chixPL) 2023")
print("="*50)

# Instalacja bazy danych
conn = None
createDB = ''
useDBIni = ''

if(os.path.exists('base/database.ini')):
    useDBIni = input("Znaleziono plik database.ini. Czy chcesz użyć tych wartości? [T/n] ")
else:
    createDB = input('Czy chcesz utworzyć bazę danych? [T/n] ')
if createDB.lower() == 't' or useDBIni.lower() == 't' or useDBIni.lower() == 'n':
    print("[1] Tworzenie bazy danych")
    if(useDBIni.lower() == 't'):
        try:
            params = config()
            db_name = params['database']
            user = params['user']
            password = params['password']
            host = params['host']
        except Exception:
            sys.exit("Błąd odczytu pliku database.ini. Sprawdź czy plik jest poprawny.")
    else:
        db_name = input('Podaj nazwę bazy danych: ')
        user = input('Podaj nazwę użytkownika DB: ')
        password = getpass('Podaj hasło użytkownika DB: ')
        host = input('Podaj host: ')
    try:
        conn = psycopg2.connect(f"dbname='postgres' user='{user}' host='{host}' password='{password}'")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {db_name}")
        conn.commit()

        if(useDBIni.lower() != 't'):
            parser = ConfigParser()
            parser['postgresql'] = { 'host': host, 'database': db_name, 'user': user, 'password': password}
            with open('base/database.ini', 'w+') as configfile:
                parser.write(configfile)

    except (Exception, psycopg2.DatabaseError) as e:
        print("Błąd połączenia z bazą danych. Jeśli usunąłeś domyślną bazę danych (postgres), przywróć ją i wykonaj program ponownie.")
        sys.exit("Error log: " + str(e))
    finally:
        if conn is not None:
            conn.close()

    try:
        conn = psycopg2.connect(f"dbname='{db_name}' user='{user}' host='{host}' password='{password}'")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS uzytkownicy (id_uzytkownika SERIAL PRIMARY KEY, email VARCHAR(128) NOT NULL, haslo VARCHAR(255) NOT NULL, rola VARCHAR(10) NOT NULL, imie VARCHAR(25) NOT NULL, nazwisko VARCHAR(25) NOT NULL, reset_token VARCHAR(50) UNIQUE)")
        cur.execute("CREATE TABLE IF NOT EXISTS przedmioty (id_przedmiotu SERIAL PRIMARY KEY, skrot_przedmiotu VARCHAR(6) UNIQUE NOT NULL, nazwa_przedmiotu VARCHAR(50) UNIQUE NOT NULL, id_nauczyciela INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika))")
        cur.execute("CREATE TABLE IF NOT EXISTS sprawdziany(id_sprawdzianu SERIAL PRIMARY KEY, id_przedmiotu INT NOT NULL REFERENCES przedmioty(id_przedmiotu), skrot_sprawdzianu VARCHAR(10) UNIQUE NOT NULL, nazwa_sprawdzianu VARCHAR(100) NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS oceny (id_oceny SERIAL PRIMARY KEY, id_ucznia INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika), id_sprawdzianu INT NOT NULL REFERENCES sprawdziany(id_sprawdzianu), ocena VARCHAR(2) NOT NULL, wartosc VARCHAR(10) DEFAULT 'Zwykła',data_oceny TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("CREATE TABLE IF NOT EXISTS uzytkownicy_przedmioty(id_uzytkownicy_przedmioty SERIAL PRIMARY KEY, id_uzytkownika INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika), id_przedmiotu INT NOT NULL REFERENCES przedmioty(id_przedmiotu))")
        
        print("[2] Dodawanie użytkownika administratora")
        email = input('Podaj e-mail użytkownika: ')
        password = 'a'
        password2 = 'b'
        while(password != password2):
            password = getpass('Podaj hasło użytkownika DB: ')
            password2 = getpass('Powtórz hasło: ')
            if(password != password2):
                print("Hasła nie są takie same. Spróbuj ponownie.")
        name = input('Podaj imię: ')
        surname = input('Podaj nazwisko: ')
        cur.execute(f"INSERT INTO uzytkownicy (email, haslo, rola, imie, nazwisko) VALUES ('{email}', '{md5(password.encode()).hexdigest()}', 'Admin', '{name}', '{surname}')")
        conn.commit()

        print("="*50)
        print("Gotowe!")
        print("Uruchom aplikację poleceniem python main.py")
        print("W tamtej aplikacji możesz utworzyć przedmiot i dodać do niego uczniów.")
        print("="*50)
    except (Exception, psycopg2.DatabaseError) as e:
        sys.exit("Błąd połączenia z bazą danych: " + str(e))
    finally:
        if conn is not None:
            conn.close()


