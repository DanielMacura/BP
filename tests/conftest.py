import sys
from pathlib import Path

# Get the parent directory of the current file (which is the tests directory)
# and append the src directory to sys.path
src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

