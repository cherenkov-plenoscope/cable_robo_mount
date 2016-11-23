import paramiko

class RayTracingMachine(object):
    """
    Connects to a remote machine via SSH.
    Can execute remote commands and put or get files.
    The public SSH RSA key of the client must be in the list of authorized_keys.
    This way, no password is needed.

    parameter
    ---------
        hostname    The remote machine hostname.

        username    The user's name on the remote host.

        key_path    The path to the private SSH RSA key of the client
    """
    def __init__(self, hostname, username, key_path):
        self._hostname = hostname
        self._username = username
        self._key_path = key_path
        self._ssh = self._enable_connection_without_password()
        self._sftp = self._ssh.open_sftp()

    def _enable_connection_without_password(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self._hostname,
            username=self._username,
            key_filename=self._key_path)
        return ssh

    def put(self, localpath, remotepath):
        self._sftp.put(localpath=localpath, remotepath=remotepath)

    def get(self, remotepath, localpath):
        self._sftp.get(remotepath=remotepath, localpath=localpath)

    def call(self, target):
        stdin, stdout, stderr = self._ssh.exec_command(target)
        return [stdin, stdout, stderr]

    def __repr__(self):
        out = 'RayTracingMachine('
        out+= self._hostname
        out+= ')'
        return out

    def __enter__(self):
        return self

    def __exit__(self):
        self._sftp.close()
        self._ssh.close()
