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
        """
        The ConfigWindow is a widget dedicated to reading and editing the OCI config file and provides functionality to create, edit, and switch profiles on the fly, updating
        the view of the main window.

        :param current_profile: The profile the ConfigWindow should be initialized with
        :type current_profile: string
        """
        super().__init__()

        #
        self.main_window = None
        self.setWindowTitle("Profile Settings")
        self.setMinimumSize(600, 200)

        #Looks for the config file in '~/.oci/config' and reads it into config
        self.DEFAULT_LOCATION = os.path.expanduser(os.path.join('~', '.oci', 'config'))
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(self.DEFAULT_LOCATION)
        self.current_profile = current_profile

        
        
        #Set up necessary dropdown and LineEdit widgets
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
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_signal)

        #Set the profile to the current_profile passed in upon init
        self.change_profile(current_profile)
        self.dropdown.setCurrentText(current_profile)
        
        #Add all widgets to a vertical layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.tenancy)
        self.layout.addWidget(self.region)
        self.layout.addWidget(self.user)
        self.layout.addWidget(self.key_file)
        self.layout.addWidget(self.fingerprint)
        self.layout.addWidget(self.passphrase)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
    
    def get_profiles_dropdown(self):
        """
        :return:
            A dropdown menu widget that lists all profiles including the default profile from the OCI config file
            When index changes, it will call the change_profile signal function
        :rtype: :class: 'Qt.QtWidgets.QComboBox'
        """
        dropdown = QComboBox()
        dropdown.addItems(['DEFAULT'] + self.config.sections())
        dropdown.addItem("Add New Profile...")
        dropdown.currentIndexChanged.connect(self.change_profile_signal)
        return dropdown

    def change_profile_signal(self, item):
        """
        Slot to change profile. If the item index is at 0, then it is the default profile.
        If it is the last index, then that means create a new profile

        :param item: The index of the item from the dropdown widget
        :type item: int
        """
        if item > len(self.config.sections()):
            self.create_new_profile()
        elif item == 0:
            self.change_profile('DEFAULT')
        else: 
            self.change_profile(self.config.sections()[item - 1])
    
    def change_profile(self, profile_name):
        """
        Changes the profile that the ConfigWindow is set for and also changes it for the MainWindow

        :param profile_name: the name of the profile to switch to
        :type profile_name: string

        TODO: Adhere to signal/slot convention
        """
        self.current_profile = profile_name
        profile = self.config[profile_name]
 
        for line, key in zip([self.tenancy, self.region, self.user, self.fingerprint, self.key_file, self.passphrase],\
        ['tenancy', 'region', 'user', 'fingerprint', 'key_file', 'pass_phrase']):
            if key in profile:
                line.setText(profile[key])
            else:
                line.setText("")
        
        if self.main_window:
            self.main_window.change_profile(self.current_profile)
    
    def create_new_profile(self):
        """
        Layout to create a new profile. Removes the dropdown widget and changes the buttons
        """
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

        self.layout.removeItem(self.layout.itemAt(7))
        self.save_button.setParent(None)

        self.layout.addWidget(self.buttonBox)
        
    
    def create_signal(self):
        """
        Create a new profile with the given information in the LineEdit widgets. Saves to the OCI config file
        """
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

        self.current_profile = profile_name
        self.cancel_signal()
    
    def save_signal(self):
        """
        Saves edits on a currently existing profile. Saves to the OCI config file
        """
        self.config[self.current_profile]['tenancy'] = self.tenancy.text()
        self.config[self.current_profile]['region'] = self.region.text()
        self.config[self.current_profile]['user'] = self.user.text()
        self.config[self.current_profile]['fingerprint'] = self.fingerprint.text()
        self.config[self.current_profile]['key_file'] = self.key_file.text()
        self.config[self.current_profile]['pass_phrase'] = self.passphrase.text()
        
        with open(self.DEFAULT_LOCATION, 'w') as configfile:
            self.config.write(configfile)
    
    def cancel_signal(self):
        """
        Cancels the creation a new profile and reverts layout to default layout
        """
        self.layout.removeItem(self.layout.itemAt(0))
        self.new_profile_name.setParent(None)

        self.dropdown = self.get_profiles_dropdown()
        self.layout.insertWidget(0, self.dropdown)

        self.layout.removeItem(self.layout.itemAt(7))
        self.buttonBox.setParent(None)

        self.change_profile(self.current_profile)
        self.dropdown.setCurrentText(self.current_profile)
        
        self.layout.addWidget(self.save_button)


if __name__ == '__main__':
    app = QApplication([])
    window = ConfigWindow('RED')
    window.show()
    sys.exit(app.exec_())