## OCI Object Storage Desktop Client

![OCI Object Storage Screenshot](/img/example.png?raw=true)

This is an UNOFFICIAL desktop client to interact with the Oracle Cloud Infrastructure Object Storage service. Please use at your own discretion. This application is not affiliated with Oracle or is an official product of Oracle. I created this to expose some of the functionality of OCI's object storage hidden behind the command-line interface and the SDK to a simple to use GUI. With this application, you can create buckets, upload multiple folders and files of any size, retry failed file uploads, and switch between buckets, compartments, and tenancies with ease.

## Download

[Windows Installer Download](https://objectstorage.us-ashburn-1.oraclecloud.com/n/orasenatdpltoci02/b/object-storage-desktop/o/OCI%20Object%20StorageSetup.exe)

[macOS Installer Download](https://objectstorage.us-ashburn-1.oraclecloud.com/n/orasenatdpltoci02/b/object-storage-desktop/o/OCI%20Object%20Storage.dmg)

NOTE: This application was only tested with a MacBook Pro 2018 running High Sierra and a Windows 10 Enterprise Virtual Machine. This application is not guaranteed to run on all variations of Windows and macOS.

## Install & Setup

The Object Storage desktop client requires the same configurations necessary for the OCI command line interface and the OCI SDKs. If you have an RSA key pair in PEM forma, the public key uploaded to OCI, and a config file based in the '~/.oci' path then the application should load up that config file. Otherwise, it will create a new config file. If you have not done these steps previously please refer to the [OCI documentation here](https://docs.cloud.oracle.com/iaas/Content/API/Concepts/apisigningkey.htm).

Afterwards, in the application click on the Edit menu and click on Profile Settings.

![Profile settings image](/img/profile_settings.png)

Fill in the required information and press Save. If the information is correct and your user have authorized access to the OCI API, then you should be connected to your OCI tenancy.

## Examples

### Profile switching!

![Profile switching](/img/switch_profiles.gif?raw=true)

### Uploading, downloading, and deleting objects!

![Uploading, downloading, and deleting objects](/img/upload_download_delete.gif?raw=true)

### Retrying failed uploads!

![Retrying failed uploads](/img/retry.gif?raw=true)

## License

This application is licensed under GPLv3

See [LICENSE](https://github.com/rosalexander/oci-object-storage-desktop/blob/master/LICENSE) for more details

This application makes use of the [PySide2](https://wiki.qt.io/Qt_for_Python) module which is available under under LGPLv3, the [fman build system](https://github.com/mherrmann/fbs) which available under GPL, and the [OCI Python SDK](https://github.com/oracle/oci-python-sdk) which is dual licensed under the Universal Permissive License 1.0 and the Apache License 2.0.

## Current Issues & Future Plans

Here are some issues I have encountered while developing this application that you should be aware of
* Uploading install/applications files (.exe, .dmg, .app files) is not supported and will cause unexpected behavior. 
* Hidden files and folders (such as files or folder that start with '.' e.g. '.git') will be uploaded to Object Storage if inside a folder. 


If there is a demand to further development of this application, I would add these features
* Set visibility of buckets
* View and edit bucket tags
* Move/copy objects to new buckets
* Create pre-authenticate requests to buckets/objects
* View URL path of objects
* Global search for compartments, buckets, and objects
* Port application to a Linux distro

Feel free to make pull requests or fork this repo!
