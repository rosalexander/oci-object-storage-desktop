from fbs_runtime.application_context import ApplicationContext, cached_property
from PySide2.QtCore import Qt, SIGNAL, QObject, QTextCodec
from PySide2.QtGui import QColor

from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QDialog, QLineEdit, QAbstractItemView
import oci
import requests
import sys

class AppContext(ApplicationContext):
    def run(self):
        stylesheet = self.get_resource('styles.qss')
        self.app.setStyleSheet(open(stylesheet).read())
        self.window.show()
        return self.app.exec_()
    @cached_property
    def window(self):
        return MainWindow()

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(800, 600)
        self.setWindowTitle("OCI Object Storage")

        self.oci_manager = oci_manager()
        self.treeWidget = self.get_compartment_tree()
        self.bucket_tree = self.get_placeholder_tree('Buckets', 'No compartment selected')
        self.obj_tree = self.get_placeholder_tree('Objects', 'No bucket selected')

        button = QPushButton('Upload Files')
        button.clicked.connect(self.select_files)

        button2 = QPushButton('New Bucket')
        button2.clicked.connect(self.create_bucket_prompt)

        button3 = QPushButton('Delete Files')
        button3.clicked.connect(self.select_files)

        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Vertical)
        buttonBox.addButton(button, QDialogButtonBox.ActionRole)
        buttonBox.addButton(button2, QDialogButtonBox.ActionRole)
        buttonBox.addButton(button3, QDialogButtonBox.ActionRole)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(buttonBox)

        self.layout.setAlignment(buttonBox, Qt.AlignHCenter)
        self.layout.addWidget(self.treeWidget)
        self.layout.addWidget(self.bucket_tree)
        self.layout.addWidget(self.obj_tree)
        self.setLayout(self.layout)
    
    def select_files(self):
        buckets = self.bucket_tree.selectedItems()
        if buckets:
            files = QFileDialog.getOpenFileNames(self, "Select one or more files to open")
            print(files)
            for bucket in buckets:
                self.upload_files(files, bucket.text(0))
                self.select_bucket(bucket)
        else:
            print("Must choose a bucket")

    def create_bucket_prompt(self):

        def create_bucket():
            print(self.bucket_form.line.text())
            namespace = self.oci_manager.get_namespace()
            create_bucket_details = oci.object_storage.models.CreateBucketDetails(name=self.bucket_form.line.text(), compartment_id=compartment[-1].text(1))
            r = self.oci_manager.get_os().create_bucket(namespace, create_bucket_details)
            print(create_bucket_details)
            print(r.data)
            self.bucket_form.hide()
            self.select_compartment(compartment[-1])

        self.bucket_form = Form()
        self.bucket_form.button.clicked.connect(create_bucket)

        compartment = self.treeWidget.selectedItems()
        if compartment:
            self.bucket_form.show()
        else:
            print("Must choose a compartment")        

    
    def upload_files(self, files, bucket_name):
        namespace = self.oci_manager.get_namespace()
        for file in files[0]:
            with open(file, 'rb') as file_object:
                self.oci_manager.get_os().put_object(namespace, bucket_name, file.split('/')[-1], file_object.read())

    def get_compartment_tree(self):

        root = self.oci_manager.get_tenancy()
        compartments = self.oci_manager.get_id().list_compartments(root, compartment_id_in_subtree=True)

        data = compartments.data

        compartment_dic = {}
        hierarchy = {}
        tree_dic = {}

        while compartments.next_page:
            compartments = self.oci_manager.get_id().list_compartments(root, compartment_id_in_subtree=True, page=compartments.next_page)
            data += compartments.data

        for compartment in data:
            if (compartment.lifecycle_state == 'ACTIVE'):
                compartment_dic[compartment.id] = compartment
                if compartment.compartment_id in hierarchy:
                    hierarchy[compartment.compartment_id] += [compartment.id]
                else:
                    hierarchy[compartment.compartment_id] = [compartment.id]

        treeWidget = Tree()
        treeWidget.setHeaderLabels(['Compartments', 'OCID'])
        tree_dic[root] = QTreeWidgetItem(treeWidget)
        tree_dic[root].setText(0, '(root)')
        tree_dic[root].setText(1, root)

        stack = [root]
        while stack:
            compartment_id = stack.pop()
            parent_tree = tree_dic[compartment_id]
            for child_id in hierarchy[compartment_id]:
                child_tree = QTreeWidgetItem(parent_tree)
                child_tree.setText(0, compartment_dic[child_id].name)
                child_tree.setText(1, child_id)
                tree_dic[child_id] = child_tree
                if child_id in hierarchy:
                    stack.append(child_id)
    
        treeWidget.itemClicked.connect(self.select_compartment)
        treeWidget.setColumnHidden(1, True)
        return treeWidget
    
    def select_compartment(self, item):
        self.layout.removeItem(self.layout.itemAt(2))
        self.bucket_tree.setParent(None)
        self.bucket_tree = self.get_buckets_tree(item.text(1))
        self.layout.insertWidget(2, self.bucket_tree)
        self.layout.removeItem(self.layout.itemAt(3))
        self.obj_tree.setParent(None)
        self.obj_tree = self.get_placeholder_tree('Objects', 'No bucket selected')
        self.layout.insertWidget(3, self.obj_tree)
    
    def select_bucket(self, item):
        self.layout.removeItem(self.layout.itemAt(3))
        self.obj_tree.setParent(None)
        self.obj_tree = self.get_objects_tree(item.text(0))
        self.layout.insertWidget(3, self.obj_tree)
        
    
    def get_buckets_tree(self, ocid):
        namespace = self.oci_manager.get_namespace()
        treeWidget = Tree()
        treeWidget.setHeaderLabel('Buckets')

        data = self.oci_manager.get_os().list_buckets(namespace, ocid).data

        if not data:
            bucket_tree = QTreeWidgetItem(treeWidget)
            bucket_tree.setText(0, 'Compartment contains no buckets')
            bucket_tree.setTextColor(0, QColor(220,220,220))
        else:
            for bucket in data:
                print(bucket.name)
                bucket_tree = QTreeWidgetItem(treeWidget)
                bucket_tree.setText(0, bucket.name)
            treeWidget.itemClicked.connect(self.select_bucket)
        return treeWidget
    
    def get_objects_tree(self, bucket_name):
        namespace = self.oci_manager.get_namespace()

        treeWidget = Tree(accept_drop=True)
        treeWidget.setColumnCount(2)
        treeWidget.setHeaderLabels(['Objects', 'Size'])

        byte_type = ['KB', 'MB', 'GB', 'PB']

        data = self.oci_manager.get_os().list_objects(namespace, bucket_name, fields='size').data.objects

        for obj in data:
            print(obj.name)
            obj_tree_item = QTreeWidgetItem(treeWidget)
            obj_tree_item.setText(0, obj.name)
            byte_type_pointer = 0
            byte_size = obj.size/1024.0
            while byte_size > 1024:
                byte_size = byte_size/1024.0
                byte_type_pointer += 1
            byte_size = round(byte_size, 2)
            obj_tree_item.setText(1, "{} {}".format(str(byte_size), byte_type[byte_type_pointer]))

        
        return treeWidget

    def get_placeholder_tree(self, header, text):
        tree_widget = Tree()
        tree_widget.setHeaderLabel(header)
        tree_item = QTreeWidgetItem(tree_widget)
        tree_item.setText(0, text)
        tree_item.setTextColor(0, QColor(220,220,220))
        return tree_widget
        

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Create Bucket")
        layout = QVBoxLayout()
        self.line = QLineEdit()
        self.line.setPlaceholderText('Bucket name')
        self.button = QPushButton("Create")
        layout.addWidget(self.line)
        layout.addWidget(self.button)
        self.setLayout(layout)

class Tree(QTreeWidget):
    def __init__(self, accept_drop=False, compartment_id=None, bucket_name=None):
        super(Tree, self).__init__()
        # self.setDefaultDropAction(Qt.MoveAction)
        # self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setAcceptDrops(accept_drop)
        self.compartment_id = compartment_id
        self.bucket_name = bucket_name

    
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

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            file_name = url.toLocalFile()
            print("Dropped file: " + file_name)
            

class oci_manager():
    def __init__(self, config=None):
        if not config:
            self.config = oci.config.from_file(profile_name='RED')
        else:
            self.config = config
        
        self.id_client = oci.identity.IdentityClient(self.config)
        self.os_client = oci.object_storage.ObjectStorageClient(self.config)
        self.tenancy = self.config['tenancy']
        self.namespace = self.os_client.get_namespace().data

        self.compartments = []
        self.objects = []
    
    def get_config(self):
        return self.config
    
    def get_id(self):
        return self.id_client
    
    def get_os(self):
        return self.os_client
    
    def get_namespace(self):
        return self.namespace
    
    def get_tenancy(self):
        return self.tenancy
    

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)