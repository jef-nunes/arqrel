from pathlib import Path
from os import scandir, stat, name as running_platform
from typing import Dict, List, Tuple
from datetime import datetime
from hashlib import sha256
import argparse
import json
import pprint


class Utils:
    # Extensões de arquivos predefinidas para diferentes categorias
    file_extensions = {
            "config": [
                ".apkproject", ".code-workspace", ".classpath", ".csproj",
                ".csv", ".dat", ".deb", ".editorconfig", ".env", 
                ".git", ".gradle", ".iml", ".ini", ".json", 
                ".makefile", ".pbix", ".pbit", ".properties", 
                ".project", "proto", ".sln", ".toml", ".vscode", ".xml", 
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

    # Carregar dados JSON de um arquivo
    @classmethod
    def json_parse(cls, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)
    
    # Salvar dados JSON em um arquivo
    @classmethod
    def json_dump(cls, file_path: str, data: dict) -> None:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    # Calcular o hash SHA-256 de um arquivo
    @classmethod
    def hash_sum(cls, target: str) -> str:
        hash_object = sha256()
        try:
            with open(target, "rb") as f:
                for block in iter(lambda: f.read(1024 * 1024), b""):
                    hash_object.update(block)
        except OSError as e:
            print(f"Erro ao ler o arquivo {target}: {e}")
            return "Erro"
        return hash_object.hexdigest()

    # Retornar uma tupla com o tamanho do arquivo formatado
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

    # Formatar data/hora como string
    @classmethod
    def get_fmt_datetime(cls, dt: datetime = datetime.now()) -> str:
        if dt is None:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    # Recolher metadados de um arquivo, incluindo hash, permissões e tamanho
    @classmethod
    def get_file_metadata(cls, file_path: str) -> Dict[str, any]:
        _stat = stat(file_path)
        _creation_time: str
        if running_platform == "posix":
            _creation_time = "?"
        elif running_platform == "nt":
            _creation_time = cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_birthtime))
        metadata: Dict = {
            "name": Path(file_path).name,
            "size_bytes": _stat.st_size,
            "permissions": oct(_stat.st_mode & 0o777),
            "creation_time": _creation_time,
            "last_access_time": cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_atime)),
            "last_modify_time": cls.get_fmt_datetime(datetime.fromtimestamp(_stat.st_mtime))
        }
        size_value, size_unit = cls.get_fmt_size_tuple(file_path)
        last_dot_index: int = str(metadata["name"]).rfind(".")
        extension = metadata["name"][last_dot_index+1:] if "." in metadata["name"] else "?"
        metadata["extension"] = extension 
        metadata["size_fmt"] = f"{round(size_value, 2)} {size_unit}"
        metadata["hash"] = cls.hash_sum(file_path)
        metadata["path_absolute"] = str(Path(file_path).resolve())
        return metadata

class ArqRel:
    # Inicializa as variáveis de instância
    def __init__(self) -> None:
        self.busca_terminada: bool = False
        self.logs_de_terminal: bool = False
        self.diretorio_inicial: Path = None
        self.tempo_inicio: datetime = None
        self.tempo_fim: datetime = None
        self.tempo_total: datetime = None
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
        self.idv_atributos: List[Dict] = []
        self.search_estatisticas: Dict = {}

    # Ativar o modo verbose
    def set_logs_terminal(self, val: bool) -> None:
        self.logs_de_terminal = val

    # Definir o diretório de início para a busca e validar o caminho
    def set_diretorio_inicial(self, StrPath: str) -> None:
        if not Path(StrPath).exists() or not Path(StrPath).is_dir():
            print("Erro - Caminho inválido.")
            return
        self.diretorio_inicial = Path(StrPath)

    # Criar logs em JSON para a busca
    def salvar_resultados(self) -> None:
        now = datetime.now()
        timestamp: str = now.strftime("%Y-%m-%d_%H-%M-%S")
        BASE_DIR: Path = Path(__file__).parent
        dir_resultados: Path = BASE_DIR / "logs"
        if not dir_resultados.is_dir():
            dir_resultados.mkdir()
        dir_este_resultado: Path = dir_resultados / f"{timestamp}"
        dir_este_resultado.mkdir()
        estatisticas_json: Path = dir_este_resultado / "estatisticas.json"
        atributos_json: Path = dir_este_resultado / "atributos.json"
        estatisticas_json.touch()
        atributos_json.touch()
        Utils.json_dump(atributos_json, self.idv_atributos)
        Utils.json_dump(estatisticas_json, self.search_estatisticas)
        print(f"Novo log criado em: {dir_este_resultado}")

    # Categorizar um arquivo com base na sua extensão e contar as ocorrências
    def _categorizar_arquivo(self, file_path: str) -> None:
        name = Path(file_path).name
        extension: str = name[name.rfind(".") + 1:]
        x = f".{extension}"

        if x in Utils.file_extensions["source"]:
            if self.logs_de_terminal:
                print(f"Arquivo de código fonte encontrado: '{file_path}'")
            self.found_sources += 1
        elif x in Utils.file_extensions["linux_shell"]:
            if self.logs_de_terminal:
                print(f"Arquivo de script Linux encontrado: '{file_path}'")
            self.found_linux_sh += 1
        elif x == Utils.file_extensions["windows_powershell"]:
            if self.logs_de_terminal:
                print(f"Arquivo PowerShell do Windows encontrado: '{file_path}'")
            self.found_win_pwshell += 1
        elif x in Utils.file_extensions["other_binary"]:
            if self.logs_de_terminal:
                print(f"Arquivo binário encontrado: '{file_path}'")
            self.found_bin_other += 1
        elif x in Utils.file_extensions["bytecode"]:
            if self.logs_de_terminal:
                print(f"Arquivo de bytecode encontrado: '{file_path}'")
            self.found_bytecode += 1
        elif x in Utils.file_extensions["config"]:
            if self.logs_de_terminal:
                print(f"Arquivo de configuração encontrado: '{file_path}'")
            self.found_config += 1
        elif x in Utils.file_extensions["media"]:
            if self.logs_de_terminal:
                print(f"Arquivo de mídia encontrado: '{file_path}'")
            self.found_media += 1
        elif x == Utils.file_extensions["windows_exe"]:
            if self.logs_de_terminal:
                print(f"Executável do Windows encontrado: '{file_path}'")
            self.found_win_exe += 1
        elif x == Utils.file_extensions["windows_bat"]:
            if self.logs_de_terminal:
                print(f"Arquivo batch do Windows encontrado: '{file_path}'")
            self.found_win_bat += 1
        elif x in Utils.file_extensions["office"]:
            if self.logs_de_terminal:
                print(f"Arquivo Microsoft Office encontrado: '{file_path}'")
            self.found_win_office += 1
        elif x in Utils.file_extensions["fonts"]:
            if self.logs_de_terminal:
                print(f"Arquivo de fonte encontrado: '{file_path}'")
            self.found_fonts += 1
        else:
            if self.logs_de_terminal:
                print(f"Arquivo com tipo desconhecido encontrado: '{file_path}'")
            self.found_unknown += 1

    # Formatar os resultados da busca
    def _fmt_search_results(self, found_files: List[Path]) -> None:
        print("\nArquivos coletados: {}".format(len(found_files)))
        self.idv_atributos = [Utils.get_file_metadata(x) for x in found_files]
        self.search_estatisticas = {
            "total_dirs": self.found_dirs_total,
            "total_arquivos": self.found_files_total,
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
            "tempo_inicio": Utils.get_fmt_datetime(self.tempo_inicio),
            "tempo_fim": Utils.get_fmt_datetime(self.tempo_fim),
            "tempo_total": str(self.tempo_total),
        }
        pprint.pprint(self.search_estatisticas)
        self.busca_terminada = True
        self.salvar_resultados()

    # Realizar a busca de arquivos a partir do diretório base
    def entrada(self) -> None:
        if self.busca_terminada:
            print("Erro - A busca já foi concluída para esta instância")
            return
        if not self.busca_terminada:
            search_queue: List[Path] = [self.diretorio_inicial]
            found_files: List[Path] = []
            self.tempo_inicio = datetime.now()
            print("Busca iniciada em {}\n".format(Utils.get_fmt_datetime()))

            while search_queue:
                current_dir = search_queue.pop(0)
                if self.logs_de_terminal:
                    print(f"Buscando em '{current_dir}'")
                try:
                    with scandir(current_dir) as it:
                        for entry in it:
                            if entry.is_dir():
                                search_queue.append(entry.path)
                                self.found_dirs_total += 1
                                if self.logs_de_terminal:
                                    print(f"Diretório encontrado em '{entry.path}'")
                            elif entry.is_file():
                                found_files.append(entry.path)
                                self.found_files_total += 1
                                self._categorizar_arquivo(entry.path)
                except OSError as e:
                    print(f"Erro ao acessar o diretório {current_dir}: {e}")

            self.tempo_fim = datetime.now()
            self.tempo_total = self.tempo_fim - self.tempo_inicio
            self._fmt_search_results(found_files)

# Entrada do programa
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI")
    parser.add_argument('--path', type=str, required=True, help='Caminho do diretório inicial')
    parser.add_argument('-v', '--verbose', action='store_true', help='Ativar logs detalhados')
    args = parser.parse_args()
    arq_rel = ArqRel()
    if args.verbose:
        arq_rel.set_logs_terminal(True)
    arq_rel.set_diretorio_inicial(args.path)
    arq_rel.entrada()
