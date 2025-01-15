import subprocess
from pathlib import Path
import tomllib as toml

cwd = Path.cwd()
makefile = Path(__file__).resolve().parent / "Makefile"

def build(version):
    # Ensure lib directory exists
    lib_path = Path("librclone/lib")
    lib_path.mkdir(parents=True, exist_ok=True)
    
    # Run make to build librclone.so
    subprocess.check_call([
        "make",
        "-C", cwd,
        "-f", makefile,
        f"VERSION=v{version}",
        "all"])

def get_version_from_pyproject():
    pyproject_path = Path("pyproject.toml")
    pyproject_data = toml.load(pyproject_path.open('rb'))
    return pyproject_data["project"]["version"]

version = get_version_from_pyproject()
build(version)