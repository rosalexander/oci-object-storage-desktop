import oci
import os
import sys

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
        return oci.object_storage.UploadManager(self.get_os())

    