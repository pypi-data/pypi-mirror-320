# Use this script to install DuplexPDF from pip (if not installed yet) and run it as a module

import subprocess
import sys

print("Starting DuplexPDF by Andreas B.")

try:
    import duplexPDF
except ModuleNotFoundError:
    print(subprocess.check_call([sys.executable, "-m", "pip", "install", "duplexPDF"]))

