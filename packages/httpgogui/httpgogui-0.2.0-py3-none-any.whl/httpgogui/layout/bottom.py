from PySide6.QtWidgets import QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from qfluentwidgets import CardWidget, TextEdit, BodyLabel, IndeterminateProgressRing


class BottomWidget(CardWidget):
    """Bottom 布局"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 定义布局方式
        self.__qvbox_layout = QVBoxLayout(self)
        # 定义label展示状态吗
        self.status_code_label = BodyLabel("status code: --", self)
        # 定义textedit展示结果
        self.result_edit = TextEdit(self)
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText("这里是结果展示区域...")
        # 添加组件到布局
        self.__qvbox_layout.addWidget(self.status_code_label)
        self.__qvbox_layout.addWidget(self.result_edit)
