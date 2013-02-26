############################################################################
#
###################### Some Utilities ##########################
#
############################################################################

__doc__ = """Utils
General utility functions module.
"""

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

    def createDirNotExists(self, dir):
        """
        Create the dir that isn't exist.
        """
        if not os.path.exists(dir):
            print "\tInfo: Create the dir: %s.." % (dir)
            os.makedirs(dir)

    def mfsInfo(self, fs):
        """
        Get the modified files list since last check. Chop off the redundant attributes. 
        Please notice the format of 'fs'.
        It looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')]
        """
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

    def dirList(self, fs):
        """
        Get all the dir list from a parent dir.Please notice the format of fs list. 
        It looks like [('d', 1361237415.0, '/tmp/zenpacks/dir345'), ('d', 1361237415.0, '/tmp/zenpacks/dir123')].
        """
        ###Checking if it's list.
        if isinstance(fs, list):
            ds = []
            for f in fs:
                if f[0] == "d":
                    ds.append(f)
                elif f[0] != 'd' and f[0] != 'f' or f[1] < 0: 
                    print "\tWarning: Unknow file format: %s" % (f)
                    continue
            return ds
        else:
            print "\tError: It must be a list: %s" % (fs)
            sys.exit(1)

    def isProperSubset(self, A, B):
        """
        Checking the relation of set A and set B. If A is a subset of,
        but not equal to,B, then return True.
        """
        ####Checking if it's sets.
        if isinstance(A, set) and isinstance(B, set):
            if A.issubset(B) and A != B:
                return True
            else:
                return False
        else:
            print "\tError: It must be sets : %s,%s" % (A, B)
            sys.exit(1)

    def getFtree(self, dir):
        """
        Get all the local file list from local dir. The list contains some attributes. 
        Notice, the function is recursive function.
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



