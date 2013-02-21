#!usr/bin/env python
class sftpPath():
    def __init__(self):
        #######
 #################
 180             fstat = self.sftp.stat(fPath)
 181             fType = str(fstat)[0]
 182             fMtime = fstat.st_mtime
 183             if fType == "d":
     184                 self._rFList.append(('d', fMtime, fPath))

