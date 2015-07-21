# -*- mode: python -*-
a = Analysis(['scan_session_tool.py'],
             pathex=['/Users/floriankrause/PycharmProjects/ScanSessionTool'],
             hiddenimports=['yaml'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Scan Session Tool',
          debug=False,
          strip=None,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='Scan Session Tool.app',
             version='0.6.0',
             icon=None)
