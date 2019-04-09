import oci

class oci_manager():
    def __init__(self, config=None):
        if not config:
            self.config = oci.config.from_file(profile_name='RED')
        else:
            self.config = config
        self.id_client = oci.identity.IdentityClient(self.config)
        self.os_client = oci.object_storage.ObjectStorageClient(self.config)
        self.tenancy = self.config['tenancy']

        try:
            self.namespace = self.os_client.get_namespace().data
        except oci.exceptions.RequestException:
            print("Error: Failure to establish connection", sys.exc_info()[0])
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