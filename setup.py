import os

print("Checking Dependencies...")
os.system("python -m pip install -q -r requirements.txt")

from biometric_easy_installer import main as run_installer
run_installer()
