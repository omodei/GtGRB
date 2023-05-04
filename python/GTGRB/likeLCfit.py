import csv
import astropy.io.fits as pyfits
import numpy
import os
import glob
import ROOT
import shutil
from GtApp import GtApp
import math
from gtgrb import *

class likelihoodInterval(object):
  def __init__(self,row,noFile=False):
    #Remove all the empty columns (if any)
    while 1==1:
      try:
        row.remove('')
      except:
        break
    pass
    self.fitNum                = int(row[0])
    self.start                 = float(row[1])
    self.end                   = float(row[2])
    self.median                = float(row[3])
    self.Emin                  = float(row[4])
    self.Emax                  = float(row[5])
    self.Ts                    = float(row[6])
    self.NobsTot               = int(row[7])
    self.Npred_100             = float(row[8])
    self.Npred_1000            = float(row[9])
    self.index                 = float(row[10])
    self.errorI                = float(row[11])
    self.Flux                  = float(row[12])
    self.ErrorF                = float(row[13])
    self.EnergyFlux            = float(row[14])
    self.ErrorEF               = float(row[15])
    self.Fluence               = float(row[16])
    
    #Each interval has 3 files. Suppose this is interval # 27:
    # background_000027_273582334.0267_273582341.9358.pha
    # events_000027_273582334.0267_273582341.9358.pha
    # response_000027_273582334.0267_273582341.9358.rsp
    # gtsrcprob_22_5.623_10.000.fits
    if(noFile==False):
      self.eventFile             = glob.glob("gtsrcprob_%d_*.fits" %(self.fitNum))[0]
      
      rootFileName               = "_".join(self.eventFile.split("_")[2:])
      rootFileName               = ".".join(rootFileName.split(".")[:-1])
    pass
    #self.bkgSpectrum           = "background_%06d_%s.pha" %(self.fitNum,rootFileName)
  
    #self.observedSpectrum      = "events_%06d_%s.pha" %(self.fitNum,rootFileName)
  
    #self.response              = "response_%06d_%s.rsp" %(self.fitNum,rootFileName)
    
    
    
    print("Interval %s:" %(self.fitNum))
    print("Tstart-tstop: %s - %s"%(self.start,self.end))
    if(noFile==False):
      print("files: %s" %(self.eventFile))
    pass
  pass         
### End of likelihoodInterval class

'''
  Implements the likelihood result file coming from Nicola's 
  likelihood analysis (producing the lightcurve of the extented
  emission)
'''
class likelihoodResults(object):
  def __init__(self,filename,noFiles=False):
    with open(filename,"rb") as f:
      #Skip the 2 header line
      header                   = f.readline()
      header                   = f.readline()
      #Read the file and split the columns
      reader                   = csv.reader(f,delimiter='\t')
      self.intervals           = []
      for row in reader: 
        self.intervals.append(likelihoodInterval(row,noFiles))        
      pass

  ###

### End of class likelihoodResults

class ROIE_interval(object):
  def __init__(self,emin,emax,roi):
    self.emin                  = float(emin)
    self.emax                  = float(emax)
    self.roi                   = float(roi)
  pass
### End of class rspInterval

def _generateLC(eventFile,tmin,tmax,rootFileName, maxBinTime, ROI=None):
    
    #open the event file
    evtFile                    = pyfits.open(eventFile)
    events                     = evtFile["EVENTS"]   
    
    evtFile.close()
    
    binTime                    = maxBinTime*10
    div                        = 0.0
    while(binTime>=maxBinTime):
      div                     += 1.0
      binTime                  = (tmax-tmin)/div
    pass
    
    #Get tmin and tmax
    tmin                      += results['GRBTRIGGERDATE']
    tmax                      += results['GRBTRIGGERDATE']
    
    #If we have a ROI(E) to apply, apply it
    if(ROI!=None):
      eventForLC               = "%s_ROI_E_%s-%sMeV.fits" %(rootFileName,ROI.emin,ROI.emax)
      
      gtselect                 = GtApp.GtApp("gtselect")
      gtselect['infile']       = eventFile
      gtselect['outfile']      = eventForLC
      gtselect['ra']           = results['RA']
      gtselect['dec']          = results['DEC']
      gtselect['rad']          = ROI.roi
      gtselect['tmin']         = 0 #no filter
      gtselect['tmax']         = 0 #no filter
      gtselect['emin']         = ROI.emin
      gtselect['emax']         = ROI.emax
      gtselect['zmax']         = 180 #no cut (already cutted in the input file)
      gtselect['evclass']      = "INDEF"
      gtselect['convtype']     = -1
      gtselect['clobber']      = "yes"
      gtselect.run()
      
      lc                       = "%s_ROI_E_%s-%sMeV.lc" %(rootFileName,ROI.emin,ROI.emax)
       
    else:
      eventForLC               = eventFile 
      lc                       = "%s.lc" %(rootFileName)
    pass
    
    #run gtbin
    gtbin                      = GtApp.GtApp("gtbin")
    gtbin['evfile']            = eventForLC
    gtbin['scfile']            = results['FT2']
    gtbin['outfile']           = lc
    gtbin['algorithm']         = "LC"
    gtbin['tbinalg']           = "LIN"
    gtbin['tstart']            = tmin
    gtbin['tstop']             = tmax
    gtbin['dtime']             = binTime
    gtbin['lcemin']            = 0.01
    gtbin['lcemax']            = 300000
    gtbin['clobber']          = "yes"
    gtbin.run()
    
    return lc
pass


def _getExposure(lc, phIndex, roi=None):
    #Now run GtExposure on the lc
    gtexposure                 = GtApp.GtApp("gtexposure")
    gtexposure['infile']       = lc
    gtexposure['scfile']       = results['FT2']
    gtexposure['irfs']         = results['IRFS']
    gtexposure['srcmdl']       = 'none'
    gtexposure['specin']       = phIndex
    gtexposure['ra']           = results['RA']
    gtexposure['dec']          = results['DEC']
    
    if(roi==None):
      gtexposure['rad']          = results['ROI']
      gtexposure['emin']         = lat[0].Emin
      gtexposure['emax']         = lat[0].Emax
      gtexposure['enumbins']     = 30
    else:
      gtexposure['rad']          = roi.roi
      gtexposure['emin']         = roi.emin
      gtexposure['emax']         = roi.emax
      gtexposure['enumbins']     = 5
    pass
      
    gtexposure['apcorr']       = 'yes'        
    gtexposure['clobber']      = 'yes'
    gtexposure.run()
    
    #open the lc and get the exposure
    lcfile                     = pyfits.open(lc)
    exposure                   = lcfile['RATE'].data.field('EXPOSURE')
    timedel                    = lcfile['RATE'].data.field('TIMEDEL')
    tstarts                    = lcfile['RATE'].data.field('TIME')-(timedel/2.0)-results['GRBTRIGGERDATE']
    tstops                     = tstarts+lcfile['RATE'].data.field('TIMEDEL')
    lcfile.close()
    return exposure, tstarts, tstops    
pass

def _writePHA(data,errors,quality,rootFileName,specType,exposure=1,sys_err=None):
    try:
      l = len(data)
    except:
      data = [data]
    
    try:
      l = len(errors)
    except:
      errors = [errors]
    
    try:
      l = len(quality)
    except:
      quality = [quality]
    if(sys_err!=None):
      try:
        l = len(sys_err)
      except:
        sys_err = [sys_err]
    pass
      
    channelCol                 = pyfits.Column(name='CHANNEL',format='I',
                                             array=numpy.array(range(1,len(data)+1)))
    if(specType=="obs"):
      dataCol                  = pyfits.Column(name='COUNTS',format='D',
                                                 array=numpy.array(data))
    else:
      dataCol                  = pyfits.Column(name='RATE',format='D',
                                                 array=numpy.array(data))
    pass
    errorsCol                  = pyfits.Column(name='STAT_ERR',format='D',
                                             array=numpy.array(errors))
    if(sys_err!=None):
      sysErrorsCol             = pyfits.Column(name='SYS_ERR',format='D',
                                             array=numpy.array(sys_err)) 
    else:
      sysErrorsCol             = pyfits.Column(name='SYS_ERR',format='D',
                                             array=numpy.array(map(lambda x:0,errors)))
    pass 
                                            
    qualityCol                 = pyfits.Column(name='QUALITY',format='I',
                                             array=numpy.array(quality))
    colDef                     = pyfits.ColDefs([channelCol,dataCol,errorsCol,
                                                 sysErrorsCol, qualityCol])
    newTable                   = pyfits.new_table(colDef)
  
    newTable.header.update("EXTNAME","SPECTRUM")
    newTable.header.update("TELESCOP","GLAST")
    newTable.header.update("INSTRUME","LAT")
    newTable.header.update("FILTER","")
    newTable.header.update("EXPOSURE",exposure)    
    newTable.header.update("CORRFILE",'none')
    newTable.header.update("AREASCAL",1.0)
    newTable.header.update("BACKSCAL",1.0)        
    newTable.header.update("HDUCLASS",'OGIP')
    if(specType=='obs'):
      newTable.header.update("BACKFILE","%s.bak" %(rootFileName))
      newTable.header.update("RESPFILE","%s.rsp" %(rootFileName))
      newTable.header.update("ANCRFILE",'none')
      newTable.header.update("HDUCLAS1",'SPECTRUM')
      newTable.header.update("HDUCLAS2",'TOTAL')
      newTable.header.update("HDUCLAS3",'COUNT')
      newTable.header.update("HDUCLAS4",'TYPE:I')
      newTable.header.update("HDUVERS",'1.2.1')
      newTable.header.update("POISSERR",True)
    else:
      newTable.header.update("BACKFILE","none")
      newTable.header.update("RESPFILE","none")
      newTable.header.update("ANCRFILE",'none')
      newTable.header.update("HDUCLAS1",'SPECTRUM')
      newTable.header.update("HDUCLAS2",'BKG')
      newTable.header.update("HDUCLAS3",'RATE')
      newTable.header.update("HDUCLAS4",'TYPE:I')
      newTable.header.update("HDUVERS",'1.2.1')
      newTable.header.update("POISSERR",False)  
      newTable.header.update("CORRSCAL",1.0) 
    pass
    
    newTable.header.update("GROUPING",'0')    
    newTable.header.update("CHANTYPE","PI")
    newTable.header.update("DETCHANS",len(data))
    newTable.header.update("TLMIN",1)
    newTable.header.update("TLMAX",len(data))
    newTable.header.update("CREATOR","likeLCfit.py v1.0.0")
    newTable.header.update("AUTHOR","G.Vianello (giacomov@slac.stanford.edu)")    
    
    if(specType=='obs'):
      outfile                    = "%s.pha" %(rootFileName)
    else:
      outfile                    = "%s.bak" %(rootFileName)
    pass
      
    newTable.writeto(outfile,clobber='yes')
    return outfile
pass

def _writeRSP(tstarts,tstops,exposures,rootFileName):
    #Write the EBOUNDS extension
    try:
      l = len(tstarts)
    except:
      tstarts = [tstarts]
    
    try:
      l = len(tstops)
    except:
      tstops = [tstops]
    
    try:
      l = len(exposures)
    except:
      exposures = [exposures]
    
    channelCol                 = pyfits.Column(name='CHANNEL',format='I',
                                               array=numpy.array(range(1,2)))
    eminCol                    = pyfits.Column(name='E_MIN',format='D',
                                               array=numpy.array([tstarts[0]]),unit='keV')
    emaxCol                    = pyfits.Column(name='E_MAX',format='D',
                                               array=numpy.array([tstops[-1]]),unit='keV')                                         
    colDef                     = pyfits.ColDefs([channelCol,eminCol,emaxCol])
    ebounds                    = pyfits.new_table(colDef)
    
    ebounds.header.update("EXTNAME","EBOUNDS")
    ebounds.header.update("TELESCOP","GLAST")
    ebounds.header.update("INSTRUME","LAT")
    ebounds.header.update("FILTER","")       
    ebounds.header.update("HDUCLASS",'OGIP')
    ebounds.header.update("HDUCLAS1",'RESPONSE')
    ebounds.header.update("HDUCLAS2",'EBOUNDS')
    ebounds.header.update("HDUVERS",'1.2.0')
    ebounds.header.update("CHANTYPE","PI")
    ebounds.header.update("DETCHANS",1)
    ebounds.header.update("TLMIN1",1)
    ebounds.header.update("TLMAX1",1)
    
    outfile                    = '%s.rsp' %(rootFileName)
    ebounds.writeto(outfile,clobber='yes')
    
    #Write the MATRIX extension
    energ_loCol                = pyfits.Column(name='ENERG_LO',format='D',
                                               array=numpy.array(tstarts),unit='keV')
    energ_hiCol                = pyfits.Column(name='ENERG_HI',format='D',
                                               array=numpy.array(tstops),unit='keV')                                           
    n_grpCol                   = pyfits.Column(name='N_GRP',format='I',
                                               array=numpy.array(map(lambda x:1, tstarts)))
    f_chanCol                  = pyfits.Column(name='F_CHAN',format='I',
                                               array=numpy.array(map(lambda x:1, tstarts)))
    n_chanCol                  = pyfits.Column(name='N_CHAN',format='I',
                                               array=numpy.array(map(lambda x:1, tstarts)))
    matrixCol                  = pyfits.Column(name='MATRIX',format='D',
                                               array=numpy.array(exposures/(tstops-tstarts)))
    colDef                     = pyfits.ColDefs([energ_loCol,energ_hiCol,n_grpCol,f_chanCol,n_chanCol,matrixCol])
    matrix                     = pyfits.new_table(colDef)
    
    matrix.header.update("EXTNAME","MATRIX")
    matrix.header.update("TELESCOP","GLAST")
    matrix.header.update("INSTRUME","LAT")
    matrix.header.update("FILTER","")       
    matrix.header.update("HDUCLASS",'OGIP')
    matrix.header.update("HDUCLAS1",'RESPONSE')
    matrix.header.update("HDUCLAS2",'RSP_MATRIX')
    matrix.header.update("HDUVERS",'1.2.0')
    matrix.header.update("CHANTYPE","PI")
    matrix.header.update("DETCHANS",1)
    matrix.header.update("LO_THRES",0)
    matrix.header.update("TLMIN4",1)
    matrix.header.update("TLMAX4",1)
    
    pyfits.append(outfile,matrix.data,matrix.header)
    
    return outfile                                                                                                                                 
pass

def likelihoodLCfit(**kwargs):
  
  try:
    likelihoodFile               = "like_%s" %(results['GRBNAME'])
  except:
    raise RuntimeError("You need to use Set() before this")
  pass
  
  photonIndex                    = None
  computeResponse                = True
    
  for key in kwargs:
    if  (key.lower()=="likelihoodfile"):               likelihoodFile  = kwargs[key]
    elif(key.lower()=="photonindex"):                  photonIndex     = kwargs[key]
    elif(key.lower()=="norsp"):                        computeResponse = False
  pass
  
  #Read the likelihood file
  like                         = likelihoodResults(likelihoodFile)
  
  for interval in like.intervals:
    rootFileName               = "%s_likeLC_int%s" %(results['GRBNAME'],interval.fitNum)
    
    #Sum all the channels in the observed spectrum
    pha                        = pyfits.open(interval.observedSpectrum)        
    counts                     = sum(pha['SPECTRUM'].data.field('COUNTS'))

    #Get also the filter keywords (DS*)
    header                     = pha['SPECTRUM'].header
    filterKeys                 = {}
    for key in header.keys():
      if(key.find("DS")==0 or key.find("NDSKEYS")>=0):
          filterKeys[key]      = header[key]
    pass
    #and the GTI extension
    gti                        = pha['GTI'].copy()
    pha.close()
    #Write the PHA
    quality                    = 0 #GOOD
    error                      = math.sqrt(counts)
    obs                        = _writePHA(counts,error,quality,rootFileName,'obs')
    
    
    #Sum all the channels in the background spectrum
    pha                        = pyfits.open(interval.bkgSpectrum)
    rate                       = pha['SPECTRUM'].data.field('RATE')
    exposure                   = float(pha['SPECTRUM'].header['EXPOSURE'])
    bkgCounts                  = sum(rate*exposure)
    #This is the root of the squared sum
    squaredErrors              = map(lambda x:pow(x*exposure,2.0),pha['SPECTRUM'].data.field('STAT_ERR'))
    bkgErrors                  = math.sqrt(sum(squaredErrors))
    pha.close()
    if(bkgErrors==0):
      bkgErrors                = 0.15*bkgCounts
    pass
      
    #Write the background
    bkg                        = _writePHA(bkgCounts,bkgErrors,0,rootFileName,'bak')
    
    
    #Get the exposure
    #time                       = results['GRBTRIGGERDATE']+interval.start
    #telapse                    = interval.end-interval.start
    #lc                         = _generateDumbLc(time,telapse,counts,gti,filterKeys,rootFileName)
    if(computeResponse):
      lc                         = _generateLC(interval.eventFile, rootFileName, 5)
      
      if(photonIndex):
         exposure,tstarts,tstops  = _getExposure(lc,photonIndex)
      else:
        exposure,tstarts,tstops  = _getExposure(lc,interval.index)
      pass    
      #Write the response
      rsp                        = _writeRSP(tstarts,tstops,
                                             exposure,
                                             rootFileName)
      print("\nInterval %s - %s" %(interval.start,interval.end))
      print("-----------------------------------")
      print("Total exposure = %s cm2 s" %(numpy.mean(exposure)))
      print("Mean eff. Area = %s cm2\n" %(numpy.mean(exposure/(tstops-tstarts))))
    pass
  pass  
pass

def _readROIEfile(filename):
  #This read the filename output of MultiRspGen, containing the energy
  #intervals and the corresponding ROI
  with open(filename,"rb") as f:
      #Skip the header line
      header                   = f.readline()
      #Read the file and split the columns
      reader                   = csv.reader(f,delimiter='\t')
      intervals                = []
      for row in reader: 
        intervals.append(ROIE_interval(row[0],row[1],row[2]))        
      pass
  return intervals
pass

def _getBackground(tstart,tstop,emin,emax,nbins):
  thisBack                   = BKGE_Tools.Make_BKG_PHA(lat[0],False,
                                          t0=tstart,
                                          t1=tstop,
                                          emin=emin,
                                          emax=emax,
                                          ebins=nbins)
  #open the file
  backFile                   = pyfits.open(thisBack)
  bkgSpectrum                = backFile['SPECTRUM']
  exposure                   = bkgSpectrum.header['EXPOSURE']
  totalBkg                   = sum(bkgSpectrum.data.field('RATE'))
  stat_errs                  = map(lambda x:pow(x*exposure,2.0), bkgSpectrum.data.field('STAT_ERR'))
  stat_err                   = math.sqrt(sum(stat_errs))
  sys_err                    = numpy.mean(bkgSpectrum.data.field('SYS_ERR'))
  backFile.close()
  
  #Deliberately multiply everythin by exposure, because
  #Xspec expect RATE in channels, so to get the rate it divides for the
  #channel energy span, which in our case is again the exposure
  return totalBkg*exposure, stat_err, sys_err
pass

def likelihoodLCfitROIE(**kwargs):
  
  try:
    likelihoodFile               = "like_%s.txt" %(results['GRBNAME'])
  except:
    raise RuntimeError("You need to use Set() before this")
  pass
  
  photonIndex                    = None
  computeResponse                = True
  computeBackgr                  = True
  computePha                     = True
    
  for key in kwargs:
    if  (key.lower()=="likelihoodfile"):               likelihoodFile  = kwargs[key]
    elif(key.lower()=="photonindex"):                  photonIndex     = kwargs[key]
    elif(key.lower()=="norsp"):                        computeResponse = False
    elif(key.lower()=="nobak"):                        computeBackgr   = False
    elif(key.lower()=="nopha"):                        
                                                       computePha      = False
                                                       computeResponse = False
                                                       print("\nNo PHA means also no RSP!")
    elif(key.lower()=="rspgenfile"):                   rspgenFile      = kwargs[key]
  pass
  
  #Read the likelihood file
  like                         = likelihoodResults(likelihoodFile)
  roi_e                        = _readROIEfile(rspgenFile)
    
  for interval in like.intervals:
    rootFileName               = "%s_likeLC_int%s" %(results['GRBNAME'],interval.fitNum)
    exposures                  = []
    counts                     = []
    
    weightFormula              = ROOT.TF1("weightFormula","TMath::Power(x,[0])")
    
    for roi in roi_e:
      #Generate the light curve at this energy with this ROI
      if(computePha):
        thisLc                   = _generateLC(interval.eventFile, 
                                               interval.start,interval.end,
                                               rootFileName, 5, roi)
        #Read the light curve and get the total number of counts at this energy
        thisLcFile               = pyfits.open(thisLc)
        thisCounts               = sum(thisLcFile['RATE'].data.field("COUNTS"))
        counts.append(thisCounts)
      pass
      
      if(computeResponse):
        #Get the equivalent exposure
        if(photonIndex):
          exposure,tstarts,tstops  = _getExposure(thisLc,photonIndex, roi)
        else:
          exposure,tstarts,tstops  = _getExposure(thisLc,interval.index, roi)
        pass
      
        exposures.append(exposure)      
      pass
    pass
    
    if(computePha):
      #Now sum all the counts
      totalCounts                = sum(counts)    
    pass
    
    if(computeResponse):
      #Now for each time bin get the total exposure, weighting it with the spectrum
      weight                     = []
      if(photonIndex):
        phIndex                  = photonIndex
      else:
        phIndex                  = interval.index
      pass
    
      #Compute the weights for this interval    
      weightFormula.SetParameter(0,interval.index)
      weights                    = []
      for roi in roi_e:
        #Get the weight for this energy and this interval      
        weights.append(weightFormula.Eval((roi.emin+roi.emax)/2.0))
      pass
      sumWeight                  = sum(weights)
      weights                    = map(lambda x:x/sumWeight,weights)

      totalExposures             = []
      for i in range(len(tstarts)):
        thisExposure             = 0
        for j,expo in enumerate(exposures):
          thisExposure          += (expo[i]*weights[j])
        pass
        totalExposures.append(thisExposure)
      pass
    pass
      
    #### write the files
    if(computePha):
      ## PHA
      #Get some info from the PHA of this interval
      pha                        = pyfits.open(interval.eventFile)        

      #Get the filter keywords (DS*)
      header                     = pha['EVENTS'].header
      filterKeys                 = {}
      for key in header.keys():
        if(key.find("DS")==0 or key.find("NDSKEYS")>=0):
            filterKeys[key]      = header[key]
      pass
      #and the GTI extension
      gti                        = pha['GTI'].copy()
      pha.close()
      #Write the PHA
      quality                    = 0 #GOOD
      error                      = math.sqrt(totalCounts)
      obs                        = _writePHA(totalCounts,error,quality,rootFileName,'obs')
    pass
    
    if(computeResponse):
      ## RSP
      #Write the response
      rsp                        = _writeRSP(tstarts,tstops,
                                             totalExposures,
                                             rootFileName)
   
    pass
    
    dt                           = interval.end-interval.start
    
    if(computeBackgr):
      ## Background from the BKGE (in RATE!)
      thisBack,stat_err,sys_err  = _getBackground(interval.start,interval.end,
                                                  roi_e[0].emin,roi_e[-1].emax,len(roi_e))
    
      bak                        = _writePHA(thisBack,stat_err,0,rootFileName,'bak',dt, sys_err)
    pass
        
    print("\nInterval %s - %s" %(interval.start,interval.end))
    print("-----------------------------------")
    if(computePha):
      print("Total number of counts = %s +/- %s" %(totalCounts,error))
    if(computeBackgr):
      print("Total number of bkg counts = %s +/- %s" %(thisBack*dt,stat_err*dt))
    if(computeResponse):  
      print("Total exposure = %s cm2 s" %(numpy.mean(totalExposures)))
      print("Mean eff. Area = %s cm2\n" %(numpy.mean(totalExposures/(tstops-tstarts))))      
    pass
    print("\n\n")
  pass
  
    
pass
