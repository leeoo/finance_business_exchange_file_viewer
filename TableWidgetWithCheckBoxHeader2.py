
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys


class custom_table(QTableWidget):

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        self.chkbox1 = QCheckBox(self.horizontalHeader())

    def resizeEvent(self, event=None):
        super().resizeEvent(event)
        self.chkbox1.setGeometry(QRect((self.columnWidth(0)/2), 2, 16, 17))

    # def test_signal_slot(self, state):
    #     print('收到信号了！！！')
    #     if state == Qt.PartiallyChecked:
    #         print('收到PartiallyChecked信号了！！！')
    #     elif state == Qt.Checked:
    #         print('收到Checked信号了！！！')
    #     elif state == Qt.Unchecked:
    #         print('收到Unchecked信号了！！！')
    #     else:
    #         print('NA')

    def test_signal_slot(self, state):
        sender = self.sender()
        print('收到%s发送的信号了！！！' % sender)
        if state == Qt.PartiallyChecked:
            print('收到PartiallyChecked信号了！！！')
        elif state == Qt.Checked:
            print('收到Checked信号了！！！')
        elif state == Qt.Unchecked:
            print('收到Unchecked信号了！！！')
        else:
            print('NA')

    def handle_header_checkbox_state_changed(self, state):
        sender = self.sender()
        print('sender -> %s' % sender)
        header_view = sender.parent()
        print('header_view -> %s' % header_view)

        # TODO
        if header_view is None:
            print('当前信号由table item的状态变化而引起，故不用处理')
            return

        table_widget = sender.parent().parent()
        print('table_widget -> %s' % table_widget)

        print('收到表头checkbox -> %s发送的信号了！！！' % sender)
        print('checkbox_on_header -> %s' % sender)
        check_state = sender.checkState()
        print('checkbox_on_header.checkState() -> %s' % check_state)

        # TODO 根据表头checkbox勾选状态对第1列的所有复选框做处理
        if check_state == Qt.PartiallyChecked:
            print('收到PartiallyChecked信号了！！！')
        elif check_state == Qt.Checked:
            print('收到Checked信号了！勾选该列所有的checkbox')
            self.update_first_column_checkbox_state(table_widget, Qt.Checked)
        elif check_state == Qt.Unchecked:
            print('收到Unchecked信号了！取消勾选该列所有的checkbox')
            self.update_first_column_checkbox_state(table_widget, Qt.Unchecked)
        else:
            print('NA')

    def update_first_column_checkbox_state(self, table_widget, check_state):
        """
        更新第1列checkbox的勾选状态
        :param table_widget:
        :param check_state:
        :return:
        """
        row_count = table_widget.rowCount()
        for _row_no in range(row_count):
            checkbox_item = table_widget.item(_row_no, 0)
            checkbox_item.setCheckState(check_state)

    # TODO 行首checkbox状态变化后，同步更新表头checkbox状态
    def handle_table_1st_column_item_clicked(self, state):
        """
        仅处理第1列item点击，其他列的item点击都丢弃！
        :param state: checkbox的勾选状态
        :return:
        """
        sender = self.sender()
        print('sender -> %s' % sender)
        checkbox_on_header = sender.chkbox1
        print('checkbox_on_header -> %s' % checkbox_on_header)
        print('checkbox_on_header.checkState() -> %s' % checkbox_on_header.checkState())
        if checkbox_on_header.checkState() == Qt.Checked:
            print('checkbox_on_header被勾选了！')
        elif checkbox_on_header.checkState() == Qt.Unchecked:
            print('checkbox_on_header取消勾选了！')
        else:
            print('NA！')

        current_item = sender.currentItem()

        item_column = current_item.column()
        if item_column != 0:
            print('当前item_column=%s，不作处理！' % item_column)
            return

        _state = current_item.checkState()
        print(_state)
        print('收到TableWidgetItem的checkbox -> %s发送的信号了！！！' % sender)
        _table = sender
        if _state == Qt.Checked:
            print('收到Checked信号了！')
            current_item.setCheckState(Qt.Checked)
            has_unchecked_checkbox = False
            for i in range(_table.rowCount()):
                if _table.item(i, 0).checkState() == Qt.Unchecked:
                    has_unchecked_checkbox = True
                    print('表格中还有未勾选的行，将header checkbox状态更新为部分勾选！')
                    _table.chkbox1.setCheckState(Qt.PartiallyChecked)
                    break

            print('has_unchecked_checkbox=%s' % has_unchecked_checkbox)
            print('表格中所有行均被勾选，将header checkbox状态更新为勾选！')
            _table.chkbox1.setCheckState(Qt.Checked)
        elif _state == Qt.Unchecked:
            print('收到Unchecked信号了！')
            current_item.setCheckState(Qt.Unchecked)
            has_checked_checkbox = False
            for i in range(_table.rowCount()):
                if _table.item(i, 0).checkState() == Qt.Checked:
                    has_checked_checkbox = True
                    print('表格中还有勾选的行，将header checkbox状态更新为部分勾选！')
                    _table.chkbox1.setCheckState(Qt.PartiallyChecked)
                    break

            print('has_checked_checkbox=%s' % has_checked_checkbox)
            print('表格中所有行均未被勾选，将header checkbox状态更新为未勾选！')
            _table.chkbox1.setCheckState(Qt.Unchecked)
        else:
            print('NA')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = QMainWindow()
    # window.setWindowTitle('测试自定义可添加CheckBox表头的TableWidget控件')
    # vbox = QVBoxLayout()
    # window.setLayout(vbox)
    # table = custom_table()
    table = custom_table()
    # vbox.addWidget(table)
    # window.setCentralWidget(table)
    # window.show()

    data = [x for x in range(3)]
    # header_labels = [str(x) for x in range(3)]
    header_labels = []
    header_labels.insert(0, '')
    print(data)
    print(header_labels)

    # table.setColumnCount(len(header_labels))
    # table.setColumnCount(2)
    # table.setRowCount(1)
    # table.setHorizontalHeaderLabels(header_labels)

    values = [(x, y) for x in range(3) for y in range(2)]
    rows = len(values)
    print('values -> %s' % values)

    values = []
    for row in range(5):
        l = []
        for column in range(2):
            l.append('%s%s' % (row, column))
        values.append(l)

    rows = len(values)
    print('values -> %s' % values)

    table.setRowCount(len(values))
    table.setColumnCount(len(values[0]) + 1)
    print('Column count: %s' % str(len(values[0]) + 1))

    header_labels = [str(i) for i in range(len(values[0]))]
    header_labels.insert(0, '')
    print('header_labels=%s' % header_labels)
    table.setHorizontalHeaderLabels(header_labels)

    for row_no in range(rows):
        print('Row %s' % row_no)
        columns = len(values[row_no])
        for column_no in range(columns):
            fix_column_no = column_no
            if column_no == 0:
                '''
                方式一：直接绘制checkbox列
                '''
                # table.setItem(row_no, column_no, QTableWidgetItem(QCheckBox()))
                # table.setCellWidget(row_no, column_no, QCheckBox())  # 直接绘制checkbox列
                # 设置信号-槽
                # table.cellWidget(row_no, column_no).stateChanged['int'].connect(table.test_signal_slot)  # This works well!

                '''
                方式二：利用QTableWidgetItem的checkState属性绘制checkbox列
                '''
                table_item = QTableWidgetItem('复选框')
                table_item.setCheckState(Qt.Unchecked)
                table.setItem(row_no, fix_column_no, table_item)

                # QTableWidgetItem().checkState.connect(self.test_signal_slot)

            fix_column_no += 1
            print('Column %s' % column_no)
            table_item = QTableWidgetItem()
            table_item.setText(str(values[row_no][column_no]))
            table.setItem(row_no, fix_column_no, table_item)

    table.show()

    print(table.cellWidget(0, 0))
    # print(type(table.cellWidget(0, 0).isChecked()))
    # table.cellWidget(0, 0).stateChanged['int'].connect(table.test_signal_slot)  # This works well!
    # table.horizontalHeader().stateChanged['int'].connect(table.test_signal_slot)
    # 针对自定义的表头checkbox的状态改变信号连接到指定的槽
    table.chkbox1.stateChanged['int'].connect(table.handle_header_checkbox_state_changed)
    table.itemClicked.connect(table.handle_table_1st_column_item_clicked)
    # # 连接第1列checkbox的信号槽
    # row_count = table.rowCount()
    # for i in range(row_count):
    #     item = table.item(i, 0)
    #     item.item
    #     QTableWidgetItem()

    # QHeaderView().

    # print(table.cellWidget(0, 0).isChecked())
    # checkbox = QCheckBox()
    # checkbox.stateChanged['int'].connect(table.test)

    sys.exit(app.exec())


