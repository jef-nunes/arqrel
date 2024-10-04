from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from os import stat
from typing import Dict, Optional, Tuple


class Utils:

    config_extensions = [
        '.code-workspace', '.sln', '.csproj', '.vbproj', '.xcodeproj',
        '.apkproject', '.gradle', '.iml', '.project', '.classpath',
        '.makefile', '.json', '.yaml', '.toml', '.editorconfig',
        '.vscode', '.env', '.xml', '.proto', '.ini', '.cfg', '.properties', '.git'
    ]

    linux_shell_extensions = [
        '.bash', '.zsh', '.sh', 'ksh', 'csh', 'tcsh'
    ]

    source_extensions = [
        '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.rb', '.php',
        '.java', '.c', 'cc', '.cpp', '.h', '.hpp', '.cs', '.go',
        '.rs', '.pl', '.R', '.r', '.swift', '.kt',
        '.lua', '.html', '.css', '.sql', '.vb', '.asm', '.m', '.tcl',
        '.dart', '.scala', '.groovy', '.clj', '.swift'
    ]

    bytecode_extensions = [
        '.jar', '.pyc', '.class', '.pyo', '.pyd'
    ]
    win_exe_extension = ".exe"
    win_bat_extension = ".bat"
    win_pwshell_extension = ".ps1"
    win_office_extensions = [
        ".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"
    ]

    media_extensions = [
        ".mp3", ".gimp", ".png", ".svg", ".jpeg", ".jpg", 
        ".gif", ".bmp", ".mp4", ".avi", ".mkv", ".flv", ".wav"
    ]

    other_bin_extensions = [
        '.bin', '.out', '.so', '.a', '.o', '.elf', '.img',
        '.tar', '.gz', '.bz2', '.xz', '.zip', '.sh',
        '.apk', '.ipa', '.app', '.dex', '.aab',
        '.dll', '.iso', '.dmg', '.rpm', '.deb', '.msi'
    ]

    @classmethod
    def json_parse(cls, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)
    
    @classmethod
    def json_dump(cls, file_path: str, data: dict) -> None:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def hash_sum(cls, target: str) -> str:
        hash_object = sha256()
        with open(target, "rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                hash_object.update(block)
        return hash_object.hexdigest()

    @classmethod
    def get_fmt_size_tuple(cls, target_path: str) -> Tuple[float, str]:
        size = float(Path(target_path).stat().st_size)
        if size < 1024:
            return size, "bytes"
        elif size < 1024 * 1024:
            return size / 1024, "KB"
        elif size < 1024 * 1024 * 1024:
            return size / (1024 * 1024), "MB"
        else:
            return size / (1024 * 1024 * 1024), "GB"

    @classmethod
    def get_fmt_datetime(cls, dt: datetime = datetime.now()) -> str:
        if dt is None:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_file_metadata(cls, file_path: str) -> Dict[str, any]:
        _stat = stat(file_path)
        metadata: Dict = {
            "name": Path(file_path).name,
            "size_bytes": _stat.st_size,
            "permissions": oct(_stat.st_mode & 0o777),
            "creation_time": cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_birthtime)),
            "last_access_time": cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_atime)),
            "last_modify_time": cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_mtime))
        }
        size_value, size_unit = cls.get_fmt_size_tuple(file_path)
        last_dot_index: int = str(metadata["name"]).rfind(".")
        extension = metadata["name"][last_dot_index+1:]
        metadata["extension"] = extension 
        metadata["size_fmt"] = f"{round(size_value, 2)} {size_unit}"
        metadata["hash"] = cls.hash_sum(file_path)
        metadata["path_absolute"] = str(Path(file_path).resolve())
        return metadata
