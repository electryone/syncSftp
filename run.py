############################################################################
#
# This is a running program. First, you must configure it, replace all parameters. 
# Then you can run it to setup syncSftp.
#
############################################################################

from syncSftp import syncSftp   

def run():
    x = syncSftp('172.16.200.153', 'tcc', 'tcc', 22, '/opt/zenpacks', '/tmp')
    x.sshConn()
    x.getRFList('/opt/zenpacks')
    x.getLFList('/tmp/zenpacks')
    #print "%s %s\n\n\n" % (x._rFList, len(x._rFList))
    #print "%s %s\n\n\n" % (x._lFList, len(x._lFList))
    print "The number of remote files: %s" % (len(x._rFList))
    print "The number of local files: %s" % (len(x._lFList))
    x.getLastCheckTime()
    x.getRMFs()
    x.putLMFs()
    x.sshClose()
    x.getCurTime()
    print "\nSync finished."

if __name__ == "__main__":
    run()
