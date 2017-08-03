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
## 打包过程中输出包含DEBUG级别的详细日志
pyinstaller --log-level DEBUG -D --windowed --noconfirm --add-data="finance_business_exchange_file_viewer.ui:." --add-data="config/:config/" -p /Users/libo/workshop/Python/finance_business_exchange_file_viewer/config --windowed --noconfirm finance_business_exchange_file_viewer.py

## 常用打包命令
pyinstaller -D --windowed --noconfirm --clean --add-data="finance_business_exchange_file_viewer.ui:." --add-data="config/:config/" -p /Users/libo/workshop/Python/finance_business_exchange_file_viewer/config finance_business_exchange_file_viewer.py

## 有问题先检查*.spec文件


