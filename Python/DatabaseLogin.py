# -*- coding: utf-8 -*-

__author__ = 'U10938'

import cx_Oracle as ora
import sys
from subprocess import Popen, PIPE


#
# Class holds the database login information and test database connection.
# Works for oracle only.
# Run also an sqlplus console
#
class DatabaseLogin():
    def __init__(self, userName, passWord, connection):
        self.userName = userName
        self.passWord = passWord
        self.connection = connection

    def getUserName(self):
        return self.userName

    def setUserName(self, userName):
        self.userName = userName

    def getPassword(self):
        return self.passWord

    def setPassword(self, passWord):
        self.passWord = passWord

    def getConnection(self):
        return self.connection

    def setConnection(self, connection):
        self.connection = connection

    def getConnectionString(self):
        return self.userName + "/" + self.passWord + "@" + self.connection

    def getDisplayConnectionString(self):
        if self.testConnection(printInfo=False):
            return self.userName + "@" + self.connection
        return ""

    def testConnection(self, printInfo=True):
        try:
            conn = ora.connect(self.getUserName(), self.getPassword(), self.getConnection())
            conn.close()
            return True
        except:
            if printInfo:
                print(sys.exc_info()[0])
                print("Verbindung ({0}@{1}) ist fehlgeschlagen".format(self.getUserName(),
                                                                       self.getConnection()))
        return False

    #
    # Execute the given File in SQL Plus
    #
    def runSqlPlus(self, filename):
        with Popen(['sqlplus', '-S', self.getConnectionString()], stdin=PIPE, stdout=PIPE, stderr=PIPE) as sqlplus:
            sqlplus.stdin.write(bytes('@' + filename, "utf-8"))
            return sqlplus.communicate()


from argparse import ArgumentParser


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--connection')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    dbLogin = DatabaseLogin(userName=args.username, passWord=args.password, connection=args.connection)
    dbLogin.testConnection()
    print(dbLogin.getConnectionString())
    print(dbLogin.getDisplayConnectionString())
