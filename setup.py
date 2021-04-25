from cx_Freeze import setup, Executable
 
buildOptions = dict(packages=['requests', 'time', 'threading', 'json', 'datetime', 'collections', 'os', 'PySide6', 'pygame'], 
excludes = ["tkinter", "numpy"],
include_files = ['./alarm.wav'], include_msvcr=True)
 
exe = [Executable('Document1.py')]
 
setup(
    name='CoinWatcher',
    version='0.0.1',
    author='Tony Min',
    description = 'description',
    options = dict(build_exe = buildOptions),
    executables = exe
)
