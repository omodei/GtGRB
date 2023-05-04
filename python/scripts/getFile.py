#!/usr/bin/env python
import os
from GTGRB.genutils import runShellCommand

def getFilesAstroServer(name,tstart,tend,emin=10, emax=100000, ra=180, dec=0.0, radius=180.0):

    sample='P6_public_v1'
    #sample='P110_P7_public_v2'
    
    ft1name='%s_ft1_%.0f_%.0f.fits' %(name,tstart,tend)
    ft2name='%s_ft2_%.0f_%.0f.fits' %(name,tstart,tend)


    #cmd='~glast/astroserver/prod/astro --event-sample P6_public_v1 --output-ft1 %s --event-sample --minEnergy %s --maxEnergy %s --minTimestamp %s --maxTimestamp %s --ra %s --dec %s --radius %s --eventClass "EVENT_CLASS > 0" store ' % (ft1name,emin,emax,tstart,tend,ra,dec,radius)

    
    #cmd1='~glast/astroserver/prod/astro --event-sample P6_public_v1 --output-ft1 %s --event-sample --minTimestamp %s --maxTimestamp %s --event-class "EVENT_CLASS > 0" store ' % (ft1name,tstart,tend)
    #cmd2='~glast/astroserver/prod/astro --event-sample P6_public_v1 --output-ft2-1s %s --event-sample --minTimestamp %s --maxTimestamp %s --event-class "EVENT_CLASS > 0" storeft2 ' % (ft2name,tstart,tend)
    
    cmd1='~glast/astroserver/prod/astro --event-sample %s --output-ft1 %s --event-sample --minTimestamp %s --maxTimestamp %s --event-class "EVENT_CLASS > 0" store ' % (sample,ft1name,tstart,tend)
    cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s %s --event-sample --minTimestamp %s --maxTimestamp %s --event-class "EVENT_CLASS > 0" storeft2 ' % (sample,ft2name,tstart,tend)


    latdir = os.path.join(os.environ['INDIR'],'LAT')
    

    if os.path.exists(latdir):
        finalFile_ft1='%s/%s' %(latdir,ft1name)
        finalFile_ft2='%s/%s' %(latdir,ft2name)
    else:
        finalFile_ft1=ft1name
        finalFile_ft2=ft2name
        pass
    
    if os.path.exists(finalFile_ft1):
        print 'File %s exists. remove it before.' % finalFile_ft1
    else:
        runShellCommand(cmd1)
        if os.path.exists(latdir):
            cmd1='mv %s %s' %(ft1name,finalFile_ft1)
            runShellCommand(cmd1)
            pass
        pass
    
    if os.path.exists(finalFile_ft2):
        print 'File %s exists. remove it before.' % finalFile_ft2
    else:
        runShellCommand(cmd2)
        if os.path.exists(latdir):
            cmd2='mv %s %s' %(ft2name,finalFile_ft2)
            runShellCommand(cmd2)
            pass
        pass
    
    print '--> file FT1: %s' % finalFile_ft1
    print '--> file FT2: %s' % finalFile_ft2
    return finalFile_ft1,finalFile_ft2


def getDataCatalogList(tstart,tend, group='FT1'):
    
    #logicalPath = "/MC-Tasks/ServiceChallenge/obssim_v9r5/fits"
    logicalPath = "/Data/Flight/Level1/LPA"
    logicalPath = "/Data/Flight/Reprocess/P110"
        
    outName='fileList%s' % group
    filter='nMetStop>=%s && nMetStart<%s' % (tstart,tend)
    
    cmd='/afs/slac.stanford.edu/g/glast/ground/bin/datacat find --group %s --filter \'%s\' %s > %s' % (group,filter,logicalPath,outName)    
    print cmd
    runShellCommand(cmd)
    return outName

def getFiles(fileListName):
    fileListFile=file(fileListName,'r')
    list = fileListFile.readlines()
    list.sort()
    print list
    list2=[]
    runShellCommand('mkdir tmp')
    baseName='%s_%06i.fits'
    
    i=0
    for ele in list:
        base= baseName % (fileListName,i)
        newFileName='tmp/%s' % base
        if ('root:' in ele):
            cmd = 'xrdcp %s %s' % (ele.strip(),newFileName)
        else:
            cmd = 'cp %s %s' % (ele.strip(),newFileName)
            pass
        print cmd
        runShellCommand(cmd)
        
        list2.append(newFileName)
        i=i+1        
    return list2


if __name__=='__main__':
    import os,sys
    from GTGRB import FTmerge as FTM
    deltat=86400
    useAstroserver=1

    try:
        tstart=float(sys.argv[1])-deltat
        tend  =float(sys.argv[1])+deltat
        int_time=int('%i' % sys.argv[1])
        name=genutils.met2date(int_time,'grbname')
        indir='$PWD'
        
    except:
        try:
            tstart = lat.GRB.TStart  - deltat
            tend   = lat.GRB.TStop  + deltat
            name   = lat.GRB.Name
            indir  = lat.IN_Directory
            
        except:
            tt    =float(raw_input(' MET of the GRB= '))
            deltat=float(raw_input(' BEFORE and AFTER= '))
            grbname=genutils.met2date(int(tt),'grbname')
            name  =raw_input(' Name of the file= [%s]'%grbname)
            if len(name)<1:
                name=grbname
                pass
            tstart = int(tt-deltat)
            tend   = int(tt+deltat)
            indir= '$INDIR/LAT/'
            pass
        pass
    print 
    if useAstroserver:
        name_ft1,name_ft2=getFilesAstroServer(name,tstart,tend,emin=10, emax=1000000, ra=180, dec=0.0, radius=180.0)
    else:
        runShellCommand('rm -rf tmp/')
        ft1Name=0
        ft2Name=0
        
        ft1Name=getDataCatalogList(tstart,tend,'FT1')        
        #ft2Name=getDataCatalogList(tstart,tend,'FT2')
        
        ft2Name=getDataCatalogList(tstart,tend,'FT2SECONDS')
        
        if not ft1Name==0:
            listFT1=getFiles(ft1Name)
            name_ft1='%s/%s_%i_%i_ft1.fits' %(indir,name,int(tstart),int(tend))
            if len(listFT1==1):
                cmd='cp %s %s' %(listFT1[0],name_ft1)
                runShellCommand(cmd)
            else:
                FTM.ft1merge(listFT1,name_ft1)            
            pass
        if not ft2Name==0:
            listFT2=getFiles(ft2Name)
            name_ft2='%s/%s_%i_%i_ft2.fits' %(indir,name,int(tstart),int(tend))
            if len(listFT2==1):
                cmd='cp %s %s' %(listFT2[0],name_ft2)
                runShellCommand(cmd)
            else:
                FTM.ft2merge(listFT2,name_ft2)
            pass
        pass
    pass
    
