# -*- coding: utf-8 -*-
import cx_Oracle as ora
from Sqls import Sqls
import codecs
import os
import json
import base64

from Crypto.Cipher import AES


class GlobalGrantExtrater():
    def __init__(self, dbLogin, source_schema, target_schema, download_path, json_parameter_file):
        self.dbLogin = dbLogin
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.download_path = download_path
        self.json_parameter_file = json_parameter_file
        self.list_source_schemas = []
        self.list_target_schemas = []


    #
    # Db Login
    #
    def getDbLogin(self):
        return self.dbLogin

    #
    # Selected Source Schema Name
    #
    def getSource_schema(self):
        return self.source_schema

    def setSource_schema(self, source_schema):
        self.source_schema = source_schema

    #
    # Selected Target Schema Name
    #
    def getTarget_schema(self):
        return self.target_schema

    def setTarget_schema(self, target_schema):
        self.target_schema = target_schema
    #
    # Download Path for script
    #
    def getDownload_path(self):
        return self.download_path

    def setDownload_path(self, download_path):
        self.download_path = download_path

    #
    # Combo Box Lists
    #
    def getList_source_schemas(self):
        return self.list_source_schemas

    def getList_target_schemas(self):
        return self.list_target_schemas


    #
    # Download and Save the Script
    #
    def downloadScript(self):
        if not self.getDbLogin().testConnection(printInfo=False):
            return False
        scripts = []
        file_name = self.__buildFileName()
        with ora.connect(self.dbLogin.getUserName(), self.dbLogin.getPassword(), self.dbLogin.getConnection()) as conn:
            cur = conn.cursor()
            cur.execute(Sqls.SELECT_GRANTS4DOWNLOAD,
                        SOURCE_SCHEMA=self.getSource_schema().upper(),
                        TARGET_SCHEMA=self.getTarget_schema().upper())
            for row in cur:
                scripts.append(row[0])
        os.makedirs(self.getDownload_path(), exist_ok=True)
        with codecs.open(os.path.join(self.getDownload_path(), file_name), mode="w", encoding="utf-8") as fWrite:
            fWrite.write("\n".join(scripts))
        return True


    #
    # Load the Schemas Info for the Combo Boxes
    #
    def loadComboBoxDataFromDB(self):
        if not self.getDbLogin().testConnection(printInfo=False):
            return
        with ora.connect(self.dbLogin.getUserName(), self.dbLogin.getPassword(), self.dbLogin.getConnection()) as conn:
            cur = conn.cursor()
            cur.execute(Sqls.SELECT_GRANT_SCHEMAS)
            self.list_source_schemas.clear()
            self.list_target_schemas.clear()
            self.list_target_schemas.append("%")
            for row in cur:
                self.list_source_schemas.append(row[0])
                self.list_target_schemas.append(row[0])

    #
    # Copy current Parameters to JSONL String.
    #
    def dupParam2String(self):
        paramDic = dict()
        paramDic["dbLogin-user"] = self.dbLogin.getUserName()
        paramDic["dbLogin-pwd"] = self.__encryptInfo(plain_text=self.dbLogin.getPassword())
        paramDic["dbLogin-connection"] = self.dbLogin.getConnection()
        paramDic["source_schema"] = self.getSource_schema().upper()
        paramDic["target_schema"] = self.getTarget_schema().upper()
        paramDic["download_path"] = self.getDownload_path()
        return json.dumps(paramDic)

    #
    # Download all Scripts in the JSONL File.
    #
    def completeAllJsonParams(self):
        with codecs.open(self.json_parameter_file,mode="r") as fReader:
            json_parameter_list = fReader.readlines()
        for parameter in json_parameter_list:
            if not parameter[0:1] == "#":
                self.__loadFromJson(json_parameters=parameter)
                print("Download Script {file_name}.".format(file_name=self.__buildFileName()))
                self.downloadScript()

    #
    # Fill in the variables from Json Parameters
    #
    def __loadFromJson(self, json_parameters):
        paramDic = json.loads(json_parameters)
        self.dbLogin.setUserName(userName=paramDic["dbLogin-user"])
        self.dbLogin.setPassword(passWord=self.__decryptInfo(paramDic["dbLogin-pwd"]))
        self.dbLogin.setConnection(connection=paramDic["dbLogin-connection"])
        self.source_schema = paramDic["source_schema"]
        self.target_schema = paramDic["target_schema"]
        self.download_path = paramDic["download_path"]



    #
    # Encryption for Password
    #
    def __encryptInfo(self, plain_text):
        # zu decodieren String muss ein mehrfaches von 16 lang sein.
        pad_len = ((len(plain_text) // 16) + 1) * 16
        start_string = plain_text.rjust(pad_len)
        encryption_suite = AES.new('Key12mitValue45Q', AES.MODE_CBC, 'NochSoEinGlump64')
        cipher_bytes = encryption_suite.encrypt(start_string)
        cipher_text = base64.urlsafe_b64encode(cipher_bytes)
        return cipher_text.decode()

    #
    # Decryption for Password
    #
    def __decryptInfo(self, cipher_text):
        cipher_text_bytes = base64.urlsafe_b64decode(cipher_text)
        decryption_suite = AES.new('Key12mitValue45Q', AES.MODE_CBC, 'NochSoEinGlump64')
        temp_string_bytes = decryption_suite.decrypt(cipher_text_bytes)
        end_string = temp_string_bytes.decode().strip()
        return end_string

    def __buildFileName(self):
        target_schema = self.getTarget_schema().upper()
        delemiter = "_"
        if target_schema == "%":
            target_schema = ""
            delemiter = ""
        file_name = "{db_name}_{source_schema}_{target_schema}{delemiter}grants.sql".format(
            db_name=self.dbLogin.getConnection().upper(),
            source_schema=self.getSource_schema().upper(),
            target_schema=target_schema,
            delemiter=delemiter)
        return file_name
