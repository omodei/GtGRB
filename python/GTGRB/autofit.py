#!/usr/bin/env python
#G.Vianello (giacomov@slac.stanford.edu)
import astropy.io.fits as pyfits
import os
import shlex, subprocess
import glob
import numpy
from operator import *
import xspecModels
import math
import pickle
import ROOT
import re, time
from math import *

#This is the delta in time below which two time stamps are considered equals
deltaTdifference               = 1E-3
deltaStatPerDOF                = 10

class detectorConfiguration(object):
  def __init__(self,name):
    #This is a string defining the channels to ignore in the fit,
    #using the syntax of the "ignore" command in Xspec. Please use
    #channels here, not energy
    self.channelsToIgnore      = "**-8.0 126-**"
    
    #This is the statistic to use for this detector (Xspec statistic)
    self.statistic             = "pgstat"
    
    self.name                  = name.upper()
  pass
  
  def getChanToIgnore(self):
    return self.channelsToIgnore
  pass
  
  def getStatistic(self):
    return self.statistic
  pass
  
  def setChanToIgnore(self,chanToIgnore):
    self.channelsToIgnore      = chanToIgnore
  pass
  
  def setStatistic(self,statistic):
    statistic                  = statistic.lower()

    if(statistic!="pgstat" and statistic!="chi" and statistic!="lstat" and statistic!="cstat"):
      raise ValueError("The statistic %s is unknown. You can use only statistic known by Xspec: chi, cstat, lstat, pgstat." %(statistic))
    pass
    
    if(statistic=="cstat"):
      print("WARNING: Xspec Cstat is different from Rmfit Cstat and is usually NOT suited for Fermi GRB analysis!")
    pass
    self.statistic             = statistic
  pass
###

#This class will contain the configuration for Autofit
class configuration(object):
  def __init__(self,confFile=None):
  
    if(confFile==None):
      confFile                   = os.path.join(os.environ['BASEDIR'],'gtgrb_data')
      confFile                   = os.path.join(confFile,"autofit.conf")      
    pass
    
    #open the file
    f                            = open(confFile,'r')
    db                           = pickle.load(f)
    
    self.confFile                = confFile
    
    self.detectors               = db['detectors']
    
    #This is the weighting scheme to use for chisq
    self.weighting               = db['weighting']
    
    #close the file
    f.close() 
  pass
  
  def Print(self,detlist=None):
    if(detlist==None):
      detlist                    = self.detectors.keys()
    for key in detlist:
      value                      = self.detectors[key]
      print("\nDetector %s:" %(key))
      print("-------------------")
      print("      Channels to be ignored  : %s" %(value.getChanToIgnore()))
      print("      Statistic to be used    : %s" %(value.getStatistic()))
    pass
  
  def _write(self,filename):
    
    f                          = open(filename,'w')
    db                         = {"detectors":self.detectors, "weighting":self.weighting}
    pickle.dump(db,f)
    f.close()
  pass
    
  def setChanToIgnore(self,detector,channels):
    '''
    setChanToIgnore(detector,channels)
    
    Change the channels to be ignored during the fit 
    for the detector "detector", which has to be a 
    known detector (for example: NAI_00, NAI_11, 
    BGO_01, BAT).
    
    "channels" is the expression for the channels to 
    be ignored, as in the "ignore" command in Xspec 
    (see Xspec manual). For example to ignore the first 
    5 channels and the last 3 channels in NAI_05:
    
    setChanToIgnore("NAI_05","1-5 126-128")
    
    You can also use part of the detector name, in which 
    case all the detectors matching that part will be 
    affected. For example, to change all at once all the
    NAI detector:
    
    setChanToIgnore("NAI","1-5 126-128")
    
    You can even change all the detectors at once (if 
    this makes any sense), by using and empty string 
    "" as detector name.
    
    WARNING: No check whatsoever is made on the "channels" 
    string.
    '''
    detlist                      = filter(lambda(x): x.find(detector.upper())>=0, 
                                          self.detectors.keys())
    
    for det in detlist:    
      try:
        thisDet                  = self.detectors[det]
      except:
        raise ValueError("Detector %s is not known, and/or %s is not part of any detector name." %(det,det))
      print("Modidying configuration of detector %s." %(det))
      self.detectors[det].setChanToIgnore(channels)
    pass
    print("\n\nNew configuration:\n")
    self.Print(detlist)
  pass

  def setStatistic(self,detector,statistic):
    '''
    setStatistic(detector,statistic)
    
    Change the statistic used for the detector "detector".
    
    The statistic known are:
    
    -chi         Chi squared
    -pgstat      A profile likelihood which assumes Poisson
                 statistic for the observed spectrum, and
                 Gaussian statistic for the background
                 (this is the recommended choice for Fermi
                 detectors)
    -cstat       A Poisson likelihood for both the observed
                 spectrum and the background. 
                 WARNING:this is different from Rmfit Cstat,
                         and it is normally wrong for Fermi
                         data (see Xspec manual)
    -lstat       Lorentzian likelihood
    
    Please see Xspec manual for a description.
    
    Examples: 
    
    set Swift/BAT statistic to "chi" (as it should):
    
    setStatistic("BAT","chi")
    
    You can also use part of the detector name, in which case 
    all the detectors matching that part will be affected. 
    For example, to change all at once all the NAI detector
    to use the Chisq statistic (for bright bursts):
    
    setStatistic("NAI","chi")
    
    To change ALL the detectors at once use an empty string as 
    detector name. For example, force every detector to use
    Chi squared:
    
    setStatistic("","chi")
    '''
    detlist                      = filter(lambda(x): x.find(detector.upper())>=0, 
                                          self.detectors.keys())
    
    for det in detlist:    
      try:
        thisDet                  = self.detectors[det]
      except:
        raise ValueError("Detector %s is not known, and/or %s is not part of any detector name." %(det,det))
      print("Modidying configuration of detector %s." %(det))
      self.detectors[det].setStatistic(statistic)
    pass
    print("\n\nNew configuration:\n")
    self.Print()
  pass
  
  def setWeighting(self,weighting):
    '''
    setWeighting(detector,statistic)
    
    Change the weighting scheme used. Note that this is a global
    property (the same weitghing scheme is used for every detector).
    The weighting scheme is used to compute error bars when using
    chisq. It does not affect in any way the analysis when using
    likelihood (pgstat, cstat or lstat).
    
    The known weighting schemes are:
    
    -standard    Error bars are sqrt(counts) or the values 
                 provided in the STAT_ERR column in the files
                 (with the systematic errors summed in quadrature).
                 For Fermi spectra: since the PHA files have the
                 POISSERR keyword set to True, Xspec will always
                 use sqrt(counts) independently of the STAT_ERR
                 column
    -model       Error bars are sqrt(model) (with the systematic
                 errors summed in quadrature). This is the right
                 choice when we are in the "mid-range" counts
                 regime (THIS IS THE DEFAULT)
    -gehrels     The error bars are computed following the
                 prescription from Gehrels, N. 1986, ApJ 303, 336.
                 Systematic errors ARE NOT USED.
    -churazov    Uses the suggestion of Churazov et al. 
                 (1996, ApJ 471, 673) to estimate the weight for 
                 a given channel by averaging the counts in 
                 surrounding channels.
    
    Please see Xspec manual for a description.
    
    Examples: 
    
    set the weighting to "gehrels":
    
    setWeighting("gehrels")
    '''
    
    if(weighting!="standard" and weighting!="model" 
       and weighting!="gehrels" and weighting!="churazov"):
      raise ValueError("Statistic %s is not known. Known values are: standard,model,gehrels,churazov" %(weighting))
    pass   
    self.weighting             = weighting
    print("\n\nWeighting changed to %s\n" %(self.weighting))
  pass
  
  def writeConfiguration(self):
    '''
    writeConfiguration()
    
    Write the current configuration as new default configuration.
    '''
    print("This will save the current configuration as the new default configuration.")
    yesno                      = raw_input("Are you sure? (yes/no)")
    
    yesno                      = yesno.lower()
    if(yesno.find("y")>=0):
      print("Writing configuration in %s..." %(self.confFile))
      self._write(self.confFile)
    else:
      print("No action taken")
    pass    
  pass
###

class spectrum(object):
  def __init__(self, filename, instrument, detector, detfilter, tstart, telapse, spec_num, exposure):
    self.tstart                = tstart
    self.tstop                 = tstart+telapse
    self.spec_num              = spec_num
    self.filename              = filename
    self.exposure              = exposure
    self.instrument            = instrument
    self.detector              = detector
    self.filter                = detfilter
  pass
###

class pha2File(object):
  def __init__(self, phafile):    
    
    splitted                   = os.path.split(phafile)
    
    self.filename              = splitted[1]
    
    self.directory             = splitted[0]
    
    #Read informations from the header of the file
    fitsFile                   = pyfits.open(phafile)
    
    #Instrument name
    self.instrument            = fitsFile['SPECTRUM'].header['INSTRUME']
    
    #Detector name (NAI_00, BGO_00, etc)
    try:
      self.detector            = fitsFile['SPECTRUM'].header['DETNAM']
    except:
      #This is not a GBM pha2file, if the instrument is the LAT, set detector to LAT, otherwise to 'unknown'
      if(self.instrument.find("LAT") >= 0):
        self.detector          = "LAT"
      else:
        self.detector          = "unknown"
    pass
    
    #Filter
    try:
      self.filter              = fitsFile['SPECTRUM'].header['FILTER']
    except:
      self.filter              = 'none'
    pass
    
    #Number of channels for this detector
    self.detchans              = fitsFile['SPECTRUM'].header['DETCHANS']
    
    #Number of spectra contained in this file
    self.nSpectra              = fitsFile['SPECTRUM'].data.shape[0]            

    #Read the SPECTRUM extension and fills a list of spectrum object
    
    self.spectra               = []
    for specID in range(self.nSpectra):
      row                      = fitsFile['SPECTRUM'].data[specID]
      thisSpectrum             = spectrum(self.filename, self.instrument, self.detector, self.filter,
                                          row.field("TSTART"),row.field("TELAPSE"),
                                          row.field("SPEC_NUM"),row.field("EXPOSURE"))
      self.spectra.append(thisSpectrum)
    pass
    
    fitsFile.close()    
    
  pass
  
  def getSpectrum(self, tstart, tstop):
    #Find the spectrum with the requested tstart and tstop, if any
    
    ##Define myComparator, which is a function which will be used to find the right interval. 
    #It will return true if spectrum has tstart and tstop compatible with the given tstart and tstop
    def myComparator( spectrum ):
      if((abs(spectrum.tstart - tstart) <= deltaTdifference) and
         (abs(spectrum.tstop - tstop) <= deltaTdifference)):
        return True
      else:
        return False
      pass
    pass
    
    #Find the spectrum compatible with the requested tstart and tstop
    spectrum                   = filter(myComparator, self.spectra)
    
    howMany                    = len(spectrum)
    if(howMany==1):
      return spectrum[0]
    elif(howMany==0):
      return None
    elif(howMany > 1):
      print("More than one spectrum compatible with tstart = %s and tstop = %s, check for problems!!" % (tstart,tstop))
      return spectrum[0]
    pass
  pass
###

class timeInterval(object):
  def __init__(self,tstart,tstop):
    self.tstart                = tstart
    self.tstop                 = tstop
    #This is the list of spectrum object pertaining this interval
    self.spectra               = []
  pass
  
  def isEqual(self, timeInterval):
    #Check if this time interval (self) is compatible with the given time interval (timeInterval)
    if( (abs(self.tstart-timeInterval.tstart) <= deltaTdifference) and
        (abs(self.tstop-timeInterval.tstop) <= deltaTdifference) ):
      return True
    else:
      return False
    pass 
  pass

  def assignSpectrum(self, spectrum):
    checkTinterval             = timeInterval(spectrum.tstart,spectrum.tstop)
    if(self.isEqual(checkTinterval)):
      self.spectra.append(spectrum)
    else:
      raise ValueError("ERROR while trying to assign a spectrum to a time interval: the two refer to different times")
  pass
###



class autofit(object):
  def __init__(self, workdir, grbName, trigger,userConf=None,**kwargs):
    self.grbName               = grbName
    self.trigger               = trigger
    
    self.XspecScriptsWritten   = False
    
    #Load the configuration
    if(userConf==None):
      confFile                   = os.path.join(os.environ['BASEDIR'],'gtgrb_data')
      confFile                   = os.path.join(confFile,"autofit.conf")
      try:
        self.configuration       = configuration(confFile)
        print("Read configuration from file %s " % (confFile))
      except:
        raise RuntimeError("Cannot load configuration for Autofit from file %s" %(confFile))
      pass
    else:
      #Use configuration already created by the user
      print("Using user-provided configuration for Autofit.")
      self.configuration         = userConf
    pass

    #Check that the workdir is accessible
    if(not os.access(workdir,os.W_OK)):
      raise ValueError("The directory %s does not exist, or is not accessible." %(workdir))
    pass    
    self.workdir               = workdir
    
    closestNaI                 = None
    PHAfilesRaw                = None
    #Default energy bands for flux computation
    fluxEnergyBandsString      = "10-1000,1000-1e5,1e5-1e7,10-1e7"
    componentByComponent       = True
    
    for key in kwargs.keys():
      if  (key.lower()=="closestnai")      :     closestNaI             = kwargs[key]
      elif(key.lower()=="fluxenergybands") :     fluxEnergyBandsString  = kwargs[key]
      elif(key.lower().find("component")==0)       :     componentByComponent   = int(kwargs[key])
      elif(key.lower()=="phafilesraw")     :     PHAfilesRaw            = kwargs[key]
    pass
    
    fluxEnergyBands        = []
    #The string is something like 10-1000,1000-1e5,1e5-1e7 
    bands                  = fluxEnergyBandsString.split(",")
    for b in bands:
      fluxEnergyBands.append(b.split("-"))
    pass
    
    print("\nConfigured energy bands for flux computation:")
    for b in fluxEnergyBands:
      print("%s - %s keV" %(b[0],b[1]))
    pass
    print("\n")
    
    if(componentByComponent==False):
      print("\nComponent-by-component flux/fluences and L/Eiso:   False")
    else:
      print("\nComponent-by-component flux/fluences and L/Eiso:   True") 
    pass
    
    self.fluxEnergyBandsString = fluxEnergyBandsString
    self.componentByComponent  = componentByComponent
    
    self._analizePHA(closestNaI,PHAfilesRaw)    
  pass
  
  def _analizePHA(self,closestNaI=None,PHAfilesRaw=None):
    if(PHAfilesRaw==None):
      #Get the name of all the PHA2 files in the working directory
      #Get first LAT data
      PHAfilesRaw                = filter(lambda el: el.rfind('.pha') > 0, os.listdir(self.workdir))    
    pass
    
    #Keep only .pha or .pha2
    PHAfilesRaw                = filter(lambda x:re.match(".*pha[2]?$",x)!=None,PHAfilesRaw)
    
    LATfiles                   = filter(lambda x: x.find("LAT") >= 0 or x.find("LLE") >= 0,PHAfilesRaw)
    
    if(closestNaI!=None):
      #Place the first available detectors in the first place
      closestNaIFile             = None
      for nai in closestNaI:
        NaINumber                = nai[1]
        if  (NaINumber=="a"):
          NaINumber              = 10
        elif(NaINumber=="b"):
          NaINumber              = 11
        else:
          NaINumber              = int(NaINumber)
        pass
            
        closestNaIFileList       = filter(lambda x: x.find("NAI_%02i" %(NaINumber)) >= 0,PHAfilesRaw)
        if(len(closestNaIFileList)>=1):
          closestNaIFile         = closestNaIFileList[0]
          break
      pass
      otherFiles               = filter(lambda x: x.find("LAT") < 0 and x.find("LLE") < 0 and x.find("NAI_%02i" %(NaINumber)) < 0,PHAfilesRaw)
      if(closestNaIFile!=None):
        otherFiles.insert(0,closestNaIFile)
    else:
      print("\nNo closest NaI detector specified. Using random order.\n")
      time.sleep(2)
      otherFiles               = filter(lambda x: x.find("LAT") < 0 and x.find("LLE") < 0,PHAfilesRaw)
    pass
    
    #This works even if LATfiles is empty (which means no LAT data in this fit)
    PHAfiles                   = LATfiles
    PHAfiles.extend(otherFiles)
    
    #Fill a list of pha2File classes
    self.pha2Files             = []
    for pha2 in PHAfiles:
      self.pha2Files.append(pha2File("%s" % (os.path.join(self.workdir,pha2))))
    pass
    
    #Now build a list containing for each time interval what spectra pertain to that interval
    #First of all build a comprehensive list of all the intervals contained in all the files,
    #avoiding duplicates
    self.intervals             = []
    for thisPha2 in self.pha2Files:
      for spectrum in thisPha2.spectra:
        thisInterval           = timeInterval(spectrum.tstart, spectrum.tstop)  
        #Is this timeInterval already present in the list?        
        filtered               = filter(thisInterval.isEqual, self.intervals)
        if(len(filtered)==0): self.intervals.append(thisInterval)        
      pass
    pass
    
    #Now assign the spectra to the time intervals
    print("\nData summary:")
    print("---------------------------------")
    for i,thisTimeInterval in enumerate(self.intervals):
      print("\n* Time interval %s (%s - %s):\n" %(i+1, thisTimeInterval.tstart-self.trigger,thisTimeInterval.tstop-self.trigger))
      for pha2 in self.pha2Files:
        thisSpectrum           = pha2.getSpectrum(thisTimeInterval.tstart,thisTimeInterval.tstop)
        if(thisSpectrum!=None):
          completeFilename     = "%s{%s}" % (thisSpectrum.filename,thisSpectrum.spec_num)
          print('  {0:10} {1:60}'.format(thisSpectrum.detector,completeFilename))
          #print("%10s %65s{%s}" %(thisSpectrum.detector,thisSpectrum.filename,thisSpectrum.spec_num))
          thisTimeInterval.assignSpectrum(thisSpectrum)
      pass
    pass    
                   
  pass
  
  def _writeEnergyBinningFileForXspec(self,intID):
    #Get the list of PHA files
    phaFiles                       = glob.glob("%s/*.rsp*" %(self.workdir))
    energies                       = []        
    
    for f in phaFiles:
      #Extract the EBOUNDS extension with fextract, reading it directly with pyfits is VERY
      #slow if the pha file is large
      cmdline                    = "fextract infile=%s[EBOUNDS] outfile=_ebounds.fits clobber=yes" % (f)
      #print(cmdline)
      args                       = shlex.split(cmdline)
      try:
        p                        = subprocess.check_call(args)
      except:
        print "ERROR IN EXECUTING FEXTRACT"
      pass
      thisF                        = pyfits.open("_ebounds.fits")
      ebounds                      = thisF['EBOUNDS']
      thisEmin                     = ebounds.data.field("E_MIN")
      thisEmax                     = ebounds.data.field("E_MAX") 
      thisF.close()
      thisEnergies                 = (thisEmin+thisEmax)/2.0
      energies.extend(list(thisEnergies))
      os.remove("_ebounds.fits")
    pass
    energies.sort()
    
    #add 100 bin between the first energy and 0.1 keV
    firstEnergy                    = energies[0]
    if(firstEnergy <= 5.0):
      nBins                        = 20
    elif(firstEnergy <= 50.0):
      nBins                        = 100
    else:
      nBins                        = 200
    pass    

    energyLowBound                 = 0.1 #keV
    
    energySpan                     = (firstEnergy-energyLowBound)
    binSize                        = energySpan/nBins
    lowBins                        = map(lambda x:energyLowBound+x*binSize,range(int(nBins)))
    energies.extend(lowBins)
    energies.sort()
    
    #add 1000 bin between 1e4 and 1.1e7 (these are needed for exponential cutoffs, otherwise
    #the flux in the band 1e4 1e7 will be unaccurate)
    nBins                          = 500.0
    energyHiBound                  = 1.1e7 #keV
    lastEnergy                     = 1e4
    energySpan                     = (energyHiBound-lastEnergy)
    binSize                        = energySpan/nBins
    hiBins                         = map(lambda x:lastEnergy+x*binSize,range(1,int(nBins)+1))
    energies.extend(hiBins)
    #Uniq the list
    mySet                          = set(energies)
    energies                       = list(mySet)
    energies.sort()
    
    filePathname                   = os.path.join(self.workdir,'__xspecEnergyBins_int%s.txt'%(intID))
    f                              = open(filePathname,"w")
    for e in energies:
      f.write("%.20g\n" %(e))
    pass  
    f.close()
    return filePathname
  pass
  
  def writeXspecScript(self,redshift=0.0,effectiveAreaCorrection=False):                
    preambol                   = ['#Automatically generated by Autofit (G. Vianello, giacomov@slac.stanford.edu)',
                                  '\n#Disable the echoing of script commands',
                                  'set xs_echo_script 0',
                                  '\n#Cd to the working directory',
                                  'cd %s' % (self.workdir),
                                  '\n#Disable the history of command (to avoid writing on the home dir. of the user)',
                                  'autosave off',
                                  'chatter 0',
                                  '\n#Set the proportional delta to 10 %',
                                  'xset delta 0.05',
                                  '\n#Load the scripts',
                                  'source $::env(AUTOFIT_XSPEC_SCRIPT)/my_writefits.xcm',
                                  'source $::env(AUTOFIT_XSPEC_SCRIPT)/superfit.xcm',
                                  '\n#Set the answer to any question "yes", to avoid Xspec waiting for the user input',
                                  'query yes\n',
                                  '\n#Define the redshift for this burst\n',
                                  "set redshift %s\n" % (redshift),
                                  "\n#Set the cosmology\n",
                                  "cosmo 71 0 0.73\n"]
    
    #Define the ad-hoc models
    preambol.append("\n#Define some ad-hoc models:")
    for adHoc in xspecModels.adHocDefinitions:
      preambol.append(adHoc)
    pass
    
    for intID, thisTimeInterval in enumerate(self.intervals):
      lines                    = list(preambol)
      print("\nWriting script for interval %s (%.4f - %.4f)" % (intID+1,thisTimeInterval.tstart-self.trigger,
                                                           thisTimeInterval.tstop-self.trigger))
      lines.append("\n#Interval %s (%.4f - %.4f)" % (intID+1,thisTimeInterval.tstart-self.trigger,
                                                           thisTimeInterval.tstop-self.trigger))
      lines.append('puts "Processing interval %s (%.4f - %.4f)" ' %(intID+1,thisTimeInterval.tstart-self.trigger,
                                                                          thisTimeInterval.tstop-self.trigger))
      lines.append('puts "-------------------------------------"\n')
      
      #Write commands to load data, and ignore the proper channels
      dataCommand              = 'data '
      ignoCommand              = 'ignore '
      for specID, thisSpectrum in enumerate(thisTimeInterval.spectra):
        dataCommand           += "%s:%s %s{%s} " % (specID+1,specID+1,thisSpectrum.filename,thisSpectrum.spec_num)
        #Decide what channels to ignore        
        try:
          thisDetConf         = self.configuration.detectors[thisSpectrum.detector]
          chanToIgnore        = thisDetConf.getChanToIgnore()
        except:
          print("\nONE OF THE DETECTORS USED FOR THE DATA IS NOT KNOWN!!")
          print("Detector %s is NOT known, using all channels" %(thisSpectrum.detector))
        pass
        
        ignoCommand          += '%s:%s ' % (specID+1,chanToIgnore)
      pass
                  
      lines.append("\n#Load the data files, and ignore the proper channels")
      lines.append(dataCommand)
      lines.append(ignoCommand)
      lines.append("ignore bad")
      
      #Set the proper energy array for the computation of the model: this affect
      #the flux computation (see the command "energies" in the Xspec manual)
      print("  Writing energy binning file...")
      energyBinningFile       = self._writeEnergyBinningFileForXspec(intID+1)
      lines.append("energies %s" %(energyBinningFile))
      print("  Done")
      #Now prepare the string which specify the statistic to be used for each dataset
      statistics              = []
      for specID, thisSpectrum in enumerate(thisTimeInterval.spectra):
        try:
          thisDetConf         = self.configuration.detectors[thisSpectrum.detector]
          statistic           = thisDetConf.getStatistic()
        except:
          statistic           = "pgstat"
          print("\nONE OF THE DETECTORS USED FOR THE DATA IS NOT KNOWN!!")
          print("Detector %s is NOT known, using default statistic (%s)" %(thisSpectrum.detector,statistic))
        pass
        statistics.append(statistic) 
      pass
      
      statisticString         = ",".join(statistics)
                  
      #now write the sections to fit the various models
      lines.append("\n#Fit various models:\n")
      for thisModel in xspecModels.models.values():
        lines.append('#==================================================')
        #Define the model
        lines.append("\n#Model %s" %(thisModel.fancyName))
        lines.append('puts "\nFitting model %s..."' %(thisModel.fancyName))
        lines.append("set initList [list]")
        for initExpr in thisModel.initExpression :
          lines.append('lappend initList "%s"' %(initExpr))
        pass

        #If the user wants to apply the effective area correction, do that
        if (effectiveAreaCorrection):          
          lines.append("\n#Apply the effective area correction")
                                                           
          #Prepare the string specifying the number in the PHA2 files
          #pha2numbersList    = []
          #referenceDetectors = []
          constString        = ""
          NaIAlreadyFound    = False
          
          for specID,thisSpectrum in enumerate(thisTimeInterval.spectra):
          
            #pha2numbersList.append(thisSpectrum.spec_num)
            
            #Use the LAT and the first NaI as reference detectors for
            #the effective area correction
            
            if(thisSpectrum.detector.lower().find("lat")>=0 or thisSpectrum.detector.lower().find("lle")>=0):
              #Fix the effective area correction for the LAT to 1
              #referenceDetectors.append(specID+1)
              constString    += "& 1.0 -1 "
            elif(thisSpectrum.detector.lower().find("nai")>=0 and NaIAlreadyFound==False):
              #Fix the effective area correction for the first NaI to 1
              #referenceDetectors.append(specID+1)
              NaIAlreadyFound = True
              constString    += "& 1.0 -1 "
            else:
              #Let the effective area correction free, allowing up to 30 % of correction
              constString    += "& 1.0 0.01 0.7 0.7 1.3 1.3 "  
          pass                                        
          
          #pha2numbersString   = ",".join(map(lambda x:str(x),pha2numbersList))
          #refDetString        = ",".join(map(lambda x:str(x),referenceDetectors))
          
          #Fit
          lines.append('#This is the init expression for the cons term for the effective area correction')
          lines.append('set constString "%s"' %(constString))
          lines.append('set fitOk [superFit %s 0 %s $initList $constString]' %(statisticString,thisModel.name))
          lines.append('') 
          
          #lines.append("divideDatasets %s %s" %(pha2numbersString,refDetString))
          lines.append("chatter 0")
          #lines.append('set fitOk [fitChain %s]' %(statisticString))
          lines.append('fixEffectiveAreaCorrections')
          lines.append('set fitOk [fitChain %s]' %(statisticString))
          lines.append('chatter 10')
          #lines.append('show parameters')
          #lines.append('show fit')
          lines.append('set fitOk [computeErrors 10]')
        else:
          #Fit
          lines.append('\n#Fit recipe: the following fit and compute the errors on the parameters')
          lines.append('set fitOk [superFit %s 1 %s $initList]' %(statisticString,thisModel.name))
          lines.append('') 
        pass
                
        #Write results in a FITS file
        lines.append('#Write results in a file: if the file already exists, the results will be appended')        
        lines.append('saveFits %s.fits %s %s %s $fitOk $redshift %s %s %s' %(thisModel.modelFilename, thisModel.suffix, 
                                                   thisTimeInterval.tstart,thisTimeInterval.tstop, intID+1, 
                                                   self.fluxEnergyBandsString,self.componentByComponent))
        lines.append('')
        
        #Plot the fit
        plotCmds = ['#Plot results (only if the fit is Ok, to avoid crashes)',
                    'if {$fitOk==1} {',
                    '  if { [catch { cpd /xs } errVal]  } { ',
                    '  cpd %s_int%s.gif/CPS' % (thisModel.modelFilename+"_noX",intID+1),
                    '  }',
                    '  setplot energy']
        
        #Set the rebinning
        niceRebinningCmds     = []
        for specID,thisSpectrum in enumerate(thisTimeInterval.spectra):                 
          #Rebin (for plotting purposes only) LAT data to 1 sigma, and GBM data to 3.0 sigma         
          if(thisSpectrum.detector.lower().find("lat")>=0 or thisSpectrum.detector.lower().find("lle")>=0):
            niceRebinningCmds.append('  setplot rebin 0.2 3 %s' %(specID+1))
          elif(thisSpectrum.detector.lower().find("bgo")>=0):
            niceRebinningCmds.append('  setplot rebin 1.0 25 %s' %(specID+1))
          else:
            niceRebinningCmds.append('  setplot rebin 3.0 25 %s' %(specID+1))
          pass
        pass  
        plotCmds.extend(niceRebinningCmds)     
        plotCmds.extend(['  file delete %s_int%s_counts.qdp' % (thisModel.modelFilename,intID+1),
                    '  setplot background',
                    '  weight gehrels',
                    '  setplot command wdata %s_int%s_counts.qdp' % (thisModel.modelFilename,intID+1),                    
                    '  catch { plot lda } errVal',
                    '  setplot nobackground',
                    '  setplot delete 1',
                    '  file delete %s_int%s_countsModel.qdp' % (thisModel.modelFilename,intID+1),
                    '  setplot command wdata %s_int%s_countsModel.qdp' % (thisModel.modelFilename,intID+1),
                    '  catch { plot foldmodel } errVal',
                    '  setplot delete 1',                    
                    '  file delete %s_int%s_nuFnu.qdp' % (thisModel.modelFilename,intID+1),
                    '  setplot command wdata %s_int%s_nuFnu.qdp' % (thisModel.modelFilename,intID+1),
                    '  catch { plot eemodel } errVal',
                    '  setplot delete 1',
                    '  file delete %s_int%s_residuals.qdp' % (thisModel.modelFilename,intID+1),
                    '  setplot command wdata %s_int%s_residuals.qdp' % (thisModel.modelFilename,intID+1),
                    '  statistic chi',
                    '  weight churazov',
                    '  catch { plot delchi } errVal',
                    '  setplot delete 1'])
                    
        plotCmds.extend(['  setplot command LAbel T %s' % (thisModel.fancyName),
                    '  setplot command LAbel OT %s' % (self.grbName),
                    '  setplot command LAbel F Interval %s (%.4f-%.4f)' % (intID+1,thisTimeInterval.tstart-self.trigger,
                                                                           thisTimeInterval.tstop-self.trigger),
                    '  setplot command hard %s_int%s.ps/cps' % (thisModel.modelFilename,intID+1),
                    '  setplot command hard %s_int%s.gif/GIF' % (thisModel.modelFilename,intID+1),
                    '  catch { plot lda delchi} errVal',
                    '  setplot delete 1',
                    '  setplot delete 1',
                    '  setplot delete 1',
                    '  setplot delete 1',
                    '  setplot delete 1',
                    '}'])
        lines.extend(plotCmds)
        lines.append('#==================================================')
        lines.append('')
      pass
      lines.append('tclexit')
      lines.append('exit')
      
      #Write the script
      scriptPathname           = os.path.join(self.workdir,'doFit_int%s.xcm' % (intID+1))      
      tclScript                = open(scriptPathname,'w')
      for line in lines:
        tclScript.write(line)
        tclScript.write('\n')
      pass
      tclScript.close()
      lines                    = []      
      print("Done!")
    pass #End of loop over time intervals
    self.XspecScriptsWritten   = True    
  pass
  
  #This is the public interface
  def performFit(self,redshift=0.0,**kwargs):
    
    effAreaCorr          = False
    
    for key in kwargs.keys():
        if key.lower()=="effectiveareacorrection": effAreaCorr = bool(kwargs[key])
        pass
    pass
  
    #Check if we already wrote the Xspec scripts:
    if(not self.XspecScriptsWritten):
      self.writeXspecScript(redshift,effAreaCorr)
    pass
    
    for intID, thisTimeInterval in enumerate(self.intervals):      
      print("Open Xspec and fit: ")
  
      #run Xspec
      try:
        os.remove("mn_output.log")
        os.remove("xspec.log")
      except:
        pass
        
      #Delete the FITS files, if they already exists
      if(intID==0):
        for thisModel in xspecModels.models.values():
          try:
            fileToRemove       = os.path.join(self.workdir, "%s.fits" %(thisModel.modelFilename))           
            os.remove(fileToRemove)
            print("File %s removed" % (fileToRemove))
          except:
            pass  
        pass
      pass
      
      scriptPathname             = os.path.join(self.workdir,'doFit_int%s.xcm' % (intID+1))
      cmdline                    = "xspec - %s" % (scriptPathname)
      print(cmdline)
      args                       = shlex.split(cmdline)
      try:
        p                        = subprocess.check_call(args)
      except:
        print "ERROR IN EXECUTING XSPEC"
      pass
    pass  
    
    self._postProcessing()
      
    self._summarizeResults()
      
  pass
  
  def _errorsAreOk(self,thisErrorMask):
    #Now check if the errors for this model are ok
    errorsAreOk            = True
    
    for errorCode in thisErrorMask:
      if(float(errorCode) < 1): 
        #At least one parameter for this model has a invalid error range
        #(this means the fit has failed to converge. Most of the time this is due
        #to overfitting)
        errorsAreOk        = False
        break
      pass
    pass
    
    return errorsAreOk
  pass
  
  def _producePlots(self, **kwargs):
    from GTGRB import readQDP
    import gc
    
    interactive            = False
    nuFnuUnits             = "keV"
    for key,value in kwargs.iteritems():
      if(key.lower()=="interactive"):     interactive = bool(value)
      elif(key.lower()=="nufnuunits"):    nuFnuUnits  = value
    pass
    
    #Get the list of all QDP files
    countsFile             = ROOT.TFile(os.path.join(self.workdir,"countsSpectra.root"),"RECREATE")
    nuFnuFile              = ROOT.TFile(os.path.join(self.workdir,"nuFnuSpectra.root"),"RECREATE")
    
    timeIntervals          = ROOT.TNtuple("TimeIntervals","TimeIntervals","start:stop")
    
    for intID,thisInterval in enumerate(self.intervals):
      timeIntervals.Fill(thisInterval.tstart,thisInterval.tstop)
      livetime             = thisInterval.tstop-thisInterval.tstart
      
      #Get the name of the detectors used in the fit
      datasetsName         = []
      for pha in thisInterval.spectra:
        detname            = " ".join(pha.filename.split(".")[0].split("_")[1:])
        datasetsName.append(detname)
      pass
      
      for thisModel in xspecModels.models.values():
        thisRoot           = os.path.join(self.workdir,"%s_int%s" % (thisModel.modelFilename,intID+1))
        
        #Get the count spectrum
        spectrumFile       = "%s_counts.qdp"%(thisRoot)
        modelFile          = "%s_countsModel.qdp"%(thisRoot)
        if(os.access(spectrumFile,os.R_OK)):        
          a,b,c              = readQDP.plot(livetime,spectrum=spectrumFile,model=modelFile,datasetsName=datasetsName)
          countsFile.cd()
          if(interactive):
            import Tkinter
            import tkMessageBox
            root = Tkinter.Tk()
            root.withdraw()
            yesno = tkMessageBox.showinfo("Question", "If you want to edit the plot, click on the View menu and select Editor. By clicking on the different parts of the plot you can customize it. When you are done, press 'ok'.")
            root.quit()
            root.destroy()
          pass
            
          c['canvas'].Print(os.path.join(self.workdir,"%s_%s_counts.png" %(thisModel.modelFilename,intID+1)))
          c['canvas'].Write("%s_%s_counts" %(thisModel.fancyName,intID+1))
          del a,b,c
          gc.collect()
                  
          #Get the nuFnu
        
          d,e,f              = readQDP.plot(livetime,nuFnu="%s_nuFnu.qdp"%(thisRoot),nuFnuUnits=nuFnuUnits)
          nuFnuFile.cd()
          if(interactive):
            import Tkinter
            import tkMessageBox
            root = Tkinter.Tk()
            root.withdraw()
            yesno = tkMessageBox.showinfo("Question", "If you want to edit the plot, click on the View menu and select Editor. By clicking on the different parts of the plot you can customize it. When you are done, press 'ok'.")
            root.quit()
            root.destroy()
          pass
          f['canvas'].Print(os.path.join(self.workdir,"%s_%s_nuFnu.png" %(thisModel.modelFilename,intID+1)))
          f['canvas'].Write("%s_%s_nuFnu" %(thisModel.fancyName,intID+1))
          del d,e,f
          gc.collect()      
        else:
          print("The fit of the model %s in interval %s was not ok, no plot produced" %(thisModel.fancyName, intID+1))  
      pass
      countsFile.cd()
      timeIntervals.Write("TimeIntervals")
      nuFnuFile.cd()
      timeIntervals.Write("TimeIntervals")      
    pass 
    countsFile.Close()
    nuFnuFile.Close()     
  pass
  
  def _postProcessing(self, **kwargs):
    
    userRanking            = None
    
    for key in kwargs.keys():
        if   key.lower()=="ranking": 
          userRanking     = kwargs[key]
        else:
          print("Unknown command line argument: %s" %(key))        
        pass
    pass
    
    #This is to create a big FITS file (autofit_res.fits) containing the results of the fitting of all the models
    #This file will also contain  a RANKING column, containing the various models ordered taking into account
    #the value of the statistic, the complexity of the model (dof of the fit) and the improvement in the statistic
    #respect to simpler models (see myComparator below)
    #It will also contain BEST_* columns with fluxes/fluences based on the best model
    
    nIntervals                   = len(self.intervals)
    
    filenames                    = []
    suffixes                     = []
    for thisModel in xspecModels.models.values():
      thisFilename               = os.path.join(self.workdir,"%s.fits" %(thisModel.modelFilename))
      filenames.append(thisFilename)
      suffixes.append(thisModel.suffix)
    pass
    
    tstarts                      = []
    tstops                       = []
    for interval in self.intervals:
      tstarts.append(interval.tstart)
      tstops.append(interval.tstop)
    pass
    
    
    #Append the output files in a single FITS file
    #Add the column containing the name of the GRB, and the interval number
    
    columnList                   = []
    
    intCol                       = pyfits.Column(name='INTERVAL',format='I',
                                                 array=numpy.array(range(nIntervals))+1)
    namesValue                   = []
    for i in range(nIntervals): namesValue.append(self.grbName)
    nameCol                      = pyfits.Column(name='GRB_NAME',format='12A',
                                                 array=numpy.array(namesValue))
    #Now add an empty ranking column
    rankCol                      = pyfits.Column(name='RANKING',format='90A',
                                                 array=numpy.array(range(nIntervals))+1)
    #add tstart and tstop columns
    tstartCol                    = pyfits.Column(name='TSTART',format='E', unit='s since self.trigger',
                                                 array=numpy.array(tstarts)-self.trigger)
    tstopCol                     = pyfits.Column(name='TSTOP',format='E', unit='s since self.trigger',
                                                 array=numpy.array(tstops)-self.trigger)
    
    columnList.extend([nameCol,intCol,tstartCol,tstopCol, rankCol])
    #and empty columns for the fluxes/fluences
    
    #First of all get the energy bands contained in the file
    firstFile                    = pyfits.open(filenames[0])
    fluxCols                     = filter(lambda x:x.find("FLUX")>=0, firstFile[1].columns.names)
    fluxCols                     = filter(lambda x:x.find("Err")<0, fluxCols)
    #Filter out component fluxes
    r                            = re.compile('_C[0-9]+_')
    fluxCols                     = filter(lambda x:r.search(x)==None, fluxCols)
    print(fluxCols)
    energyBands                  = []
    for fl in fluxCols:
      energyBands.append(fl.split("_")[2:4])
    pass
    
    #Generate columns for flux and fluences (and their errors)
    
    for fl,unit in zip(["FLUX","FLUENCE"],["erg/cm2/s","erg/cm2"]):
      for band in energyBands:
        thisCol                  = pyfits.Column(name='BEST_%s_%s_%s' %(fl,band[0],band[1]),
                                                 format='D', unit=unit,
                                                 array=numpy.array(range(nIntervals))+1)
        columnList.append(thisCol)
        thisColErrm              = pyfits.Column(name='BEST_%s_%s_%s_ErrM' %(fl,band[0],band[1]),
                                                 format='D', unit=unit,
                                                 array=numpy.array(range(nIntervals))+1)
        columnList.append(thisColErrm)                                        
        thisColErrp              = pyfits.Column(name='BEST_%s_%s_%s_ErrP' %(fl,band[0],band[1]),
                                                 format='D', unit=unit,
                                                 array=numpy.array(range(nIntervals))+1)
        columnList.append(thisColErrp)
      pass
    pass    
    
    LCol                         = pyfits.Column(name='BEST_L',format='D', unit='1E53erg',
                                                 array=numpy.array(range(nIntervals))+1)
    LerM                         = pyfits.Column(name='BEST_L_ErrM',format='D', unit='1E53erg',
                                                 array=numpy.array(range(nIntervals))+1)
    LerP                         = pyfits.Column(name='BEST_L_ErrP',format='D', unit='1E53erg',
                                                 array=numpy.array(range(nIntervals))+1)
    EisoCol                      = pyfits.Column(name='BEST_EISO',format='D', unit='1E54erg',
                                                 array=numpy.array(range(nIntervals))+1)
    EisoerM                      = pyfits.Column(name='BEST_EISO_ErrM',format='D', unit='1E54erg',
                                                 array=numpy.array(range(nIntervals))+1)
    EisoerP                      = pyfits.Column(name='BEST_EISO_ErrP',format='D', unit='1E54erg',
                                                 array=numpy.array(range(nIntervals))+1)
    LAmatiCol                    = pyfits.Column(name='BEST_LAmati',format='D', unit='1E53erg',
                                            array=numpy.array(range(nIntervals))+1)
    LAmatierM                    = pyfits.Column(name='BEST_LAmati_ErrM',format='D', unit='1E53erg',
                                            array=numpy.array(range(nIntervals))+1)
    LAmatierP                    = pyfits.Column(name='BEST_LAmati_ErrP',format='D', unit='1E53erg',
                                            array=numpy.array(range(nIntervals))+1)
    EisoAmatiCol                 = pyfits.Column(name='BEST_EISOAmati',format='D', unit='1E54erg',
                                            array=numpy.array(range(nIntervals))+1)
    EisoAmatierM                 = pyfits.Column(name='BEST_EISOAmati_ErrM',format='D', unit='1E54erg',
                                            array=numpy.array(range(nIntervals))+1)
    EisoAmatierP                 = pyfits.Column(name='BEST_EISOAmati_ErrP',format='D', unit='1E54erg',
                                                 array=numpy.array(range(nIntervals))+1)
    
    columnList.extend([LCol, LerM, LerP,
                       EisoCol, EisoerM, EisoerP,
                       LAmatiCol, LAmatierM, LAmatierP,
                       EisoAmatiCol, EisoAmatierM, EisoAmatierP])                                             
    
    #Merge all the new columsn in one column descriptor class
    cdescriptor                  = pyfits.ColDefs(columnList)
    
    #Open the FITS files containing the results of the fit of the various models, and append
    #the columns taken from each file to the column descriptor for the big file
    openFiles                    = []
    for thisFile in filenames:
      openFiles.append(pyfits.open(thisFile))
      cdescriptor += openFiles[-1][1].columns
    pass
    
    #Write the big file, containing all the columns from all the FITS files
    hdu                          = pyfits.new_table(cdescriptor)
    outFilename                  = os.path.join(self.workdir,'autofit_res.fits')
    hdu.writeto(outFilename,clobber=True)
    
    #Close all the FITS files
    for thisFile in openFiles:
      thisFile.close()
    pass
    
    #Now open the merged table and decide the ranking, then fill the BEST_* columns
    mergedFits                   = pyfits.open(outFilename,'update')
    mergedTable                  = mergedFits[1]
    
    mergedTable.header.update("EXTNAME","AUTOFIT RESULTS")
    
    ##Define myComparator, which is a function which will be used to order models. 
    #It will return 1 if y is better than x, 0 if they are equivalent, -1 if x is better than y
    def myComparator(x,y):
      #First of all check the status of the errors for the two models
      xHasGoodErrors           = x[2]
      yHasGoodErrors           = y[2]
      
      #If one model has good errors, and the other not, the former is favoured
      if(xHasGoodErrors and yHasGoodErrors==False):        
        return -1
      elif(yHasGoodErrors and xHasGoodErrors==False): 
        return 1
      else:
        #If both have good errors, or both have bad errors, check the statistic and the degrees of freedom:
        #the most complex model is favoured if the delta stat between the two models is at least
        # 10*deltaDof, where deltaDof is the difference in the number of degrees of freedom        
        deltaDof                 = y[1]-x[1]
        deltaDof                 = 0
        if(deltaDof > 0):
          #model y is simpler than model x
          deltaStat              = y[0]-x[0]
          if(deltaStat >= deltaDof*deltaStatPerDOF):
            #The most complex model is favoured (i.e., y > x)
            return -1
          else:
            return 1          
        elif(deltaDof < 0):
          #model y is more complex than model x
          deltaStat              = x[0]-y[0]
          if(deltaStat >= abs(deltaDof)*deltaStatPerDOF):
            #The most complex model is favoured (i.e., x > y)
            return 1
          else:
            return -1 
        elif(deltaDof == 0):
          #The model with the lowest statistic win
          xStat                = x[0]
          yStat                = y[0]
          if(xStat < yStat):
            return -1
          elif(xStat > yStat):
            return 1
          else:
            return 0
    pass
    
    best_fluxes                  = []
    best_fluxes_errM             = []
    best_fluxes_errP             = []
    best_fluences                = []
    best_fluences_errM           = []
    best_fluences_errP           = []
    
    best_L                       = []
    best_L_errM                  = []
    best_L_errP                  = []
    
    best_Eiso                    = []
    best_Eiso_errM               = []
    best_Eiso_errP               = []
    
    best_LAmati                  = []
    best_LAmati_errM             = []
    best_LAmati_errP             = []
    
    best_EisoAmati               = []
    best_EisoAmati_errM          = []
    best_EisoAmati_errP          = []
    
    rankings                     = []
    
    for i in range(nIntervals):
      
      #If we have user selected rankings, use them      
      if(userRanking!=None):
        suffixes                 = []
        thisUserRanking          = userRanking[i]
        for suf in thisUserRanking:
          suffixes.append("%s_" %(suf))
        pass
      pass
      
      #Select all rows referring to this time interval
      mask                       = mergedTable.data.field('INTERVAL') == i+1
      selected                   = mergedTable.data[mask]
      
      #Get the number of data points
      model1Name                 = xspecModels.suffixToFancyName(suffixes[0])
      model1                     = xspecModels.models[model1Name]
      model1nParam               = model1.nParameters
      model1Dof                  = selected.field('%sDOF' %(suffixes[0]))[0] 
      self.nDatapoint            = model1Dof+model1nParam
      
      stats                      = {}
      for value in suffixes:
        try:
          thisStat               = selected.field('%sSTAT_VALUE' %(value))[0]
          thisDof                = selected.field('%sDOF' %(value))[0]                    
          
          #Now check if the errors for this model are ok
          thisErrorMask          = selected.field('%sERROR_MASK' %(value))[0]
          errorsAreOk            = self._errorsAreOk(thisErrorMask)
          
          stats[value]           = [thisStat,thisDof,errorsAreOk]

        except:
          pass
      pass            
      
      #Now sort the dictionary respect to the criteria just defined   
      if(userRanking==None):
        orderedModels            = list(sorted(stats.iteritems(), key=itemgetter(1), reverse=False, cmp=myComparator))                
      else:
        orderedModels            = []
        for value in suffixes:
          fakeDict               = {value: stats[value]}
          fakeTuple              = sorted(fakeDict.iteritems(), key=itemgetter(1))
          orderedModels.append(fakeTuple[0])
        pass
      pass
      
      bestModel                  = orderedModels[0]    
      #Save the best values and the ranking for this interval
      thisFluxes               = []
      thisFluxes_ErrM          = []
      thisFluxes_ErrP          = []
      thisFluences             = []
      thisFluences_ErrM        = []
      thisFluences_ErrP        = []
      for band in energyBands:
        thisFluxes.append(selected.field('%sFLUX_%s_%s' %(bestModel[0],band[0],band[1]))[0])
        thisFluxes_ErrM.append(selected.field('%sFLUX_%s_%s_ErrM' %(bestModel[0],band[0],band[1]))[0])
        thisFluxes_ErrP.append(selected.field('%sFLUX_%s_%s_ErrP' %(bestModel[0],band[0],band[1]))[0])
        thisFluences.append(selected.field('%sFLUENCE_%s_%s' %(bestModel[0],band[0],band[1]))[0])
        thisFluences_ErrM.append(selected.field('%sFLUENCE_%s_%s_ErrM' %(bestModel[0],band[0],band[1]))[0])
        thisFluences_ErrP.append(selected.field('%sFLUENCE_%s_%s_ErrP' %(bestModel[0],band[0],band[1]))[0])
      pass
      
      best_fluxes.append(thisFluxes)
      best_fluxes_errM.append(thisFluxes_ErrM)
      best_fluxes_errP.append(thisFluxes_ErrP)
      best_fluences.append(thisFluences)
      best_fluences_errM.append(thisFluences_ErrM)
      best_fluences_errP.append(thisFluences_ErrP)
      
      best_L.append(selected.field('%sL' %(bestModel[0]))[0])
      best_L_errM.append(selected.field('%sL_ErrM' %(bestModel[0]))[0])
      best_L_errP.append(selected.field('%sL_ErrP' %(bestModel[0]))[0])
      
      best_Eiso.append(selected.field('%sEISO' %(bestModel[0]))[0])
      best_Eiso_errM.append(selected.field('%sEISO_ErrM' %(bestModel[0]))[0])
      best_Eiso_errP.append(selected.field('%sEISO_ErrP' %(bestModel[0]))[0])
      
      best_LAmati.append(selected.field('%sLAmati' %(bestModel[0]))[0])
      best_LAmati_errM.append(selected.field('%sLAmati_ErrM' %(bestModel[0]))[0])
      best_LAmati_errP.append(selected.field('%sLAmati_ErrP' %(bestModel[0]))[0])
      
      best_EisoAmati.append(selected.field('%sEISOAmati' %(bestModel[0]))[0])
      best_EisoAmati_errM.append(selected.field('%sEISOAmati_ErrM' %(bestModel[0]))[0])
      best_EisoAmati_errP.append(selected.field('%sEISOAmati_ErrP' %(bestModel[0]))[0])
      
      #Now fill the ranking string
      ranking = ''
      for k in range(len(orderedModels)):
        ranking+="%s " % (orderedModels[k][0])
      pass
      
      rankings.append(ranking)
    pass
    
    #now update the BEST_* columns
    for i,band in enumerate(energyBands):
      mergedTable.data.field('BEST_FLUX_%s_%s'%(band[0],band[1]))[:]           = numpy.array(map(lambda x:x[i],best_fluxes))
      mergedTable.data.field('BEST_FLUX_%s_%s_ErrM'%(band[0],band[1]))[:]      = numpy.array(map(lambda x:x[i],best_fluxes_errM))
      mergedTable.data.field('BEST_FLUX_%s_%s_ErrP'%(band[0],band[1]))[:]      = numpy.array(map(lambda x:x[i],best_fluxes_errP))
      mergedTable.data.field('BEST_FLUENCE_%s_%s'%(band[0],band[1]))[:]        = numpy.array(map(lambda x:x[i],best_fluences))
      mergedTable.data.field('BEST_FLUENCE_%s_%s_ErrM'%(band[0],band[1]))[:]   = numpy.array(map(lambda x:x[i],best_fluences_errM))
      mergedTable.data.field('BEST_FLUENCE_%s_%s_ErrP'%(band[0],band[1]))[:]   = numpy.array(map(lambda x:x[i],best_fluences_errP))  
    pass
    
    mergedTable.data.field('BEST_L')[:]                      = numpy.array(best_L)
    mergedTable.data.field('BEST_L_ErrM')[:]                 = numpy.array(best_L_errM)
    mergedTable.data.field('BEST_L_ErrP')[:]                 = numpy.array(best_L_errP)
    
    mergedTable.data.field('BEST_EISO')[:]                   = numpy.array(best_Eiso)
    mergedTable.data.field('BEST_EISO_ErrM')[:]              = numpy.array(best_Eiso_errM)
    mergedTable.data.field('BEST_EISO_ErrP')[:]              = numpy.array(best_Eiso_errP)
    
    mergedTable.data.field('BEST_LAmati')[:]                 = numpy.array(best_LAmati)
    mergedTable.data.field('BEST_LAmati_ErrM')[:]            = numpy.array(best_LAmati_errM)
    mergedTable.data.field('BEST_LAmati_ErrP')[:]            = numpy.array(best_LAmati_errP)
    
    mergedTable.data.field('BEST_EISOAmati')[:]              = numpy.array(best_EisoAmati)
    mergedTable.data.field('BEST_EISOAmati_ErrM')[:]         = numpy.array(best_EisoAmati_errM)
    mergedTable.data.field('BEST_EISOAmati_ErrP')[:]         = numpy.array(best_EisoAmati_errP)
    
    #and the RANKING column
    mergedTable.data.field('RANKING')[:]                     = numpy.array(rankings)
    mergedFits.close()
  pass
  
  def AICc(self, C,dof,npoints):
    #Akaike Information Criterion (corrected for finite-size)
    k                          = npoints-dof
    n                          = npoints
    #Mind that C = -log(Likelihood)
    #return 2.0*(k+C)+((2*k*(k+1))/(dof-1))
    return 2.0*C+(k+1)*log(npoints)
  pass
  
  def _summarizeResults(self,mode='plain',**kwargs):
    
    intervalNames              = None
    userRanking                = None
    
    for key in kwargs.keys():
        if   key.lower()=="intervalnames": 
          intervalNames        = kwargs[key]
          if(len(intervalNames)!=len(self.intervals)):
            message            = '''The number of interval names (%s) does not correspond to 
                                 the number of intervals (%s)''' % (len(intervalNames),len(self.intervals))
            raise ValueError(message)
          pass
        elif key.lower()=="ranking": 
          userRanking          = kwargs[key]
        else:
          print("Unknown command line argument: %s" %(key))        
        pass
    pass
    pass
    
    lines                      = []
    #open the autofit_res file
    resultsFilename            = os.path.join(self.workdir,'autofit_res.fits')
    resultsFile                = pyfits.open(resultsFilename)
    results                    = resultsFile["AUTOFIT RESULTS"]        
    
    print("%s:" %(self.grbName))
    print("--------------------------")
    
    for intID,interval in enumerate(self.intervals):
      
      #Decide and print interval name
      if(intervalNames!=None):
        intervalName           = intervalNames[intID]
      else:
        intervalName           = "Interval %s" % (intID+1)
      pass
      
      print("\n* %s:\n" % (intervalName))
      
      #Filter for this time interval
      mask                     = results.data.field('INTERVAL') == intID+1
      thisResults              = results.data[mask]
      
      #Get the ranking
      print("\n  # Ranking:\n")
      ranking                  = thisResults.field('RANKING')[0]
      suffixList               = ranking.split(" ")
      
      #Open the TEX file for writing
      thisTexRankingFilename   = os.path.join(self.workdir,"%s_ranking_int%s.tex" %(self.grbName,intID+1))
      thisTexRankingFile       = open(thisTexRankingFilename,'w')
      
      
      #Print the list of the models by ranking      
      format                   = "-beg-{0:>2}-sep-{1:>32} -sep- {2:^7} -sep- {3:^4}-sep-{4:^11}-sep-{5:^10}-end-"
      #User mode
      self.outputMode          = str(mode)
      print(self._openTable(6))
      lineFormat               = self._colTitlesOut(format+"-line-")
      print(lineFormat.format("#","Model","Stat.","Dof", "Delta stat.","Good fit"))
      
      #Latex
      self.outputMode          = 'latex'
      thisTexRankingFile.write(self._openTable(6))
      lineFormat               = self._colTitlesOut(format+"-line-")
      thisTexRankingFile.write(lineFormat.format("Rank","Model","Stat.","Dof", "Delta stat.","Good fit"))
      
      suffixesToPrint          = []

      for i,suffix in enumerate(suffixList):
        #Name
        fancyName              = xspecModels.suffixToFancyName(suffix)
        
        #Statistic
        thisStatColName        = suffix+"STAT_VALUE"
        thisStat               = thisResults.field(thisStatColName)[0]
        
        #Errors are ok?
        thisErrorMask          = thisResults.field(suffix+"ERROR_MASK")[0]
        errorsAreOk            = self._errorsAreOk(thisErrorMask)
        if(errorsAreOk): 
          errorsAreOkStr = "yes"
          suffixesToPrint.append(suffix) 
        else: 
          errorsAreOkStr = "no"
        pass
        
        #Dof
        dof                    = int(thisResults.field(suffix+"DOF")[0])
        
        npar                   = xspecModels.models[fancyName].nParameters
        #errorsAreOkStr         = str(self.AICc(thisStat,dof,dof+npar))
        
        #Delta stat 
        if(i==len(suffixList)-1):
          deltaStat            = " - "
        else:   
          nextStatColName      = suffixList[i+1]+"STAT_VALUE"
          nextStat             = thisResults.field(nextStatColName)[0]
          deltaStat            = nextStat-thisStat          
        pass
        
        #Print
        self.outputMode          = str(mode)
        lineFormat               = self._rowout(format)
        print(lineFormat.format(i+1,fancyName,thisStat,dof,deltaStat,errorsAreOkStr))
        self.outputMode          = 'latex'
        lineFormat               = self._rowout(format)
        thisTexRankingFile.write(lineFormat.format(i+1,fancyName,thisStat,dof,deltaStat,errorsAreOkStr))
        thisTexRankingFile.write("\n")
      pass
      
      caption                    = "%s: ranking of different models for %s (%.4g-%.4g s)" %(self.grbName, 
                                                                   intervalName,
                                                                   interval.tstart-self.trigger,
                                                                   interval.tstop-self.trigger)
      
      self.outputMode            = str(mode)
      print(self._closeTable(caption))
      self.outputMode            = 'latex'
      thisTexRankingFile.write(self._closeTable(caption))
      thisTexRankingFile.close()
      
      
      
      #Print the parameter of the two best models
      print("\n  # Best models parameters:\n")

      #If we have user selected rankings, use them      
      if(userRanking!=None):
        suffixesToPrint          = []
        thisUserRanking          = userRanking[intID]
        for suf in thisUserRanking:
          suffixesToPrint.append("%s_" %(suf))
        pass
      pass
      
      #Open the TEX file for writing
      thisTexModelFilename     = os.path.join(self.workdir,"%s_models_int%s.tex" %(self.grbName,intID+1))
      thisTexModelFile         = open(thisTexModelFilename,'w')            
      
      valueWidth               = int((72.0)/(3))
      
      thisTitleFormat          = "-beg-{0:^%s}-sep-{1:^%s}-sep-{2:^%s}-end--line-" % (valueWidth,valueWidth-3,valueWidth+3)
      
      #User mode
      self.outputMode          = str(mode)
      print(self._openTable(5))
      print(self._colTitlesOut(thisTitleFormat.format("Model","Parameter","Value")))                 
      #latex
      self.outputMode          = 'latex'
      thisTexModelFile.write(self._openTable(5))
      thisTexModelFile.write(self._colTitlesOut(thisTitleFormat.format("Model","Parameter","Value")))
      
      valueFormat              = "-beg-{0:>%s}-sep-{1:>%s}-sep-{2:>%s.4g}-math--sub-{3:<+%s.4g}-sub--sup-{4:<+%s.4g}-sup--math--end-" % (
                                                      valueWidth,valueWidth-3,valueWidth/3+1,valueWidth/3+1,valueWidth/3+1)  
      
      for modelSuf in suffixesToPrint:
        thisModelName            = xspecModels.suffixToFancyName(modelSuf)
        thisModel                = xspecModels.models[thisModelName]
        firstRow                 = True
        
        for par in thisModel.parList:        
          thisValue              = float(thisResults.field(par.getUglyName())[0])
          thisValueErrM          = float(thisResults.field(par.getUglyName()+"_ErrM")[0])
          thisValueErrP          = float(thisResults.field(par.getUglyName()+"_ErrP")[0])        
          
                 
          
          #Print the model name only in the first row of its section of the table
          if(firstRow):
            modelNameField       = thisModel.fancyName
            firstRow             = False
          else:
            modelNameField       = ""
          pass
          
          self.outputMode        = str(mode)
          print(self._rowout(valueFormat.format(modelNameField, par.getFancyName(),thisValue,thisValueErrM,thisValueErrP)))
        
          self.outputMode        = 'latex'
          thisTexModelFile.write(self._rowout(valueFormat.format(modelNameField, par.getFancyName(),thisValue,thisValueErrM,thisValueErrP)))
          thisTexModelFile.write("\n")
          
          modelNameField         = ""
        pass
        
        #Now print the fluences
        #First of all get the energy bands contained in the file
        fluxCols                     = filter(lambda x:x.find("BEST_FLUX")>=0, results.columns.names)
        fluxCols                     = filter(lambda x:x.find("Err")<0, fluxCols)
        bands                        = []
        for fl in fluxCols:
          bands.append(fl.split("_")[2:4])
        pass
        
        for thisBand in bands:
          thisModelFluence       = float(thisResults.field("%sFLUENCE_%s_%s" %(modelSuf,thisBand[0],thisBand[1])))
          thisModelFluenceErrM   = float(thisResults.field("%sFLUENCE_%s_%s_ErrM" %(modelSuf,thisBand[0],thisBand[1])))
          thisModelFluenceErrP   = float(thisResults.field("%sFLUENCE_%s_%s_ErrP" %(modelSuf,thisBand[0],thisBand[1])))         
          
          #Do not print the fluence if it is zero (i.e., no data sets in this band)
          self.outputMode        = str(mode)
          print(self._rowout(valueFormat.format(modelNameField, "Fluence (%s-%s keV)" %(thisBand[0],thisBand[1]),
                                                thisModelFluence,thisModelFluenceErrM,thisModelFluenceErrP  )) )
          self.outputMode        = 'latex'
          thisTexModelFile.write(self._rowout(valueFormat.format(modelNameField, "Fluence (%s-%s keV)" %(thisBand[0],thisBand[1]),
                                                thisModelFluence,thisModelFluenceErrM,thisModelFluenceErrP  )) )
          thisTexModelFile.write("\n")
        pass        
        
        #Print Liso and Eiso, if greater than zero
        thisModelL       = float(thisResults.field("%sL" %(modelSuf)))
        thisModelLErrM   = float(thisResults.field("%sL_ErrM" %(modelSuf)))
        thisModelLErrP   = float(thisResults.field("%sL_ErrP" %(modelSuf)))         
        
        #Do not print the fluence if it is zero (i.e., no data sets in this band)
        if(thisModelL > 0):
          self.outputMode        = str(mode)
          print(self._rowout(valueFormat.format(modelNameField, "Mean Lumin.",
                                                thisModelL,thisModelLErrM,thisModelLErrP  )) )
          self.outputMode        = 'latex'
          thisTexModelFile.write(self._rowout(valueFormat.format(modelNameField, "Mean Lumin.",
                                                thisModelL,thisModelLErrM,thisModelLErrP  )) )
          thisTexModelFile.write("\n")
        pass
        
        thisModelEISO       = float(thisResults.field("%sEISO" %(modelSuf)))
        thisModelEISOErrM   = float(thisResults.field("%sEISO_ErrM" %(modelSuf)))
        thisModelEISOErrP   = float(thisResults.field("%sEISO_ErrP" %(modelSuf)))         
        
        #Do not print the fluence if it is zero (i.e., no data sets in this band)
        if(thisModelEISO > 0):
          self.outputMode        = str(mode)
          print(self._rowout(valueFormat.format(modelNameField, "Eiso",
                                                thisModelEISO,thisModelEISOErrM,thisModelEISOErrP  )) )
          self.outputMode        = 'latex'
          thisTexModelFile.write(self._rowout(valueFormat.format(modelNameField, "E_{iso}",
                                                thisModelEISO,thisModelEISOErrM,thisModelEISOErrP  )) )
          thisTexModelFile.write("\n")
        pass
        
        #Now print the statistic for this model
        #Statistic
        thisStatColName        = modelSuf+"STAT_VALUE"
        thisStat               = float(thisResults.field(thisStatColName))
        
        #Dof
        dof                    = int(thisResults.field(modelSuf+"DOF"))
        
        statFormat             = "-beg-{0:>%s}-sep-{1:>%s}-sep-{2:>%s.4g}{3:<%s}{4:<%s}-end-" % (
                                                valueWidth,valueWidth-3,valueWidth/3+1,valueWidth/3+1,valueWidth/3+1)  

        self.outputMode        = str(mode)
        print(self._rowout(statFormat.format("", "Statistic", thisStat," (with %s" %(dof)," dof)")) )
        self.outputMode        = 'latex'
        thisTexModelFile.write(self._rowout(statFormat.format("", "Statistic", thisStat," (with %s" %(dof)," dof)")) )
        thisTexModelFile.write("\n")
        
        
        
        #Now print a line at the end of this model
        self.outputMode        = str(mode)
        print(self._colTitlesOut("-line-"))
        
        self.outputMode        = 'latex'
        thisTexModelFile.write(self._colTitlesOut("-line-"))
        thisTexModelFile.write("\n")
      pass
      
      caption                    = "%s: Best fit parameters for the best models for %s (%.4g-%.4g s)" %(
                                                                   self.grbName,intervalName, 
                                                                   interval.tstart-self.trigger,interval.tstop-self.trigger)
      
      self.outputMode          = str(mode)
      print(self._closeTable(caption))
      self.outputMode          = 'latex'
      thisTexModelFile.write(self._closeTable(caption))
      thisTexModelFile.close()
    pass
    
    resultsFile.close()
  pass
  
  def _colTitlesOut(self,string):
    mode                       = self.outputMode
    #The input line is supposed to be for a table, and it has to be "-beg- col1 -sep- col2 -sep- ... -end-")
    #-beg- will be substituted with the beginning code for a table in the three modes
    #-sep- will be the separator for columns in the three modes
    #-end- will be the end code for rows in the three modes    
    
    if(mode=='plain'):
      beg                      = ""
      sep                      = "|"
      end                      = ""
      line                     = "\n-----------------------------------------------------------------------------"
    elif(mode=='latex'):
      beg                      = ""
      sep                      = "&"
      end                      = " \\\\"
      line                     = "\n \hline \n"
    elif(mode=='confluence'):
      beg                      = "||"
      sep                      = "||"
      end                      = "||"
      line                     = ""
    pass    
    
    outstring                = string.replace("-beg-",beg)
    outstring                = outstring.replace("-sep-",sep)
    outstring                = outstring.replace("-end-",end)
    outstring                = outstring.replace("-line-", line)
      
    return outstring
  pass
  
  def _openTable(self,nColumns):
    mode                     = self.outputMode
    preambol                 = ""
    if(mode=='latex'):    
      preambol                 = "\\begin{table}\n\\begin{tabular}{|"
     
      for i in range(nColumns):
        preambol              += "l|"
      pass
      
      preambol                += "}\n \hline \n"

    pass
    return str(preambol)
  pass
  
  def _closeTable(self,caption=''):
    mode                       = self.outputMode
    
    if(mode=='plain'):
      capbeg                   = "\n[  "
      capend                   = "  ]"
      ending1                  = ""
      ending2                  = "\n"
    elif(mode=='latex'):
      capbeg                   = "\caption{"
      capend                   = " }\n"
      ending1                  = "\n\hline\end{tabular}\n"
      ending2                  = "\end{table}\n"
    elif(mode=='confluence'):
      capbeg                   = "\n[  "
      capend                   = "  ]"
      ending1                  = ""
      ending2                  = "\n"
    pass
    
    if(caption!=''): 
      closing                  = ending1+capbeg+caption+capend+ending2
    else:
      closing                  = ending1+ending2
    return str(closing)
  pass
  
  def _rowout(self,string):
    mode                       = self.outputMode
    #This is to output a line in different modes (plain, latex, confluence)
    
    #The input line is supposed to be for a table, and it has to be "-beg- col1 -sep- col2 -sep- ... -end-")
    #-beg- will be substituted with the beginning code for a table in the three modes
    #-sep- will be the separator for columns in the three modes
    #-end- will be the end code for rows in the three modes
    
    beginners                  = {}
    enders                     = {}
    if(mode=='plain'):
      beg                      = ""
      sep                      = "|"
      end                      = ""
      beginners["-sub-"]       = " "
      enders["-sub-"]          = " "
      beginners["-sup-"]       = " "
      enders["-sup-"]          = " "
      math                     = ""
    elif(mode=='latex'):
      beg                      = ""
      sep                      = " & "
      end                      = '\\\\'
      beginners["-sub-"]       = "_{"
      enders["-sub-"]          = "}"
      beginners["-sup-"]       = "^{"
      enders["-sup-"]          = "}"
      math                     = "$"
    elif(mode=='confluence'):
      beg                      = "| "
      sep                      = " | "
      end                      = " |"
      beginners["-sub-"]       = "{~}"
      enders["-sub-"]          = "{~}"
      beginners["-sup-"]       = "{^}"
      enders["-sup-"]          = "{^}"
      math                     = ""
    pass
    
    outstring                  = string.replace("-beg-",beg)
    outstring                  = outstring.replace("-sep-",sep)
    outstring                  = outstring.replace("-end-",end)
    outstring                  = outstring.replace("-math-",math)
    
    mathDisplayOpen            = False
    for tosearch in ["-sub-","-sup-"]:
      while(outstring.find(tosearch) >= 0):          
        splitted               = outstring.partition(tosearch)
        textBefore             = splitted[0]
        textToModify           = splitted[2].partition(tosearch)[0]
        textAfter              = splitted[2].partition(tosearch)[2]        
        outstring              = textBefore+beginners[tosearch]+textToModify+enders[tosearch]+textAfter        
      pass
    pass
    return outstring
  pass
  
### End of class autofit

class dataSet(object):
  def __init__(self,**kwargs):
    ROOT.gROOT.SetStyle('Plain')
    
    cut                       = ""
    workdir                   = ""
    
    for key in kwargs:
      if  (key.lower()=="cut")        :             cut     = kwargs[key]
      elif(key.lower()=="workdir")    :             workdir = kwargs[key]
      elif(key.lower()=="grbname")    :
        workdir               = os.path.join(os.environ['OUTDIR'],kwargs[key],"to_fit")    
    pass
        
    resultsFilename           = os.path.join(workdir,'autofit_res.fits')
    self.datafile             = pyfits.open(resultsFilename)
    data                      = self.datafile[1].data
    self.columns              = map(lambda x:x.upper(),self.datafile[1].columns.names)

    if(cut):
      cut                     = cut.replace("#","data.field('")
      cut                     = cut.replace(";","')")
      print("CUT is:")
      print("%s" %(cut))
      filt                    = eval(cut)
      self.data               = data[filt]
      print("Selected %s out of %s rows" %(len(self.data),len(data)))
    else:
      self.data               = data
    pass
    self.graphs               = {}    
  pass
  
  def __del__(self):
    self.datafile.close()
  pass
  
  def _colExists(self,colName):
    try:
      self.columns.index(colName.upper())
      return(True)
    except:
      return False  
  pass  
  
  def _computeExpression(self,expression,rescale=1):
    #Expression syntax: (#Var1; + #Var2;)/#Var3;
    
    #First of all remove all spaces
    expr                         = expression.replace(" ","") 
    
    #Isolate variables
    rg                           = re.compile("[^\(+/\-\*\)]*")
    varList                      = rg.findall(expr)
    variables                    = []
    for var in varList:
      if(var!=""):
        #Control if it is a number
        try:
          n                      = float(var)
        except:
          #it is not a number, it must be a variable  
          variables.append(var)
        pass  
    pass
    #Now substitute in the expression each variable with its 
    #ordinal number
    for i,var in enumerate(variables):
      expr                       = expr.replace(var,"v[%s]" %(i))
    pass
    
    #This list will contain the value of the variables
    v                            = []
    vErrM                        = []
    vErrP                        = []
    for var in variables:
      thisV, thisVErrM, thisVErrP = self._provideColumn(var)
      v.append(thisV)
      vErrM.append(thisVErrM)
      vErrP.append(thisVErrP)
    pass        
    v                            = numpy.array(v)
    vErrM                        = numpy.array(vErrM)
    vErrP                        = numpy.array(vErrP)
    
    #For the errors, just use the squared sum
    exprErrM                     = "0"
    exprErrP                     = "0"
    for i,var in enumerate(variables):
      exprErrM                   = "%s + vErrM[%s]*vErrM[%s]" %(exprErrM,i,i)
      exprErrP                   = "%s + vErrP[%s]*vErrP[%s]" %(exprErrP,i,i)
    pass
    
    #print("Evaluating:")
    #print("%s" % expr)
    #print("%s" % exprErrM)
    #print("%s" % exprErrP)
    
    results                      = eval(expr)
    resultsErrM                  = eval(exprErrM)
    resultsErrP                  = eval(exprErrP)
    
    #Rescale
    results                      = map(lambda x:x/rescale, results)
    resultsErrM                  = map(lambda x:sqrt(x)/rescale, resultsErrM)
    resultsErrP                  = map(lambda x:sqrt(x)/rescale, resultsErrP)
    
    return results, resultsErrM, resultsErrP
    
  pass
  
  def _provideColumn(self,colName):
    if(colName=="time"):
      var1                       = (self.data.field("TSTART")+self.data.field("TSTOP"))/2.0
      var1ErrM                   = (self.data.field("TSTOP")-self.data.field("TSTART"))/2.0
      var1ErrP                   = var1ErrM
      return var1, var1ErrM, var1ErrP  
    pass
    
    if(not self._colExists(colName)):
      raise ValueError("Column name %s does not exist!" %(colName))
    pass
    
    var1                        = self.data.field(colName)
    try:
      var1ErrM                  = map(lambda x:x*(-1),self.data.field(colName+"_ErrM"))
      var1ErrP                  = self.data.field(colName+"_ErrP")
    except: 
      #No errors available, silently accept the fact
      var1ErrM                  = map(lambda x:0,var1)
      var1ErrP                  = map(lambda x:0,var1)
    return var1, var1ErrM, var1ErrP
  pass
  
  def plot(self,**kwargs):
  
    var1name                  = None
    var2name                  = None
    rescale1                  = None
    rescale2                  = None
    plotOptions               = "AP"
    color                     = 1
    
    for key in kwargs:
      if  (key.lower()=="var1") :     var1name = kwargs[key]
      elif(key.lower()=="var2") :     var2name = kwargs[key]
      elif(key.lower()=="rescale1"):  rescale1 = kwargs[key]
      elif(key.lower()=="rescale2"):  rescale2 = kwargs[key]
      elif(key.lower()=="color"):     color    = kwargs[key]
      elif(key.lower()=="plotoptions") :     plotOptions     = str(kwargs[key])       
    pass
    
    #Make all var1name and var2name always lists
    if not isinstance(var1name,list):
      var1name                = [var1name]
    
    if not isinstance(var2name,list):
      var2name                = [var2name]   
    
    if(rescale1==None):
      #Use 1
      rescale1                = map(lambda x:1,var1name)
    pass
    
    if(rescale2==None):
      #Use 1
      rescale2                = map(lambda x:1,var2name)
    pass
    
    if not isinstance(rescale1,list):
      rescale1                = [rescale1] 
    
    if not isinstance(rescale2,list):
      rescale2                = [rescale2] 
    
    thisPlots                   = [] 
    for var1,var2,resc1,resc2 in zip(var1name,var2name,rescale1,rescale2):
           
      colName1                  = var1.replace("#","")
      colName2                  = var2.replace("#","")
    
      #Look if we already got this plot
      plotName                  = "%s Vs %s" %(colName1,colName2)
      if(self.graphs.get(plotName)):
        #yes, we already have it. Remove it
        dumb                    = self.graphs.pop(plotName)
      else:
        #Continue and build it
        pass
      pass
      
      v1, v1ErrM, v1ErrP        = self._computeExpression(colName1,resc1)
      
    
      v2, v2ErrM, v2ErrP        = self._computeExpression(colName2,resc2)
    
      self.graphs[plotName]     = ROOT.TGraphAsymmErrors()
      
    
      for i in range(len(self.data)): 
        self.graphs[plotName].SetPoint(i,v1[i],v2[i])
        self.graphs[plotName].SetPointError(i,v1ErrM[i],v1ErrP[i],v2ErrM[i],v2ErrP[i])
      pass
      self.graphs[plotName].SetName("%s Vs %s" %(var1,var2)) 
      self.graphs[plotName].GetXaxis().SetTitle("%s" %(var1))
      self.graphs[plotName].GetXaxis().CenterTitle()
      self.graphs[plotName].GetYaxis().SetTitle("%s" %(var2))
      self.graphs[plotName].GetYaxis().CenterTitle()
      self.graphs[plotName].SetMarkerColor(color)
      self.graphs[plotName].SetLineColor(color)
      thisPlots.append(plotName)      
    pass
    
    self.canvas                  = None

    #Now divide the canvas in pads
    self.canvas                  = ROOT.TCanvas()
    if(len(var1name)==1):
      pass
    elif(len(var1name)==2):
      self.canvas.Divide(2,1)
    elif(len(var1name)>2):  
      nDiv                         = floor(len(var1name)/2.0)
      nRows                        = ceil(len(var1name)/nDiv)
      self.canvas.Divide(numpy.int(nDiv),numpy.int(nRows))
    pass
    
    for i,name in enumerate(thisPlots):
      self.canvas.cd(i+1)
      self.graphs[name].Draw(plotOptions)
    pass
    
  pass
       
pass



