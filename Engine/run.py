############################################################################
#
# This is a running program. First, you must configure it, replace all parameters. 
# Then you can run it to setup syncSftp.
#
############################################################################

import os, sys

## The root dir of syncSftp is living.
_rootDir = os.path.dirname(os.getcwd())
#_rootDir = os.getcwd()
print '_rootDir: %s' % (_rootDir)
#### Appending _rootDir to sys.path
sys.path.append(_rootDir)

from Products.syncSftp import syncSftp   

def run():
    x = syncSftp('172.16.200.153', 'tcc', 'tcc', 22, '/opt/zenpacks/dir11', '/tmp/zenpacks')
    x.sshConn()
    x.getRFList('/opt/zenpacks/dir11')
    x.getLFList('/tmp/zenpacks/dir11')
    #print "%s %s\n\n\n" % (x._rFList, len(x._rFList))
    #print "%s %s\n\n\n" % (x._lFList, len(x._lFList))
    print "The number of remote files: %s" % (len(x._rFList))
    print "The number of local files: %s" % (len(x._lFList))
    x.getLastCheckTime()
    x.saveAppdat()
    x.getSettings()
    #print x.getDatPrevious()
    #x.cleanLocalFile()
    x.getRMFs()
    x.putLMFs()
    x.sshClose()
    x.saveAppdat()
    print "\nSync finished."

if __name__ == "__main__":
    run()
