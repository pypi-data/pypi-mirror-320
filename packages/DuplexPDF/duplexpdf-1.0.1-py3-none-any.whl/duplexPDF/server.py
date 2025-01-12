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

class IOutgoing:
    def UploadPDF(self, file_name: str, pdf: PdfWriter) -> bool:
        pass

class OutgoingFTP(IOutgoing):

    def __init__(self, source_addr, ip, port, username, password, folder):
        self.sourceAdress = source_addr
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.folder = folder

    def Connect(self, func: Callable|None = None) -> bool:
        global logger
        logger.info("Connecting to FTP")
        ftp = ftplib.FTP_TLS()
        try:
            ftp.connect(self.ip, self.port, source_address=self.sourceAdress)
            ftp.auth()
            ftp.prot_p()
            ftp.login(user=self.username, passwd=self.password)
            ftp.cwd(self.folder)
            logger.debug(f"Outgoing FTP server welcome message: {ftp.getwelcome()}")
            ftp.nlst() # Test if PORT cmd is working

            if func is not None:
                return func(ftp)
        except ftplib.all_errors as ex:
            logger.warning(f"There was an error on the outgoing FTP server connection: {str(ex)}")
            return False
        finally:
            ftp.close()
        return True
    
    def UploadFile(self, file_name: str, bytesstream: BytesIO) -> bool:
        global logger
        def _Upload(ftp: ftplib.FTP_TLS) -> bool:
            try:
                files = ftp.nlst()
            except ftplib.all_errors as ex:
                logger.warning(f"There was an error listing the files on the outgoing FTP server: {str(ex)}")
                return False
            
            if file_name in files:
                logger.warning(f"File {file_name} already exists on the server. Skip")
                return False
            
            try:
                ftp.storbinary(f"STOR {file_name}", bytesstream)
            except ftplib.all_errors as ex:
                logger.warning(f"There was an error storing the file on the outgoing FTP server: {str(ex)}")
                return False
            return True
        return self.Connect(_Upload)
        
    
    def UploadPDF(self, file_name: str, pdf: PdfWriter) -> bool:
        global logger
        try:
            with BytesIO() as bytesstream:
                pdf.write(bytesstream)
                bytesstream.flush()
                bytesstream.seek(0)
                if self.UploadFile(file_name, bytesstream):
                    logger.info(f"Uploaded merged {file_name}")   
                    return True
        except IOError as ex:
            logger.error(f"There was an error handling the pdf stream")
            return False
        finally:
            pdf.close()
        return False

class DuplexPDF_Server:

    max_tdelta = 10*60

    def __init__(self, output_obj: IOutgoing):
        self._duplex1: DuplexPDF_PDFObject|None = None
        self._duplex2: DuplexPDF_PDFObject|None = None
        if not isinstance(output_obj, IOutgoing):
            raise ValueError(f"output_obj must by of type IOutgoing. You provided ({type(output_obj)})")
        self.output_obj = output_obj

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
            self.output_obj.UploadPDF(f"{merged_name}.pdf", merged_pdf)
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
    global logger, duplexPDFServer

    ClearCache(cacheDir)
    path_crt, path_key = Load_Certificate(cacheDir)

    local_ip = socket.gethostbyname(socket.gethostname())
    nat_ip = os.environ["duplexPDF_nat_addr"] if "duplexPDF_nat_addr" in os.environ.keys() else None
    source_port = int(os.environ["duplexPDF_source_port"]) if "duplexPDF_source_port" in os.environ.keys() and os.environ["duplexPDF_source_port"].strip() != "" else None
    

    incoming_addr = os.environ["duplexPDF_incoming_addr"].split(":") if "duplexPDF_incoming_addr" in os.environ.keys() else ("", "")
    outgoing_addr = os.environ["duplexPDF_outgoing_addr"].split(":")
    if len(incoming_addr) > 2:
        logger.error("Please provide a valid incoming address")
        return
    if len(outgoing_addr) > 2:
        logger.error("Please provide a valid outgoingg address")
        return
    
    incoming_ip = incoming_addr[0] if incoming_addr[0].strip() != "" else local_ip
    outgoing_ip = outgoing_addr[0]
    incoming_port = int(incoming_addr[1]) if len(incoming_addr) == 2 and incoming_addr[1].strip() != "" else 1487
    outgoing_port = int(outgoing_addr[1]) if len(outgoing_addr) == 2 and outgoing_addr[1].strip() != "" else 21

    sourceAddr = (local_ip, source_port) if source_port is not None else None
    sourceAddr = None

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

    outgoingFTP = OutgoingFTP(source_addr=sourceAddr, ip=outgoing_ip, port=outgoing_port, username=outgoing_username, password=outgoing_password, folder=outgoing_folder)
    if not outgoingFTP.Connect():
        return
    duplexPDFServer = DuplexPDF_Server(outgoingFTP)

    authorizer = DummyAuthorizer()
    authorizer.add_user(incoming_username, incoming_password, homedir=str(cacheDir), perm="w")

    handler = DuplexPDF_FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = passive_ports
    handler.certfile = str(path_crt)
    handler.keyfile = str(path_key)
    handler.masquerade_address = nat_ip
    handler.banner = "duplexPDF Upload Server"
    
    server = FTPServer((incoming_ip, incoming_port), handler)
    server.max_cons = 64
    server.max_cons_per_ip = 32

    logger.info(f"--Started duplexPDF server on {server.address[0]}:{server.address[1]}{f" (NAT address {nat_ip})" if nat_ip is not None else ""}--")

    server.serve_forever(handle_exit=True)