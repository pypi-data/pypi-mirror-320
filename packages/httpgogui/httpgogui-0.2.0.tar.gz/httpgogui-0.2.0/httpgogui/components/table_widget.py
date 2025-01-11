from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QHeaderView,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    TableWidget,
    LineEdit,
    ToolButton,
    FluentIcon,
    Theme,
)


class CommonTableWidget(TableWidget):
    """公共表格组件"""

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # 预留参数
        self.key_lineedit = None
        self.value_lineedit = None
        # 启用边框并设置圆角
        self.setBorderVisible(True)
        self.setBorderRadius(8)
        # 关闭换行
        self.setWordWrap(False)
        # 设置col
        self.setColumnCount(2)
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 设置水平表头并隐藏垂直表头
        self.setHorizontalHeaderLabels(["参数名", "参数值"])
        self.verticalHeader().hide()

        # 设置列宽平分剩余空间
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # 默认添加一行
        self.init_row(0)
        # 添加布局与按钮绑定
        self.table_layout = QVBoxLayout(self)
        self.table_layout.addWidget(self)
        self.table_layout.addStretch()  # 把option区域顶下去
        self.table_layout.addWidget(self.option_button_layout())

    def init_row(self, row: int):
        """初始化row内容"""
        self.setRowCount(row + 1)
        self.key_lineedit = LineEdit()
        self.key_lineedit.setPlaceholderText("请输入key")
        self.key_lineedit.setStyleSheet("LineEdit { border: none; }")
        self.value_lineedit = LineEdit()
        self.value_lineedit.setPlaceholderText("请输入value")
        self.value_lineedit.setStyleSheet("LineEdit { border: none; }")
        self.setCellWidget(row, 0, self.key_lineedit)
        self.setCellWidget(row, 1, self.value_lineedit)

    def add_row(self):
        """添加行"""
        row_count = self.rowCount()
        # 增加一行
        self.init_row(row_count)

    def remove_row(self):
        """删除行"""
        # 如果只剩下一行，禁止删除
        if self.rowCount() <= 1:
            return

        self.removeRow(self.rowCount() - 1)  # 删除最后一行

    def option_button_layout(self):
        """操作按钮区域"""
        option_widget = QWidget(self)
        # 设置最大高度
        # option_widget.setMaximumHeight(30)
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        # 重置layout内边距
        layout.setContentsMargins(0, 0, 0, 0)
        # 设置布局对齐方式为居中
        layout.setAlignment(Qt.AlignCenter)

        # 定义两个按钮
        # add_button = PushButton("+", self)
        add_button = ToolButton(FluentIcon.ADD.icon(Theme.LIGHT))
        # add_button.setStyleSheet("ToolButton { border: none; }")
        remove_button = ToolButton(FluentIcon.REMOVE)
        # 添加按钮至布局
        layout.addWidget(add_button)
        layout.addWidget(remove_button)
        option_widget.setLayout(layout)
        # 按钮添加信号
        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_row)
        return option_widget
