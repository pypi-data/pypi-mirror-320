import os
import sys

def get_executable_path(): 
    '''
    Returns the path of the executable file if the script is running in a bundled executable context.
    If the script is not running as an executable, returns the path of the script file.
    '''
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.getcwd()

    
def get_temp_path():
    '''
    Returns the path of the temporary directory used by a bundled executable.
    If the script is not running as a bundled executable, returns the path of the script file.
    '''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.getcwd()
