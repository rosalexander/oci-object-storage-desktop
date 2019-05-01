import os

def get_filesize(file):
    byte_type = ['KB', 'MB', 'GB', 'TB', 'PB']
    try:
        filesize = os.stat(file).st_size
        byte_type_pointer = 0
        byte_size = filesize/1024.0
        while byte_size > 1024:
            byte_size = byte_size/1024.0
            byte_type_pointer += 1
        byte_size = round(byte_size, 2)
        filesize_readable = [str(byte_size), byte_type[byte_type_pointer]]
        return (filesize, filesize_readable)
    except FileNotFoundError as e:
        print(e)
        return (0, ['0', 'KB'])