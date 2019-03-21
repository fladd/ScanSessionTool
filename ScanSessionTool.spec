# -*- mode: python -*-
a = Analysis(['scan_session_tool.py'],
             pathex=['./'],
             hiddenimports=['yaml'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Scan Session Tool.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          version='0.7.0')
app = BUNDLE(exe,
             name='Scan Session Tool.app',
             version='0.7.0',
             icon=None)
