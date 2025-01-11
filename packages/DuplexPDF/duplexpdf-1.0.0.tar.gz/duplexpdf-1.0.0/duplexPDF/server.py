import logging
from pathlib import Path
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from typing import Callable
from pypdf import PdfWriter
import os
import ftplib
from io import BytesIO
import socket
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from .pdf_handling import DuplexPDF_PDFObject, DuplexPDF_Merge

logger = logging.getLogger("duplexPDF")
ftp = None

def UploadToFTPReceiver(pdf: PdfWriter, name: str):
    global logger, ftp
    try:
        files = ftp.nlst()
        if f"{name}.pdf" in files:
            logger.warning(f"File {name}.pdf already exists on the server. Skip")
            return
        with BytesIO() as bytes_stream:
            pdf.write(bytes_stream)
            bytes_stream.flush()
            bytes_stream.seek(0)
            ftp.storbinary(f"STOR {name}.pdf", bytes_stream)
        logger.info(f"Uploaded merged {name}.pdf")    
    except ftplib.all_errors as ex:
        logger.error(f"Transmitting the file an error was raised: {str(ex)}")
    finally:
        pdf.close()


class DuplexPDF_Server:

    max_tdelta = 10*60

    def __init__(self, output_func: Callable):
        self._duplex1: DuplexPDF_PDFObject|None = None
        self._duplex2: DuplexPDF_PDFObject|None = None
        if not isinstance(output_func, Callable):
            raise ValueError(f"output_func must by of type Callable. You provided ({type(output_func)})")
        self.output_func = output_func

    @property
    def duplex1(self) -> DuplexPDF_PDFObject|None:
        return self._duplex1
    
    @property
    def duplex2(self) -> DuplexPDF_PDFObject|None:
        return self._duplex2
    
    def AddDuplex(self, path: Path) -> bool:
        global logger
        if not isinstance(path, Path):
            raise ValueError(f"path must be a pathlib.Path. You provided {type(val)}")
        d = DuplexPDF_PDFObject(path)
        if not d.valid:
            return False
        if d.duplexNr == 1:
            self._ClearDuplex1()
            self._ClearDuplex2()
            self._duplex1 = d
        elif d.duplexNr == 2:
            self._ClearDuplex2()
            if self._duplex1 is None:
                self._ClearDuplex1()
                logger.info(f"Received Duplex2, but Duplex1 is not available. Skip")
                return False
            dt = d.fname_ts - self._duplex1.fname_ts
            if dt > DuplexPDF_Server.max_tdelta or dt < 0:
                self._ClearDuplex1()
                logger.info(f"Duplex 1 is too old ({dt} s). Skip")
                return False
            self._duplex2 = d

            merged_name = f"Duplex_{self._duplex1.fname_date}_{self._duplex1.fname_time}-{self._duplex2.fname_time}"
            merged_pdf = DuplexPDF_Merge(self._duplex1, self._duplex2)
            if merged_pdf is None:
                return False
            logger.debug("Sending merged file to output function")
            self.output_func(merged_pdf, merged_name)
            merged_pdf.close()
            self.Clear()
        return True

    def Clear(self):
        self._ClearDuplex1()
        self._ClearDuplex2()

    def _ClearDuplex2(self):
        if self._duplex2 is not None:
            self._duplex2.Deconstruct()
        self._duplex2 = None
    
    def _ClearDuplex1(self):
        if self._duplex1 is not None:
            self._duplex1.Deconstruct()
        self._duplex1 = None

duplexPDFServer = None

class DuplexPDF_FTPHandler(TLS_FTPHandler):
    def on_file_received(self, file):
        global logger
        path = Path(file).resolve()
        logger.info(f"Received file {path.name}")
        duplexPDFServer.AddDuplex(path)

def ClearCache(cacheDir: Path):
    global logger
    if not (cacheDir / ".cache").exists():
        open(cacheDir / ".cache", 'w').close()
        logger.info(f"Initialized cache at {cacheDir}")
        return
    n = 0
    for f in cacheDir.iterdir():
        if f.name not in [".cache", "ftpd.crt", "ftpd.key"]:
            f.unlink()
            n += 1
    logger.info(f"Cleared {n} files from cache")

def Load_Certificate(path: Path) -> tuple[Path, Path]:
    global logger
    path_crt = (path / "ftpd.crt").resolve()
    path_key = (path / "ftpd.key").resolve()
    if path_crt.exists() and path_key.exists(): 
        return (path_crt, path_key)
    logger.info(f"The certificates files for the upload server do not exist in the script directory. Creating them")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    valid_time = (datetime.datetime.now() - datetime.timedelta(days=1), datetime.datetime.now() + datetime.timedelta(days=20*365))
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "duplexPDF")])
    basic_contraints = x509.BasicConstraints(ca=True, path_length=0)

    cert = (x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(1000)
            .not_valid_before(valid_time[0])
            .not_valid_after(valid_time[1])
            .add_extension(basic_contraints, False)
            .sign(key, hashes.SHA256())
        )
    with open(path_crt, "wb") as f:
        f.write(cert.public_bytes(encoding=serialization.Encoding.PEM))
    with open(path_key, "wb") as f:
        f.write(key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption()))
    logger.info("Generated TLS/SSL Certificate and saved in the script directory")
    return (path_crt, path_key) 

def Run(cacheDir: Path):
    global duplexPDFServer, logger, ftp
    duplexPDFServer = DuplexPDF_Server(UploadToFTPReceiver)

    ClearCache(cacheDir)
    path_crt, path_key = Load_Certificate(cacheDir)

    local_ip = socket.gethostbyname(socket.gethostname())
    source_port = int(os.environ["duplexPDF_source_port"]) if "duplexPDF_source_port" in os.environ.keys() else None

    incoming_addr = os.environ["duplexPDF_incoming_addr"].split(":") if "duplexPDF_incoming_addr" in os.environ.keys() else ("", "")
    if len(incoming_addr) > 2:
        logger.error("Please provide a valid incoming address")
        return
    server_ip = incoming_addr[0] if incoming_addr[0].strip() != "" else local_ip
    incoming_ip = local_ip
    incoming_port = int(incoming_addr[1]) if len(incoming_addr) == 2 and incoming_addr[1].strip() != "" else 1487

    outgoing_addr = os.environ["duplexPDF_outgoing_addr"].split(":")
    if len(outgoing_addr) > 2:
        logger.error("Please provide a valid outgoingg address")
        return
    outgoing_ip = outgoing_addr[0]
    outgoing_port = int(outgoing_addr[1]) if len(outgoing_addr) == 2 and outgoing_addr[1].strip() != "" else 21

    passive_ports = None
    if "duplexPDF_incoming_passive_port_range" in os.environ.keys():
        if len(passive_ports := os.environ["duplexPDF_incoming_passive_port_range"].replace(" ", "").split("-")) != 2 or int(passive_ports[0]) >= int(passive_ports[1]):
            logger.error("Please provide the passive port range in the format START-END (for example 32000-32005)")
            return
        passive_ports = range(int(passive_ports[0]), int(passive_ports[1]) + 1)

    incoming_username ="duplexPDF"
    incoming_password = os.environ["duplexPDF_incoming_password"]
    outgoing_username = os.environ["duplexPDF_outgoing_username"]
    outgoing_password = os.environ["duplexPDF_outgoing_password"]
    outgoing_folder = os.environ["duplexPDF_outgoing_dir"]
    try:
        ftp = ftplib.FTP_TLS()
        ftp.set_pasv(False)
        sourceAdress = (local_ip, source_port) if source_port is not None else None
        ftp.connect(outgoing_ip, outgoing_port, source_address=(sourceAdress))
        ftp.auth()
        ftp.prot_p()
        ftp.login(user=outgoing_username, passwd=outgoing_password)
        ftp.cwd(outgoing_folder)
    except ftplib.all_errors as ex:
        logger.error(f"Can't connect to FTP server for upload ({str(ex)})")
        return False
    logger.debug(f"FTP server welcome message: {ftp.getwelcome()}")

    authorizer = DummyAuthorizer()
    authorizer.add_user(incoming_username, incoming_password, homedir=str(cacheDir), perm="w")

    handler = DuplexPDF_FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = passive_ports
    handler.certfile = str(path_crt)
    handler.keyfile = str(path_key)
    handler.masquerade_address = server_ip
    handler.banner = "duplexPDF Upload Server"
    
    server = FTPServer((incoming_ip, incoming_port), handler)
    server.max_cons = 64
    server.max_cons_per_ip = 32

    logger.info(f"--Started duplexPDF server on {server.address[0]}:{server.address[1]}--")

    server.serve_forever(handle_exit=True)