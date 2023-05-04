#This is to get LLE data files (lle, pha and rsp)
#Author: giacomov@slac.stanford.edu

import os,sys,glob,pyfits,string,errno,shutil
from GTGRB.genutils import runShellCommand

class LLEdataCollector(object):
  def __init__(self,grbName,dataRepository=None,localRepository=None):
    self.grbName               = grbName
    
    if(dataRepository==None):
      try:
        environRepository      = os.environ['LLEREPOSITORY']
      except:
        raise RuntimeError("No LLE repository specified, and no LLEREPOSITORY environment variable set!")
      
      self.dataRepository      = environRepository
      
    else:
      self.dataRepository      = dataRepository
    pass
    
    print("LLE data repository (source): %s" %(self.dataRepository))
    
    if(localRepository==None):
      try:
        environRepository      = os.path.join(os.environ['INDIR'],"LAT","%s_LLE" %(self.grbName))
      except:
        raise RuntimeError("No LLE local repository specified, and no INDIR environment variable set!")
      
      self.localRepository     = environRepository      
    else:
      self.localRepository     = localRepository
    pass
    
    try:
      os.makedirs(self.localRepository)
      message                  = "just created"
    except OSError, e:
      if e.errno != errno.EEXIST:
        #Couldn't create the directory
        raise
      else:
        #Directory already existed
        message                = "already existent"  
    pass
    
    print("LLE data repository (destination): %s (%s)" %(self.localRepository,message))
    
    pass
  
  def getFTP(self):
    #ftp://legacy.gsfc.nasa.gov/fermi/data/lat/triggers
    #Path in the repository is [year]/bn[grbname]/current
    
    #Get the year
    year                      = "20%s" %(self.grbName[0:2])
    #trigger number
    triggerNumber             = "bn%s" %(self.grbName)
    
    remotePath                = "%s/%s/%s/current" %(self.dataRepository,year,triggerNumber)
    
    #Use wget to get the files
    cmdLine                   = "wget -nv -c %s/* -N -P %s" %(remotePath,self.localRepository)
    runShellCommand(cmdLine)
    
    #Now assign the files to the class members
    lleName                    = "gll_lle_bn%s_v*.fit" %(self.grbName)
    lleFiles                   = glob.glob(os.path.join(self.localRepository,lleName))
    #Get the most recent version
    versions                   = map(lambda x: int(os.path.basename(x).split("_")[3].split(".")[0].split("v")[1]),lleFiles)
    maxVersion                 = max(versions)

    lleName                    = "gll_lle_bn%s_v%02i.fit" %(self.grbName,maxVersion)
    lleFiles                   = glob.glob(os.path.join(self.localRepository,lleName))
    if(len(lleFiles)<1):
      raise RuntimeError("No LLE FT1 data available in %s" %(remotePath))
    
    cspecName                  = "gll_cspec_bn%s_v%02i.pha" %(self.grbName,maxVersion)
    cspecFiles                 = glob.glob(os.path.join(self.localRepository,cspecName))
    if(len(cspecFiles)<1):
      raise RuntimeError("No LLE CSPEC data available in %s" %(remotePath))
    
    rspName                    = "gll_cspec_bn%s_v%02i.rsp" %(self.grbName,maxVersion)
    rspFiles                   = glob.glob(os.path.join(self.localRepository,rspName))
    if(len(rspFiles)<1):
      raise RuntimeError("No LLE RSP file available in %s" %(remotepath))
    
    self.ft1File               = lleFiles[0]
    self.cspecFile             = cspecFiles[0]
    self.rspFile               = rspFiles[0]
        
    print("\n\nLLE data files:")
    print("\nFT1   file : %s" %(self.ft1File))
    print("CSPEC file : %s" %(self.cspecFile))
    print("RSP   file : %s" %(self.rspFile))    
  pass
    
  def get(self):
    if(self.dataRepository.find("ftp")==0):
      self.getFTP()
    else:
      self.getLocal()
    pass  
  pass
  
  def getLocal(self):    
    path                       = os.path.join(self.dataRepository,"GRB%s" %(self.grbName))
    availableVersions          = glob.glob(os.path.join(path,"v??"))
    if(len(availableVersions)==0):
      raise ValueError("No LLE data available for %s in %s" %(self.grbName,self.dataRepository))
    pass
    print("\nLLE data versions available:\n")
    for v in availableVersions:      
      print("%s" %(os.path.basename(v)))
    pass
    numericVersions            = map(lambda x:int(string.translate(os.path.basename(x),None,"v")),availableVersions)
    recentVersionNumber        = max(numericVersions)
    recentVersionPath          = os.path.join(path,"v%02i" %(recentVersionNumber))
    print("\nDownloading data from %s..." %(recentVersionPath))
    
    lleName                    = "gll_lle_bn%s_v%02i.fit" %(self.grbName,recentVersionNumber)
    lleFiles                   = glob.glob(os.path.join(recentVersionPath,lleName))
    if(len(lleFiles)<1):
      raise RuntimeError("No LLE FT1 data available in %s" %(recentVersionPath))
    
    cspecName                  = "gll_cspec_bn%s_v%02i.pha" %(self.grbName,recentVersionNumber)
    cspecFiles                 = glob.glob(os.path.join(recentVersionPath,cspecName))
    if(len(cspecFiles)<1):
      raise RuntimeError("No LLE CSPEC data available in %s" %(recentVersionPath))
    
    rspName                    = "gll_cspec_bn%s_v%02i.rsp" %(self.grbName,recentVersionNumber)
    rspFiles                   = glob.glob(os.path.join(recentVersionPath,rspName))
    if(len(rspFiles)<1):
      raise RuntimeError("No LLE RSP file available in %s" %(recentVersionPath))
    
    #Now get the files, if needed
    try:
      hypotheticalLocalCopy    = os.path.join(self.localRepository,os.path.basename(lleFiles[0]))
      if(not os.path.exists(hypotheticalLocalCopy)):
        #Get the file
        shutil.copy(lleFiles[0],self.localRepository)    
      pass
      self.ft1File               = os.path.join(self.localRepository,os.path.basename(lleFiles[0]))
    except OSError, e:
      print("\nCould not copy the FT1 file from %s to %s" %(lleFiles[0],self.localRepository))
      raise
      
    try:
      hypotheticalLocalCopy    = os.path.join(self.localRepository,os.path.basename(cspecFiles[0]))
      if(not os.path.exists(hypotheticalLocalCopy)):
        #Get the file
        shutil.copy(cspecFiles[0],self.localRepository)    
      pass
      self.cspecFile               = os.path.join(self.localRepository,os.path.basename(cspecFiles[0]))
    except OSError, e:
      print("\nCould not copy the CSPEC file from %s to %s" %(cspecFiles[0],self.localRepository))
      raise 
    
    try:
      hypotheticalLocalCopy    = os.path.join(self.localRepository,os.path.basename(rspFiles[0]))      
      if(not os.path.exists(hypotheticalLocalCopy)):
        #Get the file
        print("Getting RSP...")
        shutil.copy(rspFiles[0],self.localRepository)    
      pass    
      self.rspFile               = os.path.join(self.localRepository,os.path.basename(rspFiles[0]))
    except OSError, e:
      print("\nCould not copy the rsp file from %s to %s" %(rspFiles[0],self.localRepository))
      raise    
    
    print("Done!")
    print("\nLLE data files:")
    print("\nFT1   file : %s" %(self.ft1File))
    print("CSPEC file : %s" %(self.cspecFile))
    print("RSP   file : %s" %(self.rspFile))
  pass
  
###

#The following is for this module to be run from the command line

if __name__=='__main__':
  if(len(sys.argv) < 2):
    print("\nUsage:\n")
    print("%s [GRBNAME] [[remote repository path] [local repository path]]\n\n" %(sys.argv[0]))
    raise ValueError("\nSyntax error on the command line")
  else:
    grbName                    = sys.argv[1]
    dataRepository             = None
    localRepository            = None
    try:
      dataRepository           = sys.argv[2]
      localRepository          = sys.argv[3]
    except:
      pass
    pass
    
    getter                     = LLEdataCollector(grbName,dataRepository,localRepository)
    getter.get()
pass
