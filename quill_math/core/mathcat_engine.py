"""ctypes binding to MathCAT (daisy/MathCATForC) for natural math speech synthesis."""

from __future__ import annotations

import ctypes
import functools
import os
import threading
from pathlib import Path


import zipfile


class MathCatUnavailable(Exception):
    """Raised when the MathCAT engine pack (DLL + Rules) is not found."""


class MathCatError(Exception):
    """Raised when MathCAT reports a conversion error."""


_lock = threading.Lock()
_dll: ctypes.CDLL | None = None


def pack_dir() -> Path:
    """Return the folder path where MathCAT DLL and Rules reside."""
    custom_dir = os.environ.get("MATHCAT_DIR", "").strip()
    if custom_dir:
        return Path(custom_dir)
    app_root = os.environ.get("QUILL_APP_ROOT", "").strip()
    if app_root:
        bundled = Path(app_root) / "tools" / "mathcat"
        if (bundled / "libmathcat_c.dll").is_file() or find_rules_dir(bundled) is not None:
            return bundled
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        return Path(local_app_data) / "quill_math" / "engine_packs" / "mathcat"
    return Path.home() / ".quill_math" / "mathcat"


def find_rules_dir(pack: Path | None = None) -> Path | None:
    """Find or unpack the MathCAT Rules directory (supports Rules-minimized and zipped rules)."""
    search_dirs: list[Path] = []
    if pack is not None:
        search_dirs.append(pack)
    search_dirs.append(pack_dir())
    
    # Also check workspace MathCAT repo if available
    workspace_root = Path(__file__).resolve().parents[3]
    search_dirs.append(workspace_root / "MathCAT")
    search_dirs.append(workspace_root / "MathCAT" / "Rules")

    for base in search_dirs:
        if not base.exists():
            continue
        # Direct Rules or Rules-minimized directories
        for candidate in ("Rules", "Rules-minimized", "rules", "rules-minimized"):
            target = base / candidate if base.is_dir() else base
            if target.is_dir() and ((target / "Languages").is_dir() or (target / "prefs.yaml").is_file()):
                return target
        # If base is itself the Rules folder
        if base.is_dir() and ((base / "Languages").is_dir() or (base / "prefs.yaml").is_file()):
            return base
        # Check for zip files to extract
        for zip_name in ("Rules-minimized.zip", "Rules.zip"):
            zip_file = base / zip_name
            if zip_file.is_file():
                extract_target = base / zip_file.stem
                if not extract_target.exists():
                    try:
                        with zipfile.ZipFile(zip_file, "r") as zf:
                            zf.extractall(extract_target)
                    except Exception:
                        pass
                if extract_target.is_dir():
                    return extract_target

    return None


def is_available() -> bool:
    """Return True if both DLL and Rules directory exist."""
    pack = pack_dir()
    dll_found = (pack / "libmathcat_c.dll").is_file() or (
        (Path(__file__).resolve().parents[3] / "MathCAT" / "target" / "release" / "libmathcat_c.dll").is_file()
    )
    rules_found = find_rules_dir(pack) is not None
    return dll_found and rules_found


def _read_and_free(dll: ctypes.CDLL, raw_ptr: int | None) -> str:
    if not raw_ptr:
        return ""
    text = ctypes.cast(raw_ptr, ctypes.c_char_p).value or b""
    dll.FreeMathCATString(ctypes.c_void_p(raw_ptr))
    return text.decode("utf-8", "replace")


def _load() -> ctypes.CDLL:
    global _dll
    if _dll is not None:
        return _dll
    pack = pack_dir()
    dll_path = pack / "libmathcat_c.dll"
    if not dll_path.is_file():
        alt_dll = Path(__file__).resolve().parents[3] / "MathCAT" / "target" / "release" / "libmathcat_c.dll"
        if alt_dll.is_file():
            dll_path = alt_dll
    rules_path = find_rules_dir(pack)
    if not dll_path.is_file() or rules_path is None:
        raise MathCatUnavailable("MathCAT engine pack is not installed.")

    dll = ctypes.CDLL(str(dll_path))
    dll.GetError.restype = ctypes.c_void_p
    dll.FreeMathCATString.argtypes = [ctypes.c_void_p]
    dll.SetRulesDir.argtypes = [ctypes.c_char_p]
    dll.SetRulesDir.restype = ctypes.c_void_p
    dll.SetMathML.argtypes = [ctypes.c_char_p]
    dll.SetMathML.restype = ctypes.c_void_p
    dll.GetSpokenText.restype = ctypes.c_void_p
    dll.GetBraille.argtypes = [ctypes.c_char_p]
    dll.GetBraille.restype = ctypes.c_void_p
    dll.GetMathCATVersion.restype = ctypes.c_void_p
    dll.SetPreference.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    dll.SetPreference.restype = ctypes.c_void_p

    result = _read_and_free(dll, dll.SetRulesDir(str(rules_path).encode("utf-8")))
    if result != "Ok":
        error = _read_and_free(dll, dll.GetError())
        raise MathCatError(f"SetRulesDir failed: {error}")
    _dll = dll
    return dll


def _check_error(dll: ctypes.CDLL) -> None:
    error = _read_and_free(dll, dll.GetError())
    if error:
        raise MathCatError(error)


def get_version() -> str:
    """Return loaded MathCAT version."""
    with _lock:
        dll = _load()
        version = _read_and_free(dll, dll.GetMathCATVersion())
        _check_error(dll)
        return version


def set_preference(pref: str, value: str) -> None:
    """Set a MathCAT preference (e.g. 'Language' -> 'en', 'BrailleCode' -> 'Nemeth')."""
    with _lock:
        dll = _load()
        result = _read_and_free(dll, dll.SetPreference(pref.encode("utf-8"), value.encode("utf-8")))
        _check_error(dll)
        if result != "Ok":
            raise MathCatError(f"SetPreference failed: {result}")
        clear_cache()


def clear_cache() -> None:
    """Clear in-memory LRU caches."""
    mathml_to_speech.cache_clear()
    mathml_to_braille.cache_clear()


@functools.lru_cache(maxsize=4096)
def mathml_to_speech(mathml: str) -> str:
    """Render MathML to natural spoken math via MathCAT with LRU memoization."""
    with _lock:
        dll = _load()
        set_result = _read_and_free(dll, dll.SetMathML(mathml.encode("utf-8")))
        _check_error(dll)
        if not set_result:
            raise MathCatError("MathCAT rejected MathML input.")
        speech = _read_and_free(dll, dll.GetSpokenText())
        _check_error(dll)
        return speech


def mathml_batch_to_speech(mathml_list: list[str]) -> list[str]:
    """Batch render a collection of MathML expressions to spoken text."""
    return [mathml_to_speech(m) for m in mathml_list]


@functools.lru_cache(maxsize=4096)
def mathml_to_braille(mathml: str, nav_node_id: str = "") -> str:
    """Render MathML to Braille via MathCAT with LRU memoization."""
    with _lock:
        dll = _load()
        set_result = _read_and_free(dll, dll.SetMathML(mathml.encode("utf-8")))
        _check_error(dll)
        if not set_result:
            raise MathCatError("MathCAT rejected MathML input.")
        braille = _read_and_free(dll, dll.GetBraille(nav_node_id.encode("utf-8")))
        _check_error(dll)
        return braille


def mathml_batch_to_braille(mathml_list: list[str], nav_node_id: str = "") -> list[str]:
    """Batch render a collection of MathML expressions to Braille."""
    return [mathml_to_braille(m, nav_node_id=nav_node_id) for m in mathml_list]
