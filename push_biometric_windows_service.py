import time
from pathlib import Path
from SMWinservice import SMWinservice
from push_to_erpnext import main

class PythonCornerExample(SMWinservice):
    _svc_name_ = "ERPNextBiometricPushService"
    _svc_display_name_ = "ERPNext Biometric Push Service"
    _svc_description_ = "Service to push biometric data from device to ERPNext"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        while self.isrunning:
            main()
            time.sleep(5)

if __name__ == '__main__':
    PythonCornerExample.parse_command_line()