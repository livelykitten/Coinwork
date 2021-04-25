from cx_Freeze import setup, Executable
 
buildOptions = dict(packages=['requests', 'time', 'threading', 'json', 'datetime', 'collections', 'os', 'PySide6', 'pygame'], 
excludes = ["tkinter", "numpy"],
include_files = ['./alarm.wav',
'./main.qml', './MsgModel.qml', './MsgDelegate.qml', './AlarmModel.qml', './AlarmDelegate.qml', './AlarmDialog.qml', './MsgDialog.qml',
'C:\Windows\System32\VCRUNTIME140.dll', 'C:\Windows\System32\MSVCP140.dll'], include_msvcr=True)
 
exe = [Executable('main.py', base = "Win32GUI")]
 
setup(
    name='CoinWatcher',
    version='0.0.1',
    author='Tony Min',
    description = 'description',
    options = dict(build_exe = buildOptions),
    executables = exe
)