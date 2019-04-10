import sys
import os
import configparser
from PySide2.QtCore import Qt, SIGNAL, QObject, QTextCodec
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QDialog, QLineEdit, QAbstractItemView, QMenuBar, QMenu, QAction, QComboBox


# DEFAULT_LOCATION = os.path.expanduser(os.path.join('~', '.oci', 'config'))
# config = configparser.ConfigParser(interpolation=None)
# config.read(DEFAULT_LOCATION)

class ConfigWindow(QWidget):
    def __init__(self, current_profile):
        super().__init__()
        print("Config Window Initialized")
        self.current_profile = current_profile
        self.DEFAULT_LOCATION = os.path.expanduser(os.path.join('~', '.oci', 'config'))
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(self.DEFAULT_LOCATION)
        
        self.setWindowTitle("Profile Settings")
        self.setMinimumSize(600, 200)

        self.layout = QVBoxLayout()

        self.dropdown = self.get_profiles_dropdown()
        self.tenancy = QLineEdit()
        self.tenancy.setPlaceholderText("Tenancy OCID")
        self.region = QLineEdit()
        self.region.setPlaceholderText("Region")
        self.user = QLineEdit()
        self.user.setPlaceholderText("User OCID")
        self.fingerprint = QLineEdit()
        self.fingerprint.setPlaceholderText("Fingerprint")
        self.key_file = QLineEdit()
        self.key_file.setPlaceholderText("Key File Path")
        self.passphrase = QLineEdit()
        self.passphrase.setEchoMode(QLineEdit.Password)
        self.passphrase.setPlaceholderText("Passphrase")
        
        self.change_profile(current_profile)
        self.dropdown.setCurrentText(current_profile)
        
        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.tenancy)
        self.layout.addWidget(self.region)
        self.layout.addWidget(self.user)
        self.layout.addWidget(self.key_file)
        self.layout.addWidget(self.fingerprint)
        self.layout.addWidget(self.passphrase)

        self.setLayout(self.layout)
    
    def get_profiles_dropdown(self):
        dropdown = QComboBox()
        dropdown.addItems(['DEFAULT'] + self.config.sections())
        dropdown.addItem("Add New Profile...")
        dropdown.currentIndexChanged.connect(self.change_profile_signal)
        return dropdown

    def change_profile_signal(self, item):
        if item > len(self.config.sections()):
            self.create_new_profile()
        elif item == 0:
            self.change_profile('DEFAULT')
        else: 
            self.change_profile(self.config.sections()[item - 1])
    
    def change_profile(self, profile_name):
        self.current_profile = profile_name
        profile = self.config[profile_name]
        self.tenancy.setText(profile['tenancy'])
        self.region.setText(profile['region'])
        self.user.setText(profile['user'])
        self.fingerprint.setText(profile['fingerprint'])
        self.key_file.setText(profile['key_file'])
        self.passphrase.setText(profile['pass_phrase'])
    
    def create_new_profile(self):
        self.layout.removeItem(self.layout.itemAt(0))
        self.dropdown.setParent(None)

        self.new_profile_name = QLineEdit()
        self.new_profile_name.setPlaceholderText("Profile Name")
        self.layout.insertWidget(0, self.new_profile_name)

        self.tenancy.setText("")
        self.region.setText("")
        self.user.setText("")
        self.fingerprint.setText("")
        self.key_file.setText("")
        self.passphrase.setText("")
        self.create_button = QPushButton('Create')
        self.create_button.clicked.connect(self.create_signal)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel_signal)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.addButton(self.create_button, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.cancel_button, QDialogButtonBox.ActionRole)
        self.layout.addWidget(self.buttonBox)
        
    
    def create_signal(self):
        profile_name = self.new_profile_name.text()
        self.config[profile_name] = {}
        self.config[profile_name]['tenancy'] = self.tenancy.text()
        self.config[profile_name]['region'] = self.region.text()
        self.config[profile_name]['user'] = self.user.text()
        self.config[profile_name]['fingerprint'] = self.fingerprint.text()
        self.config[profile_name]['key_file'] = self.key_file.text()
        self.config[profile_name]['pass_phrase'] = self.passphrase.text()
        
        with open(self.DEFAULT_LOCATION, 'w') as configfile:
            self.config.write(configfile)

        # dropdown = self.layout.itemAt(5)
        # self.layout.removeItem(self.layout.itemAt(5))
        # dropdown.setParent(None)
        # self.layout.insertItem(0, self.dropdown)

        self.current_profile = profile_name
        self.cancel_signal()
    
    def cancel_signal(self):
        self.layout.removeItem(self.layout.itemAt(0))
        self.new_profile_name.setParent(None)

        self.dropdown = self.get_profiles_dropdown()
        self.layout.insertWidget(0, self.dropdown)

        self.layout.removeItem(self.layout.itemAt(7))
        self.buttonBox.setParent(None)
        print(self.current_profile)

        self.change_profile(self.current_profile)
        self.dropdown.setCurrentText(self.current_profile)


if __name__ == '__main__':
    app = QApplication([])
    window = ConfigWindow('RED')
    window.show()
    sys.exit(app.exec_())