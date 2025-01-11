import os, platform
from .logging import error, hint

from pathlib import Path
try:
    from prompt_toolkit.styles import Style
except ModuleNotFoundError:
    error("missing dependencies detected: if you are running in a virtual environment on linux, make sure that environment has all dependencies satisfied every time you run.")
    hint("you can install all dependencies using bucket dep install")
    hint("make sure you have bkt installed (pipx install bkt)")
    exit(1)

DIR: Path = Path(__file__).parent
STORAGE_PATH: Path = DIR / "storage"
PLUGINS_PATH: Path = DIR / "plugins"
SYS_ROOT: str = os.path.abspath(os.sep)
EP_MODULE: str = str(DIR).removeprefix(SYS_ROOT).replace("\\", "/").replace("/", ".")
PLATFORM: str = platform.system().lower()
STYLE = Style.from_dict({
    'yellow': 'bold fg:yellow',
    'magenta': 'fg:magenta',
    'blue': 'bold fg:blue',
    'reset': '',
})
META_JSON_FRAME: str = """
{
    "cmd_history": [],
    "cd_history": [],
    "aliases": {},
    "props": {},
    "last_location": "",
    "scs": [],
    "times_logged_on": 0
}
""".strip()