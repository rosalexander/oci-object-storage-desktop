import oci
import os
import sys

class oci_manager():
    def __init__(self, profile='DEFAULT'):
        self.DEFAULT_LOCATION = os.path.expanduser(os.path.join('~', '.oci', 'config'))
        self.change_profile(profile)
    
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
    
    def change_profile(self, new_profile):
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

    