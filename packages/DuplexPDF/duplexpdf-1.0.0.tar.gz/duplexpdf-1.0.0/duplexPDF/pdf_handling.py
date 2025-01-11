import logging
import time
import datetime
import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PyPdfError

logger = logging.getLogger("duplexPDF")

class DuplexPDF_PDFObject:
    def __init__(self, path: Path):
        global logger

        self._Init()
        if not isinstance(path, Path):
            raise ValueError(f"[PDFObject] Path argument must be a pathlib.Path. You provided {type(file)}")
        if not path.exists():
            logger.error(f"{path.name} does not exist")
            return 
        if not path.is_file():
            logger.error(f"{path.name} is a folder")
            return
        
        self._path = path
        
        r = re.search(r"^Duplex(\d)_(([\d]{4})([\d]{2})([\d]{2}))_(([\d]{2})([\d]{2})([\d]{2})).pdf$", path.name)
        if r is None or len(r.groups()) != 9:
            self._Init()
            logger.info(f"{path.name} is not a valid duplex filename")
            return 
        self._duplexNr = int(r.groups()[0])
        if self._duplexNr not in [1,2]:
            self._Init()
            logger.info(f"{path.name} is not a valid duplex filename")
            return 
        try:
            self._fdatetime = datetime.datetime(year=int(r.groups()[2]), 
                                                month=int(r.groups()[3]),
                                                day=int(r.groups()[4]),
                                                hour=int(r.groups()[6]),
                                                minute=int(r.groups()[7]),
                                                second=int(r.groups()[8]))
        except ValueError:
            self._Init()
            logger.info(f"{path.name} does not contain a valid datetime")
            return
        self._fdate_date = r.groups()[1]
        self._fdate_time = r.groups()[5]
        self._valid = True

    def _Init(self):
        self._valid = False
        self._path = None
        self._pdfreader: PdfReader|None = None
        self._duplexNr = None
        self._fdatetime = None
        self._fdate_date = None
        self._fdate_time = None

    def Deconstruct(self):
        if isinstance(self._pdfreader, PdfReader):
            self._pdfreader.close()
            self._pdfreader = None

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def path(self) -> Path|None:
        return self._path
    
    @property
    def pdfReader(self) -> PdfReader|None:
        global logger
        if isinstance(self._pdfreader, PdfReader):
            return self._pdfreader
        if self._path is None:
            return None
        try:
            self._pdfreader = PdfReader(self._path)
        except PyPdfError:
            logger.info(f"{self._path.name} can't be decoded")
            self._pdfreader = None
            return None
        if self._pdfreader.is_encrypted:
            logger.info(f"{self._path.name} is encrypted")
            self._pdfreader.close()
            self._pdfreader = None
            return None
        return self._pdfreader
    
    @property
    def duplexNr(self) -> int|None:
        return self._duplexNr
    
    @property
    def fname_ts(self) -> int|None:
        if self._fdatetime is None:
            return None
        return time.mktime(self._fdatetime.timetuple())
    
    @property
    def fname_date(self) -> str|None:
        return self._fdate_date
    
    @property
    def fname_time(self) -> str|None:
        return self._fdate_time


def DuplexPDF_Merge(duplex1: DuplexPDF_PDFObject, duplex2: DuplexPDF_PDFObject) -> None|PdfWriter:
    global logger
    if not isinstance(duplex1, DuplexPDF_PDFObject):
        raise ValueError(f"duplex 1 needs to be of type DuplexPDF_PDFObject. You provided {type(duplex1)}")
    if not isinstance(duplex2, DuplexPDF_PDFObject):
        raise ValueError(f"duplex 2 needs to be of type DuplexPDF_PDFObject. You provided {type(duplex2)}")
    
    if duplex1.valid == False or duplex2.valid == False or duplex1.pdfReader is None or duplex2.pdfReader is None:
        logger.error("The pdf objects are not accessible")
        return None
    
    n1 = duplex1.pdfReader.get_num_pages()
    n2 = duplex2.pdfReader.get_num_pages()
    if n1 != n2:
        logger.info(f"The files ({duplex1.path.name}, {duplex2.path.name}) have not the same number of pages ({n1} and {n2})")
        return None
    
    pdf_merged = PdfWriter()
    for p1, p2 in zip(duplex1.pdfReader.pages[:], duplex2.pdfReader.pages[::-1]):
        pdf_merged.add_page(p1)
        pdf_merged.add_page(p2)

    if duplex1.pdfReader.metadata is not None:
        pdf_merged.add_metadata(duplex1.pdfReader.metadata)
    elif duplex2.pdfReader.metadata is not None:
        pdf_merged.add_metadata(duplex2.pdfReader.metadata) 
    pdf_merged.add_metadata({"/Producer": "DuplexPDF by Andreas B."})
    return pdf_merged    