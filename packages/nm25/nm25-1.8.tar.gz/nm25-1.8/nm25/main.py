from pathlib import Path
from pyperclip import copy
from IPython.core.getipython import get_ipython


def _create_new_cell(contents):
    shell = get_ipython()

    payload = dict(
        source="set_next_input",
        text=contents,
        replace=False,
    )
    shell.payload_manager.write_payload(payload, single=False)


def _name_sort(name):
    nn = [""]
    for i in name + " ":
        if i.isdigit() != nn[-1].isdigit():
            if nn[-1].isdigit():
                nn[-1] = int(nn[-1])
            nn.append("")
        nn[-1] = nn[-1] + i
    return nn


def chis():
    get_ipython().history_manager.reset()


class FO:
    """
    File ojbect
    """

    def __init__(self, path: Path):
        self.name = path.stem
        self.d = path.read_text(encoding="utf-8").splitlines()[0].strip("# ")
        self.path = path

    def __repr__(self):
        copy(self.path.read_text(encoding="utf-8"))
        return ""

    def __call__(self):
        _create_new_cell(self.path.read_text(encoding="utf-8"))
        chis()


class DO:
    """
    Dir object
    """

    def __init__(self, folder):
        self.folder = Path(folder)
        self.files = {}
        for file in self.folder.iterdir():
            self.files[file.stem] = file

    @property
    def d(self):
        names = sorted(self.files.keys(), key=_name_sort)

        def get_name(path):
            if path.is_file():
                return " - " + FO(path).d
            return ""

        print("\n".join([f"{name}{get_name(self.files[name])}" for name in names]))

    def __getattr__(self, name):
        if name in self.files:
            if self.files[name].is_dir():
                return DO(self.files[name])
            return FO(self.files[name])

    def __repr__(self):
        return ""
