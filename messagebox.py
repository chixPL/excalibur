from PyQt5.QtWidgets import QMessageBox

def messageBox(title, icon, text, infoText="", detailText=""):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setText(text)
    msg.setInformativeText(infoText)
    msg.setWindowTitle(title)
    msg.setDetailedText(detailText)
    msg.exec_()