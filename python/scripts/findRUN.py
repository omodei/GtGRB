#!/usr/bin/env python

import sys,os
from GTGRB.genutils import runShellCommand

if (__name__=='__main__'):
    MET=int(sys.argv[1])
    print MET
    logicalPath = "/Data/Flight/Level1/LPA"
    #logicalPath = "/Data/Flight/Reprocess/P100"
    
    group ="MERIT"
    #group = "FT1"
    tstart=MET
    tend=MET
    filter='nMetStart<=%f && nMetStop>%f' % (tend,tstart)
    cmd='/afs/slac.stanford.edu/g/glast/ground/bin/datacat find --group %s --filter \'%s\' %s ' % (group,filter,logicalPath)
    print '------------------------------------------------------------'
    print '---- selection: %s from %s ' %(group,logicalPath)
    print '---- MET = %s ' %(tstart)
    print cmd
    output=runShellCommand(cmd)
    print '------------------------------------------------------------'
    pass


                                                    
