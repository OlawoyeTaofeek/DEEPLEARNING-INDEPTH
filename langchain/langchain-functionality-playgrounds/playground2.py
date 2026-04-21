"""Reading text files and pdf files code implemetation from scratch."""
import chardet
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from typing import Generator, List, NamedTuple, Optional, Union, cast

from pydantic import BaseModel, Field


class EncodingResult(NamedTuple):
    encoding: str
    confidence: float
    language: str | None

class Document(BaseModel):
    metadata: dict[str, str] = Field(default_factory=dict)
    page_content: str

enc = EncodingResult(encoding="utf-8", confidence=0.99, language="en")
print(enc.confidence)
# Advantages of using NamedTuple:
# 1. Immutability: NamedTuples are immutable, which means that once an
# instance is created, its values cannot be changed. This can help prevent
# bugs and make code easier to reason about.
# 2. Readability: NamedTuples allow you to access fields by name, which can
# make code more readable and self-documenting. This can be especially helpful
# 3. Hashability: NamedTuples are hashable, which means they can be used as keys in dictionaries or stored in sets. This can be useful for certain data structures and algorithms.
# 4. Memory Efficiency: NamedTuples can be more memory efficient than regular classes because

# Chardet
# Chardet is a Python library that detects the encoding of text data. 
# It uses a combination of statistical analysis and heuristics to determine the most likely encoding of a given byte sequence. 
# Chardet can be used to handle text data that may be in various encodings, making it useful for applications that need to process text from different sources or languages.
# The output of chardet is a dictionary containing the detected encoding, confidence level, and language (if applicable): {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'en'}.

def detect_file_encodings(file_path: Union[str, Path]) -> List[EncodingResult]:

    file_path = str(file_path)

    def read_and_detect(file_path: str) -> List[dict]:
        with open(file_path, "rb") as f:
            data = f.read()
        return cast(List[dict], chardet.detect_all(data))
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future = executor.submit(read_and_detect, file_path)
        try:
            encodings = future.result(timeout=5)
        except TimeoutError:
            raise TimeoutError(f"Timeout reached while detecting encoding for {file_path}")
    
    if all(encoding['encoding'] is None for encoding in encodings):
        raise RuntimeError(f"Could not detect encoding for {file_path}")
    return [EncodingResult(**enc) for enc in encodings if enc['encoding'] is not None]

class TextLoader:
    """Load text file.


    Args:
        file_path: Path to the file to load.

        encoding: File encoding to use. If `None`, the file will be loaded
        with the default system encoding.

        autodetect_encoding: Whether to try to autodetect the file encoding
            if the specified encoding fails.
    """
    def __init__(
            self, 
            file_path: Union[str, Path],
            encoding: Optional[str] = None,
            autodetect_encoding: bool = False,
    )->None:
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding


        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
    def load(self) -> List[Document]:
        text = ""
        try:
            with open(self.file_path, encoding=self.encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detect_encoding = detect_file_encodings(self.file_path)
                for encoding in detect_encoding:
                    try:
                        with open(self.file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                            break   
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e
        metadata = {"source": str(self.file_path)}
        return [Document(page_content=text, metadata=metadata)]
        
    def lazy_load(self) -> Generator[Document, None, None]:
        text = ""
        try:
            with open(self.file_path, encoding=self.encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detect_encoding = detect_file_encodings(self.file_path)
                for encoding in detect_encoding:
                    try:
                        with open(self.file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                            break   
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e
        metadata = {"source": str(self.file_path)}
        yield Document(page_content=text, metadata=metadata)

def process(doc: Document) -> List[Document]:
    text = doc.page_content

    # 🔹 Basic cleaning
    text = text.lower()
    text = text.replace("\n", " ")
    text = text.strip()

    # 🔹 Remove extra spaces
    text = " ".join(text.split())

    # 🔹 (Optional) remove weird characters
    # import re
    # text = re.sub(r"[^\w\s.,!?]", "", text)

    # 🔹 Return NEW Document (immutability mindset)
    return [Document(
        page_content=text,
        metadata=doc.metadata  # preserve metadata
    )]

class PyPDFLoader:
    """Load PDF file.
    

    """
    ...