from pathlib import Path
from os import scandir, stat
from typing import Dict, List, Tuple
from datetime import datetime
from hashlib import sha256
import argparse
import json
import pprint


class Utils:
    # Predefined file extensions for different categories
    file_extensions = {
            "config": [
                ".apkproject", ".code-workspace", ".classpath", ".csproj",
                ".csv", ".dat", ".deb", ".editorconfig", ".env", 
                ".git", ".gradle", ".iml", ".ini", ".json", 
                ".makefile", ".pbix", ".pbit", ".properties", 
                ".project", ".sln", ".toml", ".vscode", ".xml", 
                ".yaml", ".txt"
            ],
            "linux_shell": [
                ".bash", ".csh", ".ksh", ".sh", ".tcsh", ".zsh"
            ],
            "source": [
                ".asm", ".c", ".cc", ".cs", ".dart", ".for", 
                ".go", ".groovy", ".html", ".java", ".js", 
                ".jsx", ".kt", ".lua", ".m", ".makefile", 
                ".njs", ".pl", ".pas", ".py", ".pyw", 
                ".r", ".R", ".rb", ".rs", ".scala", 
                ".sh", ".swift", ".tcl", ".tsx", ".vb", 
                ".v", ".xml", ".yaml", ".json5", ".ipynb"
            ],
            "bytecode": [
                ".class", ".jar", ".pyo", ".pyc", ".pyd"
            ],
            "windows_exe": ".exe",
            "windows_bat": ".bat",
            "windows_powershell": ".ps1",
            "office": [
                ".doc", ".docx", ".ppt", ".pptx", ".xls", 
                ".xlsx", ".pbix", ".pbit"
            ],
            "media": [
                ".aac", ".avi", ".bmp", ".flac", ".gif", 
                ".gimp", ".jpeg", ".jpg", ".m4a", ".mkv", 
                ".mp3", ".mp4", ".ogg", ".svg", ".tiff", 
                ".wav", ".webm", ".wmv"
            ],
            "fonts": [
                ".dfont", ".eot", ".otf", ".sfnt", ".ttf", 
                ".woff", ".woff2"
            ],
            "other_binary": [
                ".a", ".apk", ".app", ".bin", ".bz2", 
                ".deb", ".dmg", ".dll", ".dex", ".elf", 
                ".gz", ".img", ".iso", ".jar", ".msi", 
                ".msm", ".out", ".o", ".rpm", ".sh", 
                ".sql.gz", ".sqlite", ".sqlite3", ".tar", 
                ".zip", ".xz"
            ]
        }

     # Load JSON data from a file
    @classmethod
    def json_parse(cls, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)
    
    # Dump JSON data into a file
    @classmethod
    def json_dump(cls, file_path: str, data: dict) -> None:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    # Calculate SHA-256 hash of a file
    @classmethod
    def hash_sum(cls, target: str) -> str:
        hash_object = sha256()
        try:
            with open(target, "rb") as f:
                for block in iter(lambda: f.read(1024 * 1024), b""):
                    hash_object.update(block)
        except OSError as e:
            print(f"Error reading file {target}: {e}")
            return "Error"
        return hash_object.hexdigest()

    # Return a tuple with formatted file size
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

    # Format datetime as string
    @classmethod
    def get_fmt_datetime(cls, dt: datetime = datetime.now()) -> str:
        if dt is None:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    # Gather metadata of a file, including hash, permissions, and size
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

class ArqRel:
    # Initialize instance variables
    def __init__(self) -> None:
        self.search_completed: bool = False
        self.cli_verbose_mode: bool = False
        self.starting_dir: Path = None
        self.time_begin: datetime = None
        self.time_finish: datetime = None
        self.time_taken: datetime = None
        self.found_dirs_total = 0
        self.found_files_total: int = 0
        self.found_win_exe: int = 0
        self.found_win_bat: int = 0
        self.found_win_pwshell: int = 0
        self.found_win_office: int = 0
        self.found_media: int = 0
        self.found_sources: int = 0
        self.found_config: int = 0
        self.found_bin_other: int = 0
        self.found_bytecode: int = 0
        self.found_linux_sh: int = 0
        self.found_fonts: int = 0
        self.found_unknown: int = 0
        self.idv_attributes: List[Dict] = []
        self.search_summary: Dict = {}

    # Enabling verbose mode
    def set_cli_verbose_mode(self, val: bool) -> None:
        self.cli_verbose_mode = val

    # Set the starting directory for the search and validate the path
    def set_starting_dir(self, StrPath: str) -> None:
        if not Path(StrPath).exists() or not Path(StrPath).is_dir():
            print("Error - Invalid path.")
            return
        self.starting_dir = Path(StrPath)

    # Create JSON logs for the search
    def create_json_logs(self) -> None:
        now = datetime.now()
        timestamp: str = now.strftime("%Y-%m-%d_%H-%M-%S")
        app_dir: Path = Path(__file__).parent
        logs_dir: Path = app_dir / "logs"
        if not logs_dir.is_dir():
            logs_dir.mkdir()
        this_log_dir: Path = logs_dir / f"{timestamp}"
        this_log_dir.mkdir()
        summary_json: Path = this_log_dir / "summary.json"
        attributes_json: Path = this_log_dir / "attributes.json"
        summary_json.touch()
        attributes_json.touch()
        Utils.json_dump(attributes_json, self.idv_attributes)
        Utils.json_dump(summary_json, self.search_summary)
        print(f"New log created at: {this_log_dir}")

    # Categorize a file based on its extension and count the occurrence
    def _categorize_file(self, file_path: str) -> None:
        name = Path(file_path).name
        extension: str = name[name.rfind(".") + 1:]
        x = f".{extension}"

        if x in Utils.file_extensions["source"]:
            if self.cli_verbose_mode:
                print(f"Found a source code file: '{file_path}'")
            self.found_sources += 1
        elif x in Utils.file_extensions["linux_shell"]:
            if self.cli_verbose_mode:
                print(f"Found a Linux shell script file: '{file_path}'")
            self.found_linux_sh += 1
        elif x == Utils.file_extensions["windows_powershell"]:
            if self.cli_verbose_mode:
                print(f"Found a Windows PowerShell file: '{file_path}'")
            self.found_win_pwshell += 1
        elif x in Utils.file_extensions["other_binary"]:
            if self.cli_verbose_mode:
                print(f"Found a binary file: '{file_path}'")
            self.found_bin_other += 1
        elif x in Utils.file_extensions["bytecode"]:
            if self.cli_verbose_mode:
                print(f"Found a bytecode file: '{file_path}'")
            self.found_bytecode += 1
        elif x in Utils.file_extensions["config"]:
            if self.cli_verbose_mode:
                print(f"Found a config file: '{file_path}'")
            self.found_config += 1
        elif x in Utils.file_extensions["media"]:
            if self.cli_verbose_mode:
                print(f"Found a media file: '{file_path}'")
            self.found_media += 1
        elif x == Utils.file_extensions["windows_exe"]:
            if self.cli_verbose_mode:
                print(f"Found a Windows executable: '{file_path}'")
            self.found_win_exe += 1
        elif x == Utils.file_extensions["windows_bat"]:
            if self.cli_verbose_mode:
                print(f"Found a Windows batch file: '{file_path}'")
            self.found_win_bat += 1
        elif x in Utils.file_extensions["office"]:
            if self.cli_verbose_mode:
                print(f"Found a Microsoft Office file: '{file_path}'")
            self.found_win_office += 1
        elif x in Utils.file_extensions["fonts"]:
            if self.cli_verbose_mode:
                print(f"Found a font file: '{file_path}'")
            self.found_fonts += 1
        else:
            if self.cli_verbose_mode:
                print(f"Found a file with unknown type: '{file_path}'")
            self.found_unknown += 1

    # Format search results
    def _fmt_search_results(self, found_files: List[Path]) -> None:
        print("\nFiles collected: {}".format(len(found_files)))
        self.idv_attributes = [Utils.get_file_metadata(x) for x in found_files]
        self.search_summary = {
            "total_dirs": self.found_dirs_total,
            "total_files": self.found_files_total,
            "source_code": self.found_sources,
            "config": self.found_config,
            "bytecode": self.found_bytecode,
            "linux_shell": self.found_linux_sh,
            "win_exe": self.found_win_exe,
            "win_bat": self.found_win_bat,
            "win_powershell": self.found_win_pwshell,
            "win_office": self.found_win_office,
            "media": self.found_media,
            "fonts": self.found_fonts,
            "bin_other": self.found_bin_other,
            "unknown_file_type": self.found_unknown,
            "start_time": Utils.get_fmt_datetime(self.time_begin),
            "end_time": Utils.get_fmt_datetime(self.time_finish),
            "time_taken": str(self.time_taken),
        }
        pprint.pprint(self.search_summary)
        self.search_completed = True
        self.create_json_logs()

    # Search for files starting from the base directory
    def run_search(self) -> None:
        if self.search_completed:
            print("Error - Search already done for this instance")
            return
        if not self.search_completed:
            search_queue: List[Path] = [self.starting_dir]
            found_files: List[Path] = []
            self.time_begin = datetime.now()
            print("Search started on {}\n".format(Utils.get_fmt_datetime()))

            while search_queue:
                current_dir = search_queue.pop(0)
                if self.cli_verbose_mode:
                    print(f"Searching on '{current_dir}'")
                try:
                    with scandir(current_dir) as it:
                        for entry in it:
                            if entry.is_dir():
                                search_queue.append(entry.path)
                                self.found_dirs_total += 1
                                if self.cli_verbose_mode:
                                    print(f"Found a directory at '{entry.path}'")
                            elif entry.is_file():
                                found_files.append(entry.path)
                                self.found_files_total += 1
                                self._categorize_file(entry.path)
                except OSError as e:
                    print(f"Error accessing directory {current_dir}: {e}")

            self.time_finish = datetime.now()
            self.time_taken = self.time_finish - self.time_begin
            self._fmt_search_results(found_files)

# Program entry
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI")
    parser.add_argument('--path', type=str, required=True, help='Starting directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Activate verbose logs')
    args = parser.parse_args()
    arq_rel = ArqRel()
    if args.verbose:
        arq_rel.set_cli_verbose_mode(True)
    arq_rel.set_starting_dir(args.path)
    arq_rel.run_search()
