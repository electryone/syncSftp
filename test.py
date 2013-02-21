#!/usr/bin/env python

import paramiko

class test:
    def __init__(self):
        None

    def sshConn(self):
        t = paramiko.Transport(('172.16.200.153', 22))
        t.connect(username='tcc', password='tcc')
        self.sftp = paramiko.SFTPClient.from_transport(t)
        #print sftp.stat('/opt/zenpacks/dir2/2.1')
        #print sftp.listdir('/opt/zenpacks/dir2/2.1')

    def testList():
        l = ['a', 'b']
        if not l:
            print "Null"
        else:
            print "nonNull"

    def mysum(L):
        print(L)
        if not L:
            print "I'm here.."
            return 0
        else:
            print "Not here.."
            return L[0] + mysum(L[1:])


##### Get the remote files list from remote dir. The list contain some attributes.#####
###### Notice, the function is recursive function. #####
    def sftpGetFtree(dir):
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
                ftree += sftpGetFtree(fPath)
            else:
                #ftree.append(fPath)
                ftree.append(('f', fMtime, fPath))
        return ftree
########## Checking the file's type by sftp ####
    def sftpPathIsdir(self, path):
        fstat = self.sftp.stat(path)
        #print "Appear.."
        fType = str(fstat)[0]
        if fType == "d":
            return True
        else:
            return False

########## Checking if a directory is empty by sftp. ######
    def sftpPathIsEmptyDir(self, path):
        if self.sftp.listdir(path) == []:
            return True
        else:
            return False

######## Deleting an entire directory tree.####
######## Notice this is a recursive function ####
    def sftpRmtree(self, path):
        if self.sftpPathIsEmptyDir(path):
            print "\tInfo: Deleting the dir: %s.." % (path) 
            self.sftp.rmdir(path)
        else:
            fs = self.sftp.listdir(path)
            for f in fs:
                absfs = path + '/' + f
                if self.sftpPathIsfile(absfs):
                    print "\tInfo: Deleting the file: %s.." % (path) 
                    self.sftp.remove(absfs)
                elif self.sftpPathIslink(absfs):
                    print "\tInfo: Deleting the link: %s.." % (path) 
                    self.sftp.unlink(absfs)
                elif self.sftpPathIsdir(absfs):
                    #print "\tInfo: Deleting the dir: %s.." % (path)
                    ### RECURSIVE Function ####
                    #self.sftpRmtree(absfs)
                    if self.sftpRmtree(absfs) == "Done":
                        continue
        return "Done" 


if __name__ == "__main__":
    #a = mysum([1, 2, 3, 4, 5])
    print 'a'
    x = test()
    x.sshConn()
    #print sftpGetFtree('/opt/zenpacks/dir2')
    #print a, len(a)
    #print x.sftpPathIsdir('/tmp/dir2')
    x.sftpRmtree('/tmp/dir1')
