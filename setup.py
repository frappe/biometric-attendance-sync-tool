import os

print("Installing Dependencies...")
os.system('python -m pip install -r requirements.txt')
from biometric_easy_installer import main as run_installer
run_installer()
