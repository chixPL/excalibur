CREATE TABLE IF NOT EXISTS uzytkownicy (
id_uzytkownika SERIAL PRIMARY KEY,
email VARCHAR(128) NOT NULL,
haslo VARCHAR(255) NOT NULL,
rola VARCHAR(10) NOT NULL /* Myślałem żeby tutaj enuma wstawić ale ich nie ma w Postgresie */,
imie VARCHAR(25) NOT NULL,
nazwisko VARCHAR(25) NOT NULL,
reset_token VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS przedmioty (
id_przedmiotu SERIAL PRIMARY KEY,
skrot_przedmiotu VARCHAR(6) UNIQUE NOT NULL,
nazwa_przedmiotu VARCHAR(50) UNIQUE NOT NULL,
id_nauczyciela INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika)
);

CREATE TABLE IF NOT EXISTS sprawdziany(
id_sprawdzianu SERIAL PRIMARY KEY,
id_przedmiotu INT NOT NULL REFERENCES przedmioty(id_przedmiotu),
skrot_sprawdzianu VARCHAR(10) UNIQUE NOT NULL,
nazwa_sprawdzianu VARCHAR(100) NOT NULL
)

CREATE TABLE IF NOT EXISTS oceny (
id_oceny SERIAL PRIMARY KEY,
id_ucznia INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika),
id_sprawdzianu INT NOT NULL REFERENCES sprawdziany(id_sprawdzianu),
ocena VARCHAR(2) NOT NULL,
wartosc VARCHAR(10) DEFAULT 'Zwykła',
data_oceny TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS uzytkownicy_przedmioty(
id_uzytkownicy_przedmioty SERIAL PRIMARY KEY,
id_uzytkownika INT NOT NULL REFERENCES uzytkownicy(id_uzytkownika),
id_przedmiotu INT NOT NULL REFERENCES przedmioty(id_przedmiotu)
);


INSERT INTO uzytkownicy(email, haslo, rola, imie, nazwisko) VALUES('a.kowalski@example.com', 'TutajHasloWMD5', 'Admin', 'Adam', 'Kowalski');
INSERT INTO uzytkownicy(email, haslo, rola, imie, nazwisko) VALUES('jan.nowak@example.com', 'TutajRowniezHasloWMD5', 'Uczeń', 'Jan', 'Nowak');
INSERT INTO przedmioty(skrot_przedmiotu, nazwa_przedmiotu, id_nauczyciela) VALUES('3ainf', '3A Informatyka', 1);
INSERT INTO uzytkownicy_przedmioty(id_uzytkownika, id_przedmiotu) VALUES(2, 1);
INSERT INTO sprawdziany(id_przedmiotu,skrot_sprawdzianu,nazwa_sprawdzianu) VALUES(1, 'Spr1', 'Stawianie serwerów FTP');
INSERT INTO sprawdziany(id_przedmiotu,skrot_sprawdzianu,nazwa_sprawdzianu) VALUES(1, 'Kart1', 'Kartkówka z działu 1');
INSERT INTO oceny(id_ucznia,id_sprawdzianu, ocena) VALUES(1, 1, '5+');
