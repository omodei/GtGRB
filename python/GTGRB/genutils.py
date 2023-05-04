import datetime
import math
import numpy as np
import astropy.io.fits as pyfits
import subprocess

_missionStart = datetime.datetime(2001, 1, 1, 0, 0, 0)
_century = 2000

# Convert RA HH:MM:SS.SSS into Degrees :
def convHMS(ra):
   try :
      sep1 = ra.find(':')
      hh=int(ra[0:sep1])
      sep2 = ra[sep1+1:].find(':')
      mm=int(ra[sep1+1:sep1+sep2+1])
      ss=float(ra[sep1+sep2+2:])
   except:
      raise
   else:
      pass
   
   return(hh*15.+mm/4.+ss/240.)

# Convert Dec +DD:MM:SS.SSS into Degrees :
def convDMS(dec):

   Csign=dec[0]
   if Csign=='-':
      sign=-1.
      off = 1
   elif Csign=='+':
      sign= 1.
      off = 1
   else:
      sign= 1.
      off = 0

   try :
      sep1 = dec.find(':')
      deg=int(dec[off:sep1])
      sep2 = dec[sep1+1:].find(':')
      arcmin=int(dec[sep1+1:sep1+sep2+1])
      arcsec=float(dec[sep1+sep2+2:])
   except:
      raise
   else:
      pass

   return(sign*(deg+(arcmin*5./3.+arcsec*5./180.)/100.))


def runShellCommand(string):
  #This is to substitute os.system, which is not working well
  #in the ipython notebook
  try:
    retcode = subprocess.call(string, shell=True)
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    else:
        pass
  except OSError, e:
    print >>sys.stderr, "Execution failed:", e
pass


def date2met(*kargs):
    datestring = kargs[0]
    
    if not isinstance(datestring,str):
        if notisinstance(datestring,float): print "date2met: Single argument needs to be a string of the format 2008-05-16 00:00:00 or 2008/05/16 00:00:00"
        raise ValueError
    
    sep='-'
    if '/' in datestring : sep='/'
    year,month,day=datestring.split(sep)
    if len(year)==2: year=int(year)+_century
    time   = 0.0
    decsec = 0.0
    
    try:
        # time given in the string?
        day = day.replace(' ',':')
        day,hours,mins,secs=day.split(':')
        secs=float(secs)
        secs_i = math.floor(secs)
        decsec = secs-secs_i
        current = datetime.datetime(year=int(year),month=int(month),day=int(day),hour=int(hours),minute=int(mins),second=int(secs_i))
    except ValueError:
        try:
            # time given in second of day as a second argument?
            time=int(kargs[1])
        except:
            pass
        current = datetime.datetime(int(year), int(month), int(day), 0,0,0)
        pass
    diff = current -_missionStart
    met= diff.days*86400. + diff.seconds + time + decsec
    leap=0
    if float(year)>2005:    leap+=1
    if float(year)>2008:    leap+=1
    if float(met) >=362793601.0: leap+=1 # June 2012 leap second    
    if float(met) >=457401601.0: leap+=1 # June 2015 leap second    
    if float(met) >=504921604.0: leap+=1 # Jan 2017 leap second    
    return met+leap


def met2date(MET,opt=None):
    """
    converts a MET time into a date string, in format \"08-07-25 10:26:09\".
    If opt=="grbname", the GRB name format 080725434 is returned. 
    """
    MET  = float(MET)
    leap = 0
    if MET>=252460802:  leap+=1
    if MET>=156677801:  leap+=1
    if MET>=362793603:  leap+=1 # June 2012 leap second
    if MET>=457401604:  leap+=1 # June 2015 leap second
    if MET>=504921605:  leap+=1 # 2017 leap second

    MET=MET-leap

    metdate  = datetime.datetime(2001, 1, 1,0,0,0)
    dt=datetime.timedelta(seconds=MET)
    grb_date=metdate + dt
    yy=grb_date.year
    mm=grb_date.month
    dd=grb_date.day
    hr=grb_date.hour
    mi=grb_date.minute
    ss=grb_date.second
    rss=round(ss+grb_date.microsecond*1e-6)        
    fff=round(float(rss+60.*mi+3600.*hr)/86.4)
    #print 'genutils:',MET, ss+grb_date.microsecond*1e-6,round(ss+grb_date.microsecond*1e-6),float(rss+60.*mi+3600.*hr)/86.4,fff
    if fff>999: fff=999
    d0=datetime.datetime(int(yy), 1,1,0,0,0)
    doy=(grb_date-d0).days+1
    try:
        if (opt.upper()=="GRBNAME" or opt.upper()=="NAME"):
            return '%02i%02i%02i%03i' %(yy-_century,mm,dd,fff)
        elif (opt.upper()=='FFF'):
            return grb_date,fff
        pass
    except:
        pass
    text='%04d-%02d-%02d %02d:%02d:%02d (DOY:%03s)' %(yy,mm,dd,hr,mi,ss,doy)
    return text

    
def angsep(x1,y1,x2,y2):
    """
    spherical angle separation, aka haversine formula
    input and output are in degrees
    """
    dlat = np.math.radians(y2 - y1)
    dlon = np.math.radians(x2 - x1)
    y1 = np.math.radians(y1)
    y2 = np.math.radians(y2)
    a = np.sin(dlat/2.)*np.sin(dlat/2.) + np.cos(y1)*np.cos(y2)*np.sin(dlon/2.)*np.sin(dlon/2.)
    c  = 2*np.arctan2(np.sqrt(a), np.sqrt(1.-a))
    return np.math.degrees(c)


def getNativeCoordinate( (alpha, delta), (alpha0, delta0) ):
    da = alpha - alpha0
    sina = math.sin( math.radians(da) )
    sind = math.sin( math.radians(delta) )
    sin0 = math.sin( math.radians(delta0) )
    cosa = math.cos( math.radians(da) )
    cosd = math.cos( math.radians(delta) )
    cos0 = math.cos( math.radians(delta0) )
    
    phi = math.atan2( cosd*sina, cos0*cosd*cosa+sin0*sind )
    theta = math.asin( -sin0*cosd*cosa + cos0*sind )
    
    return ( math.degrees(phi), math.degrees(theta) )


def getAngle(theta,phi):
    cost=math.cos(math.radians(theta))
    sint=math.sin(math.radians(theta))
    cosp=math.cos(math.radians(phi))
    sinp=math.sin(math.radians(phi))
    ang=math.atan2(math.sqrt((cost*sinp)**2+sint**2),cost*cosp)    
    return ang
    

if __name__=="__main__":
  import sys
  print "2001-01-01 00 00 00",' is ', date2met("2001-01-01 00 00 00")
  try:    
    print sys.argv[1],  met2date(float(sys.argv[1]))
  except:
    print sys.argv[1],  date2met(sys.argv[1])
  
def addExtension(fileName,extension,opt=''):
    ''' Add an extension to a file
    for example:
    addExtension(\'foo.txt\',\'_1\')
    transforms the file name:
    foo.txt
    into
    foo_1.txt
    opt = \'cp\' copies the new file
    opt = \'mv\'  moves the new file    
    '''
    import os    
    ext = fileName[fileName.rfind('.'):]
    newf= fileName.replace(ext,extension+ext)
    if opt=='cp' and os.path.exists(fileName): 
        cmd='cp %s %s' %(fileName, newf)
        runShellCommand(cmd)        
        pass
    
    elif opt=='mv' and os.path.exists(fileName): 
        cmd='mv %s %s' %(fileName, newf)
        runShellCommand(cmd)        
        pass
    
    return newf

def RSPs_to_RSP2(tstarts,tstops,rsplist, rsp2, trigger=0):
#Author: G.Vianello (giacomov@slac.stanford.edu)
    if(trigger!=0):
      for i in range(len(tstarts)):
        tstarts[i]          = tstarts[i]+trigger
        tstops[i]           = tstops[i]+trigger
    pass
    
    #Copy the first rsp to the output rsp2
    firstRsp                = pyfits.open(rsplist[0])
    try:
        matrixExt           = firstRsp['MATRIX'].data
        matrixHead          = firstRsp['MATRIX'].header
    except:
        matrixExt           = firstRsp['SPECRESP MATRIX'].data
        matrixHead          = firstRsp['SPECRESP MATRIX'].header
    
    firstRsp[0].header.update("DRM_NUM",len(rsplist))
    pyfits.writeto(rsp2,firstRsp[0].data,firstRsp[0].header,clobber=True)
    pyfits.append(rsp2,firstRsp['EBOUNDS'].data,firstRsp['EBOUNDS'].header)
    firstRsp.close()
    
    #now append all the other matrices
    for i in range(len(rsplist)):
      thisRsp               = pyfits.open(rsplist[i])
      #MATRIX or SPECRESP MATRIX?
      try:
        matrixExt           = thisRsp['MATRIX'].data
        matrixHead          = thisRsp['MATRIX'].header
      except:
        matrixExt           = thisRsp['SPECRESP MATRIX'].data
        matrixHead          = thisRsp['SPECRESP MATRIX'].header

      matrixHead.update('TSTART',tstarts[i]+trigger)
      matrixHead.update('TSTOP',tstops[i]+trigger)
      matrixHead.update('RSP_NUM',i+1)
      matrixHead.update('EXTVER',i+1)
      pyfits.append(rsp2,matrixExt,matrixHead)
      
      thisRsp.close()
    pass        
pass

def PHA1s_to_PHA2(tstarts,tstops,pha1list, pha2,trigger=0):
    # Author: G.Vianello (giacomov@slac.stanford.edu)
    #Read every pha1 in the pha1list, filling the following lists
    channels  = []
    fluxes    = []
    fluxesErr = []
    sysErr    = []
    exposures = []
    if len(pha1list)==0: return
    
    if ( len(pha1list)!=len(tstarts) or len(pha1list) != len(tstops) or len(tstarts)!=len(tstops) ):
      print("PHA1s_to_PHA2: impossible to produce the PHA2, the number of time intervals does not match with the number of files")
      return
    pass
    
    #Get the header for the first PHA1 file
    firstPHA1               = pyfits.open(pha1list[0])
    firstHeader             = firstPHA1['SPECTRUM'].header
    try:
      hasDetnam             = True
      firstDetnam           = firstHeader['DETNAM']
    except:
      hasDetnam             = False
      
    firstPHA1.close()
    
    for pha1 in pha1list:
      currentPHA1           = pyfits.open(pha1)
      spectrum              = currentPHA1['SPECTRUM']
      thisHeader            = spectrum.header
      
      #Check that the current spectrum is from the same instrument as the first one
      if(firstHeader['TELESCOP']!=thisHeader['TELESCOP'] or 
         firstHeader['INSTRUME']!=thisHeader['INSTRUME'] or
         (hasDetnam and (firstDetnam != thisHeader['DETNAM']))):
        raise ValueError("Error: PHA1 files MUST refer to observations performed by the same instrument!")
      pass 
      
      thisExposure              = spectrum.header['EXPOSURE']
      if(thisExposure < 0): raise ValueError("EXPOSURE < 0 in file %s" % pha1)
      
      #Channels
      thisChannels          = spectrum.data.field('CHANNEL')
      
      #Counts or rates?
      try:
        thisCounts          = spectrum.data.field('COUNTS')
        thisCountsErr       = spectrum.data.field('STAT_ERR')
        
        thisFluxes          = thisCounts/thisExposure
        thisFluxesErr       = thisCountsErr/thisExposure
      except:
        thisFluxes          = spectrum.data.field('RATE')
        thisFluxesErr       = spectrum.data.field('STAT_ERR')
      pass
      #Systematic errors?
      try:
        thisSysErr          = spectrum.data.field('SYS_ERR')
      except:
        thisSysErr          = thisFluxes-thisFluxes #A trick to have a vector of zeroes
      pass
      
      exposures.append(thisExposure)
      channels.append(thisChannels)
      fluxes.append(thisFluxes)
      fluxesErr.append(thisFluxesErr)
      sysErr.append(thisSysErr)
      currentPHA1.close()
    pass
    
    if(trigger!=0):
      for i in range(len(tstarts)):
        tstarts[i]          = tstarts[i]+trigger
        tstops[i]           = tstops[i]+trigger
    pass
    
    writePHA2file(tstarts,tstops, channels, fluxes, fluxesErr,sysErr,exposures, pha2, spectrum.header)
    
pass

def writePHA2file(tstarts,tstops,channels,fluxes,fluxesErr,sysErr,exposures,filename,header):
#Author: G.Vianello (giacomov@slac.stanford.edu)
    
    #These keywords will be copied from the input header "header" to the output file
    keywords = ['TELESCOP','INSTRUME','FILTER','BACKFILE','CORRFILE','CORRSCAL',
                'AREASCAL','RESPFILE','BACKSCAL',
                'ANCRFILE','CHANTYPE', 'DETNAM  ','TRIGTIME','OBJECT  ']
    
    nChan          = len(channels[0])
    
    vectFormatD    = "%sD" %(nChan)
    vectFormatI    = "%sI" %(nChan)        
    
    tstartCol      = pyfits.Column(name='TSTART',format='D',
                                   array=np.array(tstarts))
    telapseCol     = pyfits.Column(name='TELAPSE',format='D',
                                   array=(np.array(tstops)-np.array(tstarts)))
    spec_numCol    = pyfits.Column(name='SPEC_NUM',format='I',
                                   array=range(1,len(tstarts)+1))
    channelCol     = pyfits.Column(name='CHANNEL',format=vectFormatI,
                                   array=np.array(channels))
    ratesCol       = pyfits.Column(name='RATE',format=vectFormatD,
                                   array=np.array(fluxes))
    stat_errCol    = pyfits.Column(name='STAT_ERR',format=vectFormatD,
                                   array=np.array(fluxesErr))
    sys_errCol     = pyfits.Column(name='SYS_ERR',format=vectFormatD,
                                   array=np.array(sysErr))
    exposureCol    = pyfits.Column(name='EXPOSURE',format='D',
                                   array=np.array(exposures))
                                                                                                 
    coldefs        = pyfits.ColDefs([tstartCol,telapseCol,spec_numCol,channelCol,
                                     ratesCol,stat_errCol,sys_errCol,exposureCol])
        
    newTable       = pyfits.new_table(coldefs)
    
    #Add the keywords for this instrument and source:
    for key in keywords:
      try:
        newTable.header.update(key,header[key])
      except:
        pass
    pass
    #Add the keywords required by the OGIP standard:
    #Set POISSERR=F because our errors are NOT poissonian!
    #(anyway, neither Rmfit neither XSPEC actually uses the errors
    #on the background spectrum, BUT rmfit ignores channel with STAT_ERR=0)
    newTable.header.update('EXTNAME','SPECTRUM')   
    newTable.header.update('HDUCLASS','OGIP')    
    newTable.header.update('HDUCLAS1','SPECTRUM')
    newTable.header.update('HDUCLAS2','TOTAL')
    newTable.header.update('HDUCLAS3','RATE')
    newTable.header.update('HDUCLAS4','TYPE:II')
    newTable.header.update('HDUVERS','1.2.0')
    newTable.header.update('POISSERR',False)
    newTable.header.update('DETCHANS',nChan)
    newTable.header.update('TLMIN4',1)
    newTable.header.update('TLMAX4',nChan)
    newTable.header.update('CREATOR',"GRBAnalysis/GBMtoolkit/ftools.py","(G.Vianello, giacomov@slac.stanford.edu)")    
    
    #Write to the required filename
    newTable.writeto(filename,clobber='yes') 
pass
