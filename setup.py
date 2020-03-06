import os
import sys

python_path = sys.executable
requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")

print("Installing Dependencies...")
os.system("{0} -m pip install -r {1}".format(python_path, requirements_path))

from biometric_easy_installer import main as run_installer
run_installer()
