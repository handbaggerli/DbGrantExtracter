# -*- coding: utf-8 -*-

import resources
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_MainWindow import Ui_MainWindow
from PyQt5.QtCore import pyqtSlot
from Ui_LoginDialog import Ui_LoginDialog

class MyMainWindow(Ui_MainWindow):
    def __init__(self, globalGrantExtracter):
        super().__init__()
        self.globalGrantExtracter = globalGrantExtracter

    def init_user_data(self):
        self.globalGrantExtracter.loadComboBoxDataFromDB()
        self.__refreshParameters()


    def connect_user_events(self):
        self.actionVersion.triggered.connect(self.__versionInfo)
        self.actionExit.triggered.connect(self.__exit)
        self.actionLogin.triggered.connect(self.__loginDB)
        self.actionBrowsePath.triggered.connect(self.__browsePath)
        self.actionScript_Donwnloaden.triggered.connect(self.__scriptDownload)
        self.actionCopyParam.triggered.connect(self.__copyParam)
        self.pushButtonLogin.clicked.connect(self.__loginDB)
        self.pushButtonBrowsePath.clicked.connect(self.__browsePath)
        self.pushButtonDownload.clicked.connect(self.__scriptDownload)
        self.comboBoxSource.currentIndexChanged.connect(self.__comboBoxChanged)
        self.comboBoxTarget.currentIndexChanged.connect(self.__comboBoxChanged)

    @pyqtSlot()
    def __versionInfo(self):
        message_text = (
            "Das Programm DB Grant Extracter wurde mit vollständig in Python mit folgenden Komponenten ertellt.\n"
            "Python Version 3.5.3 Anaconda\n"
            "Zusätzliche wurden folgende Module über die Conda Umgebung installiert.\n"
            "cx_Oracle 6.0b2\n"
            "pip 9.0.1\n"
            "pycrypto 2.6.1\n"
            "pyqt 5.6.0\n"
            "qt 5.6.2\n"
            "setuptools 27.2.0\n"
            "chardet 3.0.4"
        )
        msg_info = QtWidgets.QMessageBox()
        msg_info.setWindowTitle("Versionshinweis")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/archive-extract-2.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        msg_info.setWindowIcon(icon)
        msg_info.setText(message_text)
        msg_info.setIcon(QtWidgets.QMessageBox.Information)
        msg_info.setWindowModality(QtCore.Qt.ApplicationModal)
        msg_info.exec_()

    @pyqtSlot()
    def __exit(self):
        QtCore.QCoreApplication.instance().quit()

    @pyqtSlot()
    def __loginDB(self):
        loginShow = True
        self.statusBar.showMessage("Datenbank Verbindung setzen.", 10000)
        while loginShow:
            LoginDialog = QtWidgets.QDialog()
            LoginDialog.setWindowModality(QtCore.Qt.ApplicationModal)
            ui = Ui_LoginDialog()
            ui.setupUi(LoginDialog)
            ui.lineEdit_Username.setText("GRANTADMIN")
            result = LoginDialog.exec_()
            if result == QtWidgets.QDialog.Accepted:
                self.statusBar.showMessage("Datenbank Verbindung testen...", 10000)
                self.globalGrantExtracter.getDbLogin().setUserName(userName=ui.lineEdit_Username.text())
                self.globalGrantExtracter.getDbLogin().setPassword(passWord=ui.lineEdit_Password.text())
                self.globalGrantExtracter.getDbLogin().setConnection(connection=ui.lineEdit_Connection.text())
                if self.globalGrantExtracter.getDbLogin().testConnection(printInfo=False):
                    self.statusBar.showMessage("Datenbank Verbindung OK.", 10000)
                    loginShow = False
                    self.globalGrantExtracter.loadComboBoxDataFromDB()
                else:
                    self.statusBar.showMessage("Datenbank Verbindung fehlgeschlagen, Dialog wird neu angezeigt.", 10000)
            elif result == QtWidgets.QDialog.Rejected:
                loginShow = False
            LoginDialog.destroy()
        self.__refreshParameters()

    @pyqtSlot()
    def __browsePath(self):
        self.statusBar.showMessage("Installationspfad setzen.", 10000)
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.globalGrantExtracter.setDownload_path(download_path=folder)
        self.__refreshParameters()


    @pyqtSlot()
    def __scriptDownload(self):
        self.statusBar.showMessage("Download Grant Commands wird gestarted.")
        if self.globalGrantExtracter.downloadScript():
            self.statusBar.showMessage("Download Grant Commands erfolgreich beendet.", 10000)
        else:
            self.statusBar.showMessage("Download Grant Commands mit Fehler beendet.", 10000)


    @pyqtSlot()
    def __copyParam(self):
        parameter = self.globalGrantExtracter.dupParam2String()
        QtWidgets.QApplication.clipboard().setText(parameter)

    @pyqtSlot()
    def __comboBoxChanged(self):
        self.globalGrantExtracter.setSource_schema(self.comboBoxSource.currentText())
        self.globalGrantExtracter.setTarget_schema(self.comboBoxTarget.currentText())


    #
    # Force Refresh the Gui
    #
    def __refreshParameters(self):
        self.lineEdidConnection.setText(self.globalGrantExtracter.getDbLogin().getDisplayConnectionString())
        self.lineEditPath.setText(self.globalGrantExtracter.getDownload_path())
        self.comboBoxSource.clear()
        self.comboBoxTarget.clear()
        for schema in self.globalGrantExtracter.getList_source_schemas():
            self.comboBoxSource.addItem(schema)
        for schema in self.globalGrantExtracter.getList_target_schemas():
            self.comboBoxTarget.addItem(schema)
        self.comboBoxSource.setCurrentText(self.globalGrantExtracter.getSource_schema())
        self.comboBoxTarget.setCurrentText(self.globalGrantExtracter.getTarget_schema())
