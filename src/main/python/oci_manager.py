import oci
import os
import sys
from PySide2.QtCore import Qt, Signal, QThread, QObject

MEBIBYTE = 1024 * 1024
STREAMING_DEFAULT_PART_SIZE = 10 * MEBIBYTE
DEFAULT_PART_SIZE = 128 * MEBIBYTE
OBJECT_USE_MULTIPART_SIZE = 128 * MEBIBYTE

class oci_manager():
    def __init__(self, profile='DEFAULT'):
        """
        :param profile: The config profile the OCI manager will use
        :type profile: string
        """
        self.DEFAULT_LOCATION = os.path.expanduser(os.path.join('~', '.oci', 'config'))
        self.change_profile(profile)
    
    def get_config(self):
        """
        :return: The config file of the OCI manager
        :rtype: dict
        """
        return self.config
    
    def get_id(self):
        """
        :return: The identity client of OCI manager for identity-related jobs
        :rtype: :class: 'oci.identity.IdentityClient'
        """
        return self.id_client
    
    def get_os(self):
        """
        :return: The object storage client of OCI manager for object storage related jobs
        :rtype: :class: 'oci.object_storage.ObjectStorageClient'
        """

        return self.os_client
    
    def get_namespace(self):
        """
        :return: The name of the tenancy
        :rtype: string
        """
        return self.namespace
    
    def get_tenancy(self):
        """
        :return: The OCID of the tenancy
        :rtype: string
        """
        return self.tenancy
    
    def change_profile(self, new_profile):
        """
        :param new_profile: The profile the OCI manager will begin to use to instantiate OCI classes such as an identity client, object storage client, etc
        :rtype new_profile: string
        """
        try:
            self.config = oci.config.from_file(profile_name=new_profile)
        except:
            print("Config file does not exist. Creating config file in {}".format(self.DEFAULT_LOCATION))
            f = open(self.DEFAULT_LOCATION, "w+")
            f.write('[DEFAULT]\n')
            for key in ['user', 'fingerprint', 'key_file', 'tenancy', 'region', 'pass_phrase']:
                f.write('{}=\n'.format(key))
            f.close()
            self.config = oci.config.from_file(profile_name=new_profile)

        try:
            oci.config.validate_config(self.config)
        except:
            self.id_client = None
            self.os_client = None
            self.tenancy = None
        else:
            self.id_client = oci.identity.IdentityClient(self.config)
            self.os_client = oci.object_storage.ObjectStorageClient(self.config)
            self.tenancy = self.config['tenancy']

        try:
            self.namespace = self.os_client.get_namespace().data
        except:
            print("Error: Failure to establish connection", sys.exc_info()[0])
            self.namespace = "Not connected"
        self.compartments = []
        self.objects = []
    
    def create_bucket_details(self, name, compartment_id):
        """
        :return: Bucket details for creating a new bucket
        :rtype: :class: 'oci.object_storage.models.CreateBucketDetails'
        """
        return oci.object_storage.models.CreateBucketDetails(name=name, compartment_id=compartment_id)
    
    def get_upload_manager(self):
        """
        :return: Upload manager for calling upload jobs with object storage
        :rtype: :class: 'oci.object_storage.UploadManager'
        """
        return UploadManager(self.get_os())
    
    def delete_object(self, bucket_name, object_name):
        response = self.get_os().delete_object(self.get_namespace(), bucket_name, object_name)
        return response

class UploadId(QObject):
    test = Signal(str)
    def __init__(self):
        super().__init__()
        self.id = None
    def signal_upload_id(self, upload_id):
        self.test.emit(upload_id)
        self.id = upload_id

class UploadManager(oci.object_storage.UploadManager):
    def __init__(self, object_storage_client):
        super().__init__(object_storage_client)
        self.ma = None
    
    def abort(self, upload_id):
        if self.ma:
            self.ma.abort(upload_id = upload_id) if upload_id else self.ma.abort()

        
    
    def upload_file(self,
                    namespace_name,
                    bucket_name,
                    object_name,
                    file_path,
                    **kwargs):
        """
        Uploads an object to Object Storage. Depending on the options provided and the
        size of the object, the object may be uploaded in multiple parts.

        :param str namespace_name:
            The namespace containing the bucket in which to store the object.

        :param str bucket_name:
            The name of the bucket in which to store the object.

        :param str object_name:
            The name of the object in Object Storage.

        :param file_path:
            The path to the file to upload.

        :param int part_size (optional):
            Override the default part size of 128 MiB, value is in bytes.

        :param function progress_callback (optional):
            Callback function to receive the number of bytes uploaded since
            the last call to the callback function.

        :param str if_match (optional):
            The entity tag of the object to match.

        :param str if_none_match (optional):
            The entity tag of the object to avoid matching. The only valid value is ‘*’,
            which indicates that the request should fail if the object already exists.

        :param str content_md5: (optional)
            The base-64 encoded MD5 hash of the body. This parameter is only used if the object is uploaded in a single part.

        :param str content_type (optional):
            The content type of the object to upload.

        :param str content_language (optional):
            The content language of the object to upload.

        :param str content_encoding (optional):
            The content encoding of the object to upload.

        :param dict metadata (optional):
            A dictionary of string to string values to associate with the object to upload

        :param dict mixin (optional):
            QT mixin for signal/slots

        :return:
            The response from multipart commit operation or the put operation.  In both cases this will be a :class:`~oci.response.Response` object with data of type None.
            For a multipart upload the :class:`~oci.response.Response` will contain the :code:`opc-multipart-md5` header and for a non-multipart upload
            it will contain the :code:`opc-content-md5 header`.
        :rtype: :class:`~oci.response.Response`
        """
        part_size = STREAMING_DEFAULT_PART_SIZE
        if 'part_size' in kwargs:
            part_size = kwargs['part_size']
            kwargs.pop('part_size')

        mixin = None
        if 'mixin' in kwargs:
            mixin = kwargs['mixin']
            kwargs.pop('mixin')

        with open(file_path, 'rb') as file_object:
            file_size = os.fstat(file_object.fileno()).st_size
            if not self.allow_multipart_uploads or not UploadManager._use_multipart(file_size, part_size=part_size):
                return self._upload_singlepart(namespace_name, bucket_name, object_name, file_path, **kwargs)
            else:
                if 'content_md5' in kwargs:
                    kwargs.pop('content_md5')

                kwargs['part_size'] = part_size
                kwargs['allow_parallel_uploads'] = self.allow_parallel_uploads
                if self.parallel_process_count is not None:
                    kwargs['parallel_process_count'] = self.parallel_process_count

                ma = oci.object_storage.MultipartObjectAssembler(self.object_storage_client,
                                              namespace_name,
                                              bucket_name,
                                              object_name,
                                              **kwargs)

                self.ma = ma

                upload_kwargs = {}
                if 'progress_callback' in kwargs:
                    upload_kwargs['progress_callback'] = kwargs['progress_callback']

                ma.new_upload()

                if mixin:
                    mixin.signal_upload_id(ma.manifest['uploadId'])

                ma.add_parts_from_file(file_path)

                try:
                    ma.upload(**upload_kwargs)
                    response = ma.commit()
                except:
                    print("Connection failure. Retry with Upload ID {}".format(ma.manifest['uploadId']))
                else:
                    return response
    


    