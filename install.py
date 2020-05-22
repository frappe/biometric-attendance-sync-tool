import os

print("Checking Dependencies...")
os.system("python -m pip install -q -r requirements.txt")

from gui import setup_window
setup_window()
