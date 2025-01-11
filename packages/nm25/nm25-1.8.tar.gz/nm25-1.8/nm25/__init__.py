from .main import DO
from pathlib import Path

__path = Path(__file__).parent / "data"

l = DO(__path)