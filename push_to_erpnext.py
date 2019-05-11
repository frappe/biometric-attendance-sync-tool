
import local_config as config
import requests
import datetime
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from zk import ZK, const


# concerns to address(may be much later):
    # how will last line lookup work with log rotation when new file is created? 
        #- will that new fill be empty at any time? or will it have a partial line from the previous line?

# possible area of further developemt
    # Real-time events - setup getting events pushed from the machine rather then polling. 
        #- this is documented as 'Real-time events' in the ZKProtocol manual.

def main():
    last_line = get_last_line_from_file('/'.join([config.LOGS_DIRECTORY,'logs.log']))
    if last_line and datetime.datetime.strptime(last_line.split(',')[0], "%Y-%m-%d %H:%M:%S") < datetime.datetime.now() - datetime.timedelta(minutes = config.PULL_FREQUENCY):
        info_logger.info("Cleared for lift off!")
        for device in config.devices:
            device_attendance_logs = None
            info_logger.info("Started Device: "+ device['device_id'])
            dump_file = config.LOGS_DIRECTORY+'/'+device['ip'].replace('.','_')+'_last_fetch_dump.json'
            if os.path.exists(dump_file):
                error_logger.error('Device Attendance Dump Found in Log Directory. This can mean the program crashed unexpectedly. Retrying with dumped data.')
                with open(dump_file,'r') as f:
                    device_attendance_logs = list(map(lambda x:_apply_function_to_key(x,'timestamp',datetime.datetime.fromtimestamp), json.loads(f.read())))
            try:
                pull_process_and_push_data(device,device_attendance_logs)
                if os.path.exists(dump_file):
                    os.remove(dump_file)
                info_logger.info("Successfully processed Device: "+ device['device_id'])
            except:
                error_logger.exception('exception when calling pull_process_and_push_data function for device'+json.dumps(device,default=str))
        info_logger.info("Mission Accomplished!")


def pull_process_and_push_data(device, device_attendance_logs=None):
    """ takes a single device config as param and pulls data from that device.

    """
    attendance_success_log_file = '_'.join(["attendance_success_log",device['device_id']])
    attendance_failed_log_file = '_'.join(["attendance_failed_log",device['device_id']])
    attendance_success_logger = setup_logger(attendance_success_log_file, '/'.join([config.LOGS_DIRECTORY,attendance_success_log_file])+'.log')
    attendance_failed_logger = setup_logger(attendance_failed_log_file, '/'.join([config.LOGS_DIRECTORY,attendance_failed_log_file])+'.log')
    if not device_attendance_logs:
        device_attendance_logs = get_all_attendance_from_device(device['ip'],clear_from_device_on_fetch=device['clear_from_device_on_fetch'])

    index_of_last = -1
    last_line = get_last_line_from_file('/'.join([config.LOGS_DIRECTORY,attendance_success_log_file])+'.log')
    if last_line:
        last_uid,last_timestamp = last_line.split("\t")[4:6]
        for i,x in enumerate(device_attendance_logs):
            if last_uid == str(x['uid']) and datetime.datetime.fromtimestamp(float(last_timestamp)) == x['timestamp']:
                index_of_last = i

    for device_attendance_log in device_attendance_logs[index_of_last+1:]:
        erpnext_status_code, erpnext_message = send_to_erpnext(device_attendance_log['uid'],device_attendance_log['timestamp'],device['device_id'],device['punch_direction'])
        if erpnext_status_code == 200:
            attendance_success_logger.info("\t".join([erpnext_message,device_attendance_log['user_id'],
                str(device_attendance_log['uid']),str(device_attendance_log['timestamp'].timestamp()),
                str(device_attendance_log['punch']),str(device_attendance_log['status']),
                json.dumps(device_attendance_log,default=str)]))
        else:
            attendance_failed_logger.error("\t".join([str(erpnext_status_code),device_attendance_log['user_id'],
                str(device_attendance_log['uid']),str(device_attendance_log['timestamp'].timestamp()),
                str(device_attendance_log['punch']),str(device_attendance_log['status']),
                json.dumps(device_attendance_log,default=str)]))
            raise Exception('API Call to ERPNext Failed.')


def get_all_attendance_from_device(ip, port=4370, timeout=30, clear_from_device_on_fetch=False):
    #  Sample Attendance Logs [{'punch': 255, 'user_id': '22', 'uid': 12349, 'status': 1, 'timestamp': datetime.datetime(2019, 2, 26, 20, 31, 29)},{'punch': 255, 'user_id': '7', 'uid': 7, 'status': 1, 'timestamp': datetime.datetime(2019, 2, 26, 20, 31, 36)}]
    zk = ZK(ip, port=port, timeout=timeout)
    conn = None
    attendances = []
    try:
        conn = zk.connect()
        x = conn.disable_device()
        info_logger.info("\t".join(("Device Disable Attempted. Result:",str(x))))
        attendances = conn.get_attendance()
        info_logger.info("\t".join(("Attendances Fetched:",str(len(attendances)))))
        if len(attendances):
            # keeping a backup before clearing data in case the programs fails. 
            # if every thing goes well then this file is removed automatically at the end.
            with open(config.LOGS_DIRECTORY+'/'+ip.replace('.','_')+'_last_fetch_dump.json', 'w+') as f:
                f.write(json.dumps(attendances,default=datetime.datetime.timestamp))
            if clear_from_device_on_fetch:
                x = conn.clear_attendance()
                info_logger.info("\t".join(("Attendance Clear Attempted. Result:",str(x))))
        x = conn.enable_device()
        info_logger.info("\t".join(("Device Enable Attempted. Result:",str(x))))
    except:
        error_logger.exception('exception when fetching from device...')
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
            #todo: send email?
        else:
            error_logger.error('\t'.join(['Error during ERPNext API Call.',str(biometric_rf_id),str(timestamp.timestamp()),str(device_id),str(log_type),json.loads(json.loads(response._content)['exc'])[0]]))
        return response.status_code, json.loads(json.loads(response._content)['exc'])[0]


def get_last_line_from_file(file):
    line = None
    if os.stat(file).st_size < 5000:
        # quick hack to handle files with one line
        with open(file, 'r') as f:
            for line in f:
                pass
    else:
        # optimized for large log files
        with open(file, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR) 
            line = f.readline().decode()
    return line


def setup_logger(name, log_file, level=logging.INFO, formatter=None):

    if not formatter:
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=50)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger


def _apply_function_to_key(obj,key,fn):
    obj[key] = fn(obj[key])
    return obj

if not os.path.exists(config.LOGS_DIRECTORY):
    os.makedirs(config.LOGS_DIRECTORY)
error_logger = setup_logger('error_logger', '/'.join([config.LOGS_DIRECTORY,'error.log']),logging.ERROR)
info_logger = setup_logger('info_logger','/'.join([config.LOGS_DIRECTORY,'logs.log']))

