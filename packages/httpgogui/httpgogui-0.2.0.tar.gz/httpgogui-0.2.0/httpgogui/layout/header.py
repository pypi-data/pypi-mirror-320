from PySide6.QtWidgets import QHBoxLayout
from qfluentwidgets import ComboBox,LineEdit,PushButton,CardWidget


class HeaderWidget(CardWidget):
    """header 布局"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置card高度
        self.setMinimumHeight(80)
        self.__qhbox_layout = QHBoxLayout(self)
        self.__qhbox_layout.setContentsMargins(10,10,10,10)
        ## 下拉框
        self.method_combo_box = ComboBox()
        # 添加选项
        items = ["GET","POST","DELETE","PUT","OPTION"]
        self.method_combo_box.addItems(items)
        ## 输入框
        self.url_line_text = LineEdit()
        # 设置提示文本
        self.url_line_text.setPlaceholderText("http://example.com")
        ## 请求按钮
        self.send_button = PushButton("发送")
        self.send_button.setMinimumWidth(80)

        # 添加组件到布局
        self.__qhbox_layout.addWidget(self.method_combo_box)
        self.__qhbox_layout.addSpacing(10) # 设置组件间的间距
        self.__qhbox_layout.addWidget(self.url_line_text)
        self.__qhbox_layout.addSpacing(30) # 设置组件间的间距
        self.__qhbox_layout.addWidget(self.send_button)

