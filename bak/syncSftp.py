#!/usr/bin/env python
"""
 For Linux2Linux
 The script is usable 4 the environment of linux2Linux . If u'r in any other os environment.
 Please using the version script based on the os.


 Version:1.1
 syncSftp.py 
 Author:Jackie Ma <jacknet.ma@gmail.com>
 Please report bug to me.

 Sync the modified files by sftp protocol.

"""

import paramiko
import os, sys
import time

##### get current time & store it####
def getCurTime():
    f = open('currentTime', 'w')
    f.write(str(time.time()))
    f.close()



class syncSftp:
########## Variables #########
    ### remote files list
    _files = []

    #### The modified files list in the remote
    _Mfs = []

    #### The dir list about the remote directory architecture ###
    _dirs = []

    ### The local dir list to be created according to remote dirs ####
    localSubDir = []

    ####### the local file list to be modified #
    localFile = []


#######################################################
    def __init__(self, hostname, username, password, port, desDir, localDir):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.desDir = desDir
        self.localDir = os.path.normpath(localDir)
        self.createIniDir()


##################################### Some Utilities ##########################################
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


###### Create the dir that isn't exist. #######
    def createNotExistDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


###### Converting the remote path to the local path based on the remote dir & the local dir ####
    def rPath2lPath(self, rDir, lDir, rPath):
        ### Normalizing these paths #####
        #rDir = os.path.normpath(rDir)
        lDir = os.path.normpath(lDir)
        #rPath = os.path.normpath(rPath)
        ###########
        dirBase = os.path.basename(rDir)
        rPathList = self.path2list(rPath)
        baseNameLoc = rPathList.index(dirBase)
        nRPathList = rPathList[baseNameLoc:]
        nRPath = self.list2path(nRPathList)
        nPath = lDir + nRPath
            #self.localSubDir.append(fPath)
        return nPath


################################# Utilities Ends #########################################


###### Create the initial directory in the local ###
    def createIniDir(self):
        dirBase = os.path.basename(self.desDir)
        #print "createInidir():dirBase: %s" % (dirBase)
        iniDir = os.path.join(self.localDir, dirBase)
        self.createNotExistDir(iniDir)


###### get the local dirs list to be created according to remote dirs ####
    def getLocalDirInfo(self):
        for dir in self._dirs:
            dir = dir[2] 
            lDir = self.rPath2lPath(self.desDir, self.localDir, dir)
            self.localSubDir.append(lDir)
            

###### get the local file list that to be modified ####
    def getLocalFileInfo(self):
        for f in self._Mfs:
            lFile = self.rPath2lPath(self.desDir, self.localDir, f)
            self.localFile.append(lFile)


###### create the local dirs according to remote dirs ####
    def createLocalDir(self):
        for dir in self.localSubDir:
            self.createNotExistDir(dir)
            

##### connect to remote host by ssh ###
    def sshConn(self):
        paramiko.util.log_to_file('paramiko.log')
        t = paramiko.Transport((self.hostname, self.port))
        self.t = t
        try:
            t.connect(username=self.username, password=self.password)
        except Exception, err:
            print " Failure: Connect remote host: %s" % err
            print "Quiting, please wait for a moment..."
            sys.exit(1)
        print 'Successful: ssh connection'
        self.sftp = paramiko.SFTPClient.from_transport(t)


##### get remote files list from the remote dir #####
    def getFileInfo(self, dir):
        #dir = os.path.normpath(dir)
        fs = self.sftp.listdir(dir)
        for f in fs:
            #fPath = os.path.join(dir, f)
            fPath = dir + '/' + f
            fstat = self.sftp.stat(fPath)
            fType = str(fstat)[0]
            fMtime = fstat.st_mtime
            if fType == "d":
                self._files.append(('d', fMtime, fPath))
                self.getFileInfo(fPath)
            else:
                #self._files.append(fPath)
                self._files.append(('f', fMtime, fPath))


###### get dirs list from the remote dir #####
    def getDirInfo(self):
        for f in self._files:
            if f[0] == "d":
                self._dirs.append(f)


###### get the last modified time #######
    def getLastCheckTime(self):
        f = open('currentTime', 'r')
        lastCheckTime = f.read()
        f.close()
        self.lastCheckTime = lastCheckTime


###### get the modified files list from last check #####
    def getMfsInfo(self):
        for f in self._files:
            if f[0] != 'd' and f[1] > float(self.lastCheckTime):
                self._Mfs.append(f[2])


########## get the modified files from remote dir #####
    def get_Mfs(self):
        #self.sftp.get('/opt/Twisted/clientFactory.py', os.path.join('/tmp', 'clientFactory.py'))
        for f in self._Mfs:
            lf = self.rPath2lPath(self.desDir, self.localDir, f)
            try:
                print "\tModifying the file:%s.." % (f) 
                self.sftp.get(f, lf)
            except IOError, e:
                print "\tFailure: retrieve %s: %s" % (f, e)


#####  close ssh connection ###
    def sshClose(self):
        self.t.close()



if __name__ == "__main__":
    #self-test code
    #getCurTime()
    x = syncSftp('172.16.200.153', 'tcc', 'tcc', 22, '/opt/zenpacks', '/tmp')
    x.sshConn()
    x.getFileInfo('/opt/zenpacks')
    x.getDirInfo()
    x.getLocalDirInfo()
    x.createLocalDir()
    x.getLastCheckTime()
    x.getMfsInfo()
    print "The number of files that to be modified:%s" % len(x._Mfs)
    #x.getLocalFileInfo()
    x.get_Mfs()
    x.sshClose()
    print "\nModify finished."
    getCurTime()
