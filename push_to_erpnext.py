
import local_config as config
import requests
import datetime
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from zk import ZK, const



def pull_process_and_push_data(device):
    """ takes a single device config as param and pulls data from that device.

    """
    attendance_success_log_file = '_'.join(["attendance_success_log",device['device_id']])
    attendance_failed_log_file = '_'.join(["attendance_failed_log",device['device_id']])
    attendance_success_logger = setup_logger(attendance_success_log_file, attendance_success_log_file+'.log')
    attendance_failed_logger = setup_logger(attendance_failed_log_file, attendance_failed_log_file+'.log')
    device_attendance_logs = get_all_attendance_from_device(device['ip'])

    index_of_last = -1
    last_line = get_last_line_from_file(attendance_success_log_file+'.log')
    if last_line:
        last_uid,last_timestamp = last_line.split("\t")[4:6]
        for i,x in enumerate(device_attendance_logs):
            if last_uid == str(x['uid']) and datetime.datetime.fromtimestamp(float(last_timestamp)) == x['timestamp']:
                index_of_last = i

    for device_attendance_log in device_attendance_logs[index_of_last+1:]:
        erpnext_status_code, erpnext_message = send_to_erpnext(device_attendance_log['uid'],device_attendance_log['timestamp'],device['device_id'],device['punch_direction'])
        if erpnext_status_code == 200:
            attendance_success_logger.info("\t".join([erpnext_message,device_attendance_log['user_id'],
                str(device_attendance_log['uid']),str(device_attendance_log['timestamp'].timestamp()),str(device_attendance_log['punch']),str(device_attendance_log['status'])]))
        else:
            attendance_failed_logger.error("\t".join([str(erpnext_status_code),device_attendance_log['user_id'],
                str(device_attendance_log['uid']),str(device_attendance_log['timestamp'].timestamp()),str(device_attendance_log['punch']),str(device_attendance_log['status'])]))


def get_all_attendance_from_device(ip, port=4370, timeout=30):
    return [{'punch': 255, 'user_id': '22', 'uid': 12349, 'status': 1, 'timestamp': datetime.datetime(2019, 2, 26, 20, 31, 29)},{'punch': 255, 'user_id': '7', 'uid': 7, 'status': 1, 'timestamp': datetime.datetime(2019, 2, 26, 20, 31, 36)}]
    zk = ZK(ip, port=port, timeout=timeout)
    conn = None
    attendances = []
    try:
        conn = zk.connect()
        x = conn.disable_device()
        info_logger.info("\t".join(("Device Disable Attempted:",str(x))))
        attendances = conn.get_attendance()
        info_logger.info("\t".join(("Attendanced Fetched:",str(len(attendances)))))
        x = conn.enable_device()
        info_logger.info("\t".join(("Device Enable Attempted:",str(x))))
    except:
        error_logger.exception('error when fetching from device...')
    finally:
        if conn:
            conn.disconnect()
    return attendances


def send_to_erpnext(biometric_rf_id, timestamp, device_id=None, log_type=None):
    url = config.ERPNEXT_URL + "/api/method/erpnext.hr.doctype.employee_attendance_log.employee_attendance_log.add_log_based_on_biometric_rf_id"
    headers = {
        'Authorization': "token "+ config.ERPNEXT_API_KEY + ":" + config.ERPNEXT_API_SECRET,
        'Accept': 'application/json'
    }
    data = {
        'biometric_rf_id' : biometric_rf_id,
        'timestamp' : timestamp.__str__(),
        'device_id' : device_id,
        'log_type' : log_type
    }
    response = requests.request("GET", url, headers=headers, data=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['message']['name']
    else:
        if "No Employee found for the given 'biometric_rf_id'" in json.loads(json.loads(response._content)['exc'])[0]:
            error_logger.error('\t'.join(['Error during ERPNext API Call.',str(biometric_rf_id),str(timestamp.timestamp()),str(device_id),str(log_type),"No Employee found for the given 'biometric_rf_id'"]))
            # send email?
        else:
            error_logger.error('\t'.join(['Error during ERPNext API Call.',str(biometric_rf_id),str(timestamp.timestamp()),str(device_id),str(log_type),json.loads(json.loads(response._content)['exc'])[0]]))
        return response.status_code, json.loads(json.loads(response._content)['exc'])[0]


def get_last_line_from_file(file):
    line = None
    if os.stat(file).st_size < 2000:
        with open(file, 'r') as f:
            for line in f:
                pass
    else:
        with open(file, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR) 
            line = f.readline().decode()
    return line


def setup_logger(name, log_file, level=logging.INFO, formatter=None):

    if not formatter:
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=50)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

error_logger = setup_logger('error_logger', 'error.log',logging.ERROR)
info_logger = setup_logger('info_logger','logs.log')
