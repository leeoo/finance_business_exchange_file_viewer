

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys


class HeaderWithCheckBox(QHeaderView):
    on = False

    def __init__(self, orientation, parent=None):
        QHeaderView.__init__(self, orientation, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        QHeaderView.paintSection(self, painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(10, 10, 10, 10)
            if self.on:
                option.state = QStyle.State_On
            else:
                option.state = QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePerssEvent(self, event):
        self.on = not self.on
        self.updateSection(0)
        QHeaderView.mousePressEvent(self, event)


class TableWidgetWithCheckBoxHeader(QTableWidget):
    def __init__(self):
        QTableWidget.__init__(self, 3, 3)

        customer_header = HeaderWithCheckBox(Qt.Horizontal, self)
        self.setHorizontalHeader(customer_header)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = QMainWindow()
    # window.setWindowTitle('测试自定义可添加CheckBox表头的TableWidget控件')
    # vbox = QVBoxLayout()
    # window.setLayout(vbox)
    table = TableWidgetWithCheckBoxHeader()
    # vbox.addWidget(table)
    # window.setCentralWidget(table)
    # window.show()
    table.show()
    sys.exit(app.exec())

