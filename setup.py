from cx_Freeze import setup, Executable
 
buildOptions = dict(packages=['requests', 'time', 'threading', 'json', 'datetime', 'collections', 'ctypes', 'os', 'winsound'], excludes = ["tkinter", "numpy"])
 
exe = [Executable('Document1.py')]
 
setup(
    name='BitcoinWatcher',
    version='0.0.1',
    author='Tony Min',
    description = 'description',
    options = dict(build_exe = buildOptions),
    executables = exe
)