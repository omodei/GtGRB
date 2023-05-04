from gtgrb import *
import gtgrb
import os, subprocess
from GTGRB import submitCommand, genutils
import time, datetime
import glob, shutil
import re

def _relPath(abspath,depth=-3):
  return os.path.join(os.sep.join(abspath.split(os.sep)[depth:]))
pass

def _naturalSort(l):
    #This sort an iterable like "int1,int9,int10,int2" in "int1,int2,int9,int10" (natural sorting)
    #instead of "int1,int10,int2,int9" as the sort() method 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)
pass

def _ftmerge(pha2list,outfile,extname="SPECTRUM"):
    f                         = open("__pha2s.list","w+")
    for pha2 in pha2list:
      f.write("%s[%s]\n" %(pha2,extname))
    pass
    f.close()
    
    cmdLine                   = "ftmerge infile=@__pha2s.list outfile=%s copyall=yes clobber=yes" %(outfile)
    print("\n%s\n" %(cmdLine))
    genutils.runShellCommand(cmdLine)
pass

def _waitForJobs(subs):
    #Now wait for the job to finish
    status                    = map(lambda x:"",subs)
    finished                  = map(lambda x:False,subs)
    
    time.sleep(10)
    print("\nWaiting for the job to finish...")
    printed                   = False
    while(finished.count(False)>0):
      for i,s in enumerate(subs):
        
        if(finished[i]):
          continue
        pass
        
        try:
          curStatus             = s.getProcessStatus()
          
          if(curStatus!=status[i]):
            #This job changed state
            print("%s: %s --> %s circa %s" %(s.name,status[i],curStatus,str(datetime.datetime.now())))
            printed             = True
            status[i]           = curStatus
            
            if(status[i]=="DONE" or status[i]=="EXIT"):
              s.getResults()
              finished[i]       = True
            pass
          
          pass
              
        except:
          #Can't get status, the job is not there, don't do nothing
          pass
        pass
          
      pass    
      if(printed):
        print("\n")
      time.sleep(5)
      printed                 = False
    pass
pass

def MakeLATSpectraFarm(outsideWorld,**kwargs):
    '''
    Make the spectra using the GBM detectors. FARM VERSION! Remember to pass globals() as last parameter
    
    submitters  = MakeLATSpectraFarm(globals(),tstart=tstart,tstop=tstop,...)
    
    Parameters:
    \t sp_TSTARTs   = TSTART (list or scalar)
    \t sp_TSTOPs    = TSTOP (list or scalar)
    \t [... all other parameters are directly passed to MakeLATSpectra()
    '''
    
    commandString             = []
    
    for key in kwargs.keys():
      if   key.lower()=="sp_tstarts"   : tstart     = eval(str(kwargs[key]))
      elif key.lower()=="sp_tstops"    : tstop      = eval(str(kwargs[key]))
      else:
        commandString.append("%s=%s" %(key,eval(str(kwargs[key]))))
    pass
    
    commandString             = ",".join(commandString)
    
    subs                      = []
    for i in range(len(tstart)):
      subs.append(submitCommand.commandSubmitter("INT%s" %i,outsideWorld,copyLATdata=True,copyBKGEdata=True,verbose=True))
      if(commandString!=''):
        cmd                     = "switchToNotInteractiveExecution() ; MakeLATSpectra(sp_tstarts=%s,sp_tstops=%s,%s)" % (tstart[i],tstop[i],commandString)
      else:
        cmd                     = "switchToNotInteractiveExecution() ; MakeLATSpectra(sp_tstarts=%s,sp_tstops=%s)" % (tstart[i],tstop[i])
      print("\nSubmitting command:\n %s" %(cmd))
      subs[-1].submitCommand(cmd)
      time.sleep(2)
    pass
    
    #Wait for the jobs to finish
    _waitForJobs(subs)
    print("\nAll jobs done!\n")
    #Now that everything is finished, let's merge all the PHA2s
    pha2s                     = []
    bak2s                     = []
    rsp2s                     = []
    for i,s in enumerate(subs):
      pha2s.append(os.path.join(s.submitterDatadir,s.name,_relPath(s.results["PHA2filesLAT"])))
      
      if(s.results.has_key("backFilesLAT")):
        bak2s.append(os.path.join(s.submitterDatadir,s.name,_relPath(s.results["backFilesLAT"])))
      pass
      
      if(s.results.has_key("RSPfilesLAT")):
        rsp2s.append(os.path.join(s.submitterDatadir,s.name,_relPath(s.results["RSPfilesLAT"])))
      pass
      
    pass

    outpath                 = os.path.join(os.environ['OUTDIR'],results['GRBNAME'])
    PHA2Name                = "%s/%s" % (outpath,os.path.basename(subs[0].results['PHA2filesLAT']))
    _ftmerge(pha2s,PHA2Name)
    phaList                 = [PHA2Name]
    
    if(len(bak2s)>0):
      BAK2Name              = "%s/%s" % (outpath,os.path.basename(subs[0].results['backFilesLAT']))
      _ftmerge(bak2s,BAK2Name)
      bakList               = [BAK2Name]
    else:
      bakList               = []
    pass
      
    if(len(rsp2s)>0):
      RSP2Name              = "%s/%s" % (outpath,os.path.basename(subs[0].results['RSPfilesLAT']))
      
      genutils.RSPs_to_RSP2(tstart,tstop,rsp2s,RSP2Name, lat[0].GRB.Ttrigger)
      
      rspList               = [RSP2Name]
    else:
      rspList               = []
      
    gtgrb._addSpectraToFitDirectory(phaList,bakList,rspList,os.path.abspath(lat[0].out_dir))
    
pass

def PerformSpectralAnalysisFarm(**kwargs):
    
    if('queue' in kwargs.keys()):
      queue                 = kwargs['queue']
    else:
      queue                 = "xlong"
    
    d                       = datetime.datetime.now().timetuple()
    kwargs["performFit"]    = False

    PerformSpectralAnalysis(**kwargs)

    #Get all xcm files produced, and all pha files
    baseFitDir              = os.path.join(os.environ['OUTDIR'],results['GRBNAME'],"to_fit")
    
    #Get all the doFit*.xcm files 
    xcmFilesAll             = glob.glob(os.path.join(baseFitDir,"doFit*.xcm"))
    #Keep only the one create by the PerformSpectralAnalysis command just performed
    xcmFiles                = _naturalSort(filter(lambda x:time.localtime(os.path.getmtime(x))>=d,xcmFilesAll))
    
    #Get PHA files
    phaFiles                = glob.glob(os.path.join(baseFitDir,"*.pha*"))
    #Keep only .pha or .pha2
    phaFiles                = filter(lambda x:re.match(".*pha[2]?$",x)!=None,phaFiles)
    
    #Get BAK files
    bakFiles                = glob.glob(os.path.join(baseFitDir,"*.bak*"))
    #Keep only .bak or .bak2
    bakFiles                = filter(lambda x:re.match(".*bak[2]?$",x)!=None,bakFiles)
    
    #Get RSP files    
    rspFiles                = glob.glob(os.path.join(baseFitDir,"*.rsp*"))
    #Keep only .rsp or .rsp2
    rspFiles                = filter(lambda x:re.match(".*rsp[2]?$",x)!=None,rspFiles)            
    
    #Get the PFILES configuration
    pfilesBases,pfilesRepositories = os.environ['PFILES'].split(";")    
    
    jobs                    = []
    intervalStrings         = []
    
    for xcm in xcmFiles:
      intString             = os.path.basename(xcm).split("_")[1].split(".")[0]
      intervalStrings.append(intString)
      
      #Create the subdirectory for this interval
      thisIntervalDir       = os.path.join(os.environ['OUTDIR'],results['GRBNAME'],"to_fit",intString)
      try:
        shutil.rmtree(thisIntervalDir)
      except:
        pass
        
      os.makedirs(thisIntervalDir)
      
      #Copy all pha files, bak files and rsps to the subdir
      for pha,bak,rsp in zip(phaFiles,bakFiles,rspFiles):
        shutil.copy(pha,thisIntervalDir)
        shutil.copy(bak,thisIntervalDir)
        shutil.copy(rsp,thisIntervalDir)
      pass
      
      #Now create a copy of the xcm file in the subdir, without its line beginning
      #with "cd"
      f                       = open(xcm)
      f2                      = open("%s/%s" %(thisIntervalDir,os.path.basename(xcm)),"w+")
      
      newContent              = filter(lambda x:re.match("^cd ",x)==None,f)
      
      for line in newContent:
        f2.write(line)
      pass
      
      f2.close()
      f.close() 
      
      #Copy the text file with the energy bins
      shutil.copy(os.path.join(baseFitDir,"__xspecEnergyBins_%s.txt" %(intString)),thisIntervalDir)
      
      #Now submit the xspec job
      remoteJob                  = []
      remoteJob.append("import os, shutil")
      remoteJob.append("baseDir                  = '/scratch/spectralAnalysisFarm/%s' %(os.environ['LSB_JOBID'])")
      remoteJob.append("os.environ['BASEDIR']    = baseDir")
      #create directories
      remoteJob.append("os.system('mkdir -p %s' %(os.environ['BASEDIR']))")
      remoteJob.append("os.system('mkdir -p %s/pfiles' %(os.environ['BASEDIR']))")
      
      remoteJob.append("os.chdir(os.environ['BASEDIR'])")
      remoteJob.append("os.environ['HOME']       = baseDir")
      #Copy all the files in the farm
      remoteJob.append("os.system('cp -v %s/* '+baseDir)" %(thisIntervalDir))
      #Copy pfiles
      for pfilesDir in pfilesBases.split(":"):
        remoteJob.append("os.system('cp -v %s/* '+os.path.join(baseDir,'pfiles'))" %(pfilesDir)) 
      remoteJob.append("os.environ['PFILES']     = baseDir+'/pfiles;%s'" %(pfilesRepositories))
      remoteJob.append("print('ENVIRONMENT VARIABLES:')") 
      remoteJob.append("for key,value in os.environ.iteritems():")
      remoteJob.append("  print('%s = %s' %(key,value))")
      #Run xspec
      remoteJob.append("os.system('xspec - %s')" %(os.path.basename(xcm)))
      #Copy back results
      remoteJob.append("stageoutdir             = '%s'" %(thisIntervalDir))
      remoteJob.append("os.system('cp -v %s/* %s' %(os.environ['BASEDIR'],stageoutdir))")
      remoteJob.append("os.chdir('/scratch')")
      remoteJob.append("shutil.rmtree(os.environ['BASEDIR'])")
      
      #Write the remote job
      remoteScriptName        = "%s/remoteJob_%s.py" %(thisIntervalDir,intString)
      f                       = open(remoteScriptName,"w+")
      for line in remoteJob:
        f.write("%s\n" %(line))
      f.close()
      
      #Submit to LSF and get the job ID    
      processName                = "spectralAnalysisFarm_%s" % (intString)
      logfileName                = os.path.join(os.environ["LOGS"],"%s_spectralAnalysisFarm_%s.log" %(results['GRBNAME'],intString))
      cmdLine                    = "bsub -q %s -J %s -o %s python %s" %(queue,processName,logfileName,remoteScriptName)
      print("\n\nSubmitting jobs %s..." %(processName))
      args                       = shlex.split(cmdLine)
      output,error               = subprocess.Popen(args,stdout = subprocess.PIPE, stderr= subprocess.STDOUT).communicate()
      jobID                      = output.split("<")[1].split(">")[0]
      print("  ---> Job ID is %s" %(jobID))

      #Use the facilities of the class commandSubmitter
      jobs.append(submitCommand.commandSubmitter("spectralAnalysisFarm_%s" % (intString),globals()))
      jobs[-1].jobID             = jobID      
    pass
    
    #Wait for the jobs to finish
    _waitForJobs(jobs)
    print("\nAll jobs done!\n")
        
    #Now merge all .fits file relative to spectral models
    #Sort the intervals by number
    sortedIntervals              = _naturalSort(intervalStrings)
    #Get the list of models
    modelFiles                   = glob.glob(os.path.join(baseFitDir,sortedIntervals[0],"*.fits"))
    modelFiles                   = map(lambda x:os.path.basename(x),modelFiles)
    
    for model in modelFiles:
      listFile                   = os.path.join(baseFitDir,"%s.list" % (model.split(".")[0]))
      f                          = open(listFile,"w+")
      
      for interval in sortedIntervals:
        thisModelFilename        = os.path.join(baseFitDir,interval,model)
        if(not os.path.isfile(thisModelFilename)):
          raise RuntimeError("File %s does not exists or is not readable! Fit failed?" %(thisModelFilename))
        pass
        f.write("%s\n" %(thisModelFilename))
      pass
      
      f.close()
      #merge all the fits files
      cmdLine                   = "ftmerge infile=@%s outfile=%s copyall=yes clobber=yes" %(listFile,
                                   os.path.join(baseFitDir,model))
      print("\n%s\n" %(cmdLine))
      genutils.runShellCommand(cmdLine)
    pass  
    
    auto                        = autofit.autofit(baseFitDir,results['GRBNAME'],results['GRBTRIGGERDATE'])
    auto._postProcessing()
    auto._summarizeResults()    
pass

def MakeFilesAndPerformSpectralAnalysis(**kwargs):
  '''
    MakeFilesAndPerformSpectralAnalysis(tstart=tstart,tstop=tstop,useLAT=True|False,useLLE=True|False,
                                        useGBM=True|False,models=[models])
  '''
  
  useLAT, useGBM, useLLE      = True, True, True
  
  models                      = "B"
  
  for key in kwargs.keys():
    if  (key.lower()=="uselat"):                 useLAT     = bool(kwargs[key])
    elif(key.lower()=="uselle"):                 useLLE     = bool(kwargs[key])
    elif(key.lower()=="usegbm"):                 useGBM     = bool(kwargs[key])
    elif(key.lower()=="models"):                 models     = kwargs[key]
  pass
  
  tstart                      = kwargs['tstart']
  tstop                       = kwargs['tstop']
  
  #Remove the 'mode' keyword, if present
  if(kwargs.keys().count('mode')>0):
    kwargs.pop('mode')
  
  Nintervals                  = len(tstart)
  
  subs                        = []
  
  for i,t1,t2 in zip(range(Nintervals),tstart,tstop):
    subs.append(submitCommand.commandSubmitter("INT%s" %(i),globals(),
                                               copyGBMdata=True,
                                               copyBKGEdata=True))
    cmdSequence                 = "conf = autofit.configuration()"
    if(useGBM):
      cmdSequence              += " ; MakeGBMSpectra(tstart=%s,tstop=%s,mode='go')" %(t1,t2)
    if(useLAT):
      cmdSequence              += " ; MakeLATSpectra(tstart=%s,tstop=%s,mode='go',BKGE=1,RSPGEN=1,FLAT_ROI=0)" %(t1,t2)
    if(useLLE):
      cmdSequence              += " ; MakeLLESpectra(tstart=%s,tstop=%s,mode='go')" %(t1,t2)
      if(useLAT):
        #Use LLE up to 100 MeV, Transient above that
        cmdSequence            += " ; conf.setChanToIgnore('LLE','**-3e4 1e5-**')"
      else:
        #Use LLE up to 1 GeV
         cmdSequence           += " ; conf.setChanToIgnore('LLE','**-3e4 1e6-**')" 
    pass
    
    cmdSequence                += " ; xspecModels.useModels('%s')" %(models)
    cmdSequence                += " ; PerformSpectralAnalysis(configuration=conf)"
    
    print("\nSubmitting command sequence: %s" %(cmdSequence))
        
    subs[-1].submitCommand(cmdSequence)
  pass
  
  #Wait for the jobs to finish
  _waitForJobs(subs)
  print("\nAll jobs done!\n")
  
      
pass
