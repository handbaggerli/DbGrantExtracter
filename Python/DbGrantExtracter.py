# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from PyQt5 import QtCore, QtGui, QtWidgets
from MyMainWindow import MyMainWindow
from GlobalGrantExtracter import GlobalGrantExtrater
from DatabaseLogin import DatabaseLogin


def get_parser():
    parser = ArgumentParser()
    # Erweiterte Parameter, welche die Gui Initalisierung Regeln.
    parser.add_argument('--username', default=r"", help=r"Benutzername der Datenbank Verbindung.")
    parser.add_argument('--password', default=r"", help=r"Passwort der Datenbank Verbindung.")
    parser.add_argument('--connection', default=r"", help=r"Connection der Datenbank Verbindung.")
    parser.add_argument('--source_schema', default=r"",
                        help=r"Name des Source Schemas von wo die Grants vergeben werden.")
    parser.add_argument('--target_schema', default=r"",
                        help=r"Name des Ziel Schemas für diesem die Grants vergeben werden.")
    parser.add_argument('--download_path', default=r"", help=r"Pfad wo das Script gespeichert wird.")
    parser.add_argument('--hideGui', action='store_true', default=False, help=r"Startet DB Grant Extracter ohne GUI.")
    parser.add_argument('--json_parameter_file', default=r"",
                        help=(r"Übergabe eines Parameter Files in Jsonl Format."
                              "Zusammen mit den Argument --hideGui kann die "
                              "Arbeiten mit einem einzigen Aufruf erledigt werden. "
                              "Arbeiten in einem Jsonl File sind immer ohne Gui "
                              "und schreiben Debug Informationen auf die Konsole."))
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    dbLogin = DatabaseLogin(userName=args.username, passWord=args.password, connection=args.connection)
    globalGrantExtracter = GlobalGrantExtrater(dbLogin=dbLogin,
                                               source_schema=args.source_schema.upper(),
                                               target_schema=args.target_schema.upper(),
                                               download_path=args.download_path,
                                               json_parameter_file=args.json_parameter_file)
    if args.hideGui:
        globalGrantExtracter.completeAllJsonParams()
    else:
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = MyMainWindow(globalGrantExtracter=globalGrantExtracter)
        ui.setupUi(MainWindow)
        ui.init_user_data()
        ui.connect_user_events()
        MainWindow.show()
        sys.exit(app.exec_())
