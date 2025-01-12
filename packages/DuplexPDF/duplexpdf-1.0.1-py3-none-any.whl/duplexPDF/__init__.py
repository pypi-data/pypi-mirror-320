import logging
import sys
import os
from pathlib import Path

__version__ = "1.0.1"

for name, desc in [("duplexPDF_cache", "a folder for the cache files"),
                      ("duplexPDF_log", "a folder for the log"),
                      ("duplexPDF_incoming_password", "a password for the upload FTP server"),
                      ("duplexPDF_outgoing_addr", "the address destination FTP server (for example 127.0.0.1:1487)"),
                      ("duplexPDF_outgoing_username", "an username for the FTP server to upload"),
                      ("duplexPDF_outgoing_password", "a password for the FTP server to upload"),
                      ("duplexPDF_outgoing_dir", "a dir to upload the merged files")]:
    
    if name not in os.environ.keys():
        print(f"Please provide {desc} in the environment variable '{name}'")
        exit()

cache_dir = Path(os.environ["duplexPDF_cache"]).resolve()
log_dir = Path(os.environ["duplexPDF_log"]).resolve()
if not cache_dir.exists() or not cache_dir.is_dir():
    print(f"Your provided cache path {cache_dir} is not valid or does not exist")
    exit()
if not log_dir.exists() or not log_dir.is_dir():
    print(f"Your provided log path {log_dir} is not valid or does not exist")
    exit()    

logging.getLogger("pypdf").setLevel(logging.CRITICAL)

logger = logging.getLogger("duplexPDF")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(name)s | %(asctime)s | %(levelname)s] %(message)s')
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)
streamHandler2 = logging.StreamHandler(sys.stdout)
streamHandler2.setLevel(logging.WARNING)
streamHandler2.setFormatter(formatter)
fileHandler = logging.FileHandler(filename=log_dir / "log.txt", mode="w+")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)
logging.getLogger("pyftpdlib").addHandler(fileHandler)
logging.getLogger("pyftpdlib").addHandler(streamHandler2)
logging.getLogger("pyftpdlib").setLevel(logging.INFO)


from . import server
server.Run(cacheDir=cache_dir)