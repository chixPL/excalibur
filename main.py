# -*- coding: utf-8 -*-

"""
Excalibur - dziennik szkolny
by Jakub Rutkowski (chixPL) 2023
"""

currentVersion = "0.0.7-dev" # wersja aplikacji

# Standardowe importy

from PyQt5 import QtCore, QtGui, QtWidgets
import psycopg2
from datetime import datetime
# Własne pliki
from login import Ui_LoginWindow
from config import config
from addnote import Ui_AddNote
from adduser import Ui_AddUser
from updateuser import Ui_UpdateUser
from placeholder import Placeholder
from addclass import Ui_AddClass

# Naprawa błędu związanego z ikoną aplikacji na Windowsie
import ctypes
myappid = 'chix.pyqt.excalibur.v' + currentVersion
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except AttributeError: # Ubuntu, macOS
    pass

class Ui_MainWindow(object):

    def __init__(self):
        global currentVersion
        self.currentVersion = currentVersion

        MainWindow = QtWidgets.QMainWindow()
        self.MainWindow = MainWindow
        self.setupUi(MainWindow)
        self.params = config()
    
    def show_main(self, email):
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
        
        if(self.user_role == 'Nauczyciel'):
            self.menuStudent.menuAction().setVisible(False)
            self.menuAdmin.menuAction().setVisible(False)
        elif(self.user_role == 'Admin'):
            self.menuStudent.menuAction().setVisible(False)
        else:
            self.menuTeacher.menuAction().setVisible(False)
            self.menuAdmin.menuAction().setVisible(False)

            
        
        self.label_2.setText(f"Witaj, {self.user_name} {self.user_surname}! | Twoja rola: {self.user_role}")
        self.getClasses()

    def getClasses(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.params)       # łączenie z bazą
            cur = conn.cursor()                     # tworzenie kursora do bazy
            query = f"SELECT skrot_przedmiotu FROM przedmioty INNER JOIN uzytkownicy ON przedmioty.id_nauczyciela = uzytkownicy.id_uzytkownika WHERE id_nauczyciela = {self.user_id} ORDER BY id_przedmiotu" # query
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

            query = f"SELECT id_uzytkownika FROM uzytkownicy_przedmioty WHERE id_przedmiotu = {class_id} ORDER BY id_uzytkownika" # pobierz ID uczniów którzy się uczą w danej klasie
            cur.execute(query)
            user_ids = cur.fetchall()

            query = f"SELECT CONCAT_WS(' ', imie, nazwisko)  FROM uzytkownicy_przedmioty INNER JOIN uzytkownicy ON uzytkownicy_przedmioty.id_uzytkownika = uzytkownicy.id_uzytkownika WHERE uzytkownicy_przedmioty.id_przedmiotu = {class_id} ORDER BY uzytkownicy.id_uzytkownika" # pobierz nazwy uczniów
            cur.execute(query)
            user_names = cur.fetchall()

            query = f"SELECT skrot_sprawdzianu FROM sprawdziany INNER JOIN przedmioty ON sprawdziany.id_przedmiotu=przedmioty.id_przedmiotu WHERE sprawdziany.id_przedmiotu = {class_id} ORDER BY id_sprawdzianu" # pobierz nazwy sprawdzianów
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
                query = f"SELECT ocena, id_sprawdzianu FROM oceny WHERE id_ucznia = {user_ids[i][0]}"
                # todo: wszystkie informacje o ocenie po dwukliku na ocenę w tablicy
                cur.execute(query)
                res = cur.fetchall()
                grades = [x[0] for x in res]
                test_ids = [x[1] for x in res]
                # wstawiaj kolumnami
                for j in range(0, len(test_ids)):
                    self.tableWidget.setItem(i, test_ids[j]-1, QtWidgets.QTableWidgetItem(grades[j]))

                query = f"SELECT ROUND(AVG(CAST(LEFT(ocena, 1) AS INT)),2) FROM oceny JOIN sprawdziany ON oceny.id_sprawdzianu = sprawdziany.id_sprawdzianu WHERE id_przedmiotu = {class_id} AND id_ucznia = {user_ids[i][0]}" # pobierz średnią ucznia
                # LEFT bierze pierwszy znak (w średniej plusy/minusy pomijamy) a CAST zmienia varchary na inty
                
                cur.execute(query)
                srednia = cur.fetchone()[0]
                if srednia is not None:
                    self.tableWidget.setItem(i, len(test_names)-1, QtWidgets.QTableWidgetItem(str(srednia)))
                    
            self.tableWidget.update()
        
        except (Exception, psycopg2.DatabaseError) as err:
            print(f"Błąd połączenia z bazą: {err}")
            return False

        finally:
            if conn is not None:
                conn.close()                        # zamknięcie konektora do bazy

    def addNote(self):
        class_shortcut = self.comboBox.currentText()
        ui = Ui_AddNote(main, class_shortcut)
    
    def addUser(self):
        ui = Ui_AddUser()
    
    def updateUser(self):
        ui = Ui_UpdateUser()

    def showPlaceholder(self):
        placeholder = Placeholder()
    
    def addClass(self):
        ui = Ui_AddClass()

    def logout(self):
        self.MainWindow.hide()
        global lw
        lw.clear_show()
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(831, 649)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 50, 811, 531))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(78)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(700, 580, 121, 25))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon1)
        self.pushButton.setIconSize(QtCore.QSize(32, 32))
        self.pushButton.setObjectName("pushButton")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(0, 2, 821, 45))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(32, 32))
        self.label_3.setMaximumSize(QtCore.QSize(32, 32))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("images/logo.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.line_2 = QtWidgets.QFrame(self.widget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setMinimumSize(QtCore.QSize(32, 32))
        self.label_5.setMaximumSize(QtCore.QSize(32, 32))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_5.setFont(font)
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("images/time.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.label_4 = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 831, 22))
        self.menubar.setObjectName("menubar")
        self.menuPlik = QtWidgets.QMenu(self.menubar)
        self.menuPlik.setObjectName("menuPlik")
        self.menuStudent = QtWidgets.QMenu(self.menubar)
        self.menuStudent.setObjectName("menuStudent")
        self.menuTeacher = QtWidgets.QMenu(self.menubar)
        self.menuTeacher.setObjectName("menuTeacher")
        self.menuAdmin = QtWidgets.QMenu(self.menubar)
        self.menuAdmin.setObjectName("menuAdmin")
        MainWindow.setMenuBar(self.menubar)
        self.actionLogout = QtWidgets.QAction(MainWindow)
        self.actionLogout.setObjectName("actionLogout")
        self.actionCloseProgram = QtWidgets.QAction(MainWindow)
        self.actionCloseProgram.setObjectName("actionCloseProgram")
        self.actionAddTest = QtWidgets.QAction(MainWindow)
        self.actionAddTest.setObjectName("actionAddTest")
        self.actionAddGrade = QtWidgets.QAction(MainWindow)
        self.actionAddGrade.setObjectName("actionAddGrade")
        self.actionChangeGrade = QtWidgets.QAction(MainWindow)
        self.actionChangeGrade.setObjectName("actionChangeGrade")
        self.actionAddUser = QtWidgets.QAction(MainWindow)
        self.actionAddUser.setObjectName("actionAddUser")
        self.actionChangeUser = QtWidgets.QAction(MainWindow)
        self.actionChangeUser.setObjectName("actionChangeUser")
        self.actionAddClass = QtWidgets.QAction(MainWindow)
        self.actionAddClass.setObjectName("actionAddClass")
        self.actionChangeClass = QtWidgets.QAction(MainWindow)
        self.actionChangeClass.setObjectName("actionChangeClass")
        self.menuPlik.addAction(self.actionLogout)
        self.menuPlik.addAction(self.actionCloseProgram)
        self.menuTeacher.addAction(self.actionAddTest)
        self.menuTeacher.addSeparator()
        self.menuTeacher.addAction(self.actionAddGrade)
        self.menuTeacher.addAction(self.actionChangeGrade)
        self.menuAdmin.addAction(self.actionAddUser)
        self.menuAdmin.addAction(self.actionChangeUser)
        self.menuAdmin.addSeparator()
        self.menuAdmin.addAction(self.actionAddClass)
        self.menuAdmin.addAction(self.actionChangeClass)
        self.menubar.addAction(self.menuPlik.menuAction())
        self.menubar.addAction(self.menuStudent.menuAction())
        self.menubar.addAction(self.menuTeacher.menuAction())
        self.menubar.addAction(self.menuAdmin.menuAction())

        # Mój kod

        # Przyciski i autoodświeżanie
        self.comboBox.currentTextChanged.connect(self.showData)
        self.pushButton.clicked.connect(self.addNote)
        self.pushButton_2.clicked.connect(self.logout)

        # Zegar
        timer = QtCore.QTimer(self.label_4)
        # adding action to timer
        timer.timeout.connect(lambda: self.label_4.setText(datetime.now().strftime("%H:%M")))
        # update the timer every second
        timer.start(60000)

        # Menu
        self.actionLogout.triggered.connect(self.logout)
        self.actionCloseProgram.triggered.connect(app.closeAllWindows)
        self.actionAddGrade.triggered.connect(self.addNote)
        self.actionAddUser.triggered.connect(self.addUser)
        self.actionChangeUser.triggered.connect(self.updateUser)
        
        # Placeholdery
        self.actionAddClass.triggered.connect(self.addClass)
        self.actionChangeClass.triggered.connect(self.showPlaceholder)
        self.actionAddTest.triggered.connect(self.showPlaceholder)
        self.actionChangeGrade.triggered.connect(self.showPlaceholder)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dziennik"))
        self.pushButton.setText(_translate("MainWindow", "Dodaj ocenę"))
        self.label.setText(_translate("MainWindow", "Klasa:"))
        self.label_4.setText(_translate("MainWindow", datetime.now().strftime("%H:%M")))
        self.pushButton_2.setText(_translate("MainWindow", "Wyloguj się"))
        self.menuPlik.setTitle(_translate("MainWindow", "Plik"))
        self.menuStudent.setTitle(_translate("MainWindow", "Uczeń"))
        self.menuTeacher.setTitle(_translate("MainWindow", "Nauczyciel"))
        self.menuAdmin.setTitle(_translate("MainWindow", "Admin"))
        self.actionLogout.setText(_translate("MainWindow", "Wyloguj się"))
        self.actionCloseProgram.setText(_translate("MainWindow", "Zamknij program"))
        self.actionCloseProgram.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionAddTest.setText(_translate("MainWindow", "Dodaj sprawdzian"))
        self.actionAddGrade.setText(_translate("MainWindow", "Dodaj ocenę"))
        self.actionChangeGrade.setText(_translate("MainWindow", "Zmień ocenę"))
        self.actionAddUser.setText(_translate("MainWindow", "Dodaj użytkownika"))
        self.actionChangeUser.setText(_translate("MainWindow", "Zmień właściwości użytkownika"))
        self.actionAddClass.setText(_translate("MainWindow", "Dodaj klasę"))
        self.actionChangeClass.setText(_translate("MainWindow", "Zmień właściwości klasy"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = Ui_MainWindow()
    with open("styles/Aqua.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
        f.close()
    lw = Ui_LoginWindow(main)
    sys.exit(app.exec_())