#!/usr/bin/env python
"""
 For Linux2Linux
 The script is usable 4 the environment of linux2Linux . If u'r in any other os environment.
 Please using which version the script based on the os.


 Copyright (c) 2013-02-21 Jackie

 Version:1.0
 syncSftp.py 
 Author:Jackie Ma <jacknet.ma@gmail.com>
 Please report bug to me.

 Sync the modified files by sftp protocol.

"""

import paramiko
import os, sys
import time, shutil

##### get current time & store it####
def getCurTime():
    f = open('currentTime', 'w')
    f.write(str(time.time()))
    f.close()



class syncSftp:
########## Variables #########
    ### the deeply remote file list. The file's path is absolute path. ####
    _rFList = []

    ### The deeply local file list. The file's path is absolute path. ####
    _lFList = []

    #### The deeply modified files list in the remote. The file's path is absolute path. ####
    _rMFList = []

    #### The deeply modified dirs list in the remote. The dir's path is absolute path. ####
    _rMDList = []

    #### The deeply modified files list in the local. The file's path is absolute path. ####
    _lMFList = []

    #### The deeply modified dirs list in the local. The dir's path is absolute path. ####
    _lMDList = []

    #### The dir list about the remote directory architecture ###
    #_dirs = []

    ### The local dir list to be created according to remote dirs ####
    _newLocalDirs = []

    ### The local dir list to be created according to remote dirs ####
    _newRemoteDirs = []

    ####### The local dir list from local dir.##########
    _lDirs = []

    ####### The local file list to be modified #
    _localFile = []

    ##### The Last check time. In the other words, it's the time run this program last time.###
    _lastCheckTime = 0


#######################################################
    def __init__(self, hostname, username, password, port, desDir, localDir):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.desDir = desDir
        self.localDir = localDir
        #### Some Initial action ######
        self.checkPath(self.localDir)
        self.checkPath(self.desDir)
        self.createIniDir()


##################################### Some Utilities ##########################################
###### Checking the path that user has entered. The path must be abosulte and standard. ########
    def checkPath(self, path):
        if os.path.isabs(path):
            pass
        else:
            print "Error: Please enter the absolute path: %s" % (path)
            sys.exit(1)



###### Convert path to list #####
    def path2list(self, path):
        #path = os.path.normpath(path)
        plist = path.split('/')[1:]
        return plist


##### Convert list to path ######
    def list2path(self, list):
        n = 0
        path = ''
        while n < len(list):
            path = path + '/' + list[n]
            n = n + 1
        return path

##### Check if a path is exist by sftp. Return True or False. #####
    def sftpPathIsExist(self, path):
        try:
            self.sftp.stat(path)
        except:
            #print "sftpPathIsExist: The path is not exist: %s" (path)
            return False
        else:
            return True



###### Create the dir that isn't exist. #######
    def createDirNotExist(self, dir):
        if not os.path.exists(dir):
            print "\tInfo: Create the dir: %s.." % (dir)
            os.makedirs(dir)

###### Create the dir that isn't exist by sftp. #######
    def sftpCreateDirNotExist(self, dir):
        #print "sftpCreateDirNotExist():"
        if not  self.sftpPathIsExist(dir):
            print "\tInfo: Create the dir: %s.." % (dir)
            self.sftp.mkdir(dir)


###### Converting the path to a new path(dir2 + path[path.index((dir1'sBasename)):]) according to dir1's basename and dir2.#####
###### 4Example, path2nPath('/opt/zenpacks', '/tmp', '/opt/zenpacks/dir1'), so the result is '/tmp/zenpacks/dir1'. ############
###### Notice 'path' must be a absolute path. ######
    def path2nPath(self, dir1, dir2, path):
        ### Normalizing these paths #####
        #dir2 = os.path.normpath(dir2)
        #####Test if absolute path. ##############
        if os.path.isabs(dir1) and os.path.isabs(dir2) and os.path.isabs(path): 
            dirBase = os.path.basename(dir1)
            pathList = self.path2list(path)
            baseNameLoc = pathList.index(dirBase)
            nPathList = pathList[baseNameLoc:]
            #nPath = self.list2path(nPathList)
            nPath = dir2 + self.list2path(nPathList)
            return nPath
        else:
            print "\tError: Not absolute path: %s,%s,%s" % (dir1, dir2, path)
            sys.exit(1)

###### Get the modified files list since last check. Chop off the redundant attributes #####
###### Please notice the format of 'fs'. ##
######It looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')] ##
    def mfsInfo(self, fs):
        if isinstance(fs, list):
            mfs = []
            mds = []
            for f in fs:
                if f[0] == 'f' and f[1] > self._lastCheckTime:
                    mfs.append(f[2])
                elif f[0] == 'd' and f[1] > self._lastCheckTime:
                    mds.append(f[2])
                elif f[0] != 'd' and f[0] != 'f' or f[1] < 0: 
                    print "\tWarning: Unknow file format: %s" % (f)
                    continue

            print "\tInfo: The number of file to be modified are: file: %s dir: %s" % (len(mfs), len(mds))
            return (mfs, mds)
        else:
            print "\tError: It must be a list: %s" % (fs)
            sys.exit(1)

###### Get all the dir list from a parent dir.Please notice the format of fs list. #####
######It looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')] ##
    def dirList(self, fs):
        ###Checking if it's list.
        if isinstance(fs, list):
            dirs = []
            for f in fs:
                if f[0] == "d":
                    dirs.append(f)
                elif f[0] != 'd' and f[0] != 'f' or f[1] < 0: 
                    print "\tWarning: Unknow file format: %s" % (f)
                    continue
            return dirs
        else:
            print "\tError: It must be a list: %s" % (fs)
            sys.exit(1)

####### Checking the relation of set A and set B. If A is a subset of,
#######but not equal to,B, then return True. ##############
    def isProperSubset(self, A, B):
        ####Checking if it's sets.
        if isinstance(A, set) and isinstance(B, set):
            if A.issubset(B) and A != B:
                return True
            else:
                return False
        else:
            print "\tError: It must be sets : %s,%s" % (A, B)
            sys.exit(1)

########## Checking the file's type by sftp ####
    def sftpPathIsdir(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "d":
            return True
        else:
            return False

    def sftpPathIsfile(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "-":
            return True
        else:
            return False

    def sftpPathIslink(self, path):
        fstat = self.sftp.stat(path)
        fType = str(fstat)[0]
        if fType == "l":
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
        fs = self.sftp.listdir(path)
        print "fs: %s" % (fs)
        for f in fs:
            absfs = path + '/' + f
            #print "absfs: %s" % (absfs)
            if self.sftpPathIsdir(absfs):
                if self.sftpPathIsEmptyDir(absfs):
                    print "\tInfo: Deleting the dir: %s.." % (absfs) 
                    self.sftp.rmdir(absfs)
                else:
                    print "absfs: %s" % (absfs)
                    self.sftpRmtree(absfs)
            elif self.sftpPathIsfile(absfs):
                print "\tInfo: Deleting the file: %s.." % (absfs) 
                self.sftp.remove(absfs)
            elif self.sftpPathIslink(absfs):
                print "\tInfo: Deleting the link: %s.." % (absfs) 
                self.sftp.unlink(absfs)
            else:
                print "\tWarning: Unknow file type: %s" % (absfs)
        ######
        print "\tInfo: Deleting the dir: %s.." % (path) 
        self.sftp.rmdir(path)

##### Get all the remote files list from remote dir. The list contain some attributes.#####
###### Notice, the function is recursive function. #####
    def sftpGetFtree(self, dir):
        #####
        sftp = self.sftp
        def sftpGetFtree1(sftp, dir):
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
                    ftree += sftpGetFtree1(sftp, fPath) 
                else:
                    ftree.append(('f', fMtime, fPath))
            return ftree
        ##### Plus the attribute of parent dir to the result list##############
        ftree = [('d', sftp.stat(dir).st_mtime, dir)] + sftpGetFtree1(sftp, dir)
        return ftree

####### Get all the local file list from local dir. The list contains some attributes. ############
###### Notice, the function is recursive function. #####
    def getFtree(self, dir):
        ##### 
        def getFtree1(dir):
            fs = os.listdir(dir)
            #print "getFtree1(): dir: %s fs: %s" % (dir, fs)
            ftree = []
            for f in fs:
                fPath = os.path.join(dir, f)
                fMtime = os.stat(fPath).st_mtime
                if os.path.isdir(fPath):
                    ftree.append(('d', fMtime, fPath))
                    ftree += getFtree1(fPath) 
                    #self.getFtree1(fPath)
                else:
                    ftree.append(('f', fMtime, fPath))
            return ftree
        ##### Plus the attribute of parent dir to the result list##############
        ftree = [('d', os.stat(dir).st_mtime, dir)] + getFtree1(dir) 
        return ftree

#####Not working## List the remote dir, but the results is absolute path.#####
    def sftpLdirAbs(self, dir):
        absfs = []
        fs =  self.sftp.listdir(dir)
        for f in fs:
            fPath = dir + '/' + f
            absfs.append(fPath)
        return absfs

######Not working## # List the local dir's file list, but the results is absolute path.#####
    def ldirAbs(self, dir):
        absfs = []
        fs = os.listdir(dir)
        for f in fs:
            fPath = os.path.join(dir, f)
            absfs.append(fPath)
        return absfs


################################# Utilities Ends #########################################



##### Getting the _rFList's value ######
    def getRFList(self, dir):
        self._rFList = self.sftpGetFtree(dir)

##### Getting the _lFList's value #####
    def getLFList(self, dir):
        self._lFList = self.getFtree(dir)



###### Create the initial directory in the local ###
    def createIniDir(self):
        dirBase = os.path.basename(self.desDir)
        #print "createInidir():dirBase: %s" % (dirBase)
        iniDir = os.path.join(self.localDir, dirBase)
        self.createDirNotExist(iniDir)


####Not working## Rebuilding the local dirs list to be created according to remote dirs. Chop off the redundant attributes. #########
    def buildLDirList(self):
        rDirs = self.dirList(self._rFList)
        for d in rDirs:
            d = d[2]
            lDir = self.path2nPath(self.desDir, self.localDir, d)
            self._newLocalDirs.append(lDir)
            
####Not working## ### Rebuilding the remote dirs list to be created according to local dirs. Chop off the redundant attributes. #########
    def buildRDirList(self):
        lDirs = self.dirList(self._lFList)
        for d in lDirs:
            d = d[2]
            rDir = self.path2nPath(self.desDir, os.path.split(self.desDir)[0], d)
            self._newRemoteDirs.append(rDir)



#####Not working#### get the local file list that to be modified ####
    def getLocalFileInfo(self):
        for f in self._rMFList:
            lFile = self.path2nPath(self.desDir, self.localDir, f)
            self._localFile.append(lFile)


###### Creating the local dirs according to remote dir path. ####
###### 'dList' must be a path list.####
    def createDirLocal(self, dList):
        if isinstance(dList, list):
            for dir in dList:
                ld = self.path2nPath(self.desDir, self.localDir, dir)
                self.createDirNotExist(ld)
        else:
            print "\tError: This is not a list: %s" % (dList)
            
###### Creating the remote dirs according to local dir path. ####
###### 'dList' must be a path list.####
    def createDirRemote(self, dList):
        if isinstance(dList, list):
            for dir in dList:
                rd = self.path2nPath(self.desDir, os.path.split(self.desDir)[0], dir)
                self.sftpCreateDirNotExist(rd)
        else:
            print "\tError: This is not a list: %s" % (dList)

##### Connecting to remote host by ssh ###
    def sshConn(self):
        paramiko.util.log_to_file('paramiko.log')
        ssht = paramiko.Transport((self.hostname, self.port))
        self.ssht = ssht
        try:
            ssht.connect(username=self.username, password=self.password)
        except Exception, err:
            print "Error: Connect remote host: %s" % err
            print "Quiting, please wait for a moment..."
            sys.exit(1)
        print 'Info: Successful: ssh connection'
        self.sftp = paramiko.SFTPClient.from_transport(ssht)

###### get the last modified time #######
    def getLastCheckTime(self):
        if os.path.isfile('currentTime'):
            f = open('currentTime', 'r')
            self._lastCheckTime = float(f.read())
            f.close()
            if self._lastCheckTime == 0:
                print "Info: Initializing sync.."
            else:
                print "Last check Time: %s" % (time.strftime("%Y-%m-%d,%H:%M:%S",time.localtime(self._lastCheckTime)))
        else:
            print "Info: Initializing sync.."

########## Get the modified files from remote dir #####
    def getRMFs(self):
        print "Modifying local.."
        self._rMFList, self._rMDList = self.mfsInfo(self._rFList)
        self.createDirLocal(self._rMDList)
        #self.sftp.get('/opt/Twisted/clientFactory.py', os.path.join('/tmp', 'clientFactory.py'))
        for f in self._rMFList:
            ###### The new local path to get the modified file ######
            lf = self.path2nPath(self.desDir, self.localDir, f)
            try:
                print "\tInfo: Getting the file from remote: %s.." % (f) 
                self.sftp.get(f, lf)
            except IOError, e:
                print "\tError: Getting the file from remote: %s: %s" % (f, e)
                sys.exit(1)
    #####Removing some files ###############
        self.rmLocalFile(self._rMDList)

########## Put the modified files from local dir to the remote dir ####
    def putLMFs(self):
        print "Modifying remote.."
        self._lMFList, self._lMDList = self.mfsInfo(self._lFList)
        self.createDirRemote(self._lMDList)
        for f in self._lMFList:
            ##### The new remote path to put the modified file ####
            rf = self.path2nPath(self.desDir, os.path.split(self.desDir)[0], f)
            #print "putLMFs():rf: %s" % (rf)
            try:
                print "\tInfo: Putting the file to remote: %s.." % (f) 
                self.sftp.put(f, rf)
            except IOError, e:
                print "\tError: Putting the file to remote: %s: %s" % (f, e)
                sys.exit(1)
    #####Removing some files ###############
        self.rmRemoteFile(self._lMDList)

########## Remove the same file against the file that has been removed in the remote. ####
########## 'rdl' is the remote directory list that be modified. ###
    def rmLocalFile(self, rdl):
        for dir in rdl:
            ndir = self.path2nPath(self.desDir, self.localDir, dir)
            rl = self.sftp.listdir(dir)
            ll = os.listdir(ndir)
            print "\tInfo: rl: %s ll: %s" % (rl, ll)
            rl = set(rl)
            ll = set(ll)
            if self.isProperSubset(rl, ll):
                result = ll - rl
                print "\tInfo: rmLocalFile(): result: %s" % (result)
                for path in result:
                    path = os.path.join(ndir, path)
                    if os.path.isfile(path):
                        print "\tInfo: Deleting the file: %s.." % (path) 
                        os.remove(path)
                    elif os.path.isdir(path):
                        print "\tInfo: Deleting the dir: %s.." % (path) 
                        shutil.rmtree(path)
                    else:
                        print "\tWarning: Unknow file type: %s" % (path)
                        continue
            else:
                print "\tInfo: It's not a Proper subset:  rl(%s),ll(%s)" % (rl, ll)

########## Remove the same file against the file that has been removed in the local. ####
########## 'ldl' is the local directory list that be modified. ###
    def rmRemoteFile(self, ldl):
        for dir in ldl:
            ndir = self.path2nPath(self.desDir, os.path.split(self.desDir)[0], dir)
            ll = os.listdir(dir)
            rl = self.sftp.listdir(ndir)
            print "\tInfo: ll: %s rl: %s" % (ll, rl)
            ll = set(ll)
            rl = set(rl)
            if self.isProperSubset(ll, rl):
                result = rl - ll
                print "\tInfo: rmLocalFile(): result: %s" % (result)
                for path in result:
                    #tpath = os.path.join(dir, path)
                    path = ndir + '/' + path
                    if self.sftpPathIsfile(path):
                        print "\tInfo: Deleting the file: %s.." % (path) 
                        self.sftp.remove(path)
                    elif self.sftpPathIsdir(path):
                        self.sftpRmtree(path)
                    else:
                        print "\tWarning: Unknow file type: %s" % (path)
                        continue
            else:
                print "\tInfo: ll(%s) is not a Proper subset of rl(%s)" % (ll, rl)











#####  close ssh connection ###
    def sshClose(self):
        self.ssht.close()



if __name__ == "__main__":
    #self-test code
    #getCurTime()
    x = syncSftp('172.16.200.153', 'tcc', 'tcc', 22, '/opt/zenpacks', '/tmp')
    x.sshConn()
    #print x.sftpPathIsExist('/opt/zenpacks/dir1/dir789')
    #x.sftpCreateDirNotExist('/opt/zenpacks/dir1/dir789')
    x.getRFList('/opt/zenpacks')
    x.getLFList('/tmp/zenpacks')
    #print "%s %s\n\n\n" % (x._rFList, len(x._rFList))
    #print "%s %s\n\n\n" % (x._lFList, len(x._lFList))
    print "The number of remote files: %s" % (len(x._rFList))
    print "The number of local files: %s" % (len(x._lFList))
    #x.buildLDirList()
    #x.buildRDirList()
    x.getLastCheckTime()
    #x.getLocalFileInfo()
    x.getRMFs()
    x.putLMFs()
    x.sshClose()
    getCurTime()
    print "\nSync finished."

