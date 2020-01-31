import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QIntValidator, QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp
import os, json

class BiometricEasyInstaller(QMainWindow):

	def __init__(self):
		super().__init__()
		self.reg_exp_for_ip = "((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?=\s*netmask)"
		self.init_ui()

	def init_ui(self):
		self.counter = 0
		self.setup_window()
		self.setup_textboxes_and_label()
		self.center()
		self.show()

	def setup_window(self):
		self.setGeometry(0, 0, 500, 700)
		self.setWindowTitle('ERPNext Biometric Service')

	def setup_textboxes_and_label(self):

		self.create_label("API Secret", "api_secret", 20, 0, 200, 30)
		self.create_field("textbox_erpnext_api_secret", 20, 30, 200, 30)

		self.create_label("API Key", "api_key", 20, 60, 200, 30)
		self.create_field("textbox_erpnext_api_key", 20, 90, 200, 30)

		self.create_label("ERPNext URL", "erpnext_url", 250, 0, 200, 30)
		self.create_field("textbox_erpnext_url", 250, 30, 200, 30)

		self.create_label("Pull Frequency(In Minutes)", "pull_frequency", 250, 60, 200, 30)
		self.create_field("textbox_pull_frequency", 250, 90, 200, 30)

		#validating integer
		self.onlyInt = QIntValidator(10, 30)
		self.textbox_pull_frequency.setValidator(self.onlyInt)

		self.create_label("Import start date", "import_start_date", 250, 120, 200, 30)
		self.create_field("textbox_import_start_date", 250, 150, 200, 30)
		self.validate_data("^\d{1,2}\/\d{1,2}\/\d{4}$", "textbox_import_start_date")

		self.create_label("Device ID", "device_id", 20, 260, 0, 0)
		self.create_label("Device IP", "device_ip", 150, 260, 0, 0)
		self.create_label("Shift", "shift", 320, 260, 0, 0)	

		# First Row for table
		self.create_field("device_id_0", 20, 290, 150, 30)
		self.create_field("device_ip_0", 150, 290, 150, 30)
		self.validate_data(self.reg_exp_for_ip, "device_ip_0")
		self.create_field("shift_0", 300, 290, 150, 30)

		#Actions buttons
		self.create_button('Add', 20, 230, 130, 30, self.add_devices_fields)
		self.create_button('Remove', 320, 230, 130, 30, self.remove_devices_fields)
		self.create_button('Set Configuration', 20, 500, 130, 30, self.setup_local_config)
		self.create_button('Start Service', 320, 500, 130, 30, self.integrate_biometric)

	# Widgets Genrators
	def create_label(self, label_text, label_name, x, y, height, width):
		setattr(self,  label_name, QLabel(self))
		label  = getattr(self, label_name)
		label.move(x, y)
		label.setText(label_text)
		if height and width:
			label.resize(height, width)
		label.show()

	def create_field(self, field_name, x, y, height, width):
		setattr(self,  field_name, QLineEdit(self))
		field  = getattr(self, field_name)
		field.move(x, y)
		field.resize(height, width)
		field.show()

	def create_button(self, button_name, x, y , height, width, callback_function):
		setattr(self,  button_name, QPushButton(button_name, self))
		button = getattr(self, button_name)
		button.move(x, y)
		button.resize(height, width)
		button.clicked.connect(callback_function)

	def center(self):
		frame = self.frameGeometry()
		screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
		centerPoint = QApplication.desktop().screenGeometry(screen).center()
		frame.moveCenter(centerPoint)
		self.move(frame.topLeft())

	def add_devices_fields(self):
		if self.counter < 5:
			self.counter += 1
			self.create_field("device_id_" + str(self.counter), 20, 290+(self.counter * 30), 150, 30)
			self.create_field("device_ip_" + str(self.counter), 150, 290+(self.counter * 30), 150, 30)
			self.validate_data(self.reg_exp_for_ip, "device_ip_" + str(self.counter))
			self.create_field("shift_" + str(self.counter), 300, 290+(self.counter * 30), 150, 30)

	# data validator
	def validate_data(self, reg_exp, field_name):
		field = getattr(self, field_name)
		reg_ex = QRegExp(reg_exp)
		input_validator = QRegExpValidator(reg_ex, field)
		field.setValidator(input_validator)


	def remove_devices_fields(self):
		if self.counter > 0:
			b  = getattr(self, "shift_" + str(self.counter))
			b.deleteLater()
			b  = getattr(self, "device_id_" + str(self.counter))
			b.deleteLater()
			b  = getattr(self, "device_ip_" + str(self.counter))
			b.deleteLater()

			self.counter -=1

	def integrate_biometric(self):
		self.close()
		print("Starting Service...")
		start_service_command = 'python -c "from push_to_erpnext import infinite_loop; infinite_loop()"'
		os.system(start_service_command)
		
	def setup_local_config(self):
		print("Installing Dependencies...")
		print('Done')
		print("Setting Local Configuration...")
		if os.path.exists("local_config.py"):
			os.remove("local_config.py")

		local_config_py = open("local_config.py", 'w+')

		config = self.get_local_config()

		local_config_py.write(config)

		print("Local Configuration Updated.")

	def get_device_details(self):
		devices = []
		shifts = []
		for idx in range(0, self.counter+1):
			devices.append({'device_id':getattr(self, "device_id_" + str(idx)).text(),
				'ip':getattr(self, "device_id_" + str(idx)).text(),
				'punch_direction': '',
				'clear_from_device_on_fetch': ''})
			device = []
			device.append(getattr(self, "device_id_" + str(idx)).text())
			shifts.append({
					'shift_type_name': getattr(self, "shift_" + str(idx)).text(),
					'related_device_id': device
				})

		return devices, shifts

	def get_local_config(self):
		print(self.textbox_import_start_date.text())
		string = self.textbox_import_start_date.text()
		formated_date = "".join([ele for ele in reversed(string.split("/"))])
		
		devices, shifts = self.get_device_details()
		return '''# ERPNext related configs
ERPNEXT_API_KEY = '{0}'
ERPNEXT_API_SECRET = '{1}'
ERPNEXT_URL = '{2}'


# operational configs
PULL_FREQUENCY = {3} or 60 # in minutes
LOGS_DIRECTORY = 'logs' # logs of this script is stored in this directory
IMPORT_START_DATE = '{4}' or None # format: '20190501'

# Biometric device configs (all keys mandatory)
	#- device_id - must be unique, strictly alphanumerical chars only. no space allowed.
	#- ip - device IP Address
	#- punch_direction - 'IN'/'OUT'/'AUTO'/None
	#- clear_from_device_on_fetch: if set to true then attendance is deleted after fetch is successful.
	#(Caution: this feature can lead to data loss if used carelessly.)
devices = {5}

# Configs updating sync timestamp in the Shift Type DocType
shift_type_device_mapping = {6}
'''.format(self.textbox_erpnext_api_key.text(), self.textbox_erpnext_api_secret.text(), self.textbox_erpnext_url.text(), self.textbox_pull_frequency.text(), formated_date, json.dumps(devices), json.dumps(shifts))


def main():
	biometric_app = QApplication(sys.argv)
	biometric_window = BiometricEasyInstaller()
	biometric_app.exec_()

if __name__ == "__main__":
	main()
