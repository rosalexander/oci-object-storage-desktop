from PySide2.QtCore import Qt, Signal, QObject, QTextCodec, QThread
from PySide2.QtGui import QColor, QCursor
from PySide2.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QDialog, QLineEdit, QAbstractItemView, QMenuBar, QMenu, QAction, QProgressBar
from oci_manager import oci_manager
from config import ConfigWindow
from progress import ProgressWindow
from util import get_filesize
import sys
import os

class DownloadThread(QThread):

    file_downloaded = Signal(str, str)
    bytes_downloaded = Signal(int)
    all_files_downloaded = Signal(int)
    download_failed = Signal()

    def __init__(self, objects, bucket_name, oci_manager, thread_id):
        """
        downloadThread allows download jobs to run in a differen;t thread than the application, so the application doesn't stall or freeze
        
        :param files: A tuple of files. First element is a list of absolute paths to the files. Second element is the mimetype of files
        :type files: tuple
        :param bucket_name: The name of the bucket for downloading into
        :type bucket_name: string
        :param oci_manager: The OCI manager to use for OCI related tasks
        :type: :class: 'oci_manager.oci_manager'
        """
        super().__init__()
        self.objects = objects
        self.bucket_name = bucket_name
        self.os_client = oci_manager.get_os()
        self.namespace = oci_manager.get_namespace()
        self.threadactive = True
        self.setTerminationEnabled()
        self.thread_id = thread_id
        self.current_download = None

        self.path = os.path.expanduser('~/Downloads/')
    
    def connection_failed(self):
        print("Connection failed")
        self.download_failed.emit()
    
    def progress_callback(self, bits):
        """
        Callback function for the downloading

        :param bits: The amount of bits downloaded
        :type bits: int
        """
        self.bytes_downloaded.emit(bits)
        
    def __del__(self):
        self.wait()

    def stop(self):
        print("Connection stopped")
        self.threadactive = False
        self.wait()
    
    def download_file(self, filename, response):
        """
        download the file and pass in a callback function

        :param file: The absolute path of the file
        :type file: string
        """
        bits = 0

        duplicate = 0
        dup_modifier = ''
        name_split = filename.split(".")
        dup_path = self.path

        if len(name_split) > 1:
            for i, part in enumerate(name_split):
                if i < len(name_split) - 1:
                    dup_path += part
                if i < len(name_split) - 2:
                    dup_path += '.'
            name_split[-1] = '.' + name_split[-1]
        else:
            dup_path += name_split.pop()
            name_split.append('')
        
        while os.path.exists(dup_path + dup_modifier + name_split[-1]):
            duplicate += 1
            dup_modifier = ' ({})'.format(duplicate)
        
        path = dup_path + dup_modifier + name_split[-1]

        with open(path, "wb+") as f:
            for chunk in response.data:
                bits += f.write(chunk)
                print("{}/{}".format(bits, response.headers['Content-Length']))
                self.progress_callback(bits)

        return True
    
    def run(self):
        """

        """

        while self.objects or self.current_download:
            object_name = self.objects.pop()
            response = self.os_client.get_object(self.namespace, self.bucket_name, object_name)
            if response.status == 200 and self.threadactive:
                object_size = response.headers['Content-Length']

                self.current_download = {"object_name":object_name, "file_path":self.path + object_name, "object_size": object_size}
                try:
                    download_resp = self.download_file(object_name, response)
                except:
                    if self.threadactive:
                        self.connection_failed()
                    break
                if download_resp:
                    self.file_downloaded.emit(object_name, object_size)
                    self.current_download = None

        if not self.objects and not self.current_download:
            self.all_files_downloaded.emit(self.thread_id)