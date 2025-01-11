"""main文件"""

import sys
import json
from typing import Union
from requests import Response

from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QWidget,
    QCompleter,
)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QIcon
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets import (
    setThemeColor,
    InfoBar,
    InfoBarPosition,
    IndeterminateProgressRing,
)
from httpgogui.layout.header import HeaderWidget
from httpgogui.layout.body import BodyWidget
from httpgogui.layout.bottom import BottomWidget
from httpgogui.components.table_widget import CommonTableWidget
from httpgogui.cache.sqlite_db import Database
from httpgogui.utils.enum.error import ErrorEnum
from httpgogui.thread.request_thread import WorkerThread


class HttpgoWidget(QMainWindow):
    """窗口类"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.header_widget = None
        self.body_widget = None
        self.bottom_widget = None
        self.theme_color = None
        # 初始化数据库
        self.db = Database()
        self.completion_list = self.db.load_completion_list()
        self.url_completer = QCompleter(self.completion_list, self)
        self.url_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.url_completer.setMaxVisibleItems(10)
        # 初始化 UI 和 信号
        self.setup_ui()
        # url输入框设置 QCompleter
        self.header_widget.url_line_text.setCompleter(self.url_completer)
        self.connect_signals()

    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("httpgo-gui")
        self.setWindowIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailSend)))

        # 只能获取 Windows 和 macOS 的主题色
        if sys.platform in ["win32", "darwin"]:
            self.theme_color = getSystemAccentColor().name()
            setThemeColor(getSystemAccentColor(), save=False)
        self.resize(1000, 800)
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # 创建主布局
        main_layout = QVBoxLayout()
        # 添加分区布局
        self.header_widget = HeaderWidget()
        main_layout.addWidget(self.header_widget)
        self.body_widget = BodyWidget()
        main_layout.addWidget(self.body_widget)
        self.bottom_widget = BottomWidget()
        self.bottom_widget.status_code_label.setStyleSheet(
            f"color: {self.theme_color};"
        )
        main_layout.addWidget(self.bottom_widget)
        # main_layout.addStretch() # 添加弹性空间
        # 设置主布局到窗口
        central_widget.setLayout(main_layout)

        # loading
        self.spinner = IndeterminateProgressRing(self, False)
        self.spinner.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )  # 允许鼠标事件穿透

    def resizeEvent(self, event):
        """窗口大小缩放钩子函数"""
        super().resizeEvent(event)  # 保持默认行为
        # 获取窗口的宽度和高度
        window_width = self.width()
        window_height = self.height()
        # 获取进度环的宽度和高度
        spinner_width = self.spinner.width()
        spinner_height = self.spinner.height()

        # 计算偏移量，以使进度环居中
        offset_x = (window_width - spinner_width) // 2
        offset_y = (window_height - spinner_height) // 2

        # 设置进度环的位置，使其居中
        self.spinner.setGeometry(offset_x, offset_y, spinner_width, spinner_height)

    def showEvent(self, event):
        """窗口显示时被调用的钩子函数"""
        super().showEvent(event)
        # 聚焦
        self.header_widget.url_line_text.setFocus()

    def connect_signals(self):
        """连接信号与槽"""
        self.header_widget.send_button.clicked.connect(self.on_button_clicked)

    def save_input(self):
        """保存用户输入的内容并更新补全数据"""
        new_input = self.header_widget.url_line_text.text()
        # 如果输入不为空且不在已有列表中，则保存并更新补全菜单
        if new_input and new_input not in self.completion_list:
            self.db.save_completion(new_input)  # 保存到数据库

    def update_completer(self):
        """更新 QCompleter 使用新的补全列表"""
        self.completion_list = self.db.load_completion_list()  # 读取最新的list
        self.url_completer.setModel(QStringListModel(self.completion_list))

    def on_button_clicked(self):
        """点击发送按钮的槽函数"""
        # 创建线程实例
        self.worker = WorkerThread(
            method=self.header_widget.method_combo_box.currentText(),
            url=self.header_widget.url_line_text.text(),
            body=self.body_widget.body_widget.toPlainText(),
            params=self.parse_key_value(self.body_widget.params_widget),
            headers=self.parse_key_value(self.body_widget.header_widget),
            cookies=self.parse_key_value(self.body_widget.cookies_widget),
        )
        # 连接信号到槽函数
        self.worker.progress.connect(self.update_ui)
        # 启动线程
        self.worker.start()

    def update_ui(self, state: bool, response: Union[Response, ErrorEnum]):
        """更新ui"""
        if state:
            # 开始loading
            self.spinner.start()
            self.header_widget.send_button.setDisabled(True)
        else:
            # 停止loading
            self.spinner.stop()
            self.header_widget.send_button.setDisabled(False)
            self.worker = None  # 完成后释放线程对象，允许再次创建
            if isinstance(response, Response):
                # 展示结果
                if str(response.status_code).startswith("4") or str(
                    response.status_code
                ).startswith("5"):
                    self.bottom_widget.status_code_label.setText(
                        f"status code: <font color='red'>{response.status_code}</font>"
                    )
                elif str(response.status_code).startswith("2"):
                    self.bottom_widget.status_code_label.setText(
                        f"status code: <font color='green'>{response.status_code}</font>"
                    )
                elif str(response.status_code).startswith("3"):
                    self.bottom_widget.status_code_label.setText(
                        f"status code: <font color='{self.theme_color}'>{response.status_code}</font>"
                    )
                try:
                    self.bottom_widget.result_edit.setText(
                        json.dumps(response.json(), indent=4, ensure_ascii=False)
                    )
                except Exception:
                    self.bottom_widget.result_edit.setText(response.text)
                # 保存更新completion_list
                self.save_input()
                self.update_completer()
            elif response == ErrorEnum.JSONDECODEERROR:
                InfoBar.error(
                    title="Body",
                    content="无效的body参数",
                    orient=Qt.Horizontal,  # 内容太长时可使用垂直布局
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM,
                    duration=2000,
                    parent=self.bottom_widget,
                )
            elif (
                response == ErrorEnum.MISSINGSCHEMA or response == ErrorEnum.INVALIDURL
            ):
                InfoBar.error(
                    title="Url",
                    content="无效的URL",
                    orient=Qt.Horizontal,  # 内容太长时可使用垂直布局
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM,
                    duration=2000,
                    parent=self.bottom_widget,
                )
            elif response == ErrorEnum.READTIMEOUT:
                InfoBar.error(
                    title="Url",
                    content="接口请求超时",
                    orient=Qt.Horizontal,  # 内容太长时可使用垂直布局
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM,
                    duration=2000,
                    parent=self.bottom_widget,
                )

    def parse_key_value(self, widget: CommonTableWidget):
        """解析参数"""
        key_value_dict = dict()
        for row in range(widget.rowCount()):
            temp_list = []
            for col in range(widget.columnCount()):
                line_widget = widget.cellWidget(row, col)  # 获取该单元格的lineEdit
                text = line_widget.text()  # 获取 QLineEdit 的文本内容
                if text:
                    temp_list.append(text)
            if temp_list:
                try:
                    key_value_dict[temp_list[0]] = temp_list[1]
                except IndexError:
                    InfoBar.error(
                        title="Error",
                        content="参数不正确",
                        orient=Qt.Horizontal,  # 内容太长时可使用垂直布局
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM,
                        duration=2000,
                        parent=self.bottom_widget,
                    )
                    raise BaseException("参数不正确")
        return key_value_dict if key_value_dict else None

    def closeEvent(self, event):
        """关闭应用时关闭数据库连接"""
        self.db.close()
        super().closeEvent(event)


def main():
    """入口函数"""
    app = QApplication([])
    window = HttpgoWidget()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
