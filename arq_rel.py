from datetime import datetime
from pathlib import Path
from os import listdir
from typing import Dict, List
from utils import Utils
import argparse

class ArqRel():
    search_completed: bool
    verbose_logs: bool
    auto_create_json: bool
    summary_only: bool
    time_begin: datetime
    time_finish: datetime
    time_taken: datetime
    starting_dir: Path
    found_files_total: int
    found_dirs_total: int
    found_win_exe: int
    found_win_bat: int
    found_win_office: int
    found_media: int
    found_sources: int
    found_config: int
    found_bytecode: int
    found_bin_other: int
    list_files_metadata: List[Dict]
    summary: dict

    def __init__(self) -> None:
        self.search_completed = False
        self.verbose_logs = True
        self.auto_create_json = True
        self.starting_dir = None
        self.time_begin = None
        self.time_finish = None
        self.time_taken = None
        self.found_dirs_total = 0
        self.found_files_total = 0
        self.found_win_exe = 0
        self.found_win_bat = 0
        self.found_win_pwshell = 0
        self.found_win_office = 0
        self.found_media = 0
        self.found_sources = 0
        self.found_config = 0
        self.found_bin_other = 0
        self.found_bytecode = 0
        self.found_linux_sh = 0
        self.data_from_search = []
        self.summary = {}
        self.summary_only = False

    def set_summary_only(self, val: bool) -> None:
        self.summary_only = True

    def set_verbose_logs(self, val: bool) -> None:
        self.verbose_logs = val
    
    def set_auto_create_json(self, val: bool) -> None:
        self.auto_create_json = val

    def get_starting_dir(self) -> Path | None:
        return self.starting_dir

    def set_starting_dir(self, StrPath: str) -> None:
        if not Path(StrPath).exists() or not Path(StrPath).is_dir():
            print("Error - Invalid path.")
            return
        self.starting_dir = Path(StrPath)

    def create_json_relatory_file(self) -> None:
        app_dir = Path(__file__).parent
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        relatory_name = f"arq-rel_{timestamp}.json"
        relatory_path = app_dir / relatory_name
        relatory_path.touch()
        if self.summary_only:
            _dump = {
            "summary": self.summary
            }
        else:
            _dump = {
                "summary": self.summary,
                "individual_results": self.list_files_metadata
                }
        Utils.json_dump(relatory_path, _dump)
        print(f"New relatory created: {relatory_name}")

    def run_new_search(self) -> None:     
        search_queue: List[Path] = [self.starting_dir]
        found_files: List[Path] = []
        self.time_begin = datetime.now()
        print("Search started on {}\n".format(Utils.get_fmt_datetime()))
        
        while search_queue:
            current_dir = search_queue.pop(0)
            if self.verbose_logs:
                print("Searching on \'{}\'".format(current_dir))
            try:
                for element in listdir(current_dir):
                    element_abs_path = Path(current_dir) / element
                    if element_abs_path.is_dir():
                        search_queue.append(element_abs_path)
                        self.found_dirs_total += 1
                        if self.verbose_logs:
                            print("Found a directory at \'{}\'".format(element_abs_path))
                    else:
                        found_files.append(element_abs_path)
                        self.found_files_total += 1
                        name = element_abs_path.name
                        extension: str = "?"
                        if name.find(".") != -1:
                            last_dot_index = name.rfind(".")
                            extension = name[last_dot_index + 1:]

                        if extension != "?":
                            x = f".{extension}"
                            if x in Utils.source_extensions:
                                print("Found a source code file: \'{}\'".format(element_abs_path))
                                self.found_sources += 1
                            elif x in Utils.linux_shell_extensions:
                                if self.verbose_logs:
                                    print("Found a Linux shell script file: \'{}\'".format(element_abs_path))
                                    self.found_linux_sh += 1
                            elif x in Utils.win_pwshell_extension:
                                if self.verbose_logs:
                                    print("Found a Windows PowerShell file: \'{}\'".format(element_abs_path))
                                    self.found_win_pwshell += 1
                            elif x in Utils.other_bin_extensions:
                                if self.verbose_logs:
                                    print("Found a binary file: \'{}\'".format(element_abs_path))
                                    self.found_bin_other += 1
                            elif x in Utils.bytecode_extensions:
                                if self.verbose_logs:
                                    print("Found a bytecode file: \'{}\'".format(element_abs_path))
                                    self.found_bytecode += 1
                            elif x in Utils.config_extensions:
                                if self.verbose_logs:
                                    print("Found a config file: \'{}\'".format(element_abs_path))
                                    self.found_config += 1
                            elif x in Utils.media_extensions:
                                if self.verbose_logs:
                                    print("Found a media file: \'{}\'".format(element_abs_path))
                                    self.found_media += 1
                            elif x == Utils.win_exe_extension:
                                if self.verbose_logs:
                                    print("Found a Windows executable: \'{}\'".format(element_abs_path))
                                    self.found_win_exe += 1
                            elif x == Utils.win_bat_extension:
                                if self.verbose_logs:
                                    print("Found a Windows batch file: \'{}\'".format(element_abs_path))
                                    self.found_win_bat += 1
                            elif x in Utils.win_office_extensions:
                                if self.verbose_logs:
                                    print("Found a Microsoft Office file: \'{}\'".format(element_abs_path))
                                    self.found_win_office += 1
                            else:
                                print("Found file \'{}\' with unknown type".format(element_abs_path))
            except Exception as e:
                print(f"Error accessing directory {current_dir}: {e}")

        self.time_finish = datetime.now()
        self.time_taken = self.time_begin - self.time_finish
        print("Search finished on {}\n".format(Utils.get_fmt_datetime()))

        self.list_files_metadata = [Utils.get_file_metadata(file_path) for file_path in found_files]
        self.summary = \
            {
            "base_dir": str(self.starting_dir),
            "time_begin": str(self.time_begin),
            "time_finish": str(self.time_finish),
            "time_taken": str(self.time_taken),
            "found_directories": self.found_dirs_total,
            "found_files":{
            "total": self.found_files_total,
            "by_type":  {
                "linux_shell": self.found_linux_sh,
                "win_executable": self.found_win_exe,
                "win_bat": self.found_win_bat,
                "win_powershell": self.found_win_pwshell,
                "win_office": self.found_win_office,
                "media": self.found_media,
                "source_code": self.found_sources,
                "bytecode": self.found_bytecode,
                "config": self.found_config,
                "other_bin": self.found_bin_other
                 }
                }
            }
        self.search_completed = True

        if self.auto_create_json:
            self.create_json_relatory_file()

def main():
    rel = ArqRel()
    
    parser = argparse.ArgumentParser(description="CLI")
    parser.add_argument('--path', type=str, required=True, help='Starting directory path')
    parser.add_argument('--summary', action='store_true', help='Creates summary only')
    parser.add_argument('-v', '--verbose', action='store_true', help='Activate verbose logs')
    parser.add_argument('-s', '--silent', action='store_true', help='Deactivate verbose logs')
    args = parser.parse_args()
    
    if args.summary:
        rel.set_summary_only(True)

    if args.verbose:
        rel.set_verbose_logs(True)

    if args.silent:
        rel.set_verbose_logs(False)

    if Path(args.path.strip()).exists():
        rel.set_starting_dir(args.path.strip())
    else:
        print("Error - Invalid path.")
        exit(1)

    if rel.get_starting_dir() is not None:
        rel.run_new_search()
        if rel.search_completed and not rel.auto_create_json:
            answer = input("Create a formatted JSON relatory? [Y/N] ").strip().upper()
            if answer == "Y":
                rel.create_json_relatory_file()
    else:
        print("Error - Could not resolve starting path.")
        exit(1)

    print("End")

if __name__ == "__main__":
    main()
