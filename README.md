# finance_business_exchange_file_viewer
App to view some kinds of finance business exchange files.


目标
==============

+ 支持《开放式基金业务数据交换协议》最新正式版中的文件定义
+ 支持中证S2、S6、S7、S8、S9文件查看
+ 支持货币基金T+0相关的文件查看
+ 赢时胜金手指文件查看


解析规则
==============
- 参见 OFD_0901_20161014.ini


打包App
==============

## 常用打包命令
### For Linux/MacOS
* 文件夹格式
```Shell
pyinstaller -D --windowed --noconfirm --clean --add-data="finance_business_exchange_file_viewer.ui:." --hidden-import PySide2.QtXml --add-data="config/:config/" -p /Users/lex/workshop/Python/finance_business_exchange_file_viewer/config finance_business_exchange_file_viewer.py
```
* 单文件格式
```Shell
pyinstaller -F --windowed --noconfirm --clean --add-data="finance_business_exchange_file_viewer.ui:." --hidden-import PySide2.QtXml --add-data="config/:config/" -p /Users/lex/workshop/Python/finance_business_exchange_file_viewer/config finance_business_exchange_file_viewer.py
```
### For Windows
* 文件夹格式
```Shell
pyinstaller -D --windowed --noconfirm --clean --add-data="finance_business_exchange_file_viewer.ui;." --hidden-import PySide2.QtXml --add-data="config/;config/" -p G:\workshop\Python\finance_business_exchange_file_viewer\config finance_business_exchange_file_viewer.py
```
* 单文件格式
```Shell
pyinstaller -F --windowed --noconfirm --clean --add-data="finance_business_exchange_file_viewer.ui;." --hidden-import PySide2.QtXml --add-data="config/;config/" -p G:\workshop\Python\finance_business_exchange_file_viewer\config finance_business_exchange_file_viewer.py
```

注：在MacOS平台打包时，为了支持HDPI高清显示，需要手动在spec文件末尾添加如下配置！
```Python
app = BUNDLE(coll,
             name='finance_business_exchange_file_viewer.app',
             icon=None,
             bundle_identifier=None,
             info_plist={
                 'NSPrincipalClass': 'NSApplication',
                 'NSHighResolutionCapable': 'True',
                 'LSBackgroundOnly': '0'
             }
      )
```

## 打包过程中输出包含DEBUG级别的详细日志
```Shell
pyinstaller --log-level DEBUG -D --windowed --noconfirm --add-data="finance_business_exchange_file_viewer.ui:." --add-data="config/:config/" -p /Users/lex/workshop/Python/finance_business_exchange_file_viewer/config --windowed --noconfirm finance_business_exchange_file_viewer.py
```

## 有问题依次检查
1. <your_app_name>.spec文件。
2. 打包完毕后build/<your_app_name>/warn<your_app_name>.txt文件中的构建日志。
3. 操作系统平台。
4. 文件执行路径是否包含中文！


已知问题
==============
- app由PyInstaller打包后在Mac上含有中文字符的路径下无法运行
- 当前PyInstaller的PySide2系列hook不能正常支持含有QUiLoader模块的打包，需要在打包命令中加上` --hidden-import PySide2.QtXml`。
    - 参考：
        1. PyInstaller cannot find QtCompat.loadUi
        https://github.com/mottosso/Qt.py/issues/290
        2.  PyInstaller cannot find QtUiTools because of QtXml
        https://bugreports.qt.io/browse/PYSIDE-681

