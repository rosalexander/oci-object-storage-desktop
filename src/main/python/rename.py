import sys
from PySide2.QtWidgets import QDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QVBoxLayout, QDialogButtonBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, Signal


class RenameWindow(QDialog):

    new_name = Signal(str, str)

    def __init__(self, filename):
        super().__init__()
        self.title = 'Rename File'
        # self.left = 10
        # self.top = 10
        # self.width = 200
        # self.height = 100
        self.filename = filename
        self.initUI()
        
    
    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.textbox = QLineEdit(self)
        self.textbox.setText(self.filename)
        self.ok_button = QPushButton('Ok')
        self.ok_button.clicked.connect(self.on_click)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)

        self.button_box = QDialogButtonBox()
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        self.button_box.addButton(self.ok_button, QDialogButtonBox.AcceptRole)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
    
    def on_click(self):
        self.new_name.emit(self.filename, self.textbox.text())
        self.accept()

if __name__ == '__main__':
    print("Test")
    app = QApplication(sys.argv)
    ex = RenameWindow("test.txt")
    sys.exit(app.exec_())