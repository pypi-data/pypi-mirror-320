# Use this script to install DuplexPDF from pip (if not installed yet) and run it as a module

import subprocess
import sys

min_version = "1.0.1" # Min Version for DuplexPDF

try:
    import duplexPDF

    i = -1
    while (i := i+1) < len(duplexPDF.__version__) and i < len(min_version):
        c1: str = duplexPDF.__version__[i]
        c2: str = min_version[i]
        if not c1.isnumeric() or not c2.isnumeric():
            continue
        if int(c1) < int(c2):
            print(f"Updating DuplexPDF from version {duplexPDF.__version__}, as it is older than the min. version {min_version}")
            print(subprocess.check_call([sys.executable, "-m", "pip", "install", "duplexPDF", "--upgrade"]))
            break
        elif int(c1) > int(c2):
            break
    print(f"Detected version: {duplexPDF.__version__})")
except ModuleNotFoundError:
    print(subprocess.check_call([sys.executable, "-m", "pip", "install", "duplexPDF"]))

print(f"Starting DuplexPDF by Andreas B. (version {duplexPDF.__version__})")