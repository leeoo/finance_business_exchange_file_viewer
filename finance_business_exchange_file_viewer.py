# -*- coding: utf-8 -*-

"""
# 启动时即加载所有配置信息
# 解析《开放式基金业务数据交换协议》相关的文件时，只以规定的GB18030编码解析，其它类型的数据文件若用GB18030编码解析失败，会再尝试以UTF-8解析
# 异常提示以对话框弹出告知
TODO
# 可编辑并保存为新文件
# ~~ 可导出为Excel文件 ~~
@author         Lex Li
@version        1.0
@description
"""


import sys
import os.path
import logging.config
from configparser import ConfigParser
from PyQt5.QtCore import *
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
# from finance_business_exchange_file_viewer_ui import Ui_MainWindow


__VERSION__ = '0.5.2'
INFO_HEADER_PRE_SECTION_LIST = ['文件标识', '文件版本', '文件创建人', '文件接收人', '日期',
                                '汇总表号', '文件类型码', '发送人', '接收人', '字段数']
# 常量声明
GB18030_ENCODING = 'GB18030'
UTF_8_ENCODING = 'UTF-8'
OFD_FIELD_ID_INDEX, OFD_FIELD_NAME_INDEX, OFD_FIELD_TYPE_INDEX, OFD_FIELD_LENGTH_INDEX, \
    OFD_FIELD_DESCRIPTION_INDEX, OFD_FIELD_COMMENTS_INDEX, OFD_FIELD_REQUIRED_INDEX = 0, 1, 2, 3, 4, 5, 6
__NO_OF_REAL_ROW_NO_COLUMN__ = 0  # 真实行号所在的列


# Special function to import external files when using PyInstaller.
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')

    print('base_path -> %s, relative_path -> %s' % (base_path, relative_path))
    full_path = os.path.join(base_path, relative_path)
    print('full_path -> %s' % full_path)
    return full_path

################################
# 参考 https://my.oschina.net/u/150309/blog/123262
# 此处载入日志配置文件会导致PyInstaller打包后程序启动一闪而过，且任何错误提示！
# if getattr(sys, 'frozen', None):
#     basedir = sys._MEIPASS
# else:
#     basedir = os.path.dirname(__file__)
#
# logging.config.fileConfig(os.path.join(basedir, 'config/logging.ini'))
# logging.config.fileConfig(resource_path('config/logging.ini'))
# log = logging.getLogger()


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(module)s:%(lineno)s %(funcName)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=resource_path("app.log"),
                    filemode='w')
log = logging.getLogger()
################################


class AppWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AppWindow, self).__init__(parent)

        # Key为文件标识类型，Value为字段信息列表，其中字段信息为按固定顺序组成的列表。
        # e.g. {'01':[[4,'Address','C',120,'通讯地址'],[...],...], '02':[[4,'Address','C',120,'通讯地址'],[...],...], ...}
        self.ofd_config_map = {}

        self.exchange_info_header = {}
        self.exchange_info_fields = []
        self.exchange_info_content = []

        # 用于保存中登标准交换文件解析后的数据，以便用于搜索及导出
        self.exchange_info_content_2dimension_tuple = ()  # 二维元组，保存解析后的数据
        self.exchange_info_content_modified = ()  # 修改后的数据，用于导出

        self.mft0_fields = []
        # 用于保存货基T+0文件解析后的数据，以便用于搜索及导出
        self.mft0_content_2dimension_tuple = ()  # 二维元组，保存解析后的数据
        self.mft0_content_modified = ()  # 修改后的数据，用于导出

        self.about_message_box = None
        self.row_content_dialog = None
        self.help_message_box = None

        try:
            self.load_config()
            log.info('配置文件加载完毕')

            # 使用PyQt5的uic来加载并解析UI文件
            uic.loadUi(resource_path('finance_business_exchange_file_viewer.ui'), self)

            self.adjust_layout()

            # 支持拖拽操作
            self.setAcceptDrops(True)  # tab_open_fund_data
            # self.dragEnterEvent(True)
            # self.tab_open_fund_data.dropped.connect(self.handle_drop_action)

            self.handle_ui_action()

            # 禁用尚未开发完成的功能
            self.disable_in_developing_functions()
        except Exception as e:
            # error_msg = '程序内部错误，请检查运行日志！'
            error_msg = '程序内部错误，请检查运行日志！errorMsg=%s' % e
            log.error(error_msg + '异常信息：%s' % e)
            self.popup_error_msg_box(error_msg)

    def load_config(self):
        log.info('加载OFD数据文件结构定义')
        # self.load_data_file_construction_definition('data_exchange_file_definition_rule.ini')
        self.load_ofd_file_definition('config/OFD_0901_20161014.ini')
        # log.info('加载OFI索引文件结构定义')
        # self.load_index_file_construction_definition('exchange_index_file_definition_rule.ini')

    # 调整UI布局中控件间距
    def adjust_layout(self):
        # self.gridLayout.setSpacing(5)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout_2.setSpacing(5)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setHorizontalSpacing(5)

    def handle_ui_action(self):
        # 打开开放式基金业务数据交换文件
        self.button_browse_file.clicked.connect(self.browse_open_fund_business_data_exchange_file)
        # 点击表头按当前列排序（直接使用TableWidget内置方法）
        self.tableWidget.horizontalHeader().sectionClicked['int'].connect(self.tableWidget.sortByColumn)
        # 点击左侧行头将该行数据展示在弹出框中，以key-value形式显示
        # self.tableWidget.verticalHeader().sectionClicked['int'].connect(self.show_table_row_content)
        # 搜索
        self.button_search.clicked.connect(self.search_open_fund_data)
        # 恢复（针对于搜索或排序后，恢复到未执行操作的初始解析状态）
        self.button_restore.clicked.connect(self.restore_open_fund_content_data)
        # TODO 导出
        self.button_export.clicked.connect(self.export_open_fund_data)

        # TODO 存放编辑的数据 (注：此行将导致 PyInstaller v3.3 打包后的app在打开中登标准交换文件时闪退！！！)
        # self.tableWidget.model().dataChanged.connect(self.update_content_to_export)

        # 打开货币基金T+0对账文件
        self.button_browse_monetary_fund_t0_file.clicked.connect(self.browse_monetary_fund_t0_file)
        self.tableWidget_monetary_fund_t0.horizontalHeader().sectionClicked['int'].connect(
            self.tableWidget_monetary_fund_t0.sortByColumn)

        # 针对货币基金T+0的搜索
        self.button_search_monetary.clicked.connect(self.search_monery_t0_data)
        # 恢复（针对于搜索或排序后，恢复到未执行操作的初始解析状态）
        self.button_restore_monetary.clicked.connect(self.restore_monetary_fund_t0_content_data)

        # TODO 打开赢时胜金手指文件
        # self.button_browse_gold_finger_file.clicked.connect(self.browse_gold_finger_file)

        self.actionAbout.triggered.connect(self.show_about_info)
        self.actionContent.triggered.connect(self.show_help_info)

    def update_content_to_export(self, top_left, bottom_right):
        table_item_changed = self.tableWidget.item(top_left.row(), top_left.column())
        real_row_no_item = self.tableWidget.item(top_left.row(), __NO_OF_REAL_ROW_NO_COLUMN__)
        log.info("更新表格, real_row=%s, row=%s, column=%s" % (real_row_no_item.text(), top_left.row(), top_left.column()))
        log.info("table_item_changed -> %s" % table_item_changed.text())
        real_row_no = int(real_row_no_item.text())
        # 更新数据列表
        self.exchange_info_content_modified[real_row_no][top_left.column()] = table_item_changed.text()

    def export_open_fund_data(self):
        # TODO 根据更新后的数据列表，导出文件，文件名扩展名前添加 'yyyyMMddHHmmss_exported' 字样
        pass

    def load_ofd_file_definition(self, file_path):
        log.info('OFD配置文件路径: %s' % file_path)
        try:
            # 配置文件是UTF-8编码的，为了防止PyInstaller打包后程序启动时报编码错误，须使用UTF-8编码读取配置文件！
            ofd_config_file = open(resource_path(file_path), encoding=UTF_8_ENCODING)
            ini_parser = ConfigParser()
            ini_parser.read_file(ofd_config_file)
            config_content_sections = ini_parser.sections()

            for section in config_content_sections:
                options = ini_parser.options(section)
                field_list = []
                for option in options:
                    option_value = ini_parser.get(section, option)
                    # log.debug('option -> %s, value -> %s' % (option, option_value))
                    field_info_as_list = option_value.split(',')
                    field_info_as_list.insert(0, option)
                    # field_list.append({option: option_value})
                    field_list.append(field_info_as_list)

                self.ofd_config_map.update({section: field_list})
        except FileNotFoundError as fnfe:
            error_msg = '找不到OFD配置文件' % file_path
            log.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = '加载配置文件出错！异常信息：%s' % e
            log.error(error_msg)
            raise Exception(error_msg)
        finally:
            if ofd_config_file is not None:
                ofd_config_file.close()

    def popup_error_msg_box(self, error_msg):
        error_msg_box = QMessageBox(self)
        error_msg_box.critical(self, '错误提示', error_msg)

    def restore_open_fund_content_data(self):
        self.restore_content_data(self.exchange_info_content_2dimension_tuple,
                                  self.exchange_info_fields, self.tableWidget, self.statusbar)

    def restore_monetary_fund_t0_content_data(self):
        self.restore_content_data(self.mft0_content_2dimension_tuple,
                                  self.mft0_fields, self.tableWidget_monetary_fund_t0, self.statusbar)

    def restore_content_data(self, content, fields, table_widget, status_bar):
        if len(content) == 0:
            return

        self.setup_table_widget(table_widget, content, fields, False)
        for row_no, row in enumerate(content):
            for column_no, item in enumerate(row):
                table_item = QTableWidgetItem(item)
                table_widget.setItem(row_no, column_no, table_item)
                if column_no == __NO_OF_REAL_ROW_NO_COLUMN__:
                    table_item.setFlags(Qt.NoItemFlags)

        # 清空状态条信息
        status_bar.clearMessage()

    def setup_table_widget(self, table_widget, rows_content, header_labels, first_setup):
        """
        用于设置表格控件的初始状态 // 可重用
        :param table_widget:
        :param rows_content:
        :param header_labels:
        :param first_setup:
        :return:
        """
        table_widget.clearContents()
        table_widget.setAlternatingRowColors(True)  # 设置隔行变色
        table_widget.setRowCount(len(rows_content))
        table_widget.setColumnCount(len(header_labels))
        # 若为首次设置表格，则设置表头标示
        if first_setup:
            table_widget.setHorizontalHeaderLabels(header_labels)

    # 从当前解析的数据中查询，而不是只对当前表格中显示的内容做查询
    # 找到与否均弹出提示对话框，或者在界面搜索按钮右侧、左下角或右下角显示！
    def search_open_fund_data(self):
        # _search_key = self.lineEdit_search.text()
        # log.info('Search key=%s' % _search_key)

        self.search_and_repaint_table(self.exchange_info_content_modified, self.tableWidget,
                                      self.lineEdit_search, self.statusbar)

    def search_monery_t0_data(self):
        self.search_and_repaint_table(self.mft0_content_modified, self.tableWidget_monetary_fund_t0,
                                      self.lineEdit_search_monetary, self.statusbar)

    def search_and_repaint_table(self, content, table_widget, search_line_edit, status_bar):
        """
        用于查找并重绘表格及状态条控件 // 可重用
        :param content:
        :param table_widget:
        :param search_line_edit:
        :param status_bar:
        :return:
        """
        _search_key = search_line_edit.text()
        log.info('Search key=%s' % _search_key)

        # 查询时初始化清空表格内容和状态条
        table_widget.clearContents()
        table_widget.setRowCount(0)
        status_bar.clearMessage()

        row_no_for_search_result = 0
        row_count_for_search_result = 0
        for row_no, row in enumerate(content):
            found = False
            # 第一个循环是找出该行是否有匹配到查询关键字
            for column_no, item in enumerate(row):
                # 由于首列（隐藏或禁止编辑）是存放的真实行号，故搜索时应排除该列！
                if column_no == __NO_OF_REAL_ROW_NO_COLUMN__:
                    continue
                if _search_key in item:
                    found = True
                    break
            if not found:
                log.debug('Not found!')
                continue
            else:
                log.debug('Found it! Render current row!')
                row_count_for_search_result += 1

            # 为保证搜索后表格行号显示准确，循环每行时均设置表格行数，此处做法有待改进！
            table_widget.setRowCount(row_count_for_search_result)

            # 第二个循环是用于当第一个循环匹配到查询关键字后，渲染该行
            for column_no, item in enumerate(row):
                table_item = QTableWidgetItem(item)
                table_widget.setItem(row_no_for_search_result, column_no, table_item)
                if column_no == __NO_OF_REAL_ROW_NO_COLUMN__:
                    table_item.setFlags(Qt.NoItemFlags)

            row_no_for_search_result += 1

        # 更新状态条，以显示总结果数，查询到的结果数，是否查到等！
        status_bar.showMessage('搜索到%s条数据！' % row_no_for_search_result)

    def show_about_info(self):
        self.about_message_box = QMessageBox()
        self.about_message_box.setModal(True)
        self.about_message_box.setText('版本: %s\r\n\r\n当前支持（拖拽打开）的文件类型列表:\r\n%s\r\n%s'
                                       '\r\n\r\nBuilt with PyCharm and PyInstaller.'
                                       '\r\nWritten with Python 3, PyQt 5 and Qt Designer.\r\n'
                                       '\r\nBy Lex Li (libeely@gmail.com).' %
                                       (__VERSION__, list(self.ofd_config_map.keys()), '货币基金T+0对账文件'))
        self.about_message_box.show()

    def show_help_info(self):
        self.help_message_box = QMessageBox()
        self.help_message_box.setModal(True)
        self.help_message_box.setText('配置文件参见config目录')
        self.help_message_box.show()

    def show_table_row_content(self):
        self.row_content_dialog = QMessageBox()
        self.row_content_dialog.setModal(True)
        self.row_content_dialog.setText('建设中...')
        self.row_content_dialog.show()
        # if dialog.accepted():
        #     log.info('点击确认')

    def browse_monetary_fund_t0_file(self):
        _file_info = QFileDialog.getOpenFileName(self.tab_monetary_fund_data, '打开文件', os.path.expanduser('~'),
                                                 '信息交换数据文件(partner_fund*.txt; fund_partner*.txt; fund_*_*.TXT)')
        _filename = _file_info[0]
        log.info('filename -> %s' % _filename)
        self.lineedit_monetary_fund_t0_file_path.setText(_filename)
        if '' == _filename.strip():
            log.info('未选择文件，直接返回！')
            return

        # self.render_monetary_fund_t0_info(_filename)

        _file_input_stream = None
        _content = None

        try:
            _file_input_stream = open(_filename, 'rt', encoding=GB18030_ENCODING)
            _content = _file_input_stream.read().strip()
            log.info('以%s编码打开成功' % GB18030_ENCODING)
        except UnicodeDecodeError as e:
            log.error('以%s打开失败，尝试以UTF-8编码打开' % GB18030_ENCODING)
            try:
                _file_input_stream = open(_filename, 'rt', encoding=UTF_8_ENCODING)
                _content = _file_input_stream.read().strip()
                log.info('以%s编码打开成功' % UTF_8_ENCODING)
            except Exception as e:
                log.error('以%s编码打开失败' % UTF_8_ENCODING)
                self.popup_error_msg_box('尝试以%s和%s编码打开文件均失败，请检查文件内容编码！' % (GB18030_ENCODING, UTF_8_ENCODING))
                return
            finally:
                if _file_input_stream is not None:
                    _file_input_stream.close()
        finally:
            if _file_input_stream is not None:
                _file_input_stream.close()

        try:
            _lines = _content.splitlines()
            _first_line = _lines[0]
            _header_columns = _lines[1].split('|')
            _content_lines = _lines[2:]

            log.info('_first_line: %s' % _first_line)
            log.info('_header_columns: %s' % _header_columns)
            log.info('_content_lines: %s' % _content_lines)

            self.mft0_fields = _header_columns.copy()
            self.mft0_fields = self.insert_real_no_field_to_head(self.mft0_fields)

            self.setup_table_widget(self.tableWidget_monetary_fund_t0, _content_lines, self.mft0_fields, True)

            mft0_content_2dimension_list = []
            mft0_content_2dimension_list_mutable = []

            for row_no, row in enumerate(_content_lines):
                param_values = row.split('|')
                # 添加行号到头部，用于标识当前行位于文件中的真实行号，但展示列表时可将该列隐藏
                param_values.insert(0, str(row_no + 1))
                self.render_table_row(self.tableWidget_monetary_fund_t0, param_values, row_no)

                # 将数据保存到二维元组，供后续搜索功能使用
                mft0_content_2dimension_list.append(tuple(param_values))
                mft0_content_2dimension_list_mutable.append(param_values)

            self.mft0_content_2dimension_tuple = tuple(mft0_content_2dimension_list)
            self.mft0_content_modified = mft0_content_2dimension_list_mutable.copy()

            # 为了确保表格显示美观不拥挤，在表格表头和内容均填充完后重新设置列宽度为内容宽度
            self.tableWidget_monetary_fund_t0.resizeColumnsToContents()
        except Exception as e:
            error_msg = '解析文件内容出错！%s' % e
            log.error(error_msg)
            self.popup_error_msg_box(error_msg)
            return
        finally:
            if _file_input_stream is not None:
                _file_input_stream.close()

    def render_monetary_fund_t0_info(self, _filename):
        _basename = os.path.basename(_filename)
        self.lineEdit_t0_filename.setText(_basename)
        self.lineEdit_t0_file_date.setText(_basename.split('_')[-1].split('.')[0])
        self.lineEdit_t0_file_sender.setText(_basename.split('_')[4])
        self.lineEdit_t0_file_receiver.setText(_basename.split('_')[5])

    def browse_open_fund_business_data_exchange_file(self):
        _file_info = QFileDialog.getOpenFileName(self.tab_open_fund_data, '打开文件', os.path.expanduser('~'),
                                                 '信息交换数据文件(OFD*.TXT; OFI*.TXT)')
        _filename = _file_info[0]
        log.info('filename -> %s' % _filename)
        if '' == _filename.strip():
            log.info('未选择文件，直接返回！')
            return
        self.show_open_fund_biz_data(_filename)

        # 清空状态条信息
        self.statusbar.clearMessage()

    def show_open_fund_biz_data(self, _filename):
        self.lineEdit_interface_file_path.setText(_filename)
        # ----------- 读取 -----------
        try:
            file_input_stream = open(_filename, 'rt', encoding=GB18030_ENCODING)
            content = file_input_stream.read().strip()

            # 前10行均为固定的消息头部信息
            lines = content.splitlines()
            # log.debug('lines -> %s' % lines)
            _file_flag = lines[0]
            # log.debug('_file_flag -> %s' % _file_flag)
            _file_version = lines[1]
            # log.debug('_file_version -> %s' % _file_version)
            _file_creator = lines[2]
            # log.debug('_file_creator -> %s' % _file_creator)
            _file_receiver = lines[3]
            # log.debug('_file_receiver -> %s' % _file_receiver)
            _file_date = lines[4]
            # log.debug('_file_date -> %s' % _file_date)

            _file_end_flag = lines[len(lines) - 1]
            # log.debug('_file_end_flag -> %s' % _file_end_flag)

            FILE_CONTENT_BEGIN_FLAG = 'OFDCFDAT'
            info_header_pre_section_dict = {}  # 前10行
            info_header_middle_section_field_list = []
            # info_header_last_section_record_count = 0
            info_content_record_list = []
            FILE_CONTENT_END_FLAG = 'OFDCFEND'


            LINE_COUNT_OF_MESSAGE_HEADER_PRE_SECTION = len(INFO_HEADER_PRE_SECTION_LIST)

            # ----------- 校验 -----------
            # 检查消息头第1行文件标识
            if _file_flag != FILE_CONTENT_BEGIN_FLAG:
                raise Exception('文件内容消息头文件标识校验失败，非法的数据文件！')
            # 检查消息最后1行文件结束标识
            if _file_end_flag != FILE_CONTENT_END_FLAG:
                raise Exception('文件内容文件结束标识校验失败，非法的数据文件！')

            # ----------- 解析 -----------
            _line_no = 0
            _record_count_not_found_yet = True
            for line in lines:
                _index = _line_no
                _line_no += 1

                # 解析消息头部前面固定不变的部分
                if _line_no <= LINE_COUNT_OF_MESSAGE_HEADER_PRE_SECTION:
                    info_header_pre_section_dict[INFO_HEADER_PRE_SECTION_LIST[_index]] = line.strip()
                    # log.debug('第%d行: %s' % (_line_no, line))
                    continue

                # 解析消息头部中间可变的字段定义部分
                if _record_count_not_found_yet:
                    line_striped = line.strip()
                    if line_striped.isdigit():
                        # info_header_last_section_record_count = int(line_striped)
                        # log.debug('记录数: %d' % info_header_last_section_record_count)
                        # 当读取到记录数这一行后，设置未找到标记为假，后续就不用再执行这一大段if块了
                        _record_count_not_found_yet = False
                    else:
                        info_header_middle_section_field_list.append(line_striped)

                    continue

                if line != FILE_CONTENT_END_FLAG:
                    # 记录内容不能trim首尾空格，否则数据解析不正确！
                    info_content_record_list.append(line)
                else:
                    # log.debug('到达文件结束标识')
                    break

                    # log.info('文件内容消息头文件标识 -> %s' % FILE_CONTENT_BEGIN_FLAG)
                    # log.info('前10行固定的消息头部 -> %s' % info_header_pre_section_dict)
                    # log.info('中间数量可变的字段 -> %s' % info_header_middle_section_field_list)
                    # log.info('记录数 -> %d' % info_header_last_section_record_count)
                    # log.debug('记录 -> %s' % info_content_record_list)
                    # log.info('文件内容文件结束标识 -> %s' % FILE_CONTENT_END_FLAG)
        except Exception as e:
            error_msg = '解析文件内容出错！\r\n异常信息：%s' % e
            log.error(error_msg)
            self.popup_error_msg_box(error_msg)
            return
        finally:
            if file_input_stream is not None:
                file_input_stream.close()

        self.exchange_info_header = info_header_pre_section_dict
        self.exchange_info_fields = info_header_middle_section_field_list
        self.exchange_info_content = info_content_record_list

        # 补上手工添加的首列——真实行号
        self.exchange_info_fields = self.insert_real_no_field_to_head(self.exchange_info_fields)

        _file_flag_type_key = self.exchange_info_header[INFO_HEADER_PRE_SECTION_LIST[6]]
        if _file_flag_type_key in self.ofd_config_map.keys():
            log.info('找到当前key=%s的配置信息' % _file_flag_type_key)
        else:
            log.warning('未找到当前文件类型[%s]的配置信息，无法解析！' % _file_flag_type_key)
            return

        exchange_info_content_2dimension_list = []
        exchange_info_content_2dimension_list_mutable = []
        # 将数据解析成二维元组，供后续搜索功能使用
        field_length_list, field_length_precision_list = self.get_field_len_list(_file_flag_type_key)
        for row_no, record in enumerate(self.exchange_info_content):
            field_values = self.parse_record(field_length_list, field_length_precision_list, record)
            # 添加行号到头部，用于标识当前行位于文件中的真实行号，但展示列表时可将该列隐藏
            field_values.insert(0, str(row_no + 1))
            exchange_info_content_2dimension_list.append(tuple(field_values))
            exchange_info_content_2dimension_list_mutable.append(field_values)

        self.exchange_info_content_2dimension_tuple = tuple(exchange_info_content_2dimension_list)
        # log.info('数据二维元组exchange_info_content_2dimension_tuple：%s' % self.exchange_info_content_2dimension_tuple)
        # 复制一份数据列表，供后续更改导出用
        self.exchange_info_content_modified = exchange_info_content_2dimension_list_mutable.copy()

        # ----------- 展示 -----------
        # 展示头部信息
        self.render_header_info(_file_flag_type_key, _filename, INFO_HEADER_PRE_SECTION_LIST)
        # 展示表格数据部分
        self.render_table(_file_flag_type_key)

    def insert_real_no_field_to_head(self, fields):
        """
        用于把真实行号列添加到表头作为首列 // 可重用
        :param fields:
        :return:
        """
        fields.insert(0, '#真实行号')
        return fields

    # 获得当前文件定义的各字段长度列表
    def get_field_len_list(self, _config_key):
        field_len_list = []
        field_len_precision_list = []
        for field_info_as_list in self.ofd_config_map[_config_key]:
            field_length = field_info_as_list[3]
            length_and_precision = field_length.split('.')
            field_len_list.append(int(length_and_precision[0]))
            if len(length_and_precision) > 1:
                field_len_precision_list.append(int(length_and_precision[1]))
            else:
                field_len_precision_list.append(0)

        return field_len_list, field_len_precision_list

    def render_table(self, _config_key):
        # 获得当前文件定义的表头
        header_labels = []
        for field_info_as_list in self.ofd_config_map[_config_key]:
            field_description = field_info_as_list[OFD_FIELD_DESCRIPTION_INDEX]
            header_labels.append(field_description)

        # 补上手工添加的首列——真实行号
        header_labels = self.insert_real_no_field_to_head(header_labels)

        self.setup_table_widget(self.tableWidget, self.exchange_info_content, header_labels, True)
        # self.tableWidget.hideColumn(0)  # 隐藏首列

        # field_len_list, field_len_precision_list = self.get_field_len_list(_config_key)
        log.info('配置文件key -> %s' % _config_key)
        for row_no, row in enumerate(self.exchange_info_content_2dimension_tuple):
            for column_no, item in enumerate(row):
                table_item = QTableWidgetItem(item)
                self.tableWidget.setItem(row_no, column_no, table_item)
                if column_no == __NO_OF_REAL_ROW_NO_COLUMN__:
                    table_item.setFlags(Qt.NoItemFlags)
        # 为了确保表格显示美观不拥挤，在表格表头和内容均填充完后重新设置列宽度为内容宽度
        self.tableWidget.resizeColumnsToContents()

    def render_table_row(self, table_widget, record_values, row_no):
        """
        将数据绘制到指定表格控件的给定行
        :param table_widget:
        :param record_values:
        :param row_no:
        :return:
        """
        for column_no, cell in enumerate(record_values):
            if cell is None:
                cell = ''
            table_item = QTableWidgetItem(str(cell))
            table_item.setTextAlignment(Qt.AlignCenter)
            table_widget.setItem(row_no, column_no, table_item)

    def render_header_info(self, _file_type, _filename, info_header_pre_section_list):
        self.lineEdit_filename.setText(os.path.basename(_filename))
        self.dateEdit.setDate(QDate.fromString(self.exchange_info_header[info_header_pre_section_list[4]], 'yyyyMMdd'))
        self.lineEdit_sender.setText(self.exchange_info_header[info_header_pre_section_list[7]])
        self.lineEdit_receiver.setText(self.exchange_info_header[info_header_pre_section_list[8]])
        self.lineEdit_ta_no.setText(self.exchange_info_header[info_header_pre_section_list[3]])
        # self.lineEdit_branch_code.setText(self.exchange_info_header[info_header_pre_section_list[2]])
        # self.lineEdit_seller_name.setText(self.exchange_info_header[info_header_pre_section_list[2]])
        # self.lineEdit_interface_version.setText(self.exchange_info_header[info_header_pre_section_list[1]])
        self.comboBox_interface_version.addItems([self.tr(self.exchange_info_header[info_header_pre_section_list[1]])])
        self.lineEdit_file_type.setText(_file_type)

    def parse_record(self, field_len_list, field_len_precision_list, record):
        """
        根据配置信息按固定长度解析内容，包含小数精度的数值将被解析成实际有意义的数字
        :param field_len_list: 字段长度
        :param field_len_precision_list: 字段数值精度（仅当字段为数值类型时才有效）
        :param record: 
        :return: 单行内容解析后得到的字段值列表
        """
        _start = 0
        _end = 0
        record_values = []
        # 由于信息体中的汉字是GB18030编码，故需要转换成字节后再按索引范围取值
        record_bytes = str.encode(record, GB18030_ENCODING)
        for index, field_len in enumerate(field_len_list):
            _end = _start + field_len
            _record_value = bytes.decode(record_bytes[_start: _end], GB18030_ENCODING).strip()
            _start = _end
            # log.debug('参数%d的值为: %s' % (index, _record_value))
            _record_value = self.fix_value_if_numeric_type(_record_value, field_len_precision_list, index)
            record_values.append(_record_value)
        # log.debug('解析后的参数值 -> %s' % record_values)
        return record_values

    # 将包含给定精度的数值进行转换
    def fix_value_if_numeric_type(self, _record_value, field_len_precision_list, index):
        fixed_record_value = _record_value
        if field_len_precision_list[index] > 0:  # TODO 还应该加上字段类型为数值的判断条件！
            field_len = len(_record_value)
            precision_len = field_len_precision_list[index]
            log.debug('字段长度=%s，字段精度=%s' % (field_len, precision_len))
            _left_part = _record_value[:field_len - precision_len]
            _right_part = _record_value[field_len - precision_len:]
            fixed_record_value = '.'.join([_left_part, _right_part])
            tmp = float(fixed_record_value)
            if tmp == 0:
                fixed_record_value = '0'
            elif tmp % 1 == 0:  # 不含有小数，不用显示小数部分
                fixed_record_value = str(int(tmp))
            else:  # 含有小数，必须显示小数部分
                fixed_record_value = str(tmp)
        return fixed_record_value

    def disable_in_developing_functions(self):
        self.button_export.setDisabled(True)
        self.checkBox_remove_blank.setDisabled(True)
        # self.lineEdit_search_monetary.setDisabled(True)
        # self.button_search_monetary.setDisabled(True)
        self.checkBox_remove_blank_monetary.setDisabled(True)
        # self.button_restore_monetary.setDisabled(True)
        self.button_export_monetary.setDisabled(True)
        self.tab_ysstech_data.setDisabled(True)

    def handle_drop_action(self):
        log.info('Drop action emit!!!!!!!')

    def dragEnterEvent(self, dragEnterEvent):
        if dragEnterEvent.mimeData().hasUrls():
            dragEnterEvent.accept()
        else:
            dragEnterEvent.ignore()

    def dropEvent(self, dropEvent):
        for url in dropEvent.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path) and path.endswith(('.txt', '.TXT')):
                log.info(path)
                self.show_open_fund_biz_data(path)


def main():
    app = QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
