
# ERPNext related configs
ERPNEXT_API_KEY = ''
ERPNEXT_API_SECRET = ''
ERPNEXT_URL = 'http://dev.local:8000'


# operational configs
PULL_FREQUENCY = 60 # in minutes


# Biometric device configs
    #- device_id - must be unique, strictly alphanumerical chars only. no space allowed.
    #- ip - device IP Address
    #- punch_direction - IN/OUT
devices = [
    {'device_id':'test_1','ip':'192.168.0.209', 'punch_direction': None},
    {'device_id':'test_2','ip':'192.168.2.209', 'punch_direction': None}
]