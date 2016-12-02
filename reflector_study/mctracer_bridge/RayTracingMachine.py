import paramiko
import os

class RayTracingMachine(object):
    """
    Connects to a remote machine via SSH.
    Can execute remote commands and put or get files.
    The public SSH RSA key of the client must be in the list of authorized_keys
    of the remote host. Further, a SSH server must be running on the
    remote host.

    parameter
    ---------
        hostname    The remote machine hostname.

        username    The user's name on the remote host.

        key_path    The path to the private SSH RSA key of the client
    """
    def __init__(self, config_dict):
        self._hostname = config_dict['system']['ssh_connection']['hostname']
        self._username = config_dict['system']['ssh_connection']['username']
        self._key_path = config_dict['system']['ssh_connection']['key_path']
        self._ssh = self._make_ssh_client()
        self._sftp = self._ssh.open_sftp()

    def _make_ssh_client(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self._hostname,
            username=self._username,
            key_filename=self._key_path)
        return ssh

    def put(self, localpath, remotepath):
        """
        Copies the localpath of the local host to the remotepath on the
        remote host.
        """
        self._sftp.put(localpath=localpath, remotepath=remotepath)

    def get(self, remotepath, localpath):
        """
        Copies the remotepath from the remote host to the localpath
        of the local host.
        """
        self._sftp.get(remotepath=remotepath, localpath=localpath)

    def execute(self, command, out_path=None):
        """
        Executes the command on the remote host and returns the exit status
        of the command when the process on the remote host is done (blocking).

        Parameters
        ----------
        command         The command string to be executed on the remote host

        [out_path]      A path to store the stdout and stderr streams of the
                        command. Two text files will be created:
                        'out_path.stdout' and 'out_path.stderr'
                        The suffix 'stdout' and 'stderr' is appended to the
                        out_path.
        """
        transport = self._ssh.get_transport()
        channel = transport.open_session()
        channel.exec_command(command)
        if out_path is not None:
            stdout = channel.makefile('r')
            stderr = channel.makefile_stderr('r')
        exit_status = channel.recv_exit_status()
        if out_path is not None:
            self._write_out_stream_to_file(stdout, out_path+'.stdout')
            self._write_out_stream_to_file(stderr, out_path+'.stderr')
        return exit_status

    def _write_out_stream_to_file(self, stream, path):
        f = open(path, 'w')
        for line in stream.readlines():
            f.write(line)
        f.close()

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
