from PySide6.QtWidgets import (
    QVBoxLayout,
    QStackedWidget,
    QWidget,
    QSizePolicy,
    QCompleter,
)
from qfluentwidgets import (
    CardWidget,
    SegmentedWidget,
    qrouter,
    TextEdit,
)
from PySide6.QtCore import Qt
from httpgogui.components.table_widget import CommonTableWidget
from httpgogui.utils.header_list import header_lsit


class BodyWidget(CardWidget):
    """Body布局"""

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # 定义layout
        self.__qvbox_layout = QVBoxLayout(self)
        # 定义tabbar
        self.segmented_widget = SegmentedWidget(self)
        # 定义stackedWidget
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.stacked_widget.setContentsMargins(10, 10, 10, 10)
        # 定义tab item
        # params
        self.params_widget = CommonTableWidget(self)
        # body
        self.body_widget = TextEdit(self)
        # header
        self.header_widget = CommonTableWidget(self)
        # header key输入框添加自动补全
        self.header_completer = QCompleter(header_lsit, self)
        self.header_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.header_completer.setMaxVisibleItems(10)
        self.header_widget.key_lineedit.setCompleter(self.header_completer)
        # cookies
        self.cookies_widget = CommonTableWidget(self)
        # init body layout
        self.init_body_layout()

    def add_widget_interface(self, widget: QWidget, object_name: str, text: str):
        """添加item并设置stacked widget"""
        widget.setObjectName(object_name)
        self.stacked_widget.addWidget(widget)
        self.segmented_widget.addItem(
            routeKey=object_name,
            text=text,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget),
        )

    def on_current_index_changed(self, index: int):
        """更改stacked窗口"""
        widget = self.stacked_widget.widget(index)
        self.segmented_widget.setCurrentItem(widget.objectName())
        qrouter.push(self.stacked_widget, widget.objectName())

    def init_body_layout(self):
        """初始化body布局"""
        # 添加tab与stacked
        self.add_widget_interface(self.params_widget, "paramsInterface", "Params")
        self.add_widget_interface(self.body_widget, "bodyInterface", "Body")
        self.add_widget_interface(self.header_widget, "headerInterface", "Headers")
        self.add_widget_interface(self.cookies_widget, "cookiesInterface", "Cookies")
        # 布局添加组件
        self.__qvbox_layout.addWidget(self.segmented_widget)
        self.__qvbox_layout.addWidget(self.stacked_widget)
        # self.__qvbox_layout.addLayout(self.option_layout())
        # 配置
        self.stacked_widget.currentChanged.connect(
            self.on_current_index_changed
        )  # 连接切换stack信号
        self.stacked_widget.setCurrentWidget(self.params_widget)  # 定义默认stack
        self.segmented_widget.setCurrentItem("paramsInterface")  # 定义默认tab
