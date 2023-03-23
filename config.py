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