import os
import socket
import time
import json


class FileSharingSender(object):
    """Sender class for file sharing project"""

    def __init__(self, ip='localhost', port=5000, packet_size=8192):
        self.port = port
        self.packet_size = packet_size
        self.ip = ip
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_name = None
        self.dir_name = None
        self.home_dir = os.getcwd()
        self.conn = None

    def _send_file(self):
        """Sends a file specified by name in attribute file_name"""
        self.conn.send(bytes([len(self.file_name)]))
        self.conn.send(self.file_name.encode())

        if os.path.exists(self.file_name):

            with open(self.file_name, 'rb') as file:

                buffer = file.read(self.packet_size)
                while buffer != b'':
                    self.conn.send(buffer)

                    buffer = file.read(self.packet_size)
        print('Sent {}'.format(self.file_name))

    def _send_dir_nt(self, path=None):
        """Sends a directory on windows operating system"""
        if path is None:
            path = [self.dir_name.split('\\')[-1]]

        try:
            items = os.listdir('.')
        except:
            items = list()
        files = []
        dirs = []
        for item in items:
            if os.path.isfile(item):
                files.append(item)
            elif os.path.isdir(item):
                dirs.append([item])

        for dir in dirs:
            os.chdir(dir[0])
            self._send_dir_nt(dir)

        for item in files + dirs:
            path.append(item)
        os.chdir('..')

    def _send_dir_files(self):
        """Sends files from current directory"""
        try:
            items = os.listdir('.')
        except:
            items = list()

        for item in items:
            if os.path.isfile(item):
                self.file_name = item
                self._send_file()
                self.conn.recv(1)
            elif os.path.isdir(item):
                os.chdir(item)
                self._send_dir_files()
        os.chdir('..')

    def _send_dir(self):
        """Handles sending directory depending on OS"""
        if os.name == 'nt' and os.path.exists(self.dir_name):
            os.chdir(self.dir_name)
            name = self.dir_name.split('\\')[-1]
            path = [name]
            self._send_dir_nt(path)
            path_to_send = json.dumps(path)

            self.conn.send(bytes([len(path_to_send)]))
            self.conn.send(path_to_send.encode())

            os.chdir(path[0])
            self._send_dir_files()
        else:
            print('Unsupported yet')

    def send_files(self, file_name=None):
        """Main method to call from outside"""
        self.connection.bind((self.ip, self.port))
        self.connection.listen(1)

        if file_name is None:
            self.file_name = input('filename/path to file: ')
        else:
            self.file_name = file_name
        self.conn, address = self.connection.accept()

        if os.path.exists(self.file_name):
            if os.path.isdir(self.file_name):
                agree = input('This is a folder. Do you want to send all it\'s content? (Y/N): ')
                if agree.upper() == 'Y':
                    self.conn.send(b'1')
                    self.dir_name = self.file_name
                    self._send_dir()
                elif agree.upper() == 'N':
                    pass
            elif os.path.isfile(self.file_name):
                self.conn.send(b'0')
                self._send_file()

        self.conn.close()


class FileSharingReceiver(object):

    def __init__(self, ip='localhost', port=5000, packet_size=8192):
        self.port = port
        self.packet_size = packet_size
        self.ip = ip
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_name = None
        self.dir_name = None
        self.home_dir = os.getcwd()
        self.conn = None

    def _append_to_file(self, partial_file):
        with open(self.file_name, 'ab') as file:
            file.write(b''.join(partial_file))

    def _next_file_name(self, name):
        index = 0
        if not os.path.exists(name):
            self.file_name = name
            return self.file_name

        name_array = name.split('.')
        name = ''.join(['.'.join(name_array[:-1]), ' ({index}) .', name_array[-1]])

        while os.path.exists(name.format(index=index)):
            index += 1

        return name.format(index=index)

    def _create_file_name(self, file_name):
        if os.name == 'nt':
            file_name = file_name.split('\\')[-1]
        else:
            file_name = file_name.split('/')[-1]

        self.file_name = self._next_file_name(file_name)

    def _receive_file(self):
        name_len = self.connection.recv(1)
        file_name = self.connection.recv(int.from_bytes(name_len, 'big')).decode()
        self._create_file_name(file_name)

        complete_file = []
        while True:
            item = b''
            try:
                self.connection.settimeout(1.2)
                item = self.connection.recv(self.packet_size)
                self.connection.settimeout(None)
            except:
                pass

            if item == b'':
                break
            complete_file.append(item)

            if len(complete_file) > 500:
                self._append_to_file(complete_file)
                complete_file.clear()

        self._append_to_file(complete_file)

    def _create_dirs(self, path, files=None, create=False):
        if files is None:
            files = []

        if isinstance(path, list) and create:
            name = path[0] + '_'
            os.mkdir(name)
            os.chdir(name)

        for index, item in enumerate(path):
            if isinstance(item, list):
                name = item[0] + "_"
                os.mkdir(name)
                os.chdir(name)
                self._create_dirs(item, files=files)
                os.chdir('..')
            elif index != 0:
                files.append(item)

    def _receive_files(self, path, files):

        for index, item in enumerate(path):
            if isinstance(item, list):
                self._receive_files(item, files)
                os.chdir('..')
            elif index == 0:
                os.chdir(item + "_")
            else:
                self._receive_file()
                self.connection.send(b'1')

    def _receive_dir(self):
        name_len = int.from_bytes(self.connection.recv(1), 'big')
        path = self.connection.recv(name_len).decode()
        path = json.loads(path)

        files = []
        self._create_dirs(path, files, True)
        os.chdir('..')
        self._receive_files(path, files)

    def receive_files(self):
        self.connection.connect((self.ip, self.port))

        item_type = self.connection.recv(1)

        if item_type == b'0':
            # is a file
            self._receive_file()
        elif item_type == b'1':
            # is a folder
            self._receive_dir()

        self.connection.close()


# todo request files (with accept or password)?

if __name__ == '__main__':

    print('send or receive?')
    inp = input()
    if inp == 'send':
        fs = FileSharingSender()
        fs.send_files()
    else:
        start = time.time()
        fs = FileSharingReceiver()
        fs.receive_files()
        end = time.time()

        print('Total time: ', end - start)
