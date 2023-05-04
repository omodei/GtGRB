import os, errno
import pickle
import shelve
import glob
import types
import subprocess, shlex
import time, datetime
import sys, string

#This module implements a solution to run a command from a GtGRB session
#in the SLAC farm

#Author: G.Vianello (giacomov@slac.stanford.edu)

class copier(object):
  def __init__(self,speedLimit=10240,compress=True):
    self.speedLimit            = speedLimit #In Kb/s
    self.compress              = True
  pass
  
  def getCopyCommand(self,source,destination):
    source                     = self._normalizePath(source)
    #Directory or file?
    if(os.path.isdir(source)):
      isDirectory              = True
    else:
      isDirectory              = False
    cmdLine                    = "rsync --copy-links --verbose -a"
    if(self.compress):
      cmdLine                 += "z "
    cmdLine                   += "--bwlimit=%s " %(self.speedLimit)
    cmdLine                   += "%s %s" %(source,destination)
    #print("\n\nCopy command %s \n" %(cmdLine))
    return cmdLine
  pass
  
  def _normalizePath(self,listOfPath):
    '''
      This:
      -Solves symbolic links
      -Transform every path in the list in its /nfs or /afs path
    '''
    isAlist                      = isinstance(listOfPath,list)
    if(not isAlist):
      listOfPath                 = [listOfPath]

    doubleSlashedSolved          = map(lambda x:os.path.normpath(x),listOfPath)
    homeReferenceSolved          = map(lambda x:os.path.expanduser(x),doubleSlashedSolved)
    envVariablesSolved           = map(lambda x:os.path.expandvars(x),homeReferenceSolved)
    symbolicSolved               = map(lambda x:os.path.realpath(x),envVariablesSolved) 
    absolutePath                 = map(lambda x:os.path.abspath(x),envVariablesSolved) 
    
    def myMapper(abspath):
      nfsRoot                    = '/nfs/farm'
      afsRoot                    = '/afs/slac'
      
      #Directory or file?
      if(os.path.isdir(abspath)):
        directory                = abspath
        filename                 = None
      else:
        directory                = os.path.dirname(abspath)
        filename                 = os.path.basename(abspath)  
            
      #now, the absolute path can start with /u, or /a, or /nfs, or /afs
      firstElement                = abspath.split(os.sep)[1]
      if  (firstElement.find("nfs")>=0 or firstElement.find("u")>=0):
        pathToReturn             = abspath     
      else:                
        if(firstElement.find("afs")>=0):      
          #Get a path of the kind /a/wain006/g.glast.u55/grb/BKGESTIMATOR_FILES/Bkg_Estimator
          curWorkDir             = os.getcwd()
          os.chdir(directory)
          userDiskPath           = os.getcwd() #this is it
          os.chdir(curWorkDir)
        elif(firstElement.find("a")>=0):
          userDiskPath           = os.path.normpath(directory)        
        #At this point, no matter what, we should have something like /a/wain006/g.glast.u55/*        
        url                      = userDiskPath.split("/")[3] #this is g.glast.u55
        g                        = url.split(".")[0] #this is g
        glast                    = url.split(".")[1] #this is glast
        disk                     = url.split(".")[2] #this is u55
        user                     = userDiskPath.split("/")[4] #this is grb
        restOfThePath            = "/".join(userDiskPath.split("/")[5:]) #this is BKGESTIMATOR_FILES/Bkg_Estimator
        
        if(filename):
          pathToReturn           = "%s/%s/%s/%s/%s/%s/%s" %(nfsRoot,g,glast,disk,user,restOfThePath,filename)
        else:
          pathToReturn           = "%s/%s/%s/%s/%s/%s" %(nfsRoot,g,glast,disk,user,restOfThePath)    
      return os.path.normpath(pathToReturn)
    pass
    
    absolutePath                 = map(lambda x:myMapper(x),absolutePath)
    if(not isAlist):
      absolutePath               = absolutePath[0]
    return absolutePath
  pass
###

class datafile(object):
  def __init__(self,localFilename,remoteDir,label):
    self.localFilename         = localFilename
    self.remoteDir             = remoteDir
    self.label                 = label
  pass
  
  def getTransferCommand(self):
    transferAgent              = copier()
    return transferAgent.getCopyCommand(self.localFilename,self.remoteDir)
  pass
  
###

#Here remote means the farm environment, while local means the user environment
class commandSubmitter(object):
  '''
    Usage:
      submitter = commandSubmitter([name],globals(),[copyLATdata=True,copyGBMdata=False,copyBKGEdata=True])
      
    You HAVE to provide globals()!  
  '''
  def __init__(self,name,outsideWorld,**kwargs):
    
    #The farm is at 64 bit!
    if(os.environ['OS_ARCH'].find("32bit")>0):
      raise ValueError("You are running on a 32 bit machine, while the farm run 64bit machines. Please retry from a 64bit machine")
    
    copyLATdata                 = True
    copyGBMdata                 = False
    copyBKGEdata                = False
    verbose                     = False
    storeSession                = True
    for key in kwargs.keys():
      if  (key.lower()=="copylatdata")  :          copyLATdata    = bool(kwargs[key])
      elif(key.lower()=="copygbmdata")  :          copyGBMdata    = bool(kwargs[key])
      elif(key.lower()=="copybkgedata") :          copyBKGEdata   = bool(kwargs[key])
      elif(key.lower()=="verbose")      :          verbose        = bool(kwargs[key])
      elif(key.lower()=="storesession") :          storeSession   = bool(kwargs[key])
    ###
    
    
    self.name                  = name
    self.grbName               = outsideWorld['results']['GRBNAME']
    self.verbose               = verbose
    self.copyLATdata           = copyLATdata
    self.copyGBMdata           = copyGBMdata
    self.copyBKGEdata          = copyBKGEdata
    
    if(self.copyBKGEdata==False):
      print("\nWARNING: copyBKGEdata is False, it means that the remote process would NOT be able to use the BKGE!")
      print("If this is not what you want, specify copyBKGEdata=True in the constructor.")
      time.sleep(2)
    
    #Save the values of the environment variables
    self.localIndir            = os.environ['INDIR']
    self.localOutdir           = os.environ['OUTDIR']
    self.localFT1              = "%s" %(os.path.expandvars(os.path.abspath(outsideWorld['results']['FT1'])))
    self.localDatadir          = os.path.join(os.environ['BASEDIR'],'gtgrb_data')
    self.pfilesBase            = os.environ['PFILES'].split(";")[0]
    try:
      self.pfilesRepositories  = os.environ['PFILES'].split(";")[1]
    except:
      self.pfilesRepositories  = ""  
    
    #Remote dir
    self.remoteIndir           = "$BASEDIR/INDIR"
    self.remoteOutdir          = "$BASEDIR/OUTDIR"
    self.remoteDatadir         = "$BASEDIR/gtgrb_data"
    self.remotePfilesBase      = "$BASEDIR"
    
    self.remoteFT1_gtmktime    = "%s/%s/%s" %(self.remoteOutdir,outsideWorld['results']['GRBNAME'],
                                              os.path.basename(outsideWorld['lat'][0].FilenameFT1_mktime))
    
    self.remoteFT2             = "$BASEDIR/INDIR/LAT/%s" %(os.path.basename(outsideWorld['results']['FT2']))
    #Determine files to copy on the farm
    datafiles                  = []
    if(self.copyLATdata):
      datafiles.append(datafile(outsideWorld['lat'][0].FilenameFT1_mktime,"%s/%s"%(self.remoteOutdir,outsideWorld['results']['GRBNAME']),"FT1 from gtmktime"))
      datafiles.append(datafile(outsideWorld['results']['FT2'],"%s/LAT"%(self.remoteIndir),"FT2"))
      #Check if we have LLE data for this burst
      lleDirectory             = glob.glob(os.path.join(self.localIndir,"LAT","%s_LLE" %(outsideWorld['results']['GRBNAME']),"*"))
      for ff in lleDirectory:
        datafiles.append(datafile(ff,"%s/LAT/%s_LLE"%(self.remoteIndir,outsideWorld['results']['GRBNAME']),"LLE data"))
    pass
    
    #The following will actually return the directory containing GBM files
    if(self.copyGBMdata):
      fitsDirGBM                 = glob.glob(os.path.join(self.localIndir,"GBM","*%s*"%(outsideWorld['results']['GRBNAME'][0:-3])))[0]
      cspecFiles                 = glob.glob(os.path.join(self.localIndir,"GBM","%s/*cspec*"%(fitsDirGBM)))
      tteFiles                   = glob.glob(os.path.join(self.localIndir,"GBM","%s/*tte*"%(fitsDirGBM)))
      for f in cspecFiles:
        datafiles.append(datafile(f,"%s/GBM/%s" %(self.remoteIndir,outsideWorld['results']['GRBNAME']),"GBM CSPEC files"))
      for f in tteFiles:
        datafiles.append(datafile(f,"%s/GBM/%s" %(self.remoteIndir,outsideWorld['results']['GRBNAME']),"GBM TTE files"))    
      
      dumpFiles                  = glob.glob(os.path.join(self.localDatadir,"GBMtoolsDumps","*%s*.dump"%(outsideWorld['results']['GRBNAME'][0:-3])))
      for f in dumpFiles:
        datafiles.append(datafile(f,"%s/GBMtoolsDumps"%(self.remoteDatadir),"GBMtools background model"))
      pass        
    pass
    
    #autofit configuration file
    f                            = glob.glob(os.path.join(self.localDatadir,"autofit.conf"))[0]
    datafiles.append(datafile(f,"%s"%(self.remoteDatadir),"Autofit configuration"))
    
    if(self.copyBKGEdata):
      BKGEFiles                  = glob.glob(os.path.join(self.localDatadir,"Bkg_Estimator","*%s*"%(outsideWorld['results']['IRFS'])))
      for f in BKGEFiles:
        datafiles.append(datafile(f,"%s/Bkg_Estimator"%(self.remoteDatadir),"BKGE files"))
      pass    
    pass
    
    pfilesDirectories          = self.pfilesBase.split(":")
    for f in pfilesDirectories:
      datafiles.append(datafile(f,"%s"%(self.remotePfilesBase),"pfiles"))
    pass
    datafiles.append(datafile(os.path.join(os.environ['GTGRB_DIR'],"syspfiles"),"%s"%(self.remotePfilesBase),"GtGRB pfiles"))
    
    if(self.verbose): 
      print("\nFiles and directories scheduled for being copied on the farm:\n")
    totalSize                  = 0
    for f in datafiles:
      size                     = os.path.getsize(f.localFilename)/1024.0/1024.0
      totalSize               += size
      if(self.verbose):
        print("\n  Local filename : %s" %(f.localFilename))
        print("  Size           : %.3f Mb" %(size))
        print("  Remote path    : %s" %(f.remoteDir))
        print("  File type      : %s" %(f.label))
      pass
    pass
    
    print("\nTotal files to be transferred : %s" %(len(datafiles)))
    print("Total size to be transferred  : %.2f Mb" %(totalSize))
    
    self.datafiles             = list(datafiles)
    self.submitterDatadir      = os.path.join(self.localOutdir,outsideWorld['results']['GRBNAME'],"_commandSubmitter")
    
    #Save the current list of active models for autofit
    self.currentlyActiveModels = ",".join(map(lambda x:x.suffix.strip("_"),outsideWorld['xspecModels'].models.values()))
    
    #Save the current status of the gtgrb session (all variables!)
    if not os.path.exists(self.submitterDatadir):
      os.makedirs(self.submitterDatadir)
    
    self.shelfName             = "%s.data" %(name) 
    self.shelfPath             = os.path.join(self.submitterDatadir,self.shelfName)
    self.shelf                 = shelve.open(self.shelfPath,"n")
    print("Saving variables in data files...")
    for key in outsideWorld.keys():
      #print("Considering {0}".format(key))
      thisType                 = type(outsideWorld[key])
      if(thisType==types.ModuleType or 
         thisType==types.BuiltinMethodType or
         thisType==types.MethodType):
        #Do not store modules
        continue
      if(thisType==types.FunctionType):
        #Is this a function of gtgrb?
        if(outsideWorld[key].__module__=='gtgrb'):
          #YES! do not store it
          continue  
      try:
        self.shelf[key]        = outsideWorld[key]        
        #if(self.verbose):
        #print("Shelving {0}".format(key))      
      except:        
        pass
        #if(self.verbose):
        #print('NOT shelving {0}'.format(key))
    pass    
    self.shelf.close()
    print("Done!")
    self.datafiles.append(datafile(self.shelfPath,"$BASEDIR","Shelf file with the current python session"))
    
    self.remoteScriptName       = os.path.join(self.submitterDatadir,"%s.py"%(name))
    self.logfileName            = os.path.join(self.submitterDatadir,"%s.log"%(name))
    self.processName            = name
    self.jobID                  = None
  pass
  
  def submitCommand(self,command,**kwargs):
    '''
    submitCommand([command],[queue=queue])
    '''
    queue                      = "long"
    
    for key in kwargs.keys():
      if  (key.lower()=="queue"):            queue       = kwargs[key]
    pass
    
    if(self.jobID!=None):
      raise ValueError("Only one job per submitter! You already submit job %s" %(self.jobID))
    pass
    
    #Write the python script to be executed remotely
    remoteJob                  = []
    remoteJob.append("import os, shelve, shutil")
    remoteJob.append("#Copy everything from the user space to the local (farm) space")
    
    #Set up all environment variables
    remoteJob.append("#Set up variables")
    remoteJob.append("baseDir                  = '/scratch/submitFitJobs/%s' %(os.environ['LSB_JOBID'])")
    remoteJob.append("os.environ['BASEDIR']    = baseDir")    
    remoteJob.append("farmIndir                = os.path.expandvars('%s') "%(self.remoteIndir))
    remoteJob.append("os.environ['INDIR']      = farmIndir")
    remoteJob.append("farmOutdir               = os.path.expandvars('%s') "%(self.remoteOutdir))
    remoteJob.append("os.environ['OUTDIR']     = farmOutdir")
    #create directories
    remoteJob.append("os.system('mkdir -p %s' %(os.environ['BASEDIR']))")
    remoteJob.append("os.system('mkdir -p %s' %(os.environ['INDIR']))")    
    remoteJob.append("os.system('mkdir -p %s' %(os.environ['OUTDIR']))")
    remoteJob.append("os.chdir(os.environ['BASEDIR'])")
    remoteJob.append("os.environ['HOME']       = baseDir")
    
    #Create all the other directories needed
    dirToCreate                = []
    for f in self.datafiles:
      dirToCreate.append(f.remoteDir)
    pass
    #Unify the list of directories
    dirToCreate                = set(dirToCreate)
    for d in dirToCreate:
      remoteJob.append("os.system('mkdir -p %s')" %(d))
    pass
    
    #Now copy all the files
    for df in self.datafiles:
      thisCopyCommand          = df.getTransferCommand()
      remoteJob.append("os.system('%s')"%(thisCopyCommand))
    pass
        
    remoteJob.append("os.environ['PFILES']     = os.path.expandvars('%s/pfiles;%s')" %(self.remotePfilesBase,self.pfilesRepositories))  
        
    #Print the configuration
    remoteJob.append("\nprint('')")
    remoteJob.append("print('ENVIRONMENT VARIABLES:')")
    remoteJob.append("for key,value in os.environ.iteritems():")
    remoteJob.append("  print('%s = %s' %(key,value))")
    remoteJob.append("print('Remote directory content:')")
    remoteJob.append("for dirname, dirnames, filenames in os.walk('.'):")
    remoteJob.append("  for subdirname in dirnames:")
    remoteJob.append("    print os.path.join(dirname, subdirname)")
    remoteJob.append("  for filename in filenames:")
    remoteJob.append("    print os.path.join(dirname, filename)")
    remoteJob.append("\n\n")
    
    remoteJob.append("from gtgrb import *")
    
    #Reload all the variables from the remote session
    remoteJob.append("shelf                    = shelve.open('%s')" %(self.shelfName))
    remoteJob.append("for key in shelf:")
    remoteJob.append("  try:")
    remoteJob.append("    if(key=='results'):")
    remoteJob.append("      remoteResults          = shelf[key].copy()")
    remoteJob.append("    elif(key=='lat' or key=='grb'):")
    remoteJob.append("      continue")
    remoteJob.append("    else:")
    remoteJob.append("      globals()[key]         = shelf[key]")
    remoteJob.append("  except:")
    remoteJob.append("    print('Could not load %s' %(key))")
    remoteJob.append("pass")
    remoteJob.append("shelf.close()")   
    
    #Replace FT1 and FT2 with the copy on the batch worker    
    remoteJob.append("#We can finally start the command")
    
    remoteJob.append("remoteFT1                      = '%s'" %(self.localFT1))
    remoteJob.append("remoteResults['FT1']           = os.path.expandvars('%s')" %(self.remoteFT1_gtmktime))
    remoteJob.append("remoteResults['FT2']           = os.path.expandvars('%s')" %(self.remoteFT2))
    remoteJob.append("remoteResults['quick']         = True #This is to skip gtmktime")
    remoteJob.append("remoteResults['mode']          = 'go'")     
    remoteJob.append("Set(**remoteResults)")
    remoteJob.append("Print()")
    remoteJob.append("xspecModels.useModels('%s')" %(self.currentlyActiveModels))
    #remoteJob.append("eval(%s)"%(repr(command)))
    for cmd in command.split(";"):
      remoteJob.append("%s" %(cmd.strip().replace("!"," ")))
    pass  
    remoteJob.append("Print()")
    
    #Stage out
    remoteJob.append("stageoutdir              = '%s/%s'" %(self.submitterDatadir, self.processName))
    remoteJob.append("#Remove the stageout directory if it already exists")
    remoteJob.append("try:")
    remoteJob.append("  shutil.rmtree(stageoutdir)")
    remoteJob.append("except:")
    remoteJob.append("  pass")
    remoteJob.append("pass")
    remoteJob.append("shutil.copytree('%s' %(os.environ['OUTDIR']),stageoutdir,ignore=shutil.ignore_patterns('*rmfit*','*Bkg_Estimates*','pha1','*_LAT_MKT.fits'))")
    
    #Cleanup
    remoteJob.append("os.chdir('/scratch')")
    remoteJob.append("os.system('rm -rf $BASEDIR')")
    #Handle Pfiles
    self.remoteJob             = "\n".join(remoteJob)
    
    #Write it to a file
    f                          = open(self.remoteScriptName,"w")
    f.write(self.remoteJob)
    f.close()
    
    #Submit to LSF and get the job ID    
    cmdLine                    = "bsub -q %s -J %s -o %s python %s" %(queue,self.processName,self.logfileName,self.remoteScriptName)
    print("\n\nSubmitting jobs %s..." %(self.processName))
    args                       = shlex.split(cmdLine)
    output,error               = subprocess.Popen(args,stdout = subprocess.PIPE, stderr= subprocess.STDOUT).communicate()
    self.jobID                 = output.split("<")[1].split(">")[0]
    print("  ---> Job ID is %s" %(self.jobID))
  pass
  
  def getProcessStatus(self):
    if(self.jobID==None):
      raise ValueError("You have to submit a job before! Use the submitCommand method")
    pass
    
    cmdLine                    = "bjobs %s" %(self.jobID)
    args                       = shlex.split(cmdLine)
    output,error               = subprocess.Popen(args,stdout = subprocess.PIPE, stderr= subprocess.STDOUT).communicate()
    status                     = "Cannot get status"
    for i in range(30):
      try:
        parsedOut                  = filter(lambda x:x!='',output.splitlines()[1].split(" "))
        status                     = parsedOut[2]
        break
      except:
        time.sleep(2)
        continue
    pass    
    return status
  pass
  
  def watch(self,refreshTime=10):
    previousStatus             = ''
    while(1==1):
      status                   = self.getProcessStatus()
      if(status!=previousStatus):
        print("\n%s->%s circa %s" %(previousStatus,status,str(datetime.datetime.now())))
        previousStatus         = status
      else:
        sys.stdout.write(".")
        sys.stdout.flush()    
      if(status=="DONE" or status=="EXIT"):
        break
      time.sleep(refreshTime)
    pass
    return status
  pass
  
  def isFinished(self):
    status                   = self.getProcessStatus()
    if(status=="DONE" or status=="EXIT"):
      return 1
    else:
      return 0  
  pass
  
  def getResults(self):
    self.results               = {}
    
    resultsFilename            = os.path.join(self.submitterDatadir,self.processName,self.grbName,"results_%s.txt" %(self.grbName))
    
    try:
      f                          = open(resultsFilename)
    except:
      return -1
    
    for row in f:
      if(row[0]=="#"):
        #This is a comment
        continue
      pass
      atoms                    = row.split("=")
      key                      = atoms[0].strip()
      value                    = atoms[1].strip()
      self.results[key]        = value
    pass
    f.close()
    return 1    
  pass  
###
