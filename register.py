# -*- coding: utf-8 -*-
# @Time : 2021/3/15 15:13
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : register.py
# @notice ：注册页面、注册连接线程

import json
import socket

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from registerDialog import Ui_RegisterDialog


class RegisterUI(QMainWindow, Ui_RegisterDialog):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)

        self.registerThread = None

        self.slot_init()

    def slot_init(self):
        self.registerButton.clicked.connect(self.register)
        self.cancelButton.clicked.connect(self.cancel)

    def register(self):
        if self.userNameInputRegister.text() == '' or ' ' in self.userNameInputRegister.text() or \
                self.passwordInputRegister.text() == '' or ' ' in self.passwordInputRegister.text():
            self.tip.setText('为空或存在空格')
            return

        self.registerThread = RegisterThread(self.userNameInputRegister.text(), self.passwordInputRegister.text(),
                                             self.ipInputRegister.text(), int(self.portInputRegister.text()))
        self.registerThread.enabled_signal.connect(self.control_enabled)
        self.registerThread.tip_signal.connect(self.print_tip)
        self.registerThread.start()

    def control_enabled(self, b):  # 控制是否禁用
        self.registerButton.setEnabled(b)
        self.userNameInputRegister.setEnabled(b)
        self.passwordInputRegister.setEnabled(b)
        self.ipInputRegister.setEnabled(b)
        self.portInputRegister.setEnabled(b)

    def print_tip(self, tip_str):
        self.tip.setText(tip_str)

    def cancel(self):  # 取消按钮
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            super().closeEvent(a0)
            if self.registerThread and self.registerThread.isRunning():
                self.registerThread.close()
        except BaseException as e:
            print(e)


class RegisterThread(QtCore.QThread):
    enabled_signal = pyqtSignal(bool)
    tip_signal = pyqtSignal(str)

    def __init__(self, user_name, password, ip, port):
        super().__init__()
        self.user_name = user_name
        self.password = password
        self.ip = ip
        self.port = port

        self.connect = socket.socket()  # 创建 socket 对象

    def run(self):
        try:
            self.enabled_signal.emit(False)
            self.tip_signal.emit('注册中...')

            self.connect.connect((self.ip, self.port))

            message = {'code': 210, 'userName': self.user_name, 'password': self.password}  # 注册
            self.connect.send(json.dumps(message).encode())

            jsonMessage = self.connect.recv(1024).decode()
            message = json.loads(jsonMessage)
            # print(message)

            if message['code'] == 310:  # 注册成功
                self.tip_signal.emit('已注册')
            elif message['code'] == 311:  # 注册失败
                self.tip_signal.emit('用户已存在')
            else:
                self.tip_signal.emit(message['code'])

        except BaseException as e:
            print(e)
            self.tip_signal.emit('Error')

        self.enabled_signal.emit(True)

