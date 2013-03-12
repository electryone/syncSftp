############################################################################
#
###################### Some Utilities ##########################
#
############################################################################

__doc__ = """Utils
General utility functions module.
"""

import os, sys
import pickle

class Utils:
    def checkPath(self, path):
        """
        Checking the path that user has entered. The path must be abosulte and standard.
        """
        if os.path.isabs(path):
            pass
        else:
            print "Error: Please enter the absolute path: %s" % (path)
            sys.exit(1)

    def path2list(self, path):
        """
        Convert path to list.
        """
        #path = os.path.normpath(path)
        plist = path.split('/')[1:]
        return plist

    def list2path(self, list):
        """
        Convert list to path.
        """
        n = 0
        path = ''
        while n < len(list):
            path = path + '/' + list[n]
            n = n + 1
        return path

    def path2nPath(self, dir1, dir2, path):
        """
        Converting the path to a new path(dir2 + path[path.index((dir1'sBasename)):]) according to dir1's basename and dir2.
        4Example, path2nPath('/opt/zenpacks', '/tmp', '/opt/zenpacks/dir1'), so the result is '/tmp/zenpacks/dir1'.
        Notice 'path' must be a absolute path.
        """
        #####Test if absolute path. ##############
        if os.path.isabs(dir1) and os.path.isabs(dir2) and os.path.isabs(path): 
            dirBase = os.path.basename(dir1)
            pathList = self.path2list(path)
            baseNameLoc = pathList.index(dirBase)
            nPathList = pathList[baseNameLoc:]
            nPath = dir2 + self.list2path(nPathList)
            return nPath
        else:
            print "\tError: Not absolute path: %s,%s,%s" % (dir1, dir2, path)
            sys.exit(1)

    def mkdirIfNotExists(self, dir):
        """
        Create the dir that isn't exist.
        """
        if not os.path.exists(dir):
            print "\tInfo: Create the dir: %s.." % (dir)
            os.makedirs(dir)

    def mfsInfo(self, fList, tm):
        """
        Get the new file list against the time. Chop off the redundant attributes.
        @param fList:  the file list to be check out.
        @param tm:  time since the epoch. 
        @type fList:   list.  The format looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')]
        @type tm:   float 
        @return:    a list is new against the time.  
        @rtype: list
        """
        ###Checking if it's list.
        self.testIsinstance(fList, list)
        ###Checking if it's float.
        self.testIsinstance(tm, float)
        ######
        mfs = []
        mds = []
        for f in fList:
            if f[0] == 'f' and f[1] > tm:
                mfs.append(f[2])
            elif f[0] == 'd' and f[1] > tm:
                mds.append(f[2])
            elif f[0] != 'd' and f[0] != 'f' or f[1] < 0: 
                print "\tWarning: Unknow file format: %s" % (f)
                continue
        print "\tInfo: The number of file to be modified are: file: %s dir: %s" % (len(mfs), len(mds))
        return (mfs, mds)

    def dirList(self, fList):
        """
        Get all the dir list from a parent dir.Please notice the format of fList list. 
        It looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')].
        """
        ###Checking if it's list.
        self.testIsinstance(fList, list)
        ####
        ds = []
        for f in fList:
            if f[0] == "d":
                ds.append(f)
            elif f[0] != 'd' and f[0] != 'f' or f[1] < 0: 
                print "\tWarning: Unknow file format: %s" % (f)
                continue
        return ds

    def isProperSubset(self, A, B):
        """
        Checking the relation of set A and set B. If A is a subset of,
        but not equal to,B, then return True.
        """
        ####Checking if it's sets.
        self.testIsinstance(A, set)
        self.testIsinstance(B, set)
        #####
        if A.issubset(B) and A != B:
            return True
        else:
            return False

    def getFtree(self, dir):
        """
        Get all the local file list from local dir. The list contains some attributes. 
        Notice, the function is recursive function.
        @param dir: the path of dir
        @type : str
        @return : all the local file list in the dir. The list contains some attributes.
        @rtype: list
        """
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

    def getDeletedFiles(self, fs1, fs2):
        """
        Finding out the deleted files according to the files list that the last sync period.
        Cleaning the deleted files since last sync period.
        @param fs1: the previous file list.
        @param fs2: the current list.
        @return : return the relative complement of fs2 in fs1.
        @rtype  : list
        @type fs1:  list
        @type fs2:  list
        """
        ###Checking if it's list.
        self.testIsinstance(fs1, list)
        self.testIsinstance(fs2, list)
        ####
        sets1 = set(fs1)
        sets2 = set(fs2)
        sets3 = sets1 - sets2
        return list(sets3)

    def getDatPrevious(self, setFile):
        """
        Getting the app data that last saved from the setting file
        Converting the format of these data to dict.
        @param setFile: the name of the saved setting file
        @type : string
        @return : the all app data that last saved
        @rtype : dict
        """
        datPrevious = {}
        fp = open(setFile, 'r')
        string = fp.read()
        fp.close()
        try:
            wlist = pickle.loads(string)
        except EOFError:
            print "Error: EOF Error: %s" % (setFile)
            sys.exit(1)
        datPrevious = dict(wlist)
        #print "datPrevious: %s" % datPrevious
        return datPrevious
        
    def chopAttr(self, fList):
        """
        Chopping off the redundant attribute. Only retain the path attribute.
        @param fs: the list to be chopped off.
        @type fs:   list.  The format looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')]
        @rtype : list
        """
        ###Checking if it's list.
        self.testIsinstance(fList, list)
        ####
        #print "fList: %s" % (fList)
        #print type(fList)
        fs = []
        for f in fList:
            fs.append(f[2])
        return fs

    def testIsinstance(self, Instance, Type):
        """
        Checking the type of instance.
        @param Instance: the instance to be checked.
        @param Type: the type of instance to be checked
        @return : If the type of instance is right, do nothing. But if not,
        return some Error and quite the program.
        """
        ###Checking if it's list.
        if isinstance(Instance, Type):
            pass
        else:
            print "\tError: It must be a %s: %s" % (Type, Instance)
            sys.exit(1)

