from pathlib import Path
from typing import Generator, Optional, Union

try:
    from charset_normalizer import from_bytes
except ImportError:
    from_bytes = None


class TextFileLoader:
    """
    Load text file.


    Args:
        file_path: Path to the file to load.

        encoding: File encoding to use. If `None`, the file will be loaded
        with the default system encoding.

        autodetect_encoding: Whether to try to autodetect the file encoding
            if the specified encoding fails.

    Strategy:
    1. Use user-provided encoding if given
    2. Try UTF-8
    3. Fallback to charset-normalizer detection (if enabled)
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        autodetect_encoding: bool = False,
    ) -> None:
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding
        self._resolved_encoding: Optional[str] = None  # cache

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if self.autodetect_encoding and from_bytes is None:
            raise ImportError(
                "charset-normalizer is required for autodetect_encoding=True. "
                "Install with `pip install charset-normalizer`."
            )

    # -----------------------------
    # 🔍 Internal Helpers
    # -----------------------------
    def _detect_encoding(self) -> str:
        """
        Detect encoding using charset-normalizer.
        """
        with open(self.file_path, "rb") as f:
            raw_data = f.read(100_000)  # sample

        results = from_bytes(raw_data)
        best_match = results.best()

        if best_match is None or best_match.encoding is None:
            raise ValueError("Failed to detect encoding.")

        return best_match.encoding

    def _resolve_encoding(self) -> str:
        """
        Resolve encoding using a multi-step strategy.
        """
        # cache result
        if self._resolved_encoding:
            return self._resolved_encoding

        # 1. User-provided encoding
        if self.encoding:
            self._resolved_encoding = self.encoding
            return self._resolved_encoding

        # 2. Try UTF-8 first
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                f.read(10_000)
            self._resolved_encoding = "utf-8"
            return self._resolved_encoding
        except UnicodeDecodeError:
            pass

        # 3. Fallback to detection
        if self.autodetect_encoding:
            detected = self._detect_encoding()
            self._resolved_encoding = detected
            return self._resolved_encoding

        # 4. Final fallback
        self._resolved_encoding = "utf-8"
        return self._resolved_encoding

    # -----------------------------
    # 📥 Public API
    # -----------------------------
    def load(self) -> str:
        """
        Load entire file into memory.
        """
        encoding = self._resolve_encoding()

        try:
            with open(self.file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                f"Failed to decode file {self.file_path} with encoding '{encoding}'."
            ) from e

    def lazy_load(self) -> Generator[str, None, None]:
        """
        Lazily yield file lines.
        """
        encoding = self._resolve_encoding()

        try:
            with open(self.file_path, "r", encoding=encoding) as f:
                for line in f:
                    yield line
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                f"Failed to decode file {self.file_path} with encoding '{encoding}'."
            ) from e