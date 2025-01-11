import paramiko
import os
from os.path import dirname
import stat


def remote_isdir(attr):
    """
    Checks if the given attribute corresponds to a directory.

    Parameters:
        attr (stat_result): The file attributes of the remote file/directory.

    Returns:
        bool: True if the attribute corresponds to a directory, False otherwise.
    """
    return stat.S_ISDIR(attr.st_mode)


def mkdir_p(sftp: 'SFTPClient', remote_directory: str):
    """
    Recursively creates directories on the remote server if they do not exist.

    Parameters:
        sftp (SFTPClient): The SFTP client used for communication with the remote server.
        remote_directory (str): The remote directory path to create.

    Returns:
        bool: True if any directories were created, False otherwise.
    """

    print("Trying to create %s folder" % remote_directory)
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname) # make parent directories
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)
        return True


class SSH:
    """
    Initializes an SSH connection and sets up SFTP.

    Parameters:
        user (str): The username for SSH authentication.
        host (str): The host address of the remote server.
        remote_scratch (str, optional): Path to the remote scratch directory. Defaults to "".
    """
    def __init__(self, user: str, host: str, remote_scratch: str=""):
        # Init
        self.user = user
        self.host = host
        self._host_config_id = None
        self._ssh = None
        self._ssh_config = None
        self._user_config_file = None
        self._host_config = None
        self.sftp = None
        self.remote_scratch = remote_scratch

        # SSH
        self.connect()
        self.init_transport()

    def init_transport(self):
        """
        Initializes the SFTP transport for file transfers.
        """
        self.sftp = self._ssh.open_sftp()

    def get(self, remote_path: str, local_path: str):
        """
        Downloads a file from the remote server to the local machine.

        Parameters:
            remote_path (str): The remote file path.
            local_path (str): The local destination file path.
        """
        if not self.sftp:
            self.init_transport()
        self.sftp.get(remote_path, local_path)

    def put(self, local_path: str, remote_path: str):
        """
        Uploads a file from the local machine to the remote server.

        Parameters:
            local_path (str): The local file path.
            remote_path (str): The remote destination file path.
        """
        if not self.sftp:
            self.init_transport()
        remote_folder_path = dirname(remote_path)
        try:
            self.sftp.chdir(remote_folder_path)  # Test if remote_path exists
        except IOError:
            mkdir_p(self.sftp, remote_folder_path)
        self.sftp.put(local_path, remote_path)

    def write_file(self, text: str, remote_path: str):
        """
        Writes text content to a file on the remote server.

        Parameters:
            text (str): The text to write to the file.
            remote_path (str): The remote file path to write the text.
        """
        if not self.sftp:
            self.init_transport()
        remote_folder_path = dirname(remote_path)
        try:
            self.sftp.chdir(remote_folder_path)  # Test if remote_path exists
        except IOError:
            mkdir_p(self.sftp, remote_folder_path)
        remote_file = self.sftp.open(remote_path, "w")
        remote_file.write(text)

    def connect(self):
        """
        Establishes an SSH connection to the remote host.

        Returns:
            bool: True if the connection is established, False otherwise.

        Raises:
            IOError: If the connection cannot be established.
        """
        try:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh_config = paramiko.SSHConfig()
            self._user_config_file = os.path.expanduser("~/.ssh/config")
            if os.path.exists(self._user_config_file):
                with open(self._user_config_file) as f:
                    # noinspection PyTypeChecker
                    self._ssh_config.parse(f)
            self._host_config = self._ssh_config.lookup(self.host)
            if 'identityfile' in self._host_config:
                self._host_config_id = self._host_config['identityfile']
            if 'proxycommand' in self._host_config:
                self._proxy = paramiko.ProxyCommand(self._host_config['proxycommand'])
                self._ssh.connect(self._host_config['hostname'], 22, username=self.user,
                                    key_filename=self._host_config_id, sock=self._proxy)
            else:
                self._ssh.connect(self._host_config['hostname'], 22, username=self.user,
                                    key_filename=self._host_config_id)
            return True
        except IOError as e:
            print('Can not create ssh connection to {0}: {1}', self.host, e.strerror)
            raise e

    def execute(self, command: str):
        """
        Executes a command on the remote server.

        Parameters:
            command (str): The command to execute.

        Returns:
            (stdin, stdout, stderr): A tuple of file-like objects for the command's stdin, stdout, and stderr.
        """
        return self._ssh.exec_command(command)

    def list_dir(self, dir_path: str):
        """
        Lists the contents of a remote directory.

        Parameters:
            dir_path (str): The remote directory path to list.

        Returns:
            list[str]: A list of file and directory names in the remote directory.
        """
        return self.sftp.listdir(dir_path)

    def is_remote_file(self, path: str):
        """
        Checks if a given path on the remote server is a file.

        Parameters:
            path (str): The remote file path to check.

        Returns:
            bool: True if the path is a file, False otherwise.
        """
        try:
            file_attr = self.sftp.stat(path)
            # Check if the path is a regular file
            return stat.S_ISREG(file_attr.st_mode)
        except IOError as e:
            # If an IOError occurs, the file does not exist or there's an error accessing it
            return False

