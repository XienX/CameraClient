# -*- coding: utf-8 -*-
# @Time : 2021/3/9 23:03
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：程序入口，ClientMainWindow类

import sys

from PIL import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QApplication

from clientWindow import Ui_MainWindow
from register import RegisterUI
from fullScreen import fullScreenUI
from controlThread import ControlThread


class ClientMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)

        self.registerUI = RegisterUI()
        self.fullScreenUI = fullScreenUI()
        screenRect = QGuiApplication.primaryScreen().availableVirtualGeometry()
        # print(f'{screenRect.width()}, {screenRect.height()}')
        self.fullScreenUI.resize(screenRect.width(), screenRect.height()-28)
        self.fullScreenUI.cameraLabel.resize(screenRect.width(), screenRect.height()-28)

        self.controlThread = None

        self.cameraList = ['0']
        self.nowCameraNum = '0'
        self.definitionList = ['480P', '360P']
        self.nowDefinition = '480P'
        self.frameRateList = ['25FPS', '10FPS']
        self.nowRate = '25FPS'

        self.slot_init()

    def slot_init(self):
        self.connectButton.clicked.connect(self.connect_server)
        self.closeButton.clicked.connect(self.close_connect)
        self.registerButton.clicked.connect(self.registerUI.show)
        self.fullScreenButton.clicked.connect(self.fullScreenUI.showMaximized)

        self.cameraNumInput.addItems(self.cameraList)
        self.cameraNumInput.currentIndexChanged[str].connect(self.change_camera)
        self.definitionInput.addItems(self.definitionList)
        self.definitionInput.currentIndexChanged[str].connect(self.change_definition)
        self.frameRateInput.addItems(self.frameRateList)
        self.frameRateInput.currentIndexChanged[str].connect(self.change_rate)

        self.moveLeftButton.clicked.connect(lambda: self.move_servo('4'))
        self.moveRightButton.clicked.connect(lambda: self.move_servo('6'))
        self.moveUpButton.clicked.connect(lambda: self.move_servo('8'))
        self.moveDownButton.clicked.connect(lambda: self.move_servo('2'))

    def change_camera(self, camera_num):  # 改变摄像头
        # print('change_camera  ' + camera_num)
        if camera_num != '' and camera_num != self.nowCameraNum \
                and self.controlThread is not None and self.controlThread.isRunning():
            self.controlThread.operationQueue.put({'code': 220, 'camera': int(camera_num)})
            self.nowCameraNum = camera_num

            # 重置分辨率和帧率
            self.nowDefinition = '480P'
            self.definitionInput.setCurrentIndex(0)
            self.nowRate = '25FPS'
            self.frameRateInput.setCurrentIndex(0)

    def change_definition(self, definition):  # 改变分辨率
        # print('change_definition  ' + definition)
        if definition != self.nowDefinition and self.controlThread is not None and self.controlThread.isRunning():
            self.controlThread.operationQueue.put(
                {'code': 510, 'camera': int(self.nowCameraNum), 'definition': int(definition[0:len(definition) - 1])})
            self.nowDefinition = definition

    def change_rate(self, rate):  # 改变帧率
        # print('change_rate  ' + rate)
        if rate != self.nowRate and self.controlThread is not None and self.controlThread.isRunning():
            self.controlThread.operationQueue.put(
                {'code': 511, 'camera': int(self.nowCameraNum), 'rate': 0.04 if rate == '25FPS' else 0.1})
            self.nowRate = rate

    def connect_server(self):  # 连接服务器
        self.controlThread = ControlThread(self.userNameInput.text(), self.passwordInput.text(),
                                           self.ipInput.text(), int(self.portInput.text()),)
        self.controlThread.frame_signal.connect(self.show_camera)  # 连接信号
        self.controlThread.log_signal.connect(self.print_log)
        self.controlThread.enabled_signal.connect(self.control_enabled)
        self.controlThread.camera_list_signal.connect(self.set_camera_list)
        self.controlThread.start()

        # 重置
        self.nowCameraNum = '0'
        self.nowDefinition = '480P'
        self.nowRate = '25FPS'
        self.cameraNumInput.setCurrentIndex(0)
        self.definitionInput.setCurrentIndex(0)
        self.frameRateInput.setCurrentIndex(0)

    def show_camera(self, frame):  # 显示一帧
        # print(frame)
        # self.cameraLabel.setPixmap(QPixmap.fromImage(showImage))
        if self.fullScreenUI.isHidden():
            self.cameraLabel.setPixmap(ImageQt.toqpixmap(frame))
        else:
            self.fullScreenUI.cameraLabel.setPixmap(ImageQt.toqpixmap(frame).scaled(
                self.fullScreenUI.cameraLabel.width(), self.fullScreenUI.cameraLabel.height(), Qt.KeepAspectRatio))

    def print_log(self, log_str):  # UI上打印日志
        self.log.append(log_str)

    def control_enabled(self, b):  # 控制是否禁用
        self.connectButton.setEnabled(b)
        self.closeButton.setEnabled(not b)
        self.userNameInput.setEnabled(b)
        self.passwordInput.setEnabled(b)
        self.ipInput.setEnabled(b)
        self.portInput.setEnabled(b)

    def close_connect(self):  # 断开连接
        self.controlThread.operationQueue.put({'code': 250})

    def set_camera_list(self, num):  # 设置摄像头列表范围
        if num != len(self.cameraList):
            self.cameraNumInput.clear()
            self.cameraList = [str(i) for i in range(num)]
            self.cameraNumInput.addItems(self.cameraList)

    def move_servo(self, direction):  # 控制云台
        if self.controlThread is not None and self.controlThread.isRunning():
            self.controlThread.operationQueue.put({'code': 520, 'camera': int(self.nowCameraNum), 'move': direction})

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:  # 关闭程序
        try:
            super().closeEvent(a0)
            self.registerUI.close()

            if self.controlThread and self.controlThread.isRunning():
                self.controlThread.close()
        except BaseException as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = ClientMainWindow()
    ui.show()
    sys.exit(app.exec_())
