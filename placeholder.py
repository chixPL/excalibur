from PyQt5.QtWidgets import QMessageBox

class Placeholder:
    def messageBox(self, title, icon, text, infoText="", detailText=""):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(infoText)
        msg.setWindowTitle(title)
        msg.setDetailedText(detailText)
        msg.exec_()
    
    def __init__(self) -> None:
        self.messageBox("Funkcja niegotowa", QMessageBox.Information, "Ta funkcja jeszcze nie została dodana do programu.", "Wróć później!")