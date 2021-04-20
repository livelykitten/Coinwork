from cx_Freeze import setup, Executable
 
buildOptions = dict(packages=['requests', 'time', 'threading', 'json', 'datetime', 'collections', 'ctypes', 'os', 'winsound', 'PySide6'], excludes = ["tkinter", "numpy"])
 
exe = [Executable('main.py', base = "Win32GUI")]
 
setup(
    name='CoinWatcher',
    version='0.0.1',
    author='Tony Min',
    description = 'description',
    options = dict(build_exe = buildOptions),
    executables = exe
)