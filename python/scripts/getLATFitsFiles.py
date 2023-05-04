#!/usr/bin/env python
import os, subprocess
import socket
import sys
from astropy.io import fits as pyfits


from GTGRB.genutils import runShellCommand

def checkFILES(ft1,ft2,tstart, tend,patch=600.0):
	ok=True
	print("Checking FT1 file...")
	if ft1 is None: return False
	if ft2 is None: return False
	if not os.path.exists(ft1): return False
	if not os.path.exists(ft2): return False

	ft1_data = pyfits.open(ft1)['EVENTS'].data
	TIME     = ft1_data.TIME
	DT=tend-TIME.max()
	print 'TIME range from: %.1f to %.1f' %(TIME.min()-tstart,tend-TIME.max())
	if DT>patch: 
		print("====> FT1 file probably incomplete. %.1f" % DT)
		ok=False
		os.system('rm -rf %s' % ft1)
		pass
	else: print("====> FT1 file complete. %.1f" % DT)
	print("Checking FT2 file...")
	ft2_data = pyfits.open(ft2)[1].data
	STOP     = ft2_data.STOP
	DT=tend-STOP.max()
	if DT>patch: 
		print("====> FT2 file probably incomplete. %.1f" % DT)
		ok=False
		os.system('rm -rf %s' % ft2)
	else: 	print("====> FT2 file complete. %.1f" % DT)
	return ok


def getFilesAstroServer(name,tstart,tend,emin=10, emax=1000000, ra=180, dec=0.0, radius=180.0,Type=3,**kwargs):
    chatter=1
    OneSec=1
    sampleFT1='P6_public_v3' # Second Release    
    sampleFT2='P6_public_v3' # Second Release
    
    if chatter>0:
        print ' You need FT1 and FT2 file for running the analysis. '
        print ' gtgrb will try to download the data around the burst...'
        pass
    ResponseFunction=""
    for key in kwargs.keys():
	if key=='chatter': chatter=kwargs[key]
        if key=='OneSec': OneSec=int(kwargs[key])
        if key=='sample':
            sampleFT1=kwargs[key]
            sampleFT2=kwargs[key]
            pass
        if key=='ResponseFunction': ResponseFunction=kwargs[key]
        pass
    sampleFT2=sampleFT2.replace('ALL','BASE')
    #sampleFT2=sampleFT2.replace('BASE','ALL')
    #if sampleFT2=='P8_P302_BASE': sampleFT2='P7_P203_BASE'
    #check if input dirs exist first
    latdir = os.path.join(os.environ['INDIR'],'LAT')
    if (os.path.exists(os.environ['INDIR'])==False):
	os.mkdir(os.environ['INDIR'])
    if (os.path.exists(latdir)==False):
	os.mkdir(latdir)

    
    ft1name='%s_%s_ft1_%.0f_%.0f.fits' %(name,sampleFT1,tstart,tend)
    ft2name='%s_%s_ft2_%.0f_%.0f.fits' %(name,sampleFT2,tstart,tend)

    finalFile_ft1='%s/%s' %(latdir,ft1name)
    finalFile_ft2='%s/%s' %(latdir,ft2name)

    #Decide if we are running locally at SLAC or not
    hostname = socket.getfqdn() # this is thefully qualified domain name
    run_at_slac=1
    if hostname.find("slac.stanford.edu")==-1:
	run_at_slac=0
        pass

    if (run_at_slac):
	cmd1='~glast/astroserver/prod/astro --event-sample %s --output-ft1 %s --minTimestamp %s --maxTimestamp %s store ' % (sampleFT1,finalFile_ft1,tstart,tend)
        if OneSec==1: cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s %s --minTimestamp %s --maxTimestamp %s storeft2 ' % (sampleFT2,finalFile_ft2,tstart,tend)
	else:         cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-30s %s --minTimestamp %s --maxTimestamp %s storeft2 ' % (sampleFT2,finalFile_ft2,tstart,tend)
        #apply extra Transient-class cut to P7 data
        classname={'P8R2_TRANSIENT100E_V6':'Transient100E',
                   'P8R2_TRANSIENT100_V6':'Transient100',
                   'P8R2_TRANSIENT020E_V6':'Transient020E',
                   'P8R2_TRANSIENT020_V6':'Transient020',
                   'P8R2_TRANSIENT010E_V6':'Transient010E',
                   'P8R2_TRANSIENT010_V6':'Transient010',
                   'P8R2_SOURCE_V6':'Source',
                   'P8R2_CLEAN_V6':'Clean',
                   'P8R2_ULTRACLEAN_V6':'UltraClean',
                   'P8R2_ULTRACLEANVETO_V6':'UltraCleanVeto',
                   'P8R2_TRANSIENT100S_V6':'Transient100S',
                   'P8R2_TRANSIENT015S_V6':'Transient015S',
                   'P7REP_TRANSIENT_V15':'Transient',
                   'P7REP_SOURCE_V15':'Source',
                   'P7REP_CLEAN_V15':'Clean',
                   'P7REP_ULTRACLEAN_V15':'UltraClean'
                   }
        try:
            cmd1+=' --event-class-name %s' %(classname[ResponseFunction])
            print "Applying extra %s cut for %s IRFS taken from the %s repository" % (classname[ResponseFunction],ResponseFunction,sampleFT1)
            pass
        except: pass
            
        if (Type==1 or Type==3):
	    if os.path.exists(finalFile_ft1):
                print 'Using existing file %s' % finalFile_ft1
            else:
                if chatter>0 :print cmd1
	        runShellCommand(cmd1)
                pass
            if chatter>0 :print '--> file FT1: %s' % finalFile_ft1
            pass
        
        if (Type==2 or Type==3):
	    if os.path.exists(finalFile_ft2):
    	        if chatter>0 :print 'Using existing file %s' % finalFile_ft2
            else:
                if chatter>0 :print cmd2
                runShellCommand(cmd2)
                # cmd2='mv %s %s' %(ft2name,finalFile_ft2)
                # runShellCommand(cmd2)
                pass
            if chatter>0 :print '--> file FT2: %s' % finalFile_ft2
            pass
        pass
    else:
	
	cmd1='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft1 /tmp/%s --minTimestamp %s --maxTimestamp %s store ' % (sampleFT1,ft1name,tstart,tend)
        
	if OneSec==1:
    	    cmd2='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s /tmp/%s --minTimestamp %s --maxTimestamp %s storeft2 \"' % (sampleFT2,ft2name,tstart,tend)
	else:
    	    cmd2='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft2-30s /tmp/%s --minTimestamp %s --maxTimestamp %s storeft2 \"' % (sampleFT2,ft2name,tstart,tend)
	    latdir = os.path.join(os.environ['INDIR'],'LAT')
	    
        #apply extra Transient-class cut to P7 data        
        if 'TRANSIENT' in ResponseFunction:
            cmd1+=' --event-class-name Transient "'
            print "Applying extra Transient-class cut to P7TRANSIENT data taken from the %s repository" %sampleFT1
        else: cmd1+='"'
        
        if not (os.path.exists(finalFile_ft1) and os.path.exists(finalFile_ft2)):
            print "\n\nYou are running gtgrb on a computer that is not in the SLAC network."
            print " HOSTNAME = %s " % hostname
	    print "We may need to ssh to slac to talk to the astroserver...Please login if asked (you may be asked twice)..\n\n"
        
        if (Type==1 or Type==3):
	    if os.path.exists(finalFile_ft1):
		if chatter>0 :print 'Using existing file %s' % finalFile_ft1
	    else:
	        if chatter>0 :print "-----------------------------------"
	    	rsync_cmd='rsync -pave ssh --progress rhel6-64.slac.stanford.edu:/tmp/%s %s' %(ft1name,finalFile_ft1)
                runShellCommand(cmd1+";"+rsync_cmd)
		runShellCommand('ssh rhel6-64.slac.stanford.edu \"rm /tmp/%s\"' %(ft1name))
                if chatter>0 :print "-----------------------------------\n\n"
                if chatter>0 :print '--> file FT1: %s' % finalFile_ft1
    
        if (Type==2 or Type==3):
	    if os.path.exists(finalFile_ft2):
		if chatter>0 :print 'Using existing file %s' % finalFile_ft2
	    else:
	        if chatter>0 :print "-----------------------------------"
    	        rsync_cmd='rsync -pave  ssh --progress rhel6-64.slac.stanford.edu:/tmp/%s %s' %(ft2name,finalFile_ft2)
		runShellCommand(cmd2+";"+rsync_cmd)
		runShellCommand('ssh rhel6-64.slac.stanford.edu \"rm /tmp/%s\"' %(ft2name))
		if chatter>0 :print "-----------------------------------"
                if chatter>0 :print '--> file FT2 %s' % finalFile_ft2

    if (os.path.exists(finalFile_ft1)==False):
	print 'For some reason we could not obtain the FT1 file....'
        pass
    if (os.path.exists(finalFile_ft2)==False):
	print 'For some reason we could not obtain the FT2 file....'
        pass
    
    return finalFile_ft1,finalFile_ft2



def getDataCatalogList(tstart,tend, name, group='EXTENDEDFT1',logicalPath='/Data/Flight/Level1/LPA'):
    outdir = os.environ['OUTDIR']
    tmpdir = '%s/%s' %(outdir,name)
    
    if 'FT2' in group: logicalPath='/Data/Flight/Reprocess/P202'
    if 'FT2SECONDS' in group: logicalPath='/Data/Flight/Reprocess/P203'
    if 'P305' in logicalPath and tstart > 564943566: logicalPath = "/Data/Flight/Level1/LPA" # Level one pipeline
    if 'P302' in logicalPath and tstart > 456835199: logicalPath = "/Data/Flight/Level1/LPA" # Level one pipeline
    if 'P203' in logicalPath and tstart > 423447612: logicalPath = "/Data/Flight/Level1/LPA" # Level one pipeline
    if 'P202' in logicalPath and tstart > 405333211: logicalPath = "/Data/Flight/Level1/LPA" # Level one pipeline
    
    outName='%s/fileList%s' % (tmpdir,group)

    filter='nMetStop>=%s && nMetStart<%s' % (tstart,tend)    
    cmd='/afs/slac.stanford.edu/g/glast/ground/bin/datacat find --group %s --filter \'%s\' %s > %s' % (group,filter,logicalPath,outName)    
    print cmd
    runShellCommand(cmd)
    return outName

def getFiles(fileListName,name):
    outdir = os.environ['OUTDIR']
    tmpdir = '%s/%s/tmp' %(outdir,name)
    print 'getFiles, tmpdir=',tmpdir

    runShellCommand('rm -rf %s/*' % tmpdir)
    runShellCommand('mkdir -p %s' % tmpdir)
    runShellCommand('chmod 777 %s' % tmpdir)

    fileListFile = file(fileListName,'r')
    list = fileListFile.readlines()
    list.sort()
    list2=[]

    shortName = fileListName[fileListName.rfind('/')+1:]    
    baseName= '%s_%06i.fits' 
    
    i=0
    for ele in list:
        base= baseName % (shortName,i)
        newFileName='%s/%s' % (tmpdir,base)
        if ('root:' in ele):
            cmd = 'xrdcp %s %s' % (ele.strip(),newFileName)
        else:
            cmd = 'cp %s %s' % (ele.strip(),newFileName)
            pass
        runShellCommand(cmd)
        
        list2.append(newFileName)
        i=i+1        
    return list2


def getFilesDataCatalog(name,tstart,tend, emin=10, emax=1000000, ra=180, dec=0.0, radius=180.0,Type=3,logicalPath='/Data/Flight/Level1/LPA',extended=True):
    from GTGRB import FTmerge as FTM
    
    OneSec=1
    
    #check if input dirs exist first
    latdir = os.path.join(os.environ['INDIR'],'LAT')
    outdir = os.environ['OUTDIR']
    tmpdir = '%s/%s' %(outdir,name)
    runShellCommand('mkdir -p %s' % tmpdir)
    runShellCommand('chmod 777 %s' % tmpdir)
    if (os.path.exists(os.environ['INDIR'])==False):
	os.mkdir(os.environ['INDIR'])
        pass
    if (os.path.exists(latdir)==False):
	os.mkdir(latdir)
        pass
    
    ft1name='%s_ft1_%.0f_%.0f.fits' %(name,tstart,tend)
    ft2name='%s_ft2_%.0f_%.0f.fits' %(name,tstart,tend)
    
    finalFile_ft1='%s/%s' %(latdir,ft1name)
    finalFile_ft2='%s/%s' %(latdir,ft2name)
    
    # ################################
    
    ft1Name=0
    ft2Name=0
    if ((Type==1 or Type==3) and os.path.exists(finalFile_ft1)==False):
        if extended:
		ft1Name=getDataCatalogList(tstart,tend,name,'EXTENDEDFT1',logicalPath)
	else:
		ft1Name=getDataCatalogList(tstart,tend,name,'FT1',logicalPath)
        pass
    
    if ((Type==2 or Type==3) and os.path.exists(finalFile_ft2)==False):        
        if OneSec==1:
            ft2Name=getDataCatalogList(tstart,tend,name,'FT2SECONDS',logicalPath)
            runShellCommand('pwd')
            runShellCommand('ls -l %s' % ft2Name)
            
            if len(file(ft2Name,'r').readlines())==0:
                ft2Name=getDataCatalogList(tstart,tend,name,'FT2',logicalPath)
                pass
            pass
        else:
            ft2Name=getDataCatalogList(tstart,tend,name,'FT2',logicalPath)
            pass
        pass
    # print ft1Name,ft2Name
    # GET THE FT1 FILE
    if not ft1Name==0:
        listFT1=getFiles(ft1Name,name)
        if len(listFT1)==0:
            finalFile_ft1=None
        elif len(listFT1)==1:
            cmd='cp %s %s' %(listFT1[0],finalFile_ft1)
            runShellCommand(cmd)
        else:
            FTM.ft1merge(listFT1,finalFile_ft1)            
            pass
        pass
    
    # GET THE FT2 FILE    
    if not ft2Name==0:
        listFT2=getFiles(ft2Name,name)
        if len(listFT2)==0:
            finalFile_ft2 = None
        elif len(listFT2)==1:
            cmd='cp %s %s' %(listFT2[0],finalFile_ft2)
            runShellCommand(cmd)
        else:
            FTM.ft2merge(listFT2,finalFile_ft2)
            pass
        pass
    runShellCommand('chmod 777 %s' % finalFile_ft1)
    runShellCommand('chmod 777 %s' % finalFile_ft2)
    return finalFile_ft1,finalFile_ft2




if __name__=='__main__':
    import os,sys
    from gtgrb import genutils

    deltat=1000
    useAstroserver=0
    _logicalPath= '/Data/Flight/Reprocess/P305' 
    _DataSample='P7.6_P130_BASE'
    _ResponseFunction='P7SOURCE'
    extended=True
    for (i,a) in enumerate(sys.argv):
        if a=='--output-ft1': output_ft1=str(sys.argv[i+1]) 
        if a=='--output-ft2': output_ft2=str(sys.argv[i+1]) 
        if a=='--minTimestamp':  tstart=float(sys.argv[i+1])-deltat
        if a=='--maxTimestamp':  tend  =float(sys.argv[i+1])+deltat
        if a=='--name':   name  =str(sys.argv[i+1])
        if a=='--noextended':   extended=False
        pass
    if tstart<tend: print('retriving %f of data...' %(tend-tstart))
    else: exit()
    if useAstroserver:
        getFilesAstroServer(name,tstart,tend, emin=10, emax=100000,
                            ra=180, dec=0, radius=180, sample=_DataSample,
                            ResponseFunction=_ResponseFunction,Type=2,chatter=1)
    else:
        ft1,ft2=getFilesDataCatalog(name,tstart,tend,emin=10, emax=1000000, ra=180, dec=0.0, radius=180.0,Type=3,logicalPath=_logicalPath,extended=extended)
        checkFILES(ft1,ft2,tstart+deltat, tend-deltat)
        os.system('mv %s %s' % (ft1,output_ft1))
        os.system('mv %s %s' % (ft2,output_ft2))
        pass
    pass

