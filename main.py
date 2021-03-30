# -*- coding: utf-8 -*-
# @Time : 2021/3/9 23:03
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：程序入口，ClientMainWindow类

import sys

from PIL import ImageQt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication

from clientWindow import Ui_MainWindow
from register import RegisterUI
from controlThread import ControlThread


class ClientMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)

        self.registerUI = RegisterUI()

        self.controlThread = None

        self.slot_init()

    def slot_init(self):
        self.connectButton.clicked.connect(self.connect_server)
        self.closeButton.clicked.connect(self.close_connect)
        self.registerButton.clicked.connect(self.registerUI.show)

        self.moveLeftButton.clicked.connect(lambda: self.move_servo('4'))
        self.moveRightButton.clicked.connect(lambda: self.move_servo('6'))
        self.moveUpButton.clicked.connect(lambda: self.move_servo('8'))
        self.moveDownButton.clicked.connect(lambda: self.move_servo('2'))

    def connect_server(self):  # 连接服务器
        self.controlThread = ControlThread(self.userNameInput.text(), self.passwordInput.text(),
                                           self.ipInput.text(), int(self.portInput.text()))
        self.controlThread.frame_signal.connect(self.show_camera)  # 连接信号
        self.controlThread.log_signal.connect(self.print_log)
        self.controlThread.enabled_signal.connect(self.control_enabled)
        self.controlThread.start()

    def show_camera(self, frame):  # 显示一帧
        # print(frame)
        # show = cv2.resize(frame, (400, 300))

        # show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        # self.cameraLabel.setPixmap(QPixmap.fromImage(showImage))

        self.cameraLabel.setPixmap(ImageQt.toqpixmap(frame))


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
        # self.controlThread.close()
        # self.controlThread.terminate()
        # self.controlThread.wait()
        self.controlThread.operationQueue.put({'code': 250})

    def move_servo(self, direction):  # 控制云台
        if self.controlThread is not None and self.controlThread.isRunning():
            self.controlThread.operationQueue.put({'code': 520, 'camera': 0, 'move': direction})

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
