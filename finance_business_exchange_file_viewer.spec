# -*- mode: python -*-

block_cipher = None


a = Analysis(['finance_business_exchange_file_viewer.py'],
             pathex=['G:\\workshop\\Python\\finance_business_exchange_file_viewer\\config', 'G:\\workshop\\Python\\finance_business_exchange_file_viewer'],
             binaries=[],
             datas=[('finance_business_exchange_file_viewer.ui', '.'), ('config/', 'config/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='finance_business_exchange_file_viewer',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='finance_business_exchange_file_viewer')
