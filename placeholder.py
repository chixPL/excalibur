from messagebox import messageBox
from PyQt5.QtWidgets import QMessageBox

class Placeholder:

    def __init__(self) -> None:
        messageBox("Funkcja niegotowa", QMessageBox.Information, "Ta funkcja jeszcze nie została dodana do programu.", "Wróć później!")