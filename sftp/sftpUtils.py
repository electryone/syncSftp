#################################################################
#
################################################################
__doc__ = """syncUtils
General utility functions module about sftp.
"""

class sftpUtils:
    def __init__(self, sftp):
        """
        The parameter "sftp" is the name of transport of SFTPClient.
        Just like 'sftp', if sftp = paramiko.SFTPClient.from_transport(ssht)

        @param sftp: the name of transport of SFTPClient
        @type sftp: str
        """
        self.sftp = sftp

    def rmtree(self, path):
        """
        Deleting an entire directory tree.
        Notice this is a recursive function.
        """
        fs = self.sftp.listdir(path)
        print "fs: %s" % (fs)
        for f in fs:
            absfs = path + '/' + f
            #print "absfs: %s" % (absfs)
            if self.sftpPath1.isdir(absfs):
                if self.sftpPath1.isEmptyDir(absfs):
                    print "\tInfo: Deleting the dir: %s.." % (absfs) 
                    self.sftp.rmdir(absfs)
                else:
                    print "absfs: %s" % (absfs)
                    self.rmtree(absfs)
            elif self.sftpPath1.isfile(absfs):
                print "\tInfo: Deleting the file: %s.." % (absfs) 
                self.sftp.remove(absfs)
            elif self.sftpPath1.islink(absfs):
                print "\tInfo: Deleting the link: %s.." % (absfs) 
                self.sftp.unlink(absfs)
            else:
                print "\tWarning: Unknow file type: %s" % (absfs)
        ######
        print "\tInfo: Deleting the dir: %s.." % (path) 
        self.sftp.rmdir(path)

    def getfstree(self, dir):
        """
        Get all the remote files list from remote dir. The list contain some attributes.
        Notice, the function is recursive function.
        """ 
        sftp = self.sftp
        def getfstree1(sftp, dir):
            ftree = []
            #dir = os.path.normpath(dir)
            fs = sftp.listdir(dir)
            for f in fs:
                #fPath = os.path.join(dir, f)
                fPath = dir + '/' + f
                fstat = sftp.stat(fPath)
                fType = str(fstat)[0]
                fMtime = fstat.st_mtime
                if fType == "d":
                    ftree.append(('d', fMtime, fPath))
                    ftree += getfstree1(sftp, fPath) 
                else:
                    ftree.append(('f', fMtime, fPath))
            return ftree
        ##### Plus the attribute of parent dir to the result list##############
        ftree = [('d', sftp.stat(dir).st_mtime, dir)] + getfstree1(sftp, dir)
        return ftree


