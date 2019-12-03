# push-biometric-erpnext
Python Script to poll for biometric logs and push to ERPNext via API.

## Instructions to run this script
1. Install python3 and git (please note python 2 is **NOT** supported)
2. Clone this repository using `git clone https://github.com/frappe/push-biometric-erpnext`
3. Setup dependencies using `cd push-biometric-erpnext && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
4. Setup `local_config.py` by making a copy of and renaming `local_config.py.template` file. ([Learn More](#Note-on-setting-up-local-config))
5. Run this script using `python3 push_to_erpnext.py`

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

### Note on setting up local config
- You need to make a copy of `local_config.py.template` file and rename it to `local_config.py`
- Please fill in the relevant sections in this file as per the comments in it.
- Below are the delineation of the keys contained in `local_config.py`:
  - ERPNext Connection Configs:
    - `ERPNEXT_API_KEY`: The API Key of the ERPNext User
    - `ERPNEXT_API_SECRET`: The API Secret of the ERPNext User
      > Please refer to [this link](https://frappe.io/docs/user/en/guides/integration/how_to_set_up_token_based_auth#generate-a-token) to learn how to generate API key and secret for a user in ERPNext. 

      > The ERPNext User who's API key and secret is used, needs to have the following permissions: 

      > 1. Create Permissions for 'Employee Checkin' DocType.

      > 2. Write access to 'Shift Type' DocType.
    - `ERPNEXT_URL`: The web address at which you would access your ERPNext. eg:`'https://yourcompany.erpnext.com'`, `'https://erp.yourcompany.com'`
> TODO: fill this section with more info to help Non-Technical Individuals.

#### Other TODO:
 - Write a setup/auto-install script and ask questions to fill-in/update the `local_config.py` file.
 - Write a dev note on how stuff works in the `push_to_erpnext.py` script?