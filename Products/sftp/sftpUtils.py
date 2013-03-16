#################################################################
#
################################################################
__doc__ = """syncUtils
General utility functions module about sftp.
"""
from sftpPath import sftpPath
import sys

class sftpUtils(sftpPath):
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
        #print "fs: '%s'" % (fs)
        for f in fs:
            absfs = path + '/' + f
            #print "absfs: '%s'" % (absfs)
            if self.isdir(absfs):
                if self.isEmptyDir(absfs):
                    #print "\tInfo: Deleting the dir: '%s'.." % (absfs) 
                    self.sftp.rmdir(absfs)
                else:
                    #print "absfs: '%s'" % (absfs)
                    self.rmtree(absfs)
            elif self.isfile(absfs):
                #print "\tInfo: Deleting the file: '%s'.." % (absfs) 
                self.sftp.remove(absfs)
            elif self.islink(absfs):
                #print "\tInfo: Deleting the link: '%s'.." % (absfs) 
                self.sftp.unlink(absfs)
            else:
                print "\tWarning: Unknow file type: '%s'" % (absfs)
        ######
        #print "\tInfo: Deleting the dir: '%s'.." % (path) 
        self.sftp.rmdir(path)

    def getfstree(self, dir):
        """
        Get all the remote files list from remote dir. The list contain some attributes.
        Notice, the function is recursive function.
        @param dir: the path of dir
        @type : str
        @return : all the remote file list in the dir. The list contains some attributes.
        @rtype: list
        """ 
        sftp = self.sftp
        def getfstree1(sftp, dir):
            ftree = []
            #dir = os.path.normpath(dir)
            fs = sftp.listdir(dir)
            for f in fs:
                #fPath = os.path.join(dir, f)
                fPath = dir + '/' + f
                fstat = sftp.lstat(fPath)
                fType = str(fstat)[0]
                #print "%s %s" % (f, fType)
                fMtime = fstat.st_mtime
                if fType == "d":
                    ftree.append(('d', fMtime, fPath))
                    ftree += getfstree1(sftp, fPath) 
                elif fType == "-":
                    ftree.append(('f', fMtime, fPath))
                elif fType == "l":
                    print "\tWarning: This is a Symbolic Links file, it will not be sync: '%s'" % (fPath)
                    continue
                    #ftree.append(('l', fMtime, fPath))
                else:
                    print "\tWarning: Unknow file type: '%s'" % (fType)
            return ftree
        ##### Plus the attribute of parent dir to the result list##############
        ftree = [('d', sftp.stat(dir).st_mtime, dir)] + getfstree1(sftp, dir)
        return ftree

    def deleteRemoteFile(self, dlist):
        """
        Deleting the remote files that be deleted since last sync period.
        """
        for path in dlist:
            print "\tInfo: The file to be synced in remote: '%s'" % (path)
            if self.isfile(path):
                print "\tInfo: Deleting the file: '%s'.." % (path) 
                self.sftp.remove(path)
            elif self.isdir(path):
                print "\tInfo: Deleting the dir: '%s'.." % (path) 
                self.rmtree(path)
            else:
                print "\tWarning: Unknow file type: '%s'" % (path)
                continue

    def getFile(self, rf, lf):
        """
        Getting some files by sftp
        """
        try:
            print "\tInfo: Getting the file from remote: '%s'.." % (rf) 
            self.sftp.get(rf, lf)
        except IOError, e:
            print "\tError: Getting the file from remote: '%s': '%s'" % (rf, e)
            sys.exit(1)

    def putFile(self, lf, rf):
        try:
            print "\tInfo: Putting the file to remote: '%s'.." % (lf) 
            self.sftp.put(lf, rf)
        except IOError, e:
            print "\tError: Putting the file to remote: '%s': '%s'" % (lf, e)
            sys.exit(1)

