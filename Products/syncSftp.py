############################################################
#
#
############################################################

import paramiko
import os, sys
import time, shutil

##Import my modules
from Products.sftp.sftpPath import sftpPath
from Products.sftp.sftpUtils import sftpUtils
from Products.Utils import Utils


class syncSftp:
    """
    Headquarters of this program.
    """

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

    ##### The Last check time. In the other words, it's the time run this program last time.###
    _lastCheckTime = 0

    #### The root dir of syncSftp is living.
    _rootDir = os.path.dirname(os.getcwd()) 

    #### The Products dir of syncSftp is living.
    _proDir = os.path.join(_rootDir, 'Products') 

    #### The Logs dir of syncSftp is living.
    _logDir = os.path.join(_rootDir, 'Logs') 

    #### The Engine dir of syncSftp is living.
    _engDir = os.path.join(_rootDir, 'Engine') 

    #### The Setting dir of syncSftp is living.
    _setDir = os.path.join(_rootDir, 'Setting')

    #### The time control file
    timeContr = os.path.join(_setDir, 'currentTime')

    #### The log file of ssh connection.
    paramikoLog = os.path.join(_logDir, 'paramiko.log')
    

#############################################################################
#### Bounding some methods from function module.
    utilities = Utils()


#######################################################
    def __init__(self, hostname, username, password, port, desDir, localDir):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.desDir = desDir
        self.localDir = localDir
        #### Some Initial action ######
        self.utilities.checkPath(self.localDir)
        self.utilities.checkPath(self.desDir)
        self.createIniDir()

    def getCurTime(self):
        """
        get current time & store it
        """
        
        f = open(self.timeContr, 'w')
        f.write(str(time.time()))
        f.close()

    def getLastCheckTime(self):
        """
        get the last modified time.
        """
        if os.path.isfile(self.timeContr):
            f = open(self.timeContr, 'r')
            self._lastCheckTime = float(f.read())
            f.close()
            if self._lastCheckTime == 0:
                print "Info: Initializing sync.."
            else:
                print "Last check Time: %s" % (time.strftime("%Y-%m-%d,%H:%M:%S",time.localtime(self._lastCheckTime)))
        else:
            print "Info: Initializing sync.."

    def getRFList(self, dir):
        """
        Getting the _rFList's value
        """
        self._rFList = self.sftpUtils1.getfstree(dir)

    def getLFList(self, dir):
        """
        Getting the _lFList's value.
        """
        self._lFList = self.utilities.getFtree(dir)



    def createIniDir(self):
        """
        Create the initial directory in the local.
        """
        dirBase = os.path.basename(self.desDir)
        #print "createInidir():dirBase: %s" % (dirBase)
        iniDir = os.path.join(self.localDir, dirBase)
        self.utilities.createDirNotExists(iniDir)

    def createDirLocal(self, dList):
        """
        Creating the local dirs according to the remote path of dir. 
        'dList' must be a path list.
        """
        if isinstance(dList, list):
            for dir in dList:
                ld = self.utilities.path2nPath(self.desDir, self.localDir, dir)
                self.utilities.createDirNotExists(ld)
        else:
            print "\tError: This is not a list: %s" % (dList)
            
    def createDirRemote(self, dList):
        """
        Creating the remote dirs according to the local dir path. 
        'dList' must be a path list.
        """
        if isinstance(dList, list):
            for dir in dList:
                rd = self.utilities.path2nPath(self.desDir, os.path.split(self.desDir)[0], dir)
                self.sftpPath1.mkdirIfNotExists(rd)
        else:
            print "\tError: This is not a list: %s" % (dList)

    def getRMFs(self):
        """
        Getting the modified files from remote dir.
        """
        print "Modifying local.."
        self._rMFList, self._rMDList = self.utilities.mfsInfo(self._rFList, self._lastCheckTime)
        self.createDirLocal(self._rMDList)
        #self.sftp.get('/opt/Twisted/clientFactory.py', os.path.join('/tmp', 'clientFactory.py'))
        for f in self._rMFList:
            ###### The new local path to get the modified file ######
            lf = self.utilities.path2nPath(self.desDir, self.localDir, f)
            try:
                print "\tInfo: Getting the file from remote: %s.." % (f) 
                self.sftp.get(f, lf)
            except IOError, e:
                print "\tError: Getting the file from remote: %s: %s" % (f, e)
                sys.exit(1)
    #####Removing some files ###############
        self.rmLocalFile(self._rMDList)

    def putLMFs(self):
        """
        Putting the modified files from local dir to the remote dir.
        """
        print "Modifying remote.."
        self._lMFList, self._lMDList = self.utilities.mfsInfo(self._lFList, self._lastCheckTime)
        self.createDirRemote(self._lMDList)
        for f in self._lMFList:
            ##### The new remote path to put the modified file ####
            rf = self.utilities.path2nPath(self.desDir, os.path.split(self.desDir)[0], f)
            #print "putLMFs():rf: %s" % (rf)
            try:
                print "\tInfo: Putting the file to remote: %s.." % (f) 
                self.sftp.put(f, rf)
            except IOError, e:
                print "\tError: Putting the file to remote: %s: %s" % (f, e)
                sys.exit(1)
    #####Removing some files ###############
        self.rmRemoteFile(self._lMDList)

    def rmLocalFile(self, rdl):
        """
        Remove the same file against the file that has been removed in the remote. 
        'rdl' is the remote directory list that has be modified.
        """
        for dir in rdl:
            ndir = self.utilities.path2nPath(self.desDir, self.localDir, dir)
            rl = self.sftp.listdir(dir)
            ll = os.listdir(ndir)
            print "\tInfo: rl: %s ll: %s" % (rl, ll)
            rl = set(rl)
            ll = set(ll)
            if self.utilities.isProperSubset(rl, ll):
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
                continue

    def rmRemoteFile(self, ldl):
        """
        Remove the same file against the file that has been removed in the local. 
        'ldl' is the local directory list that has be modified.
        """
        for dir in ldl:
            ndir = self.utilities.path2nPath(self.desDir, os.path.split(self.desDir)[0], dir)
            ll = os.listdir(dir)
            rl = self.sftp.listdir(ndir)
            print "\tInfo: ll: %s rl: %s" % (ll, rl)
            ll = set(ll)
            rl = set(rl)
            if self.utilities.isProperSubset(ll, rl):
                result = rl - ll
                print "\tInfo: rmLocalFile(): result: %s" % (result)
                for path in result:
                    #tpath = os.path.join(dir, path)
                    path = ndir + '/' + path
                    if self.sftpPath1.isfile(path):
                        print "\tInfo: Deleting the file: %s.." % (path) 
                        self.sftp.remove(path)
                    elif self.sftpPath1.isdir(path):
                        self.sftpUtils1.rmtree(path)
                    else:
                        print "\tWarning: Unknow file type: %s" % (path)
                        continue
            else:
                print "\tInfo: ll(%s) is not a Proper subset of rl(%s)" % (ll, rl)
                continue

    def sshConn(self):
        """
        Connecting to remote host by ssh.
        """
        paramiko.util.log_to_file(self.paramikoLog)
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
        # Bounding the method
        self.sftpPath1 = sftpPath(self.sftp)
        self.sftpUtils1 = sftpUtils(self.sftp)

    def sshClose(self):
        """
        close ssh connection.
        """ 
        self.ssht.close()



#if __name__ == "__main__":
    #self-test code
    #x = syncSftp()
