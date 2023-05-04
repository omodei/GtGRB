#!/usr/bin/env python
import mySkimmer,os
from GTGRB.genutils import runShellCommand

mycut0='ObfGamState==0'
#logicalPath = "/Data/Flight/Reprocess/P105"
#logicalPath = "/Data/Flight/Reprocess-Test/P100-Test" # P7.1
#logicalPath = "/Data/Flight/Reprocess/P110" # P7.2
logicalPath = "/Data/Flight/Level1/LPA" # Flight Data
    
if __name__=='__main__':
    grbName=raw_input('name of the burst: ')
    met=float(raw_input('TRIGGER TIME in MET: '))
    ra=float(raw_input('RA :'))
    dec=float(raw_input('DEC :'))
    radius=float(raw_input('RADIUS (>180 for no radius selection):'))    
    before=float(raw_input('SEC BEFORE THE TRIGGER:'))
    after =float(raw_input('SEC AFTER  THE TRIGGER:'))
    group =raw_input('MERIT | SVAC [MERIT]:')
    cutIn =raw_input('+TCut [%s]:'% mycut0)
    if group!='SVAC':
        group = 'MERIT'        
        logicalPath = "/Data/Flight/Level1/LPA"
        p6 =raw_input('P6|P7 [P6]:')
        if p6=='P7':
            logicalPath = "/Data/Flight/Reprocess/P110"
    else:
        grbName='%s_%s' % (grbName,group)
        
    if len(cutIn)>0:
        mycut0=cutIn
        pass

    
    
    print grbName, os.path.exists('%s.root'  % grbName)
    if(not os.path.exists('%s.root'  % grbName)):
        t0=met-before
        t1=met+after
    
        print t0, t1, before, after, radius
        mySkimmer.QueryMET(t0,t1,group,logicalPath)
    ########
        if(radius<180):
            mycut=mySkimmer.ROI(ra,dec,t0,t1,radius)
        else:
            mycut=mySkimmer.TIME(T0=t0,T1=t1,group=group)
            pass
    ########
        mycut1= '%s && %s' % (mycut0,mycut)
        
        mySkimmer.mySkimmer(mycut=mycut1,group=group)
        if not os.path.exists('DATA/MERIT/'):
            runShellCommand('mkdir -p DATA/MERIT')
            pass
        cmd='mv Selected.root DATA/MERIT/%s.root' % grbName
        print cmd
        runShellCommand(cmd)
        pass
    pass

