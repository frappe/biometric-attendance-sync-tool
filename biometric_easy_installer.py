import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QLabel
import os, json

class BiometricEasyInstaller(QMainWindow):

	def __init__(self):
		super().__init__()
		self.init_ui()


	def init_ui(self):
		self.counter = 1
		self.setup_window()
		self.setup_textboxes_and_label()
		#self.setup_buttons()
		self.center()
		self.show()


	def setup_window(self):
		self.setGeometry(0, 0, 500, 1000)
		self.setWindowTitle('Integrate Biometric')


	def setup_textboxes_and_label(self):
		label_1 = QLabel(self)
		label_1.setText("Website URL")
		label_1.move(250, 0)

		self.textbox_erpnext_url = QLineEdit(self)
		self.textbox_erpnext_url.move(250, 30)
		self.textbox_erpnext_url.resize(200, 30)

		label_7 = QLabel(self)
		label_7.setText("Pull Frequency")
		label_7.move(250, 60)

		self.textbox_pull_frequency = QLineEdit(self)
		self.textbox_pull_frequency.move(250, 90)
		self.textbox_pull_frequency.resize(200, 30)

		label_8 = QLabel(self)
		label_8.setText("Import start date")
		label_8.move(250, 120)
		label_8.resize(200, 30)

		self.textbox_import_start_date = QLineEdit(self)
		self.textbox_import_start_date.move(250, 150)
		self.textbox_import_start_date.resize(200, 30)

		label_2 = QLabel(self)
		label_2.setText("API Secret")
		label_2.move(20, 0)

		self.textbox_erpnext_api_secret = QLineEdit(self)
		self.textbox_erpnext_api_secret.move(20, 30)
		self.textbox_erpnext_api_secret.resize(200, 30)

		label_3 = QLabel(self)
		label_3.setText("API Key")
		label_3.move(20, 60)

		self.textbox_erpnext_api_key = QLineEdit(self)
		self.textbox_erpnext_api_key.move(20, 90)
		self.textbox_erpnext_api_key.resize(200, 30)

		self.button_connect = QPushButton('Add More Devices', self)
		self.button_connect.move(14, 140)
		self.button_connect.resize(150, 30)
		self.button_connect.clicked.connect(self.on_click_connect)

		label_4= QLabel(self)
		label_4.setText("Device ID")
		label_4.move(20, 200)

		label_5= QLabel(self)
		label_5.setText("Device IP")
		label_5.move(170, 200)

		label_6= QLabel(self)
		label_6.setText("Shift")
		label_6.move(320, 200)

		# First Row for table
		setattr(self, "device_id_0", QLineEdit(self))
		b  = getattr(self, "device_id_0")
		b.resize(150, 30)
		b.move(20, 230)
		b.show()

		setattr(self, "device_ip_0", QLineEdit(self))
		b  = getattr(self, "device_ip_0")
		b.resize(150, 30)
		b.move(170, 230)
		b.show()

		setattr(self, "shift_0", QLineEdit(self))
		b  = getattr(self, "shift_0")
		b.resize(150, 30)
		b.move(320, 230)
		b.show()

		self.button_connect = QPushButton('Configure', self)
		self.button_connect.move(14, 600)
		self.button_connect.resize(150, 30)
		self.button_connect.clicked.connect(self.setup_local_config)


	def center(self):
		frame = self.frameGeometry()
		screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
		centerPoint = QApplication.desktop().screenGeometry(screen).center()
		frame.moveCenter(centerPoint)
		self.move(frame.topLeft())


	def on_click_connect(self):
		if self.counter < 5:
			setattr(self, "device_id_" + str(self.counter), QLineEdit(self))
			b  = getattr(self, "device_id_" + str(self.counter))
			b.resize(150, 30)
			b.move(20, 230+(self.counter * 30))
			b.show()

			setattr(self, "device_ip_" + str(self.counter), QLineEdit(self))
			b  = getattr(self, "device_ip_" + str(self.counter))
			b.resize(150, 30)
			b.move(170, 230+(self.counter * 30))
			b.show()

			setattr(self, "shift_" + str(self.counter), QLineEdit(self))
			b  = getattr(self, "shift_" + str(self.counter))
			b.resize(150, 30)
			b.move(320, 230+(self.counter * 30))
			b.show()


			self.counter += 1


	def setup_local_config(self):
		if os.path.exists("local_config.py"):
			os.remove("local_config.py")

		local_config_py = open("local_config.py", 'w+')

		config = self.get_local_config()

		local_config_py.write(config)

	def get_device_details(self):
		from pprint import pprint
		devices = []
		shifts = []
		for idx in (0, self.counter-1):
			# print(getattr(self, "device_id_" + str(idx)).text())
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
'''.format(self.textbox_erpnext_api_key.text(), self.textbox_erpnext_api_secret.text(), self.textbox_erpnext_url.text(), self.textbox_pull_frequency.text(), self.textbox_import_start_date.text(), json.dumps(devices), json.dumps(shifts))


def main():
	biometric_app = QApplication(sys.argv)
	biometric_window = BiometricEasyInstaller()
	biometric_app.exec_()

if __name__ == "__main__":
	main()