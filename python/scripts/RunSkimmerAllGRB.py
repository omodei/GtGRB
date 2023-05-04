#!/usr/bin/env python
from GTGRB.genutils import runShellScript

GRBs={'GRB080825C' : [241366429.105,        233.96,     -4.72,  35.],
      'GRB080916C' : [243216766.613542,   119.8459, -56.63891, 100.],
      'GRB081024B' : [246576161.8,           322.9,    21.204,   4.],
      'GRB081215'  : [251059717.41 ,        78.201,    17.575,  10.],
      'GRB090217'  : [256539404.56 ,        205.93,     -8.42,  35.],
      'GRB090323'  : [259459364.63 ,     190.70940,  17.05390, 100.],
      'GRB090328'  : [259925808.0 ,       90.66494, -41.88265, 100.],
      'GRB090510'  : [263607781.971090,  333.55271, -26.58266,  10.],
      'GRB090626'  : [267683530.88,         170.01,    -33.50,200.0],
      'GRB090902'  : [273582310.312714,  264.93859,  27.32448, 30.0],
      'GRB090926'  : [275631628.99,      353.40070, -66.32390, 50.0],
      'GRB091003'  : [276237347.584656,  251.51980,  36.62470, 30.0],
      #'GRB091031'  : [278683230.85,          70.58,    -59.08, 50.0],
      'GRB100116A' : [285370262.24,         305.02,     14.45, 10.0],
      'GRB100225A' : [288758533.15,         310.25,    -59.40, 50.0]}


import mySkimmer,os
BEFORE = 1000
AFTER  = 1000
RADIUS = 666

#logicalPath = "/Data/Flight/Reprocess/P105"
#logicalPath = "/Data/Flight/Reprocess-Test/P100-Test" # P7.1
P63DB = "/Data/Flight/Level1/LPA"     # Flight Data
P72DB = "/Data/Flight/Reprocess/P110" # P7.2

OUTPUTDIR='/afs/slac/g/glast/groups/grb/DATA/MERIT'

if __name__=='__main__':
    GRBlist=GRBs.keys()
    GRBlist.sort()
    for GRB in GRBlist:
        N63OUT='%s_P63' % GRB
        N72OUT='%s_P72' % GRB
        
        FN63OUT='%s/%s_P6_V3.root' % (OUTPUTDIR,GRB)
        FN72OUT='%s/%s_P7_V2.root' % (OUTPUTDIR,GRB)
        T0=GRBs[GRB][0]
        T1=T0-BEFORE
        T2=T0+AFTER
        print '---- processing : %s ' % GRB
        if (not os.path.exists(FN63OUT)):
            mySkimmer.QueryMET(T1,T2,P63DB)
            mycut=mySkimmer.TIME(T1,T2)
            mySkimmer.mySkimmer(mycut)
            cmd='mv Selected.root %s' % FN63OUT
            print cmd
            runShellScript(cmd)
            pass
        if (not os.path.exists(FN72OUT)):
            mySkimmer.QueryMET(T1,T2,P72DB)
            mycut=mySkimmer.TIME(T1,T2)
            mySkimmer.mySkimmer(mycut)
            cmd='mv Selected.root %s' % FN72OUT
            print cmd
            runShellScript(cmd)
            pass
        pass
    print 'done!'
    
