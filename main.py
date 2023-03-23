# -*- coding: utf-8 -*-

"""

Excalibur - dziennik szkolny
by Jakub Rutkowski (chixPL) 2023

"""

# Standardowe importy

from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import hashlib
import psycopg2
from PyQt5.QtWidgets import QTableWidgetItem

# Własne pliki
from login import Ui_LoginWindow
from config import config
from addnote import Ui_AddNote
from adduser import Ui_AddUser

class Ui_MainWindow(object):

    def __init__(self):
        MainWindow = QtWidgets.QMainWindow()
        self.MainWindow = MainWindow
        self.setupUi(MainWindow)
        self.params = config()
    
    def show(self, email):
        self.MainWindow.show() # startuj UI
        self.getUserInfo(email) # startuj kod

    def getUserInfo(self, email):
        conn = None
        try:                    # wczytujemy paramtery połaczenia z bazą
            conn = psycopg2.connect(**self.params)       # łączenie z bazą
            cur = conn.cursor()                     # tworzenie kursora do bazy
            query = f"SELECT id_uzytkownika, imie, nazwisko, rola FROM uzytkownicy WHERE email = \'{email}\'" # query
            cur.execute(query)
            result = cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as err:
            print(f"Błąd połączenia z bazą: {err}")
            return False
        finally:
            if conn is not None:
                conn.close()                        # zamknięcie konektora do bazy
        # informacje o użytkowniku
        self.user_id = result[0]
        self.user_name = result[1]
        self.user_surname = result[2]
        self.user_role = result[3]

        # odpowiednie menu według roli
        if(self.user_role == 'Uczeń'):
            self.menuNauczyciel.menuAction().setVisible(False)
            self.menuAdmin.menuAction().setVisible(False)
        elif(self.user_role == 'Nauczyciel'):
            self.menuAdmin.menuAction().setVisible(False)
            self.menuUcze.menuAction().setVisible(False)
        
        self.label_2.setText(f"Witaj, {self.user_name} {self.user_surname} | Rola: {self.user_role}")
        self.getClasses()

    def getClasses(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.params)       # łączenie z bazą
            cur = conn.cursor()                     # tworzenie kursora do bazy
            query = f"SELECT skrot_przedmiotu FROM przedmioty INNER JOIN uzytkownicy ON przedmioty.id_nauczyciela = uzytkownicy.id_uzytkownika WHERE id_nauczyciela = {self.user_id} " # query
            cur.execute(query)
            results = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as err:
            print(f"Błąd połączenia z bazą: {err}")
            return False
        finally:
            if conn is not None:
                conn.close()                        # zamknięcie konektora do bazy
        
        for i in results:
            self.comboBox.addItem(i[0])

    def showData(self):
        self.tableWidget.clear()

        class_shortcut = self.comboBox.currentText()
        # Pobierz nazwy sprawdzianów i uczniów
        conn = None
        try:
            conn = psycopg2.connect(**self.params)       # łączenie z bazą
            cur = conn.cursor()                     # tworzenie kursora do bazy

            #todo: refactor do executemany(), na razie zostaje w ten sposób dla przejrzystości

            query = f"SELECT id_przedmiotu FROM przedmioty WHERE skrot_przedmiotu = \'{class_shortcut}\'" # pobierz ID klasy
            cur.execute(query)
            class_id = cur.fetchone()[0]

            query = f"SELECT id_uzytkownika FROM uzytkownicy_przedmioty WHERE id_przedmiotu = {class_id}" # pobierz ID uczniów którzy się uczą w danej klasie
            cur.execute(query)
            user_ids = cur.fetchall()

            query = f"SELECT CONCAT_WS(' ', imie, nazwisko)  FROM uzytkownicy_przedmioty INNER JOIN uzytkownicy ON uzytkownicy_przedmioty.id_uzytkownika = uzytkownicy.id_uzytkownika WHERE uzytkownicy_przedmioty.id_przedmiotu = {class_id}" # pobierz nazwy uczniów
            cur.execute(query)
            user_names = cur.fetchall()

            query = f"SELECT skrot_sprawdzianu FROM sprawdziany INNER JOIN przedmioty ON sprawdziany.id_przedmiotu=przedmioty.id_przedmiotu WHERE sprawdziany.id_przedmiotu = {class_id}" # pobierz nazwy sprawdzianów
            cur.execute(query)
            test_names = cur.fetchall()

            test_names = [x[0] for x in test_names] # usuwamy tuple
            test_names.append('Średnia') # na koniec dodajemy średnią
            user_names = [x[0] for x in user_names]

            self.tableWidget.setColumnCount(len(test_names))
            self.tableWidget.setRowCount(len(user_names))
            self.tableWidget.setHorizontalHeaderLabels(test_names)
            self.tableWidget.setVerticalHeaderLabels(user_names)

            for i in range(0, len(user_ids)):
                query = f"SELECT ocena FROM oceny WHERE id_ucznia = {user_ids[i][0]}"
                cur.execute(query)
                res = [x[0] for x in cur.fetchall()]
                # wstawiaj kolumnami
                try:
                    for j in range(0, len(test_names)-1):
                        if res[j] is not None:
                            self.tableWidget.setItem(i, j, QTableWidgetItem(res[j]))
                except IndexError:
                    pass # todo: usunąć te NULL, jeśli nie wstawiamy wsadowo to nie może ich tutaj być bo będzie kłopot z tym
                query = f"SELECT ROUND(AVG(CAST(LEFT(ocena, 1) AS INT)),2) FROM oceny JOIN sprawdziany ON oceny.id_sprawdzianu = sprawdziany.id_sprawdzianu WHERE id_przedmiotu = {class_id} AND id_ucznia = {user_ids[i][0]}" # pobierz średnią ucznia
                # LEFT bierze pierwszy znak (w średniej plusy/minusy pomijamy) a CAST zmienia varchary na inty
                
                cur.execute(query)
                srednia = cur.fetchone()[0]
                if srednia is not None:
                    self.tableWidget.setItem(i, len(test_names)-1, QTableWidgetItem(str(srednia)))

            self.tableWidget.repaint()
            self.tableWidget.update()
        
        except (Exception, psycopg2.DatabaseError) as err:
            print(f"Błąd połączenia z bazą: {err}")
            return False

        finally:
            if conn is not None:
                conn.close()                        # zamknięcie konektora do bazy

    def addNote(self):
        class_shortcut = self.comboBox.currentText()
        ui = Ui_AddNote(class_shortcut)
        if(ui.refresh == True):
            # todo: (?) ustawić repaint kiedy widżet nadal jest aktywny, obecnie dopiero po zamknięciu się odświeża
            self.showData()
            ui.refresh = False
    
    def addUser(self):
        ui = Ui_AddUser()

    def logout(self):
        self.MainWindow.hide()
        global lw
        lw.clear_show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(795, 617)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(530, 0, 261, 31))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 40, 781, 501))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(78)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 10, 131, 21))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 134, 27))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(670, 540, 121, 25))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(32, 32))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 22))
        self.menubar.setObjectName("menubar")
        self.menuPlik = QtWidgets.QMenu(self.menubar)
        self.menuPlik.setObjectName("menuPlik")
        self.menuNauczyciel = QtWidgets.QMenu(self.menubar)
        self.menuNauczyciel.setObjectName("menuNauczyciel")
        self.menuAdmin = QtWidgets.QMenu(self.menubar)
        self.menuAdmin.setObjectName("menuAdmin")
        self.menuUcze = QtWidgets.QMenu(self.menubar)
        self.menuUcze.setObjectName("menuUcze")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionWyloguj_si = QtWidgets.QAction(MainWindow)
        self.actionWyloguj_si.setObjectName("actionWyloguj_si")
        self.actionZamknij_program = QtWidgets.QAction(MainWindow)
        self.actionZamknij_program.setObjectName("actionZamknij_program")
        self.actionDodaj_u_ytkownika = QtWidgets.QAction(MainWindow)
        self.actionDodaj_u_ytkownika.setObjectName("actionDodaj_u_ytkownika")
        self.actionDodaj_klas = QtWidgets.QAction(MainWindow)
        self.actionDodaj_klas.setObjectName("actionDodaj_klas")
        self.actionDodaj_sprawdzian = QtWidgets.QAction(MainWindow)
        self.actionDodaj_sprawdzian.setObjectName("actionDodaj_sprawdzian")
        self.actionDodaj_ocen = QtWidgets.QAction(MainWindow)
        self.actionDodaj_ocen.setObjectName("actionDodaj_ocen")
        self.actionDodaj_wiele_ocen = QtWidgets.QAction(MainWindow)
        self.actionDodaj_wiele_ocen.setObjectName("actionDodaj_wiele_ocen")
        self.actionZmie_oceny = QtWidgets.QAction(MainWindow)
        self.actionZmie_oceny.setObjectName("actionZmie_oceny")
        self.actionDodaj_oceny = QtWidgets.QAction(MainWindow)
        self.actionDodaj_oceny.setObjectName("actionDodaj_oceny")
        self.actionDodaj_wiele_ocen_2 = QtWidgets.QAction(MainWindow)
        self.actionDodaj_wiele_ocen_2.setObjectName("actionDodaj_wiele_ocen_2")
        self.actionZmie_oceny_2 = QtWidgets.QAction(MainWindow)
        self.actionZmie_oceny_2.setObjectName("actionZmie_oceny_2")
        self.actionZmie_w_a_ciwo_ci_u_ytkownika = QtWidgets.QAction(MainWindow)
        self.actionZmie_w_a_ciwo_ci_u_ytkownika.setObjectName("actionZmie_w_a_ciwo_ci_u_ytkownika")
        self.actionDodaj_klas_2 = QtWidgets.QAction(MainWindow)
        self.actionDodaj_klas_2.setObjectName("actionDodaj_klas_2")
        self.actionZmie_w_a_ciwo_ci_klasy = QtWidgets.QAction(MainWindow)
        self.actionZmie_w_a_ciwo_ci_klasy.setObjectName("actionZmie_w_a_ciwo_ci_klasy")
        self.menuPlik.addAction(self.actionWyloguj_si)
        self.menuPlik.addAction(self.actionZamknij_program)
        self.menuNauczyciel.addAction(self.actionDodaj_sprawdzian)
        self.menuNauczyciel.addSeparator()
        self.menuNauczyciel.addAction(self.actionDodaj_oceny)
        self.menuNauczyciel.addAction(self.actionDodaj_wiele_ocen_2)
        self.menuNauczyciel.addSeparator()
        self.menuNauczyciel.addAction(self.actionZmie_oceny_2)
        self.menuAdmin.addAction(self.actionDodaj_u_ytkownika)
        self.menuAdmin.addAction(self.actionZmie_w_a_ciwo_ci_u_ytkownika)
        self.menuAdmin.addSeparator()
        self.menuAdmin.addAction(self.actionDodaj_klas_2)
        self.menuAdmin.addAction(self.actionZmie_w_a_ciwo_ci_klasy)
        self.menubar.addAction(self.menuPlik.menuAction())
        self.menubar.addAction(self.menuUcze.menuAction())
        self.menubar.addAction(self.menuNauczyciel.menuAction())
        self.menubar.addAction(self.menuAdmin.menuAction())

        # Mój kod

        self.actionWyloguj_si.triggered.connect(self.logout)
        self.actionZamknij_program.triggered.connect(app.closeAllWindows)
        self.comboBox.currentTextChanged.connect(self.showData)
        self.pushButton.clicked.connect(self.addNote)
        self.actionDodaj_oceny.triggered.connect(self.addNote)
        self.actionDodaj_u_ytkownika.triggered.connect(self.addUser)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dziennik"))
        self.label_2.setText(_translate("MainWindow", "Witaj, username ! | Rola: role"))
        self.label.setText(_translate("MainWindow", "Klasa:"))
        self.pushButton.setText(_translate("MainWindow", "Dodaj ocenę"))
        self.menuPlik.setTitle(_translate("MainWindow", "Plik"))
        self.menuNauczyciel.setTitle(_translate("MainWindow", "Nauczyciel"))
        self.menuAdmin.setTitle(_translate("MainWindow", "Admin"))
        self.menuUcze.setTitle(_translate("MainWindow", "Uczeń"))
        self.actionWyloguj_si.setText(_translate("MainWindow", "Wyloguj się"))
        self.actionZamknij_program.setText(_translate("MainWindow", "Zamknij program"))
        self.actionZamknij_program.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionDodaj_u_ytkownika.setText(_translate("MainWindow", "Dodaj użytkownika"))
        self.actionDodaj_klas.setText(_translate("MainWindow", "Dodaj klasę"))
        self.actionDodaj_sprawdzian.setText(_translate("MainWindow", "Dodaj sprawdzian"))
        self.actionDodaj_ocen.setText(_translate("MainWindow", "Dodaj ocenę"))
        self.actionDodaj_wiele_ocen.setText(_translate("MainWindow", "Dodaj wiele ocen"))
        self.actionZmie_oceny.setText(_translate("MainWindow", "Zmień oceny"))
        self.actionDodaj_oceny.setText(_translate("MainWindow", "Dodaj ocenę"))
        self.actionDodaj_wiele_ocen_2.setText(_translate("MainWindow", "Dodaj wiele ocen"))
        self.actionZmie_oceny_2.setText(_translate("MainWindow", "Zmień oceny"))
        self.actionZmie_w_a_ciwo_ci_u_ytkownika.setText(_translate("MainWindow", "Zmień właściwości użytkownika"))
        self.actionDodaj_klas_2.setText(_translate("MainWindow", "Dodaj klasę"))
        self.actionZmie_w_a_ciwo_ci_klasy.setText(_translate("MainWindow", "Zmień właściwości klasy"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = Ui_MainWindow()
    lw = Ui_LoginWindow(main)
    sys.exit(app.exec_())

