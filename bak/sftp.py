##########################################
#
#
##########################################

__doc__ = """sftp
"""

def __init__():
    """
        The parameter "sftp" is the name of transport of SFTPClient.
        Just like 'sftp', if sftp = paramiko.SFTPClient.from_transport(ssht)
    
        @param sftp: the name of transport of SFTPClient
        @type sftp: str
    """
    #self.sftp = sftp
    import os
    os.mkdir('/tmp/dir002')
    print 'Hello, World!'

class path:
    """ 
    This module implements some functions on pathnames.
    """
    def sshConn(self, hostname, port, username, password):
        """
        Connecting to remote host by ssh.
        """
        paramiko.util.log_to_file('paramiko.log')
        ssht = paramiko.Transport((hostname, port))
        #self.ssht = ssht
        try:
            ssht.connect(username=username, password=password)
        except Exception, err:
            print "Error: Connect remote host: %s" % err
            print "Quiting, please wait for a moment..."
            sys.exit(1)
        print 'Info: Successful: ssh connection'
        self.sftp = paramiko.SFTPClient.from_transport(ssht)

    def exists(self, path):
        """
        Check if a path is exist by sftp. Return True or False.
        """
        try:
            self.sftp.stat(path)
        except:
            #print "exists: The path is not exist: %s" (path)
            return False
        else:
            return True

    def mkdirIfNotExists(self, dir):
        """
        Create the dir that isn't exist by sftp.
        """
        if not  self.exists(dir):
            print "\tInfo: Create the dir: %s.." % (dir)
            self.sftp.mkdir(dir)

    # Some below functions are used to check the file's type by sftp.
    def isdir(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "d":
            return True
        else:
            return False

    def isfile(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "-":
            return True
        else:
            return False

    def islink(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "l":
            return True
        else:
            return False

    def isEmptyDir(self, path):
        """
        Checking if a directory is empty by sftp.
        """
        if self.sftp.listdir(path) == []:
            return True
        else:
            return False




