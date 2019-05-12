# push-biometric-erpnext
Python Script to poll for Bio-metric Attendance and push to ERPNext via API

## Instructions to run this script
1. Install python3.7 and git
2. Clone `pyzk` library using `git clone https://github.com/karthikeyan5/pyzk`
3. Clone this repository using `git clone https://github.com/karthikeyan5/push-biometric-erpnext`
4. Setup `local_config.py` from `local_config.py.template` file
5. Run this script using `python push_to_erpnext.py`

## Installing as a windows service
1. Install pywin32 using `pip install pywin32`
2. Got to this repository's Directory
3. Install the windows service using `python push_biometric_windows_service.py install`
4. Done

#### Update the installed windows service
> python push_biometric_windows_service.py update

#### Stop the windows service
> net stop ERPNextBiometricPushService

#### To see the status of the service
> mmc Services.msc

