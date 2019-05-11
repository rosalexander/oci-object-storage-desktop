from PySide2.QtCore import Qt, Signal, QSortFilterProxyModel
from PySide2.QtGui import QColor, QCursor
from PySide2.QtWidgets import QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QDialog, QLineEdit, QAbstractItemView, QMenuBar, QMenu, QAction, QDialog, QMessageBox, QInputDialog, QLayout
from rename import RenameWindow
import os

byte_type = {'KB':1, 'MB':2, 'GB':3, 'TB':4, 'PB':5}

class Tree(QTreeWidget):
    def __init__(self, accept_drop=False, bucket_name=None, oci_manager=None):
        """
        Tree is a widget for displaying object storage information for compartments, buckets, and objects.
        This especially important for the object tree as the widget has functionality to perform drag and drop uploads

        :param accept_drop: Enable drag and drop events
        :type accept_drop: boolean
        :param bucket_name: The name of the bucket for an object tree
        :type bucket_name: string
        :param oci_manager: The OCI manager used by the main application
        :type: oci_manager :class: 'oci_manager.oci_manager'
        """
        super(Tree, self).__init__()
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.accept_drop = accept_drop
        if accept_drop:
            self.customContextMenuRequested.connect(self.object_context_menu)
            self.setAcceptDrops(accept_drop)
            self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.bucket_name = bucket_name
        self.oci_manager = oci_manager
        self.proxy_model = SizeSort()
        self.setSortingEnabled(True)

    def object_tree_init(self):
        self.customContextMenuRequested.connect(self.object_context_menu)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()
    
    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()
    
    def object_context_menu(self):
        """
        Context menu when the object tree is right clicked
        """
        selected_items = self.selectedItems()
        if self.accept_drop and selected_items:
            menu = QMenu(self)
            # copy_action = menu.addAction("Copy")
            download_action = menu.addAction("Download")
            rename_action = menu.addAction("Rename")
            if len(selected_items) > 1:
                rename_action.setEnabled(False)
            rename_action.triggered.connect(self.rename_object)
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self.delete_objects)
            download_action.triggered.connect(self.download_objects)
            menu.exec_(QCursor.pos())
    
    def download_objects(self):
        objects = [item.text(0) for item in self.selectedItems()]
        filesizes = [(int(item.text(2)), item.text(1).split(" ")) for item in self.selectedItems() if item.text(2)]
        self.parentWidget().download_files(objects, filesizes, self.bucket_name)

    
    def delete_objects(self):
        items = self.selectedItems()
        # item_names = [item.text(0) for item in items]
        delete_confirm = QMessageBox()
        delete_confirm.setText("Are you sure you want to delete " + (items[0].text(0) if len(items) == 1 else (str(len(items))) + " items")  + "?")
        delete_confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        delete_confirm.setDefaultButton(QMessageBox.Cancel)
        delete_confirm.layout().setSizeConstraint(QLayout.SetMinimumSize)
        ret = delete_confirm.exec_()
        if ret == QMessageBox.Ok:
            for item in items:
                self.oci_manager.delete_object(self.bucket_name, item.text(0))
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
    
    def rename_object(self):
        item = self.selectedItems()[0]
        rename_window = RenameWindow(item.text(0))
        rename_window.new_name.connect(self.rename_object_handler)
        ret = rename_window.exec_()
            
    def rename_object_handler(self, source_name, new_name):
        response = self.oci_manager.rename_object(self.bucket_name, source_name, new_name)
        if response.status == 200:
            print("Object {} renamed to {}".format(source_name, new_name))
            item = self.selectedItems()[0]
            item.setText(0, new_name)


    def dropEvent(self, e):
        """
        If the event has urls (such as dropped files), and the class is given an OCI manager and and bucket name, upload the files to the bucket

        TODO: Use signals/slots
        """
        if self.accept_drop:
            print(e.mimeData().urls())
            files = []

            for url in e.mimeData().urls():
                file = url.toLocalFile()

                if os.path.isfile(file):
                    files.append(file)
                    
                elif os.path.isdir(file):
                    root_dir = True
                    for dir, _, filenames in os.walk(file):
                        for filename in filenames:
                            subfile = "{}/{}".format(dir, filename) if not root_dir else "{}{}".format(dir, filename)
                            files.append(subfile)
                        root_dir = False

            self.parentWidget().upload_files((files, "All files"), self.bucket_name)
    
    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

class SizeSort(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
    
    def lessThan(source_left, source_right):
        left_string = self.sourceModel().data(source_left).toString()
        right_string = self.sourceModel().data(source_right).toString()

        return left_string < right_string

class TreeWidgetItem(QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            if column == 1:
                if byte_type[key1[-2:]] != byte_type[key2[-2:]]:
                    return byte_type[key1[-2:]] < byte_type[key2[-2:]]
            return float(key1[0:-3]) < float(key2[0:-3])
        except:
            return key1 < key2