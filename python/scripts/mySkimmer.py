#! /afs/slac/g/ki/bin/ipython
#/usr/bin/env python

import sys,os
from GTGRB.genutils import runShellCommand
import ROOT    
def QueryMET(tstart,tend, group ="MERIT", logicalPath="/Data/Flight/Level1/LPA"):
    # Possible logical Paths:
    # DATA:
    #logicalPath = "/Data/Flight/Level1/LPA"
    # REPROCESSED DATA:
    #logicalPath = "/Data/Flight/Reprocess/P100"

    # POSSIBLE GROUPS:
    #group ="MERIT"
    #group ="SVAC"
    #group = "FT1"
    
    filter='nMetStart<%f && nMetStop>%f' % (tend,tstart)
    cmd='/afs/slac.stanford.edu/g/glast/ground/bin/datacat find --group %s --filter \'%s\' %s >filelist' % (group,filter,logicalPath)
    print '------------------------------------------------------------'
    print '---- selection: %s from %s ' %(group,logicalPath)
    print '---- Tstart = %s , Tend = %s (%s)' %(tstart,tend,float(tend)-float(tstart))
    print '------------------------------------------------------------'
    print cmd    
    output=runShellCommand(cmd)
    pass


def ROI(Ra,Dec,T0,T1,Radius):
    timeBranch='EvtElapsedTime'
    cut="%s>%f && %s <%f && FT1ZenithTheta<105.0 && ((cos(FT1Dec*0.0174533)*(FT1Ra - (%f)))^2+(FT1Dec- (%f))^2)< (%f)^2" %(timeBranch,T0,timeBranch,T1,Ra,Dec,Radius)
    print ' -------------------------------------------------- '
    print ' ROI CUT: at Ra=%s, Dec=%s, with radius=%s' %(Ra,Dec,Radius)    
    print ' Time CUT: T0=%s, T1=%s (%s)' %(T0,T1,T1-T0)
    print cut
    print ' -------------------------------------------------- '
    
    return cut;

def TIME(T0,T1,group ="MERIT"):
    timeBranch='EvtElapsedTime'
    if group == 'SVAC':
        timeBranch='EvtTime'
        pass
    cut="%s > %f && %s <%f " %(timeBranch,T0,timeBranch,T1)
    print ' -------------------------------------------------- '
    print ' Time CUT: T0=%s, T1=%s (%s)' %(T0,T1,T1-T0)
    print cut
    print ' -------------------------------------------------- '
    return cut;



def mySkimmer(mycut="CTBClassLevel>0",group ="MERIT",filelist='filelist'):
    if group == "SVAC":
        chain=ROOT.TChain("Output")
    else:
        chain=ROOT.TChain("MeritTuple")
        pass
    fin=file(filelist,'r')
    list_of_files=fin.readlines()
    N0=0
    for filename in list_of_files:
        print filename,' adding...'
        chain.AddFile(filename.strip())
        N0=N0+chain.GetEntries()
        pass
    pid=os.getpid()
    output='/scratch/nicola/mySimpleSkimmer/%s' % pid
    try:
        os.makedirs(output)
    except:
        output='.'
        pass
    print 'output dir = %s' % output
    fout=ROOT.TFile("%s/Selected.root" % output ,"RECREATE")
    fout.cd()
    fout.ls()
    print 'copying with cuts:'
    print mycut
    t00=chain.CopyTree(mycut)
    N1=t00.GetEntries()


    print "original tree has: %i events. Selected tree: %i. Selected percentage: %f %%" %(N0,N1,float(N1)/float(N0)*100.0)
    t00.Write()
    fout.Close()
    
    cmd='mv %s/Selected.root Selected.root' % output
    runShellCommand(cmd)
    pass

if __name__=='__main__':
    
    radius=45
    before=100
    after =100
    #try:
    names=[sys.argv[1]]
    mets =[float(sys.argv[2])]
    ras  =[float(sys.argv[3])]
    decs =[float(sys.argv[4])]
    logicalPath="/Data/Flight/Level1/LPA"
    print names
    print mets
    print ras
    print decs
    
    
    #except:
    #    names=['080825593','080916009','081006604']
    #    mets=[241366428,243216766, 244996175]
    #    ras=[232.2,119.8,135]
    #    decs=[-4.9,-56.6,-62]
    #    pass
    for i in range(len(mets)):
        print names[i],os.path.exists('%s.root'  % names[i])

        if(not os.path.exists('%s.root'  % names[i])):
            met=mets[i]
            ra=ras[i]
            dec=decs[i]
            
            t0=met-before
            t1=met+after
            
            print t0, t1, before, after, radius
            QueryMET(t0,t1)
            ########
            if(radius<180):
                mycut=ROI(ra,dec,t0,t1,radius)
            else:
                mycut=TIME(t0,t1)
                pass
            ########

            mycut1= ' ObfGamState==0 && TkrNumTracks>0 && %s ' % mycut            
            #mycut1= ' ObfGamState==0 && FT1ZenithTheta<105.0 && %s' % mycut
            
            mySkimmer(mycut1)
            cmd='mv Selected.root %s.root' % names[i]
            print cmd
            runShellCommand(cmd)
            pass
        pass

    print 'All Done!'
