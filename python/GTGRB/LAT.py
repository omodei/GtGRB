#!/usr/bin/env python
"""Class managing LAT information for a given burst, defined by an instance of the GRB class.
Parameters : the GRB instance class (possibly None), and the path to the FT1 and FT2 files (possibly empty if grb is not None).
"""
import glob
import astropy.io.fits as pyfits
import ROOT

from Detector import Detector
from GRB import *
import plotter
import gtrmfit
import XSPEC
import genutils
import latutils
from GtGRB_IO import *
import math
from GtApp import GtApp
from scripts import LikelihoodFit
from GTGRB.genutils import runShellCommand

if  os.getenv('NOST') is None:
    import UnbinnedAnalysis
    pass

class LAT(Detector):
    """Class managing LAT information for a given burst, defined by an instance of the GRB class.
    Parameters : the GRB instance class (possibly None), and the path to the FT1 and FT2 files (possibly empty if grb is not None).
    """
    def __init__(self,grb=None):
        """The constructure inherits the members from the GRB provided. If a GRB object is not created, LAT creates one with the default constructor
        """
        if not isinstance(grb,GRB) and grb is not None :
            print 'Incorrect initialization, pass a GRB object as the 1st argument instead of ', grb.__class__
            raise TypeError
        elif grb is None:
            self.GRB = GRB()
        else:
            self.GRB = grb
            pass
        Detector.__init__(self,detector_name='LAT',grb=self.GRB)
        
        self.FilenameFT1  = ''
        self.FilenameFT2  = ''        
        self.IN_Directory = self.GRB.latdir
        self.Emin            =  10.0
        self.Emax            =  300000.0
        #self.Exposure       = 100
        self.Ebins           =  10
        self.EbinsRSP        =  100
        self.energybinalg    = 'LOG'
        self.radius          =  20
        self.zmax            =  180
        self._ResponseFunction='P6_V3_TRANSIENT' #'PASS5_v0_TRANSIENT' 'P5_v0_transient'
        self._eventClass      = "INDEF"
        self._evclsmin        = 0
        self._evclsmax        = 10
        self._Astroserver    = ""
        self._Datacatalog    = ""
        self.theta           = -1
        self.zenith          = -1
        self.phi             =  0
        self.chatter	     = 1
        self.FilenameFT1_sel    = self.out_dir+'/'+self.grb_name+'_LAT_SEL.fits'
        self.FilenameFT1_mktime = self.out_dir+'/'+self.grb_name+'_LAT_MKT.fits'
        self.evt_file        = self.out_dir+'/'+self.grb_name+'_LAT_ROI.fits'
        self.pha2_outFile    = self.out_dir+'/'+self.grb_name+'_LAT.pha2'
        self.expCube         = self.out_dir+'/'+self.grb_name+'_LAT_expCube.fits'
        self.expMap          = self.out_dir+'/'+self.grb_name+'_LAT_expMap.fits'
        self.likeFit         = self.out_dir+'/'+self.grb_name+'_LAT_spectrum.fits'
        #self.cmp_outFile     = self.out_dir+'/'+self.grb_name+'_LAT_ctsmap.fits'
        self.tsmap_outFile   = self.out_dir+'/'+self.grb_name+'_LAT_tsmap.fits'
        self.findsrc_outFile = self.out_dir+'/'+self.grb_name+'_LAT_findsrc.txt'
        self.like            = None
        self.AdditionalFiles = []
        self.like_optimizer="MINUIT"
        pass
    
    def SetResponseFunction(self,ResponseFunction):
        '''Use this method to set the ResponseFunction of the LAT object.'''
        # THIS FILE NEEDS TO BE CHANGED :: IRFS
        from GtBurst import IRFS
        myIRF = IRFS.IRFS[ResponseFunction]
        self._ResponseFunction = myIRF.name    # ResponseFunction
        self._eventClass       = myIRF.evclass # "INDEF"
        self._evclsmin         = myIRF.evclass # 0
        self._reprocessingVersion=myIRF.reprocessingVersion.split(',')[-1]
        
        
        # #################################################
        ASTROSERVER_REPOSITORY = '%s_P%s' %(myIRF.name[:2].upper(),self._reprocessingVersion) #os.getenv('P7REPOSITORY','P7.6_P130')
        if 'TRANSIENT' in self._ResponseFunction: self._Astroserver=ASTROSERVER_REPOSITORY+'_ALL'
        else: self._Astroserver=ASTROSERVER_REPOSITORY+'_BASE'
        self._Datacatalog = '/Data/Flight/Reprocess/P%s' % self._reprocessingVersion
        # #################################################
        print '--------------------------------------------------'
        print ' RESPONSE FUNCTION...:',self._ResponseFunction
        print ' EVENT CLASS.........:',self._eventClass
        print ' ASTRO REPOSITORY....:',self._Astroserver
        print ' DATA  REPOSITORY....:',self._Datacatalog
        # THIS SETS THE GALACTIC COMPONENTS:
        # try: 
        #    print ' ==> ISODIFFUSE DEFINED AS ENV VARIABLE AS    :',os.environ['ISODIFFUSE']
        # except:
        DIFFUSEMODELS_PATH=os.path.expandvars(os.path.expanduser(os.environ['DIFFUSEMODELS_PATH']))
        a=myIRF.isotropicTemplate.split(',')
        a.reverse()
        for x in a:
            _ISODIFFUSE=os.path.join(DIFFUSEMODELS_PATH,x.replace(' ',''))
            if os.path.exists(_ISODIFFUSE):
                os.environ['ISODIFFUSE'] = _ISODIFFUSE
                pass
            pass
        print ' ISODIFFUSE..........:',os.environ['ISODIFFUSE']
        #try: 
        #   print ' ==> GALDIFFUSE DEFINED AS ENV VARIABLE AS    :',os.environ['GALDIFFUSE']
        # except:
        DIFFUSEMODELS_PATH=os.path.expandvars(os.path.expanduser(os.environ['DIFFUSEMODELS_PATH']))
        a=myIRF.galacticTemplate.split(',')
        a.reverse()
        for x in a:
            _GALDIFFUSE=os.path.join(DIFFUSEMODELS_PATH,x.replace(' ','') )
            print _GALDIFFUSE,os.path.exists(_GALDIFFUSE)
            if os.path.exists(_GALDIFFUSE):
                os.environ['GALDIFFUSE'] = _GALDIFFUSE
                pass
            pass
        print ' GALDIFFUSE..........:',os.environ['GALDIFFUSE']
        print '--------------------------------------------------'
        pass
    def AddFileToSave(self,oneFile):
        self.AdditionalFiles.append(oneFile)
        pass
    
    def SaveFiles(self,suffix=''):
        if suffix=='': suffix='.'
        suffix = suffix.upper()
        print 'Saving files with SUFFIX: %s '% suffix
        
        
        sub_dir='%s/%s' %(self.out_dir,suffix)
        runShellCommand('mkdir -p %s' % sub_dir)
        
        if os.path.exists(sub_dir):            
            file1 = self.lc_outFile
            file2 = file1.replace('_lc','_lc%s' % suffix)
            
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.lc_outFile.replace('_lc.fits','_lc.png')
            file2 = file1.replace('_lc','_lc%s' % suffix)
            
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.mp_outFile
            file2 = file1.replace('.fits','%s.fits' % suffix)            
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.mp_outFile.replace('_map.fits','_map.png')
            file2 = file1.replace('.png','%s.png' % suffix)
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
        
            file1 = self.evt_file
            file2 = file1.replace('_ROI.fits','%s.fits' % suffix)
            if os.path.exists(file1):
                runShellCommand('cp %s %s' %(file1,file2))    
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
        
            file1 = self.evt_file.replace('_ROI.fits','_ROI.root')
            file2 = file1.replace('_ROI','%s' % suffix)
            if os.path.exists(file1):                
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
        
            file1 = self.evt_file.replace('_ROI.fits','_ROI.txt')
            file2 = file1.replace('_ROI','%s' % suffix)
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.evt_file.replace('_ROI.fits','_ROIevt.png')
            file2 = file1.replace('_ROI','%s' % suffix)
            if os.path.exists(file1):                 
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.pha2_outFile
            file2 = file1.replace('.pha2','%s.pha2' % suffix)
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))                
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass
            
            file1 = self.rsp_File
            file2 = file1.replace('.rsp.','%s.rsp' % suffix)
            if os.path.exists(file1):
                runShellCommand('mv %s %s' %(file1,file2))
                runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass

            for file2 in self.AdditionalFiles:
                if os.path.exists(file2): runShellCommand('mv %s %s/.' %(file2,sub_dir))
                pass            
            print '--------------------------------------------------'
            runShellCommand('ls -al %s' % sub_dir)
            print '--------------------------------------------------'
        else:
            print 'ERROR CREATING %s Directory!' % sub_dir
            pass
        pass
    
    def FindFITS(self,extName='FT1',ftfile=None):
        """ Look in the input directory and search for the file. @param extName specifies which fits file
        needs to be searched (options are FT1 and FT2). As optional parameter, @param ftfile is the name of the file.
        In this case FindFITS wiull check that the file exists and match the requested type. If None is passed (default option)
        FindFits will look into the IN_Directory and will scan all the file, searching the one that corerctly contains the Trigger time.        
        """
        
        if extName=='FT1':
            ext='EVENTS'
        elif extName=='FT2':
            ext='SC_DATA'
        else:
            raise SystemExit('%s is not FT1 or FT2' % extName)

        if os.path.exists(ftfile):
            if 'FT1' in extName:
                self.FilenameFT1=ftfile
                if self.chatter>0: print 'FT1 file set to: %s ' % self.FilenameFT1
            else:
                self.FilenameFT2=ftfile
                if self.chatter>0:print 'FT2 file set to: %s ' % self.FilenameFT2                                                
                pass            
            return  os.path.abspath(ftfile)
        
        if self.chatter>0: print "-- Searching (%s) in directory: %s" %(ext,self.IN_Directory)
        filelist = glob.glob(self.IN_Directory+'/*.fits') + glob.glob(self.IN_Directory+'/*.fit')
        
        for filename in sorted(filelist):
            fits = pyfits.open(filename)
            
            # FIRST DO A QUICK LOOK AT THE HEADER:            
            hd1   = fits[1]
            start = float(hd1.header['TSTART'])
            stop  = float(hd1.header['TSTOP'])
            
            # print '-- File: %-60s\tTSTART=%s\tTSTOP=%s\tTTRIG.=%s'%(filename,start-self.GRB.Ttrigger,stop-self.GRB.Ttrigger,self.GRB.Ttrigger)
            
            if (start>self.GRB.Ttrigger) or(stop<self.GRB.Ttrigger): continue
            
            
            if 'FT1' in extName:
                try:
                    start=fits['EVENTS'].data.field('TIME').min()
                    stop =fits['EVENTS'].data.field('TIME').max()
                except:
                    continue
                pass
            if 'FT2' in extName:
                try:
                    start = fits['SC_DATA'].data.field('START').min()
                    stop  = fits['SC_DATA'].data.field('STOP').max()
                    pass
                except:
                    continue
                pass
            
            #print ' ** File: %-60s\tTSTART=%s\tTSTOP=%s\tTTRIG.=%s'%(filename,start-self.GRB.Ttrigger,stop-self.GRB.Ttrigger,self.GRB.Ttrigger)
            
            if (start<self.GRB.Ttrigger) and (stop>self.GRB.Ttrigger):
		if hd1.header['EXTNAME']==ext:
                    if self.chatter>0: print 'found file %s ' % filename                    
                    if 'FT1' in extName:
                        self.FilenameFT1=filename
                        if self.chatter>0: print 'FT1 file set to: %s ' % self.FilenameFT1
                        pass
                    else:
                        self.FilenameFT2=filename
                        if self.chatter>0: print 'FT2 file set to: %s ' % self.FilenameFT2                                                
                        pass
                    fits.close()
                    return filename
                pass
            pass
        print 'trigger time not in FT1/FT2 file!!'        
        return None
    
    
    def print_parameters(self):
        """ Print all the parameters values."""
        theta=self.getGRBTheta()
        #d_grb_trigger=genutils.met2date(self.GRB.Ttrigger,'fff')[0].isoformat()
        d_grb_trigger=genutils.met2date(self.GRB.Ttrigger)

        print '--------------------------------------------------'
        print 'GRBname       :',self.GRB.Name
        print 'Trigger       : %.4f (%s)' %(self.GRB.Ttrigger,d_grb_trigger)
        print 'T start       :',self.GRB.TStart
        print 'T   end       :',self.GRB.TStop
        print '(Time Interval:',self.GRB.TStop-self.GRB.TStart,')'
        print 'Ra            :',self.GRB.ra
        print 'Dec           :',self.GRB.dec
        print 'THETA         : %.1f' % theta
        print 'Rad           :',self.radius
        print 'Emin          :',self.Emin
        print 'Emax          :',self.Emax
        print 'Zmax          :',self.zmax
        print 'IRFs          :',self._ResponseFunction
        print '####################################################################################################'
        print 'FT1 FILE      :',self.FilenameFT1
        print 'FT2 FILE      :',self.FilenameFT2
        print 'EVT FILE      :',self.evt_file
        print 'OUT DIRECTORY :',self.out_dir
        print '####################################################################################################'

        pass
    
    # ROOT files:
    #------------

    def saveEvents2Root(self):
        """This calls the convert methods of latutils. It save the Events into a ROOT Tree Object. @param time is used as offset"""
        
        print 'Now making a root tree with the selected events...'
        time=self.GRB.Ttrigger
        ra=self.GRB.ra
        dec=self.GRB.dec
        latutils.convert(self.evt_file,time,ra,dec)
        pass
    ## It return the time of the first events in the current event selection after the time @param time
    def GetFirstTimeAfter(self,time=0,evcls=0):
        """ It return the time of the first events in the current event selection after the time @param time
        @param evcls is the minimum event class"""
        if time==0:
            time=self.GRB.Ttrigger
            pass
        return latutils.GetFirstTimeAfter(self.evt_file,time,evcls)
    
    
    ## Returns the minimum and the maximum energy in the filename
    ## param filename is the input FT1 fits file
    def GetEMaxMin(self, filename=None):        
        if filename is None:
            filename=self.evt_file
            pass
        ft1      = pyfits.open(filename)
        energies = ft1['EVENTS'].data.field('ENERGY')
        emin     = energies.min()
        emax     = energies.max()
        ft1.close()
        if self.chatter>0: 
	    print ' **** File %s '% filename
    	    print ' -------- emin: %s' %(emin)
    	    print ' -------- emax: %s' %(emax)
        return emin, emax

    def GetTMaxMin_quick(self,filename):
        if filename is None:
            filename = self.evt_file
            pass
        ft1       = pyfits.open(filename)
        tmin      = float(ft1['EVENTS'].header['TSTART'])
        tmax      = float(ft1['EVENTS'].header['TSTOP'])
        dmin      = genutils.met2date(tmin,'fff')
        dmax      = genutils.met2date(tmax,'fff')
        ft1.close()
        if self.chatter>0: 
	    print ' **** File %s '% filename
            print ' -------- tmin: %s (%s): %s' %(tmin, tmin-self.GRB.Ttrigger,dmin[0].isoformat())
	    print ' -------- tmax: %s (%s): %s' %(tmax, tmax-self.GRB.Ttrigger,dmax[0].isoformat())        
        return tmin,tmax
    

    def GetTMaxMin(self,filename):
        if filename is None:
            filename = self.evt_file
            pass
        ft1       = pyfits.open(filename)
        table     = ft1['EVENTS'].data
        met_time  = table.field('TIME')
        tmin      = met_time.min()
        tmax      = met_time.max()
        dmin      = genutils.met2date(tmin,'fff')
        dmax      = genutils.met2date(tmax,'fff')
        
        ft1.close()
        if self.chatter>0: 
	    print ' **** File %s '% filename
            print ' -------- tmin: %s (%s): %s' %(tmin, tmin-self.GRB.Ttrigger,dmin[0].isoformat())
	    print ' -------- tmax: %s (%s): %s' %(tmax, tmax-self.GRB.Ttrigger,dmax[0].isoformat())        
        return tmin,tmax

    def setE(self,emin,emax,ebins):
	self.Emin=emin
	self.Emax=emax
	self.Ebins=ebins
	pass

    def setEmin(self,value):
        self.Emin=value
        pass

    def setEmax(self,value):
        self.Emax=value
        pass

    def setTmin(self,value):
        self.GRB.TStart=value
        pass

    def setTmax(self,value):
        self.GRB.TStop=value
        pass

    def setRa(self,value):
        self.GRB.ra=value
        pass

    def setDec(self,value):
        self.GRB.dec=value
        pass

    def setROI(self,value):
        self.radius=value
        pass

    
    def countEVT(self,t1_offset=0,t2_offset=9999999999,evtcls=0,energyMin=0,show=False,ApplyPSFCut=False,ReturnEventList=False,FT1_File="",Containment=0):
        
        ''' counts the events in some FT1_File between t1_offset and t2_offset'''
        import pyIrfLoader,sys

        if (energyMin==0): 
            energyMin=self.Emin
        
        if (FT1_File==""):  
           #try using the evt_file

           if   os.path.exists(self.evt_file):            FT1_File=self.evt_file
           elif os.path.exists(self.FilenameFT1_mktime):  FT1_File=self.FilenameFT1_mktime
           else: 
               print "Can't file from which file to plot!"
               return 
        elif not os.path.exists(FT1_File):
           print "File %s does not exist" %FT1_File
           return
         
        print "Using file %s" %FT1_File
        f1=pyfits.open(FT1_File)

        evt1=f1['EVENTS'].data  
        ENE  = evt1.field('ENERGY')
        TIME = evt1.field('TIME')
        EVENTID     = evt1.field('EVENT_ID')
        EVENT_CLASS = latutils.GetEventClass(evt1.field('EVENT_CLASS'))
        
        if ApplyPSFCut:
            print '********** counting events compatible with the GRB location, within %.0f of the containment radius **********'    %(Containment*100)

            RA   = evt1.field('RA')
            DEC  = evt1.field('DEC')
            CONV = evt1.field('CONVERSION_TYPE')    
        
            irfsname = self._ResponseFunction
            grb_ra   = self.GRB.ra
            grb_dec  = self.GRB.dec
            grb_err  = self.GRB.LocalizationError
        
            theta    = self.getGRBTheta()
            phi      = 0.0 # not implemented yet
        
            pyIrfLoader.Loader_go()
            irfs = pyIrfLoader.IrfsFactory.instance()
            irfsF=irfs.create(irfsname+'::FRONT')
            irfsB=irfs.create(irfsname+'::BACK')
            psf=[]
            psf.append(irfsF.psf())
            psf.append(irfsB.psf())
            
	pass
	
        if (ReturnEventList): EventList=[]
          
        nselected=0
        for i in range(len(TIME)):

            time= float(TIME[i])-self.GRB.Ttrigger
            if time<t1_offset or time>t2_offset: continue
        
            ene = float(ENE[i])
            if ene<energyMin: continue
        
            
            if EVENT_CLASS[i]<=evtcls: continue
        
            if ApplyPSFCut:
                ra  =  RA[i]
                dec = DEC[i]
                conv= int(CONV[i])
        


                #tt00=psf_f.angularIntegral(500,0,0,2) # to have psf_f work 
                #tt11=psf_b.angularIntegral(500,0,0,2) # to have psf_b work
                rad  =0.0
  	        dang =10.0
  	        sign =1
  	        while dang>=0.01:
                   while (1) :
                       anAngInterval=psf[conv].angularIntegral(ene,theta,phi,rad)
                       if   (sign==1  and anAngInterval >Containment): break
                       elif (sign==-1 and anAngInterval <Containment): break
                       #print "arad=%f sign=%d dang=%f" %(rad,sign,dang)
                       rad+=dang*sign
                   pass
   
                   dang/=10.
                   sign*=-1
		pass
		rad-=dang/2.
		#print "%f %f %f %f" %(ene,theta,phi,rad)
                rad=math.sqrt(rad**2+grb_err**2)
                sep=genutils.angsep(ra,dec,grb_ra,grb_dec)
                #print "separation=%f, 95% containment radius=%f" %(float(sep),float(rad))
                if(sep > rad): continue
            pass    
             
              
            nselected+=1
            if (show):
               aline="t=%11.3f ID=%8d E=%10.2f CLASS=%1d" %(time,int(EVENTID[i]),ene,int(EVENT_CLASS[i]))
               if ApplyPSFCut: aline+=" %.0fpctROIRadius=%5.2f Ang. Distance=%4.2f" %(100*Containment,rad,sep)
               print aline
              
            if (ReturnEventList): EventList.append([time+self.GRB.Ttrigger,ene])
         
	pass
        
        print 'NUMBER OF EVENTS: START: %f, STOP: %f, MINCLASS: %d, ENERGYMIN: %9.1f MeV =%d' % (t1_offset,t2_offset,evtcls,energyMin,nselected)
        if (ReturnEventList): return EventList
        else:                 return nselected

    def countEVT_PSF(self,t1_offset=0, t2_offset=99999990, evtcls=0,energyMin=0,show=False, FT1_File="", ReturnEventList=False, Containment=0.95):        
        ''' counts the events compatible with the PSF '''
        return self.countEVT(t1_offset=t1_offset,t2_offset=t2_offset,evtcls=evtcls,energyMin=energyMin,show=show,ApplyPSFCut=True,ReturnEventList=ReturnEventList,FT1_File=FT1_File,Containment=Containment)

    # Compute Duration taking into account the PSF and the expected background
    def make_ComputeKEYDuration(self):
        ''' counts the events compatible with the PSF '''
        print '********** counting events compatible with the GRB location, within %.0f of the containment radius **********' %(100*Containment)
        import pyIrfLoader
        irfsname = self._ResponseFunction
        grb_ra   = self.GRB.ra
        grb_dec  = self.GRB.dec
        grb_err  = self.GRB.LocalizationError        
        theta    = self.getGRBTheta()
        phi      = 0.0 # not implemented yet
        
        pyIrfLoader.Loader_go()
        irfs = pyIrfLoader.IrfsFactory.instance()
        irfsF=irfs.create(irfsname+'::FRONT')
        irfsB=irfs.create(irfsname+'::BACK')
        psf_f = irfsF.psf()
        psf_b = irfsB.psf()        
        aeff_f= irfsF.aeff()
        aeff_b= irfsB.aeff()
        
        f1=pyfits.open(self.evt_file)
        evt1=f1['EVENTS'].data  
        RA   = evt1.field('RA')
        DEC  = evt1.field('DEC')
        ENE  = evt1.field('ENERGY')
        TIME = evt1.field('TIME')
        
        nevt=len(RA)
        
        nselected  = 0
        ntotal    = 0


        import ROOT
        TimeMin = min(TIME)  - self.GRB.Ttrigger
        TimeMax = max(TIME)  - self.GRB.Ttrigger
        timeS = ROOT.RooRealVar("TIME","timeS",TimeMin, TimeMax,"s")
        timeB = ROOT.RooRealVar("TIME","timeB",TimeMin, TimeMax,"s")
        
        argsS = ROOT.RooArgSet(timeS)
        argsB = ROOT.RooArgSet(timeB)
        
        #fout = ROOT.TFile("timeout.root","RECRATE")
        dataS = ROOT.RooDataSet("TimeS","TimeS",argsS)
        dataB = ROOT.RooDataSet("TimeB","TimeB",argsB)
        containment = 0.95
        dang        = 0.001
        for i in range(nevt):
            ra   =  RA[i]
            dec  = DEC[i]
            ene  = float(ENE[i])
            time = float(TIME[i])-self.GRB.Ttrigger
            rad  = 0.0
            #print ene,theta,phi
            AF   = aeff_f.value(ene,theta,phi)
            AB   = aeff_b.value(ene,theta,phi)
            tt00 = psf_f.angularIntegral(500,0,0,2) # to have psf_f work 
            tt11 = psf_b.angularIntegral(500,0,0,2) # to have psf_b work
            #print AF,AB,tt00,tt11
            
            while (AF*psf_f.angularIntegral(ene,theta,phi,rad)+ AB*psf_b.angularIntegral(ene,theta,phi,rad))/(AF+AB) < containment:
                rad+=dang
                pass
            rad = math.sqrt(rad**2+grb_err**2)
            sep = genutils.angsep(ra,dec,grb_ra,grb_dec)
            # print 'separation=%s, %s containment radius=%s (ROI: %s)' %(sep,containment,rad,self.radius)
            outer = self.radius #min(2.*rad,self.radius) 
            inner = outer/2.
            if (sep < inner):
                timeS.setVal(time)
                dataS.add(argsS)
                nselected += 1
            elif (sep < outer):
                timeB.setVal(time)
                dataB.add(argsB)
                ntotal    += 1
                pass
            pass
        keysS = ROOT.RooKeysPdf("keysS","keysS",timeS,dataS)
        keysB = ROOT.RooKeysPdf("keysB","keysB",timeB,dataB)

        g  = ROOT.TGraph()
        gI = ROOT.TGraph()
        Npts = 10000.0
        integral = 0.0
        MaxIntegral=0.0
        for i in range(Npts):
            time= TimeMin + 1.0*i/(Npts-1.) * (TimeMax-TimeMin) 
            timeS.setVal(time)
            timeB.setVal(time)
            valS = keysS.getVal()
            valB = keysB.getVal()
            
            prob  = ((nselected*valS)-(ntotal*valB/3.))
            
            #print time, valS,valB, prob, integral
            
            g.SetPoint(i,time,prob)
            gI.SetPoint(i,time,integral)
            MaxIntegral = max(integral,MaxIntegral)
            integral += prob*((TimeMax-TimeMin)/(Npts))

            pass
        t05=0.0
        t95=0.0
        z05=True
        z95=True
        
        for i in range(Npts):
            time= TimeMin + 1.0*i/(Npts-1.) * (TimeMax-TimeMin)            
            y = gI.Eval(time)
            
            if y <= 0.05 * MaxIntegral and z05==True:
                t05=time
            else:
                z05==False
                pass
            
            
            if y <= 0.95 * MaxIntegral and z95==True:
                t95=time
            else:
                z95=False
                pass
            #print t05,t95,MaxIntegral, time, y
            pass
        
        
        
        ll = ROOT.RooLinkedList()
        plotS = ROOT.RooPlot(timeS,TimeMin, TimeMax,100)
        plotB = ROOT.RooPlot(timeB,TimeMin, TimeMax,100)
        
        dataS.plotOn(plotS,ll)
        dataB.plotOn(plotB,ll)
        pS = keysS.plotOn(plotS)
        pB = keysB.plotOn(plotB)
        c1=ROOT.TCanvas("RooPlot","",1000,1000)
        c1.Divide(2,2)
        c1.cd(1)
        pB.Draw()
        
        c1.cd(2)
        
        pS.Draw()
        c1.cd(3)
        g.Draw('ap')
        gI.SetLineColor(ROOT.kBlue)
        gI.SetMarkerColor(ROOT.kBlue)
        
        c1.cd(4)
        gI.Draw('ap')
        
        # #################################################
        htl05 = ROOT.TLine(TimeMin,0.05*MaxIntegral,t05,0.05*MaxIntegral)
        htl95 = ROOT.TLine(TimeMin,0.95*MaxIntegral,t95,0.95*MaxIntegral)
        vtl05 = ROOT.TLine(t05,0.0,t05,0.05*MaxIntegral)
        vtl95 = ROOT.TLine(t95,0.0,t95,0.95*MaxIntegral)
        htl05.SetLineStyle(3)
        htl95.SetLineStyle(3)
        vtl05.SetLineStyle(3)
        vtl95.SetLineStyle(3)
        htl05.Draw()
        htl95.Draw()
        vtl05.Draw()
        vtl95.Draw()
        
        c1.Update()
        c1.Print(self.out_dir+'/'+self.grb_name+'rootPlot.png')

        
        print 'Selected: %s Events' % nselected
        results={}
        results['T05_key']=t05
        results['T95_key']=t95
        results['T90_key']=t95-t05
        
        return results


    # Compute Duration taking into account the PSF and the expected background
    def make_ComputeProbabilities(self):
        ''' counts the events compatible with the PSF '''
        
        print '********** counting events compatible with the GRB location ***********'
        import pyIrfLoader,ROOT
        
        dang            = 0.001
        threshold_psf   = 0.95   # Within this containment        (95 containment)
        threshold_time  = 0.9973 # That is not a background event (3-sigma level)
        print '  PSF CONTAINMENT RADIUS.................: %.2f '% threshold_psf
        print '  PROBABILITY OF NOT BEING A BKG EVENT...: %.4f ' % threshold_time
                
        threshold_psf   = 1.0-threshold_psf
        
        NumberTimeBins = 50
        t05=0.0
        t95=0.0
        z05=True
        z95=True        
        

        irfsname = self._ResponseFunction
        grb_ra   = self.GRB.ra
        grb_dec  = self.GRB.dec
        grb_err  = self.GRB.LocalizationError        
        theta    = self.getGRBTheta()
        phi      = 0.0 # not implemented yet
        
        pyIrfLoader.Loader_go()
        irfs = pyIrfLoader.IrfsFactory.instance()
        irfsF=irfs.create(irfsname+'::FRONT')
        irfsB=irfs.create(irfsname+'::BACK')
        psf_f = irfsF.psf()
        psf_b = irfsB.psf()        
        aeff_f= irfsF.aeff()
        aeff_b= irfsB.aeff()
        
        f1=pyfits.open(self.evt_file)
        evt1=f1['EVENTS'].data  
        RA   = evt1.field('RA')
        DEC  = evt1.field('DEC')
        ENE  = evt1.field('ENERGY')
        TIME = evt1.field('TIME')
        
        # CONVERSION_TYPE==0 -> FRONT ,
        # CONVERSION_TYPE==1 -> BACK
        # (https://confluence.slac.stanford.edu/display/ST/Event+Class+Handling)
        BACK = evt1.field('CONVERSION_TYPE') 


        
        nevt=len(RA)
        # #################################################
        
        nannulus  = 0
        nsignal   = 0
        
        TimeMin = min(TIME)  - self.GRB.Ttrigger
        TimeMax = max(TIME)  - self.GRB.Ttrigger
        
        timeB = ROOT.RooRealVar("TIME","Time",TimeMin, TimeMax,"s")
        argsB = ROOT.RooArgSet(timeB)
        dataB = ROOT.RooDataSet("Time","Time",argsB)
        
        gProb       = ROOT.TGraph()
        gProb_psf   = ROOT.TGraph()
        gProb_time  = ROOT.TGraph()
        gProb.SetPoint(0,TimeMin,0.)
        gProb.SetPoint(1,TimeMax,1.)
        gProb_psf.SetPoint(0,TimeMin,0.)
        gProb_psf.SetPoint(1,TimeMax,1.)
        gProb_time.SetPoint(0,TimeMin,0.)
        gProb_time.SetPoint(1,TimeMax,1.)
        
        gProb_psf0  = ROOT.TGraph()
        gProb_psf1  = ROOT.TGraph()
        gProb_time0 = ROOT.TGraph()
        gProb_time1 = ROOT.TGraph()
        
        i_psf0=0
        i_psf1=0
        i_time0=0
        i_time1=0
        print ' LAT::make_ComputeProbabilities ---  CREATE THE BACKGROUND... '
        for i in range(nevt):
            ra   =  RA[i]
            dec  = DEC[i]
            ene  = float(ENE[i])                
            time = float(TIME[i])-self.GRB.Ttrigger
            
            sep = genutils.angsep(ra,dec,grb_ra,grb_dec)
            
            outer = self.radius
            inner = outer/2.
            
            if (sep> inner and sep < outer):
                timeB.setVal(time)
                dataB.add(argsB)
                nannulus    += 1
                pass
            pass
        print ' LAT::make_ComputeProbabilities ---  EVALUATING THE KERNEL...'        
        keysB = ROOT.RooKeysPdf("keysB","keysB",timeB,dataB)
        
        print ' LAT::make_ComputeProbabilities ---  COMPUTE PROBABILITIES... '
        
        asciif = self.out_dir+'/'+self.grb_name+'_evt_prob.txt'
        fout = file(asciif,'w')
        txt  = '# %13s %10s %10s %10s %10s %10s %10s %10s %10s %10s' %('TIME','ENERGY','RA','DEC','ANGSEP','CONT','EXPECTED','PROB_SP','PROB_TIME','PROB')
        print txt
        fout.write('%s\n' % txt)
        
        light_curve = ROOT.TH1D('light_curve','light_curve',NumberTimeBins,TimeMin, TimeMax)
        
        
        prob_time_0 = 0
        
        max_events_r   = 0.0
        max_events_t   = 0.0
        max_events_e   = 0.0
        max_events_p1  = 0.0
        max_events_p2  = 0.0

        first_events_r   = 0.0
        first_events_t   = 0.0
        first_events_e   = 0.0
        first_events_p1  = 0.0
        first_events_p2  = 0.0

        last_events_r   = 0.0
        last_events_t   = 0.0
        last_events_e   = 0.0
        last_events_p1  = 0.0
        last_events_p2  = 0.0
        
        ene_max     = 0.0
        
        for i in range(0,nevt-1):
            ra   =  RA[i]
            dec  = DEC[i]
            
            ene  = float(ENE[i])
            time = float(TIME[i])-self.GRB.Ttrigger
            back = int(BACK[i])

            light_curve.Fill(time)
            # AF   = aeff_f.value(ene,theta,phi)
            # AB   = aeff_b.value(ene,theta,phi)
            tt00 = psf_f.angularIntegral(500,0,0,2) # to have psf_f work 
            tt11 = psf_b.angularIntegral(500,0,0,2) # to have psf_b work
            # print AF,AB,tt00,tt11
            
            # compute the containment:
            
            cont = 0.0
            rad  = 0.0
            sep  = genutils.angsep(ra,dec,grb_ra,grb_dec)
            
            if (sep < inner):
                nsignal+=1
                while (rad <= sep):
                    if back: 
                        cont = psf_b.angularIntegral(ene,theta,phi,rad)
                    else:
                        cont = psf_f.angularIntegral(ene,theta,phi,rad)
                        pass
                    rad += dang
                    # rad = math.sqrt(rad**2+grb_err**2)
                    pass
                # PROBABILITY PSF = 1- CONTAINMENT:
                prob_psf   = 1.0 - cont

                
                # Time of this event:                
                t_this = float(TIME[i])                
                # Time of the next event, withing the signal region:
                
                for j in range(i+1,nevt-1):                    
                    cont1 = 0.0
                    rad1  = 0.0
                    sep1  = genutils.angsep(RA[j],DEC[j],grb_ra,grb_dec)
                    if (sep1 < inner):
                        t_next = float(TIME[j])
                        break
                    pass
                
                dt =  t_next - t_this                
                
                # 2: compute the probability that the event belongs to the background:
                
                timeB.setVal(time)
                
                # This compute the PDF (t) in the annular region. The PDF is normalized to 1.            
                valB = keysB.getVal()
                
                # Number of expected events in rad^2 when there are nannulus in the full time range, in the annular region ((2*inner)^2-inner^2). 
                nExpected = (valB)*(nannulus)*(rad*rad)/(3.*inner*inner)
                
                # Probability to get the Nexpected events in dt:
                
                #print 'dt = ',dt
                nExpected = nExpected*dt
                
                # The probability to get 1 event when the expected number is nExpected:
                prob_time = ROOT.TMath.Poisson(1.0,nExpected)
                
                # The probability thart the event belongs to the signal:
                prob_time_1   = 0.5 * (1.0 - prob_time) + prob_time_0 # 1/2 probability to this event
                prob_time_0   = 0.5 * (1.0 - prob_time) # this will be associated to the next event in the signal region.
                # The composite probability:
                prob_time = (1.0 - prob_time) #prob_time_1
                prob = prob_psf * prob_time
                
                # gProb.SetPoint(i,time,prob)
                # gProb_psf.SetPoint(i,time,prob_psf)
                # gProb_time.SetPoint(i,time,prob_time)                
                
                if prob_psf > threshold_psf and prob_time > threshold_time:                   
                    gProb_psf1.SetPoint(i_psf1,time,prob_psf)
                    i_psf1 += 1
                    gProb_time1.SetPoint(i_time1,time,prob_time)
                    i_time1+=1                    
                else:
                    gProb_psf0.SetPoint(i_psf0,time,prob_psf)
                    i_psf0 += 1
                    gProb_time0.SetPoint(i_time0,time,prob_time)
                    i_time0+=1
                    pass
                
                if prob_psf > threshold_psf and prob_time > threshold_time:
                    
                    if time>TimeMin and first_events_t == 0.0:
                        first_events_r   = sep
                        first_events_t   = time
                        first_events_e   = ene
                        first_events_p1  = prob_psf
                        first_events_p2  = prob_time
                        pass
                    if time < TimeMax:
                        last_events_r   = sep
                        last_events_t   = time
                        last_events_e   = ene
                        last_events_p1  = prob_psf
                        last_events_p2  = prob_time
                        pass
                    if ene > ene_max and time>TimeMin and time<TimeMax:
                        ene_max   =ene
                        max_events_r   = sep
                        max_events_t   = time
                        max_events_e   = ene
                        max_events_p1  = prob_psf
                        max_events_p2  = prob_time
                        pass
                    
                    if z05==True:
                        t05 = time
                        z05 = False
                        pass
                    t95 = time
                    txt='*%14.4f %10.1f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f*'%(time,ene,ra,dec,sep, cont, nExpected, prob_psf,prob_time,prob)                            
                else:
                    txt='%15.4f %10.1f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f'%(time,ene,ra,dec,sep, cont, nExpected, prob_psf,prob_time,prob)
                    pass
                print txt
                fout.write('%s\n' % txt)            
                pass
            pass
        print '++++++++++++++++++++++++++++++++++++++++++++++++++'
        print ' Total number of events : ', nevt
        print ' Total number of events in the annulus: ',nannulus
        print ' Total number of events in the signal region : ',nsignal
        print ' Total number of events compatible with the PSF  cut: ' ,i_psf1
        print ' Total number of events compatible with the RATE cut: ' ,i_time1
        print '++++++++++++++++++++++++++++++++++++++++++++++++++'
        
        fout.close()
        ll = ROOT.RooLinkedList()
        plotB = ROOT.RooPlot(timeB,TimeMin, TimeMax,NumberTimeBins)
        dataB.plotOn(plotB,ll)
        pB = keysB.plotOn(plotB)
        c1=ROOT.TCanvas("RooPlot","",1000,1000)
        c1.Divide(1,3)
        c1.cd(1)
        
        #gProb.SetPoint(0,TimeMin,0.)
        #gProb.SetPoint(1,TimeMax,light_curve.GetMaximum())
        #gProb.GetXaxis().SetTitle("Time (s)")
        #gProb.GetYaxis().SetTitle("Events/bin")
        #gProb.Draw('ap')
        
        light_curve.SetMarkerStyle(20)
        light_curve.SetMarkerColor(ROOT.kGray)
        
        light_curve.Draw('E1')
        pB.Draw("same")

        
        c1.cd(2)

        gProb_time.SetMinimum(0.95)
        gProb_time.SetMaximum(1)
        gProb_time.GetXaxis().SetRangeUser(TimeMin, TimeMax)
        gProb_time.GetXaxis().SetTitle("Time (s)")
        gProb_time.GetYaxis().SetTitle("Probability - TIME")
        gProb_time.Draw('ap')
        
        gProb_time.SetMarkerColor(10)
        gProb_time1.Draw('p')
        gProb_time1.SetMarkerStyle(20)
        gProb_time1.SetMarkerSize(0.8)
        gProb_time1.SetMarkerColor(ROOT.kGreen)
        gProb_time0.Draw('p')
        gProb_time0.SetMarkerStyle(20)
        gProb_time0.SetMarkerSize(0.8)
        gProb_time0.SetMarkerColor(ROOT.kRed)
        
        
                
        c1.cd(3)
        gProb_psf.GetXaxis().SetRangeUser(TimeMin, TimeMax)                
        gProb_psf.GetXaxis().SetTitle("Time (s)")
        gProb_psf.GetYaxis().SetTitle("Probability - PSF")
        gProb_psf.Draw('ap')
        gProb_psf.SetMarkerColor(10)
        gProb_psf1.Draw('p')
        gProb_psf1.SetMarkerStyle(20)
        gProb_psf1.SetMarkerSize(0.8)
        gProb_psf1.SetMarkerColor(ROOT.kGreen)
        gProb_psf0.Draw('p')
        gProb_psf0.SetMarkerStyle(20)
        gProb_psf0.SetMarkerSize(0.8)
        gProb_psf0.SetMarkerColor(ROOT.kRed)
        
        # #################################################
        ht_psf  = ROOT.TLine(TimeMin,threshold_psf,TimeMax,threshold_psf)
        ht_time = ROOT.TLine(TimeMin,threshold_time,TimeMax,threshold_time)


        ht_psf.SetLineStyle(3)
        ht_time.SetLineStyle(3)

        c1.cd(2)
        ht_time.Draw()                
        c1.cd(3)
        ht_psf.Draw()
        #ht_total.Draw()

        
        #htl05 = ROOT.TLine(TimeMin,threshold,TimeMax,threshold)
        ##htl95 = ROOT.TLine(TimeMin,0.95,TimeMax,0.95)
        #vtl05 = ROOT.TLine(t05,0.0,t05,1.0)
        #vtl95 = ROOT.TLine(t95,0.0,t95,1.0)
        #htl05.SetLineStyle(3)
        ##htl95.SetLineStyle(3)
        #vtl05.SetLineStyle(3)
        #vtl95.SetLineStyle(3)
        #htl05.Draw()
        ##htl95.Draw()
        #vtl05.Draw()
        #vtl95.Draw()
        
        c1.Update()
        c1.Print(self.out_dir+'/'+self.grb_name+'_probPlot.png')
        
        results={}
        results['T05_prob']=t05
        results['T95_prob']=t95
        results['T90_prob']=t95-t05
        results['PROB_EMAX_R']  = max_events_r
        results['PROB_EMAX_T']  = max_events_t
        results['PROB_EMAX_E']  = max_events_e
        results['PROB_EMAX_P1']  = max_events_p1
        results['PROB_EMAX_P2']  = max_events_p2

        results['PROB_FIRST_R']  = first_events_r
        results['PROB_FIRST_T']  = first_events_t
        results['PROB_FIRST_E']  = first_events_e
        results['PROB_FIRST_P1']  = first_events_p1
        results['PROB_FIRST_P2']  = first_events_p2

        results['PROB_LAST_R']  = last_events_r
        results['PROB_LAST_T']  = last_events_t
        results['PROB_LAST_E']  = last_events_e
        results['PROB_LAST_P1']  = last_events_p1
        results['PROB_LAST_P2']  = last_events_p2
        
        return results

    # Compute Duration taking into account the PSF and the expected background
    
    def make_ComputeBayesProbabilities(self):
        ''' counts the events compatible with the PSF
        Here I use the Bayes Theorem:
        P(S|R) = P(R|S) P(S)/P(R)
        With P(R|S) is the probability of the signal at radius R (this is given by the PSF)
        With P(S) is the prior probability to be signal (I use the time probability)        
        With P(R) is the probability at radius R which is:
        P(R) = P(S) * P(R|S) + (1-P(S))*(P(R|B)) where P(R|B) is just proportional to the area.        
        '''
        print '********** counting events compatible with the GRB location ***********'
        import pyIrfLoader,ROOT
        
        dang            = 0.001
        threshold_psf   = 1.0 - 0.68   # Within this containment        (68 containment)
        #threshold_time  = 0.9973 # That is not a background event (3-sigma level)
        threshold_prob  = 0.997

        NumberTimeBins = 50
        t05=0.0
        t95=0.0
        z05=True
        z95=True        
        

        irfsname = self._ResponseFunction
        grb_ra   = self.GRB.ra
        grb_dec  = self.GRB.dec
        grb_err  = self.GRB.LocalizationError        
        theta    = self.getGRBTheta()
        phi      = 0.0 # not implemented yet
        
        pyIrfLoader.Loader_go()
        irfs   = pyIrfLoader.IrfsFactory.instance()
        irfsF  = irfs.create(irfsname+'::FRONT')
        irfsB  = irfs.create(irfsname+'::BACK')
        psf_f  = irfsF.psf()
        psf_b  = irfsB.psf()        
        aeff_f = irfsF.aeff()
        aeff_b = irfsB.aeff()
        
        f1 = pyfits.open(self.evt_file)
        evt1        =  f1['EVENTS'].data  
        RA          = evt1.field('RA')
        DEC         = evt1.field('DEC')
        ENE         = evt1.field('ENERGY')
        TIME        = evt1.field('TIME')
        EVENT_CLASS =  latutils.GetEventClass(evt1.field('EVENT_CLASS')) #evt1.field('EVENT_CLASS')        
        # CONVERSION_TYPE==0 -> FRONT ,
        # CONVERSION_TYPE==1 -> BACK
        # (https://confluence.slac.stanford.edu/display/ST/Event+Class+Handling)
        BACK = evt1.field('CONVERSION_TYPE')
        
        nevt=len(RA)
        # #################################################
        
        nannulus  = 0
        nsignal   = 0
        
        TimeMin = min(TIME)  - self.GRB.Ttrigger
        TimeMax = max(TIME)  - self.GRB.Ttrigger
        
        timeB = ROOT.RooRealVar("TIME","Time",TimeMin, TimeMax,"s")
        argsB = ROOT.RooArgSet(timeB)
        dataB = ROOT.RooDataSet("Time","Time",argsB)
        
        gProb       = ROOT.TGraph()
        gProb_psf   = ROOT.TGraph()
        gProb_time  = ROOT.TGraph()
        
        gProb.SetPoint(0,TimeMin,0.)
        gProb.SetPoint(1,TimeMax,1.)        
        gProb_psf.SetPoint(0,TimeMin,0.)
        gProb_psf.SetPoint(1,TimeMax,1.)
        gProb_time.SetPoint(0,TimeMin,0.)
        gProb_time.SetPoint(1,TimeMax,1.)
        
        gProb_0  = ROOT.TGraph()
        gProb_1  = ROOT.TGraph()
        gProb_psf0  = ROOT.TGraph()
        gProb_psf1  = ROOT.TGraph()
        gProb_time0 = ROOT.TGraph()
        gProb_time1 = ROOT.TGraph()

        hProb  = ROOT.TH1D("hProb","Probability Distribution",20,0,1)
        
        i_prob0=0
        i_prob1=0

        print ' LAT::make_ComputeProbabilities ---  CREATE THE BACKGROUND... '
        for i in range(nevt):
            ra   =  RA[i]
            dec  = DEC[i]
            ene  = float(ENE[i])                
            time = float(TIME[i])-self.GRB.Ttrigger
            
            sep = genutils.angsep(ra,dec,grb_ra,grb_dec)
            
            outer = self.radius
            inner = outer/2.
            
            if (sep> inner and sep < outer):
                timeB.setVal(time)
                dataB.add(argsB)
                nannulus    += 1
                pass
            pass
        print ' LAT::make_ComputeProbabilities ---  EVALUATING THE KERNEL...'        
        keysB = ROOT.RooKeysPdf("keysB","keysB",timeB,dataB)
        
        print ' LAT::make_ComputeProbabilities ---  COMPUTE PROBABILITIES... '
        
        asciif = self.out_dir+'/'+self.grb_name+'_evt_prob.txt'
        fout = file(asciif,'w')
        txt  = '# %13s %10s %10s %10s %10s %10s %10s %10s %10s %10s %10s %10s' %('TIME','ENERGY','CLASS','RA','DEC','ANGSEP','CONT','EXPECTED','PROB_B','PROB_SP','PROB_TIME','PROB')
        print txt
        fout.write('%s\n' % txt)
        
        light_curve = ROOT.TH1D('light_curve','light_curve',NumberTimeBins,TimeMin, TimeMax)
        
        
        prob_time_0 = 0
        
        max_events_r     = 0.0
        max_events_t     = 0.0
        max_events_e     = 0.0
        max_events_p1    = 0.0
        max_events_p2    = 0.0
        max_events_class =0
        
        first_events_r   = 0.0
        first_events_t   = 0.0
        first_events_e   = 0.0
        first_events_p1  = 0.0
        first_events_p2  = 0.0
        first_events_class  = 0
        
        last_events_r   = 0.0
        last_events_t   = 0.0
        last_events_e   = 0.0
        last_events_p1  = 0.0
        last_events_p2  = 0.0
        last_events_class  = 0
        
        ene_max     = 0.0
        nExpected_tot = 0
        
        for i in range(0,nevt-1):
            ra   =  RA[i]
            dec  = DEC[i]
            
            ene  = float(ENE[i])
            time = float(TIME[i])-self.GRB.Ttrigger
            back = int(BACK[i])

            light_curve.Fill(time)
            # AF   = aeff_f.value(ene,theta,phi)
            # AB   = aeff_b.value(ene,theta,phi)
            tt00 = psf_f.angularIntegral(500,0,0,2) # to have psf_f work 
            tt11 = psf_b.angularIntegral(500,0,0,2) # to have psf_b work
            # print AF,AB,tt00,tt11
            
            # compute the containment:
            
            cont = 0.0
            rad  = 0.0
            sep  = genutils.angsep(ra,dec,grb_ra,grb_dec)
            
            if (sep < inner):
                nsignal+=1
                while (rad <= sep):
                    if back: 
                        cont = psf_b.angularIntegral(ene,theta,phi,rad)
                    else:
                        cont = psf_f.angularIntegral(ene,theta,phi,rad)
                        pass
                    rad += dang
                    # rad = math.sqrt(rad**2+grb_err**2)
                    pass
                # P(R|S) = PROBABILITY PSF = 1- CONTAINMENT:
                prob_psf   = 1.0 - cont
                
                
                # Time of this event:                
                t_this = float(TIME[i])
                
                # Time of the next event, within the signal region:
                t_next = t_this #float(TIME[-1])
                
                for j in range(i+1,nevt-1):                    
                    cont1 = 0.0
                    rad1  = 0.0
                    sep1  = genutils.angsep(RA[j],DEC[j],grb_ra,grb_dec)
                    if (sep1 < inner):
                        t_next = float(TIME[j])
                        break
                    pass
                
                dt =  t_next - t_this                
                
                # 2: compute the probability that the event belongs to the background:
                
                timeB.setVal(time)
                
                # This compute the PDF (t) in the annular region. The PDF is normalized to 1 (on the background?)            
                valB = keysB.getVal()
                
                # Number of expected events in rad^2 when there are nannulus in the full time range, in the annular region ((2*inner)^2-inner^2). 
                # Number of expected events in inner^2 when there are nannulus in the full time range, in the annular region ((2*inner)^2-inner^2). 
                nExpected = (valB)*(nannulus)/3. * dt                
                nExpected_tot += nExpected
                
                # The probability to get 1 event when the expected number is nExpected:
                prob_time = ROOT.TMath.Poisson(1.0, nExpected)
                
                # The probability that the event belongs to the signal:
                prob_time_1   = 0.5 * (1.0 - prob_time) + prob_time_0 # 1/2 probability to this event
                prob_time_0   = 0.5 * (1.0 - prob_time) # this will be associated to the next event in the signal region.
                # The composite probability:
                # This is the Prior: P(S)
                prob_time = prob_time_1 #(1.0 - prob_time) #prob_time_1
                prob_b    = math.pow(sep/inner,2) # math.pow(sep/inner,2)

                # for the bayes theorem:
                
                prob = (prob_psf * prob_time)/(prob_psf * prob_time + (1.0 - prob_time) * prob_b)
                hProb.Fill(prob)
                # gProb_psf.SetPoint(i,time,prob_psf)
                # gProb_time.SetPoint(i,time,prob_time)                
                evt_class = EVENT_CLASS[i]
                if prob > threshold_prob and prob_psf > threshold_psf:
                    gProb_psf1.SetPoint(i_prob1,time,prob_psf)
                    gProb_time1.SetPoint(i_prob1,time,prob_time)
                    gProb_1.SetPoint(i_prob1,time,prob)
                    i_prob1 += 1
                else:
                    gProb_psf0.SetPoint(i_prob0,time,prob_psf)
                    gProb_time0.SetPoint(i_prob0,time,prob_time)
                    gProb_0.SetPoint(i_prob0,time,prob)
                    i_prob0 += 1
                    pass
                
                if prob > threshold_prob and prob_psf > threshold_psf:                    
                    if time > TimeMin and first_events_t == 0.0:
                        first_events_r   = sep
                        first_events_t   = time
                        first_events_e   = ene
                        first_events_p1  = prob_psf
                        first_events_p2  = prob_time
                        first_events_class = evt_class
                        pass
                    if time < TimeMax:
                        last_events_r   = sep
                        last_events_t   = time
                        last_events_e   = ene
                        last_events_p1  = prob_psf
                        last_events_p2  = prob_time
                        last_events_class = evt_class
                        pass
                    if ene > ene_max and time > TimeMin and time<TimeMax:
                        ene_max   =ene
                        max_events_r   = sep
                        max_events_t   = time
                        max_events_e   = ene
                        max_events_p1  = prob_psf
                        max_events_p2  = prob_time
                        max_events_class = evt_class
                        pass
                    
                    if z05==True:
                        t05 = time
                        z05 = False
                        pass
                    t95 = time
                    txt='*%14.4f %10.1f %10i %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f*'%(time,ene,evt_class,ra,dec,sep, cont, nExpected, prob_b,prob_psf,prob_time,prob)                            
                else:
                    txt='%15.4f %10.1f %10i %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f'%(time,ene,evt_class,ra,dec,sep, cont, nExpected, prob_b,prob_psf,prob_time,prob)
                    pass
                print txt
                fout.write('%s\n' % txt)            
                pass
            pass
        print '++++++++++++++++++++++++++++++++++++++++++++++++++'
        print ' Total number of events ..............................: ', nevt
        print ' Total number of events in the annulus ...............: ',nannulus
        print ' Total number of events Expected in the signal region : ',nExpected_tot
        print ' Total number of events in the signal region .........: ',nsignal
        print ' Total number of events above threshold ..............: ' ,i_prob1
        print ' Total number of events below threshold ..............: ' ,i_prob0
        print '++++++++++++++++++++++++++++++++++++++++++++++++++'
        
        fout.close()
        ll = ROOT.RooLinkedList()
        plotB = ROOT.RooPlot(timeB,TimeMin, TimeMax,NumberTimeBins)
        dataB.plotOn(plotB,ll)
        pB = keysB.plotOn(plotB)
        c1=ROOT.TCanvas("RooPlot","",1000,1200)
        c1.Divide(1,4)
        c1.cd(1)
        
        #gProb.SetPoint(0,TimeMin,0.)
        #gProb.SetPoint(1,TimeMax,light_curve.GetMaximum())
        #gProb.GetXaxis().SetTitle("Time (s)")
        #gProb.GetYaxis().SetTitle("Events/bin")
        #gProb.Draw('ap')
        
        light_curve.SetMarkerStyle(20)
        light_curve.SetMarkerColor(ROOT.kGray)
        
        light_curve.Draw('E1')
        pB.Draw("same")

        
        c1.cd(2)

        gProb_time.SetMinimum(0.0)
        gProb_time.SetMaximum(1)
        gProb_time.GetXaxis().SetRangeUser(TimeMin, TimeMax)
        gProb_time.GetXaxis().SetTitle("Time (s)")
        gProb_time.GetYaxis().SetTitle("Probability - TIME")
        gProb_time.Draw('ap')
        
        gProb_time.SetMarkerColor(10)
        gProb_time1.Draw('p')
        gProb_time1.SetMarkerStyle(20)
        gProb_time1.SetMarkerSize(0.8)
        gProb_time1.SetMarkerColor(ROOT.kGreen)
        gProb_time0.Draw('p')
        gProb_time0.SetMarkerStyle(20)
        gProb_time0.SetMarkerSize(0.8)
        gProb_time0.SetMarkerColor(ROOT.kRed)
        
        c1.cd(3)

        gProb_psf.SetMinimum(0.0)
        gProb_psf.SetMaximum(1)
        gProb_psf.GetXaxis().SetRangeUser(TimeMin, TimeMax)
        gProb_psf.GetXaxis().SetTitle("Time (s)")
        gProb_psf.GetYaxis().SetTitle("Probability - PSF")
        gProb_psf.Draw('ap')
        
        gProb_psf.SetMarkerColor(10)
        gProb_psf1.Draw('p')
        gProb_psf1.SetMarkerStyle(20)
        gProb_psf1.SetMarkerSize(0.8)
        gProb_psf1.SetMarkerColor(ROOT.kGreen)
        gProb_psf0.Draw('p')
        gProb_psf0.SetMarkerStyle(20)
        gProb_psf0.SetMarkerSize(0.8)
        gProb_psf0.SetMarkerColor(ROOT.kRed)
        
                       
        c1.cd(4)
        gProb.GetXaxis().SetRangeUser(TimeMin, TimeMax)                
        gProb.GetXaxis().SetTitle("Time (s)")
        gProb.GetYaxis().SetTitle("Probability - Total")
        gProb.Draw('ap')
        gProb.SetMarkerColor(10)
        gProb_1.Draw('p')
        gProb_1.SetMarkerStyle(20)
        gProb_1.SetMarkerSize(0.8)
        gProb_1.SetMarkerColor(ROOT.kGreen)
        gProb_0.Draw('p')
        gProb_0.SetMarkerStyle(20)
        gProb_0.SetMarkerSize(0.8)
        gProb_0.SetMarkerColor(ROOT.kRed)
        
        # #################################################
        #ht_psf  = ROOT.TLine(TimeMin,threshold_psf,TimeMax,threshold_psf)
        #ht_time = ROOT.TLine(TimeMin,threshold_time,TimeMax,threshold_time)


        #ht_psf.SetLineStyle(3)
        #ht_time.SetLineStyle(3)

        #c1.cd(2)
        #ht_time.Draw()                
        #c1.cd(3)
        #ht_psf.Draw()
        #ht_total.Draw()

        
        #htl05 = ROOT.TLine(TimeMin,threshold,TimeMax,threshold)
        ##htl95 = ROOT.TLine(TimeMin,0.95,TimeMax,0.95)
        #vtl05 = ROOT.TLine(t05,0.0,t05,1.0)
        #vtl95 = ROOT.TLine(t95,0.0,t95,1.0)
        #htl05.SetLineStyle(3)
        ##htl95.SetLineStyle(3)
        #vtl05.SetLineStyle(3)
        #vtl95.SetLineStyle(3)
        #htl05.Draw()
        ##htl95.Draw()
        #vtl05.Draw()
        #vtl95.Draw()
        
        c1.Update()
        c1.Print(self.out_dir+'/'+self.grb_name+'_probPlot.png')
        c2 = ROOT.TCanvas("probDist","probDist",400,400)
        hProb.Draw()
        c2.Update()
        c2.Print(self.out_dir+'/'+self.grb_name+'_probDist.png')
        
        results={}
        results['T05_prob']=t05
        results['T95_prob']=t95
        results['T90_prob']=t95-t05
        results['PROB_NSIG']    = i_prob1
        results['PROB_EMAX_R']  = max_events_r
        results['PROB_EMAX_T']  = max_events_t
        results['PROB_EMAX_E']  = max_events_e
        results['PROB_EMAX_P1']  = max_events_p1
        results['PROB_EMAX_P2']  = max_events_p2
        results['PROB_EMAX_CL']  = max_events_class
        
        results['PROB_FIRST_R']  = first_events_r
        results['PROB_FIRST_T']  = first_events_t
        results['PROB_FIRST_E']  = first_events_e
        results['PROB_FIRST_P1']  = first_events_p1
        results['PROB_FIRST_P2']  = first_events_p2
        results['PROB_FIRST_CL']  = first_events_class

        results['PROB_LAST_R']  = last_events_r
        results['PROB_LAST_T']  = last_events_t
        results['PROB_LAST_E']  = last_events_e
        results['PROB_LAST_P1']  = last_events_p1
        results['PROB_LAST_P2']  = last_events_p2
        results['PROB_LAST_CL']  = last_events_class
        
        return results
    



    
    # Compute Duration taking into account the PSF and the expected background
    
    def make_ComputePoissonProbabilities(self):
        ''' counts the events compatible with the PSF '''
        print '********** counting events compatible with the GRB location, within 95% of the containment radius **********'
        import pyIrfLoader,ROOT
        
        dang        = 0.001
        threshold_psf   = 0.95   # Within this containment        (95 containment)
        threshold_time  = 0.9973 # That is not a background event (3-sigma level)

        EnergyBands=[100,100000]
        NEnergyBands = len(EnergyBands)-1
        
        NumberTimeBins = 50
        t05=0.0
        t95=0.0
        z05=True
        z95=True        
        

        irfsname = self._ResponseFunction
        grb_ra   = self.GRB.ra
        grb_dec  = self.GRB.dec
        grb_err  = self.GRB.LocalizationError        
        theta    = self.getGRBTheta()
        phi      = 0.0 # not implemented yet
        
        pyIrfLoader.Loader_go()
        irfs = pyIrfLoader.IrfsFactory.instance()
        irfsF=irfs.create(irfsname+'::FRONT')
        irfsB=irfs.create(irfsname+'::BACK')
        psf_f = irfsF.psf()
        psf_b = irfsB.psf()        
        aeff_f= irfsF.aeff()
        aeff_b= irfsB.aeff()
        
        f1=pyfits.open(self.evt_file)
        evt1=f1['EVENTS'].data  
        RA   = evt1.field('RA')
        DEC  = evt1.field('DEC')
        ENE  = evt1.field('ENERGY')
        TIME = evt1.field('TIME')
        
        # CONVERSION_TYPE==0 -> FRONT ,
        # CONVERSION_TYPE==1 -> BACK
        # (https://confluence.slac.stanford.edu/display/ST/Event+Class+Handling)
        BACK = evt1.field('CONVERSION_TYPE') 
        
        nevt=len(RA)
        # #################################################        
        
        TimeMin = min(TIME)  - self.GRB.Ttrigger
        TimeMax = max(TIME)  - self.GRB.Ttrigger
        
        timeB = [ROOT.RooRealVar("TIME","Time",TimeMin, TimeMax,"s")]*NEnergyBands
        argsB = [None]*NEnergyBands
        dataB = [None]*NEnergyBands
        plotB = [None]*NEnergyBands
        pB    = [None]*NEnergyBands
        gProb       = [ROOT.TGraph()]*NEnergyBands
        gProb_time  = [ROOT.TGraph()]*NEnergyBands
        gProb_time0 = [ROOT.TGraph()]*NEnergyBands
        gProb_time1 = [ROOT.TGraph()]*NEnergyBands
        light_curveT = [None]*NEnergyBands
        light_curveS = [None]*NEnergyBands
        light_curveB = [None]*NEnergyBands
        probability  = [None]*NEnergyBands
        
        RooLinkedList = [ROOT.RooLinkedList()]*NEnergyBands
        
        # ##################################################
        asciif = self.out_dir+'/'+self.grb_name+'_evt_prob.txt'
        fout = file(asciif,'w')
        txt  = '# %13s %10s %10s %10s %10s %10s %10s %10s' %('TIME','ENERGY','RA','DEC','ANGSEP','RAD','EXPECTED','PROB_TIME')
        print txt
        fout.write('%s\n' % txt)            

        events={}
        # #################################################
        c1=ROOT.TCanvas("RooPlot","",1000,1000)
        c1.Divide(NEnergyBands,2)        
        # #################################################
        for i in range(NEnergyBands):            
            light_curveT[i] = ROOT.TH1D('light_curveT_%d' % i,'light_curve',NumberTimeBins,TimeMin, TimeMax)            
            light_curveS[i] = ROOT.TH1D('light_curveS_%d' % i,'light_curve',NumberTimeBins,TimeMin, TimeMax)            
            light_curveB[i] = ROOT.TH1D('light_curveB_%d' % i,'light_curve',NumberTimeBins,TimeMin, TimeMax)
            probability[i]  = ROOT.TH1D('probability_%d' % i,'probability',NumberTimeBins,TimeMin, TimeMax)
            pass
        
        for i in range(NEnergyBands):            
            argsB[i] = ROOT.RooArgSet(timeB[i])
            dataB[i] = ROOT.RooDataSet("TimeB","TimeB",argsB[i])
            
            nannulus  = 0
            nsignal   = 0
        
            ELOW = EnergyBands[i]
            ESUP = EnergyBands[i+1]
            
            EMEAN = ELOW# math.sqrt(ELOW*ESUP)

            AF   = aeff_f.value(EMEAN,theta,phi)
            AB   = aeff_b.value(EMEAN,theta,phi)
            tt00 = psf_f.angularIntegral(500,0,0,2) # to have psf_f work 
            tt11 = psf_b.angularIntegral(500,0,0,2) # to have psf_b work
            # compute the containment:            
            #cont = 0.95
            RAD  = 0.0
            CONT = 0.0
            while (CONT <= threshold_psf):
                CONT = (AB*psf_b.angularIntegral(EMEAN,theta,phi,RAD)+AF*psf_f.angularIntegral(EMEAN,theta,phi,RAD))/(AF+AB)
                RAD += dang
                pass            
            print ' -- %s %% Containment Radius for %d MeV is: %s ' %(threshold_psf,EMEAN,RAD)
            
            gProb[i].SetPoint(0,TimeMin,0.)
            gProb[i].SetPoint(1,TimeMax,1.)
            gProb_time[i].SetPoint(0,TimeMin,0.)
            gProb_time[i].SetPoint(1,TimeMax,1.)
            
            print ' LAT::make_ComputeProbabilities ---  CREATE THE BACKGROUND... %d-%d' %(ELOW,ESUP)
            i_time0=0
            i_time1=0

            outer = min(self.radius,2.0*RAD)
            inner = outer/2.
            
            for j in range(nevt):
                ene  = float(ENE[j])
                if ene<ELOW or ene>ESUP:
                    continue
                ra   =  RA[j]
                dec  = DEC[j]
                
                time = float(TIME[j])-self.GRB.Ttrigger                
                sep = genutils.angsep(ra,dec,grb_ra,grb_dec)
                light_curveT[i].Fill(time)                
                if (sep> inner and sep < outer):
                    light_curveB[i].Fill(time)
                    nannulus    += 1
                    pass
                elif(sep<inner):
                    nsignal += 1
                    light_curveS[i].Fill(time)
                    pass
                pass
            
            
            for b in range(NumberTimeBins):                
                nExpected = light_curveB[i].GetBinContent(b+1)/3.
                nSignal   = light_curveS[i].GetBinContent(b+1)
                time      = light_curveS[i].GetBinCenter(b+1)
                # The probability to get 1 event when the expected number is nExpected:
                prob_time = ROOT.TMath.Poisson(nSignal,nExpected)
                # The probability thart the event belongs to the signal:
                prob_time = 1.0 - prob_time
                #probability[i].SetBinContent(prob_time)
                #events[time]=(ene,ra,dec,sep,RAD,nExpected,prob_time)
                print nExpected, nSignal ,time, prob_time
                if prob_time > threshold_time:      
                    gProb_time1[i].SetPoint(i_time1,time,prob_time)
                    i_time1+=1
                else:
                    gProb_time0[i].SetPoint(i_time0,time,prob_time)
                    i_time0+=1
                    pass
                pass
            print '++++++++++++++++++++++++++++++++++++++++++++++++++'
            print ' Total number of events : ', nevt
            print ' Total number of events in the annulus: ',nannulus
            print ' Total number of events in the signal region : ',nsignal
            #print ' Total number of events compatible with the RATE cut: ' ,i_time1
            print '++++++++++++++++++++++++++++++++++++++++++++++++++'                
            
            c1.cd(i + 1)            
            light_curveT[i].SetMarkerStyle(20)
            light_curveT[i].Draw('E1')
            
            light_curveB[i].SetMarkerStyle(20)
            light_curveB[i].SetMarkerColor(ROOT.kGray)
            
            light_curveS[i].SetMarkerStyle(20)
            #light_curveS[i].SetMarkerColor(ROOT.kGray)            
            light_curveS[i].Draw('E1same')
            light_curveB[i].Draw('E1same')
            #pB[i].Draw("same")
            
            c1.cd(2*i + NEnergyBands + 1)
            
            gProb_time[i].SetMinimum(0.95)
            gProb_time[i].SetMaximum(1)
            gProb_time[i].GetXaxis().SetRangeUser(TimeMin, TimeMax)
            gProb_time[i].GetXaxis().SetTitle("Time (s)")
            gProb_time[i].GetYaxis().SetTitle("Probability - TIME")
            gProb_time[i].Draw('ap')
        
            gProb_time[i].SetMarkerColor(10)
            gProb_time1[i].Draw('p')
            gProb_time1[i].SetMarkerStyle(20)
            gProb_time1[i].SetMarkerSize(0.8)
            gProb_time1[i].SetMarkerColor(ROOT.kGreen)
            gProb_time0[i].Draw('p')
            gProb_time0[i].SetMarkerStyle(20)
            gProb_time0[i].SetMarkerSize(0.8)
            gProb_time0[i].SetMarkerColor(ROOT.kRed)
            ht_time = ROOT.TLine(TimeMin,threshold_time,TimeMax,threshold_time)
            ht_time.SetLineStyle(3)
            ht_time.Draw()                
            pass
        
        c1.Update()
        c1.Print(self.out_dir+'/'+self.grb_name+'_probPlot.png')
        '''
        times = sorted(events.keys())
        for t in times:
            (ene,ra,dec,sep,RAD,nExpected,prob_time) = events[t]
            if prob_time > threshold_time:      
                gProb_time1[i].SetPoint(i_time1,time,prob_time)
                i_time1+=1
                if z05==True:
                    t05 = time
                    z05 = False
                    pass
                t95 = time
                txt='*%14.4f %10.1f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f*'%(time,ene,ra,dec,sep, RAD, nExpected, prob_time)
            else:
                gProb_time0[i].SetPoint(i_time0,time,prob_time)
                i_time0+=1
                txt='*%14.4f %10.1f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f*'%(time,ene,ra,dec,sep, RAD, nExpected, prob_time)

                pass
            print txt
            fout.write('%s\n' % txt)            
            pass
        
        fout.close()



        '''
        results={}
        #results['T05_prob']=t05
        #results['T95_prob']=t95
        #results['T90_prob']=t95-t05
        
        return results
    

    
    # Calls to various ScienceTools:
    #-------------------------------
    
    def make_gtmktime(self,**kwargs):
        gtmktime=GtApp('gtmktime')
        scfile  = self.FilenameFT2
        input   = self.FilenameFT1
        outfile = self.FilenameFT1_mktime
        
        filter='IN_SAA!=T && LIVETIME>0'
        ## filter_2='((ANGSEP(RA_ZENITH,DEC_ZENITH,RA_SCZ,DEC_SCZ) < 43)||(ANGSEP(RA_ZENITH,DEC_ZENITH,%s,%s) + %s < %s))' %(self.GRB.ra,self.GRB.dec,self.radius,self.zmax)
        filter_2='(ANGSEP(RA_ZENITH,DEC_ZENITH,%s,%s) + %s < %s)' %(self.GRB.ra,self.GRB.dec,self.radius,self.zmax)
        if self.zmax<180:
            filter='%s && %s' %(filter,filter_2)
            pass
        
        gtmktime['scfile'] =scfile
        gtmktime['filter'] =filter
        gtmktime['evfile'] =input
        gtmktime['outfile']=outfile
        gtmktime['roicut']='no'
        gtmktime['overwrite']='yes'
        for key in kwargs.keys():
            if key in gtmktime.keys():
                gtmktime[key]=kwargs[key]
            else:
                print 'WARNING : gtselect invalid argument %s discarded'%key
                pass
            pass
        
        gtmktime.run(chatter=self.chatter)
        
        # This will remove the evtfile if already existing
        
        #cmd='rm %s ' % (gtmktime['evfile'])
        #    runShellCommand(cmd)            
        #    pass
        
        # The following lines are obsolete if the file has been removed
        #
        #archived=gtmktime['evfile'].replace('.fit','_archive_0.fit')
        #i=1
        #while (os.path.exists(archived)):
        #    archived=archived.replace('_%i.fit' %(i-1),'_%i.fit' %i)
        #    i=i+1
        #    
        #    pass
        #cmd='mv %s %s' % (gtmktime['evfile'],archived)
        #runShellCommand(cmd)
        # runShellCommand('ls -lh %s' % gtmktime['evfile'])        

        #if (os.path.exists(gtmktime['outfile'])):
        #    cmd = 'mv -f %s %s' % (gtmktime['outfile'],gtmktime['evfile'])
        #    print cmd
        #    runShellCommand(cmd)
        #    pass
        
        # runShellCommand('ls -lh %s' % gtmktime['evfile'])
        pass
                
    def make_select(self,**kwargs):
        
        if os.path.exists(self.FilenameFT1_mktime):
            input_file = self.FilenameFT1_mktime
        else:
            input_file = self.FilenameFT1
        ##################################################
        if self._ResponseFunction.find('FRONT')>0:
            input_file = self.fselect(infile = input_file,expr='CONVERSION_TYPE==0')
        elif self._ResponseFunction.find('BACK')>0:
            input_file = self.fselect(infile = input_file,expr='CONVERSION_TYPE==1')
            pass
        
        gtselect = GtApp('gtselect')
        gtselect['infile'] =input_file
        gtselect['outfile']=self.evt_file
        gtselect['ra']  = self.GRB.ra
        gtselect['dec'] = self.GRB.dec
        gtselect['rad']  = self.radius
        gtselect['tmin'] = self.GRB.TStart
        gtselect['tmax'] = self.GRB.TStop
        if self._eventClass!="INDEF" and self._eventClass>=0:  #P7
    	   gtselect['evclass'] = self._eventClass
        else:   #P6
           gtselect['evclsmin']=self._evclsmin
           gtselect['evclsmax']=self._evclsmax                  
        #        self.GetEMaxMin()
        gtselect['emin'] = self.Emin
        gtselect['emax'] = self.Emax
        gtselect['zmax'] = self.zmax
	
        #        gtselect['eventClass']=self._eventClass
        for key in kwargs.keys():
            if key in gtselect.keys():
                gtselect[key]=kwargs[key]
            else:
                print 'WARNING : gtselect invalid argument %s discarded'%key
                
        self.radius   = gtselect['rad']
        self.zmax     = gtselect['zmax']
        self.evt_file = gtselect['outfile']

        gtselect.run()
        

        ft1 = pyfits.open(gtselect['outfile'])
        hea=ft1['EVENTS'].header
        nevents=hea.get('NAXIS2')
        ft1.close()
        if self.chatter>0 : print 'gtselect: selected : %i Events...' % (nevents)
        '''
        if self.radius==50:
        print 'Selecting events using a polinomial expansion of the PSF...'
        nsigma=3.0
        runShellCommand('mv %s roi.fits' % (self.evt_file))
        selectROI(fin='roi.fits',fout=self.evt_file,ra=self.GRB.ra,dec=self.GRB.dec,nsigma=nsigma)
        pass
        '''
        return nevents
    
    def getMaximumEvent(self,t1,t2,evtcls=0):
        ''' Return the event with the maximum Energy'''
        f1=pyfits.open(self.evt_file)
        evt1=f1['EVENTS'].data  
        TIME       = evt1.field('TIME')
        ENERGY     = evt1.field('ENERGY')
        EVENT_CLASS= latutils.GetEventClass(evt1.field('EVENT_CLASS'))
        energy_max = 0
        time_max   = 0
        nevt=len(TIME)
        nselected=0
        for i in range(nevt):
            time=float(TIME[i])-self.GRB.Ttrigger
            if time>=t1 and time <t2 and EVENT_CLASS[i] > evtcls:
                if ENERGY[i] > energy_max:
                    energy_max = ENERGY[i]
                    time_max   = time
                    pass
                pass
            pass
        return time_max, energy_max
    
    def computeTSignificance(self, tstart, tstop):        
        t0=self.GRB.Ttrigger
        
        ft1 = pyfits.open(self.evt_file)
        table = ft1['EVENTS'].data
        met_time=table.field('TIME')
        met_time = met_time-t0

        tmin=met_time.min()
        tmax=met_time.max()
                
        noff = 0.0
        non  = 0.0
        for t in met_time:
            if t<tstart or t > tstop:
                noff=noff+1
                pass
            else:
                non = non+1
                pass
            pass
        grbdur=(tstop-tstart)
        exposu=(tmax-tmin)
        
        a=grbdur/(exposu-grbdur)
        R=math.pow((1.0+noff/non)*a/(1.0+a),non)*math.pow((1.0+non/noff)/(1.0+a),noff)
        TS=-2.0*math.log(R)
        S = math.sqrt(TS)
        print 'Non=%f, Noff=%f ' %(non,noff)
        print 'R= %f, TS=%f S=%.2f sigma' % ( R, TS, S)
        return TS
    
    # This method provides a general call to fselect (ftool).
    # usage: fselect(expr='CTBCLASSLEVEL>1'), for example
    def fselect(self,**kwargs):
        expr='CTBCLASSLEVEL>0'
        fselect = GtApp('fselect')
        if os.path.exists(self.FilenameFT1_mktime):
            input_file = self.FilenameFT1_mktime
        else:
            input_file = self.FilenameFT1
            pass
        fselect['infile'] = input_file
        fselect['outfile']= self.FilenameFT1_sel
        fselect['expr']  = expr
        fselect['index']='OBSOLETE'
        fselect['clobber'] = 'yes'

        for key in kwargs.keys():
            if key in fselect.keys():
                fselect[key]=kwargs[key]
            else:
                print 'WARNING : fselect invalid argument %s discarded'%key
                
        fselect.run()
        ft1 = pyfits.open(fselect['infile'])
        hea=ft1['EVENTS'].header
        nevents=hea.get('NAXIS2')
        ft1.close()        
        print 'Selected : %i Events...' % (nevents)
        
        ft1 = pyfits.open(fselect['outfile'])
        hea=ft1['EVENTS'].header
        nevents=hea.get('NAXIS2')
        print 'Selected : %i Events...' % (nevents)
        ft1.close()
        return fselect['outfile']
    
    def make_pha1(self,**kwargs):
        
        gtbin = GtApp('gtbin')
        gtbin['algorithm']='PHA1'
        gtbin['evfile'] = self.evt_file
        gtbin['scfile'] = self.FilenameFT2
        gtbin['outfile'] = self.sp_outFile
        gtbin['ebinalg'] = self.energybinalg

        #self.GetEMaxMin()
        gtbin['emin'] = self.Emin
        gtbin['emax'] = self.Emax
        gtbin['enumbins'] = self.Ebins
        #gtbin['tstart']   = self.GRB.Ttrigger + self.GRB.Onset
        #gtbin['tstop']    = self.GRB.Ttrigger + self.GRB.Duration
        for key in kwargs.keys():
            if key in gtbin.keys():
                gtbin[key]=kwargs[key]
            else:
                print 'WARNING : gtbin invalid argument %s discarded'%key
                pass
            pass
        print '--------------------------------------------------'
        print 'Make PHA1 FILE: ENERGY = %.0f - %.0f MeV, (%d bins)' %(gtbin['emin'],
                                                                     gtbin['emax'],
                                                                     gtbin['enumbins'])
        print '--------------------------------------------------'
        gtbin.run()
        #from latutils import setPoissonPHAError
        #setPoissonPHAError(gtbin['outfile'])
        pass

    def make_pha2(self,**kwargs):
        if os.path.isfile(self.evt_file):
            ft1 = pyfits.open(self.evt_file)
        else:
            ft1 = pyfits.open(self.FilenameFT1)
            pass
        '''
        table = ft1['EVENTS'].data
        i = 0
        for line in table:
            t = line.field('TIME')
            if i == 0:
                start = t
            i = i+1
        stop = t
        ft1.close()
        '''
        #start   = self.GRB.TStart-self.GRB.Ttrigger
        #stop    = self.GRB.TStop-self.GRB.Ttrigger    

        gtbin = GtApp('gtbin')
        gtbin['algorithm']='PHA2'
        gtbin['evfile'] = self.evt_file
        gtbin['scfile'] = self.FilenameFT2
        gtbin['outfile'] = self.pha2_outFile
            
        gtbin['ebinalg'] = self.energybinalg
        
        #self.GetEMaxMin()
        gtbin['emin'] = self.Emin
        gtbin['emax'] = self.Emax
        gtbin['enumbins'] = self.Ebins
        
        gtbin['tbinalg'] = 'LIN'
        gtbin['tstart']  = self.GRB.TStart # tstart
        gtbin['tstop']   = self.GRB.TStop   # tstop
        gtbin['dtime']   = self.TimeBinWidth
        
        for key in kwargs.keys():
            if key in gtbin.keys():
                gtbin[key]=kwargs[key]
            else:
                print 'WARNING : gtbin invalid argument %s discarded'%key
                pass
            pass
        print '--------------------------------------------------'
        print 'Make PHA2 FILE: ENERGY = %.0f - %.0f MeV, (%d bins)' %(gtbin['emin'],
                                                                     gtbin['emax'],
                                                                     gtbin['enumbins'])
        
        print 'Make PHA2 FILE:  TIME = %.3f - %.3f MeV, (%d bins)' %(gtbin['tstart']-self.GRB.Ttrigger,
                                                                     gtbin['tstop']-self.GRB.Ttrigger,
                                                                     (gtbin['tstop']-gtbin['tstart'])/gtbin['dtime'])
        print '--------------------------------------------------'
        self.TimeBinWidth = gtbin['dtime']
        gtbin.run()
        gtrmfit.pha2rmfit(gtbin['outfile'],self.GRB.Ttrigger)
        pass
    
    def make_skymap(self,**kwargs):
        binsz=1
        coordsys='CEL'
        proj='CAR'
        
        if (self.radius>90):
            nxpix=2*int(self.radius/binsz)
            coordsys='GAL'
            proj='AIT'            
        else:
            nxpix=int(self.radius/binsz)
            pass
        nxpiy=int(self.radius/binsz)
        
        #self.mp_outFile=outFile
        gtbin = GtApp('gtbin')
        
        gtbin['algorithm']='CMAP'
        gtbin['evfile']  = self.evt_file
        gtbin['scfile']  = self.FilenameFT2
        gtbin['outfile'] = self.mp_outFile
        #gtbin['tstart']  = self.GRB.Ttrigger + self.GRB.Onset    # self.GRB.TStart # tstart
        #gtbin['tstop']   = self.GRB.Ttrigger + self.GRB.Duration # self.GRB.TStop   # tstop
        gtbin['nxpix']  = nxpix
        gtbin['nypix']  = nxpiy
        gtbin['binsz']  = binsz
        gtbin['coordsys']  = coordsys
        gtbin['axisrot']  = 0
        
        if (self.radius>90):
            gtbin['xref']  = 0.0
            gtbin['yref']  = 0.0
            gtbin['rafield']  = "L"
            gtbin['decfield']  = "B"

        else:
            gtbin['xref']  = self.GRB.ra
            gtbin['yref']  = self.GRB.dec
            gtbin['rafield']  = "RA"
            gtbin['decfield']  = "DEC"
            
        gtbin['proj']  = proj
        
        print '---- Make Sky Map ---- '
        print 'Emin: %s Emax: %s Ebins: %s Ealg: %s' %(self.Emin, self.Emax, self.Ebins, self.energybinalg)
        print 'projection: %s, coordsys: %s ' % (proj,coordsys)
        
        for key in kwargs.keys():
            if key in gtbin.keys():
                gtbin[key]=kwargs[key]
                print key, gtbin[key]

            else:
                print 'WARNING : gtbin invalid argument %s discarded'% key        
                pass
            pass
        
        gtbin.run()
        return self.mp_outFile

    def make_rsp2(self,PHAtype='FITS'):
        # print 'make_rsp2 with dt= %s ' % self.TimeBinWidth
        #theta  = self.getGRBTheta()        
        tmin   = self.GRB.TStart - self.GRB.Ttrigger
        tmax   = self.GRB.TStop  - self.GRB.Ttrigger    
        err    = self.GRB.LocalizationError
        dt     = self.TimeBinWidth

        trsp   = max(self.GRB.Ttrigger,self.GRB.TStart)
        theta  = latutils.GetTheta(self.GRB.ra, self.GRB.dec, trsp, self.FilenameFT2)
        # print 'trsp (MET),tmax,theta:',trsp,trsp-self.GRB.Ttrigger,tmax,theta
        
        time_bin_name = '%s/rspgen_timebins_pha2.txt' % self.out_dir
        rspgen_name   = '%s/rspgen_config.txt' % self.out_dir
                
        t= tmin
        fileout=file(time_bin_name,'w')
        while t<=tmax:
            txt='%s %s\n' % (t,t+dt)
            fileout.writelines(txt)
            t=t+dt
            pass
        fileout.close()
        #pass
        if PHAtype=='PHA1': PHAoutput=self.sp_outFile
        else:  PHAoutput=self.pha2_outFile
        
        txt='''
        #
        # Parameter file
        #
        
        PHAtype= %s
        
        ### Output files ###
        FIT = %s
        PHA = %s
        RSP = %s
        
        ### Input parameters ###
        FT1 = %s
        FT2 = %s
        
        Tstart = %s
        Tstop = %s
        
        Ttrig  = %s
        RA = %s
        DEC = %s
        ERROR_RADIUS = %s
        THETA = %.1f
        EMIN = %s
        EMAX = %s
        Ebins = %s
        dTime = %s
        tbInputFile = \'%s\'
        ResponseFunction = %s
        ''' % (PHAtype,
               self.evt_file,
               PHAoutput,
               self.rsp_File,
               self.evt_file,
               self.FilenameFT2,
               tmin,
               tmax,
               self.GRB.Ttrigger,
               self.GRB.ra,
               self.GRB.dec,
               err,
               theta,
               self.Emin,
               self.Emax,
               self.Ebins,
               dt,
               time_bin_name,
               self._ResponseFunction
               )
        fileout=file(rspgen_name,'w')
        fileout.writelines(txt)
        fileout.close()
        print txt

        import rspgen as newrspgen
        multirspgen=newrspgen.MultiRspGen(rspgen_name)
	try:     
          multirspgen.run()
        except:  
          print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! multirspgen.run() failed!'
          print sys.exc_info()[0]
          
          
        print '-- Files produced by multi rspgen:'
        filesOutput={}
        
        if PHAtype=='PHA1' or PHAtype=='PHA2':
            filesOutput[PHAtype]= multirspgen.PHA
            filesOutput['RSP']  = multirspgen.RSP
            filesOutput['FIT'] = None # This is because it created a wrong fits file.
        else:
            #filesOutput[PHAtype]= multirspgen.PHA
            #filesOutput['RSP']  = multirspgen.RSP
            filesOutput['FIT']= multirspgen.FIT # This must be run as latest
            pass
        import genutils
        
        for k in filesOutput.keys():
            f = filesOutput[k]
            if f is not None: newf = genutils.addExtension(f,'_ROI_E',opt='cp')
            pass
        return filesOutput
    
        
    def make_rsp(self,**kwargs):

        gtrspgen = GtApp('gtrspgen')
        gtrspgen['respalg']='PS'
        gtrspgen['specfile']=self.sp_outFile
        gtrspgen['scfile']=self.FilenameFT2
        gtrspgen['outfile']=self.rsp_File
        gtrspgen['irfs']=self._ResponseFunction
        
        gtrspgen['ebinalg'] = self.energybinalg
        gtrspgen['emin']    = 70 #self.Emin
        gtrspgen['emax']    = 250000 #self.Emax
        gtrspgen['enumbins']= self.EbinsRSP
        
        
        # GRB MODE ONLY:
        #gtrspgen['time']=self.GRB.TTrigger

        # PS MODE ONLY:
        gtrspgen['thetacut']=70.0
        gtrspgen['dcostheta']=0.05
        
        for key in kwargs.keys():
            if key in gtrspgen.keys():
                gtrspgen[key]=kwargs[key]
            else:
                print 'WARNING : gtrspgen invalid argument %s discarded'%key
                pass
            pass
        print '--------------------------------------------------'
        print 'Generating LAT response matrix... RSP:'
        print ' ENERGY: %.0f - %.0f MeV (%d BINS - %s) ' %(gtrspgen['emin'],
                                                           gtrspgen['emax'],
                                                           gtrspgen['enumbins'],
                                                           self.energybinalg)
        print ' USING METHOD: ', gtrspgen['respalg']
        print '--------------------------------------------------'
        try:
            gtrspgen.run()
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  An error occoured in running gtrspgen in LAT.make_rsp()'
            gtrspgen['outfile']=None
            pass
        return gtrspgen['outfile']

    def make_countsmap(self,**kwargs):
        binsz=0.25
        coordsys='CEL'
        proj='TAN'
        nxpix=2*int(self.radius/binsz)
        nypix=2*int(self.radius/binsz)
        
        
        gtbin = GtApp('gtbin')
        gtbin['algorithm']='CCUBE'
        gtbin['evfile']  = self.evt_file
        gtbin['scfile']  = self.FilenameFT2
        gtbin['outfile'] = self.mp_outFile

        gtbin['nxpix']  = nxpix
        gtbin['nypix']  = nypix
        gtbin['binsz']  = binsz
        gtbin['coordsys']  = coordsys
        gtbin['axisrot']  = 0
        gtbin['xref']  = self.GRB.ra
        gtbin['yref']  = self.GRB.dec
        gtbin['rafield']  = "RA"
        gtbin['decfield']  = "DEC"
        gtbin['proj']  = proj
        
        gtbin['ebinalg']='LOG'
        gtbin['emin']=self.Emin
        gtbin['emax']=self.Emax
        gtbin['enumbins']=self.Ebins
        
        for key in kwargs.keys():
            if key in gtbin.keys():
                gtbin[key]=kwargs[key]
            else:
                print 'WARNING : gtbin invalid argument %s discarded'% key        
                pass
            pass
        
        gtbin.run()

    def make_expCube(self,**kwargs):
        overwrite="undefined"
        gtltcube = GtApp('gtltcube','Likelihood')
        gtltcube['evfile']   = self.evt_file
        gtltcube['scfile']   = self.FilenameFT2
        gtltcube['outfile']  = self.expCube
        gtltcube['dcostheta']= 0.025
        gtltcube['binsz']    = 1.0
        gtltcube['zmax']     = 180 #self.zmax
        gtltcube['phibins']  = 0
	chatter=1
        for key in kwargs.keys():
	    goodkey=False
            if key in gtltcube.keys():
                gtltcube[key]=kwargs[key]
		goodkey=True
                pass
	    if key.lower()=='overwrite': 
		overwrite=bool(kwargs[key])
	    elif key.lower()=='chatter': 
		chatter  =kwargs[key]
            elif not goodkey:
                print 'WARNING : gtltcube invalid argument %s discarded' %key
                pass
            pass
        
        if os.path.exists(gtltcube['outfile']):
	    if overwrite==False: 
                if chatter>0 : print 'File %s exists. User chose not to overwrite it.' % gtltcube['outfile']
		return
	    else:
		if overwrite==True: 
		    a="Y"
	        elif overwrite=="undefined":
        	    cmd='make_expCube: %s file exists. Remove? [y/N] ' % gtltcube['outfile']
	    	    a=raw_input(cmd)
                    pass
                if (a.upper()=='Y'):
	            cmd='rm %s' % gtltcube['outfile']
    	            runShellCommand(cmd)
	            if chatter>0:
                        print 'File %s exists. User chose to overwrite it.' % gtltcube['outfile']
                        pass
                    pass
                else:
	            print 'Skipping gtltcube, file %s exists' % gtltcube['outfile']
                    return
                pass
            pass
        gtltcube.run()
        
    
    def make_expMap(self,**kwargs):
	overwrite="undefined";
        gtexpmap = GtApp('gtexpmap','Likelihood')
        gtexpmap['evfile']=self.evt_file
        gtexpmap['scfile']=self.FilenameFT2
        gtexpmap['expcube']=self.expCube
        gtexpmap['outfile']=self.expMap
        gtexpmap['irfs']=self._ResponseFunction
        
        if('srcrad' in kwargs.keys()):
          gtexpmap['srcrad'] = float(kwargs['srcrad'])
          #Default choice: 0.8 deg binning
          gtexpmap['nlong'] = int(2*float(kwargs['srcrad'])/0.5)
          #Default choice: 0.8 deg binning
          gtexpmap['nlat']  = int(2*float(kwargs['srcrad'])/0.5)
        else:
          gtexpmap['srcrad']=self.radius+10
          gtexpmap['nlong']=int(2*(self.radius+10)) # ,2,1000,Number of longitude points
          gtexpmap['nlat']=int(2*(self.radius+10)) # ,2,1000,Number of latitude points
        pass
        
        gtexpmap['nenergies']=10#,i,a,20,2,100,Number of energies
	chatter = 1
        for key in kwargs.keys():
	    goodkey=False
            if key in gtexpmap.keys():
                gtexpmap[key]=kwargs[key]
		goodkey = True
	    if key.lower()=="overwrite": 
		overwrite=kwargs[key]
	    elif key.lower()=="chatter": 
		chatter  =kwargs[key]
            elif not goodkey:
                print 'WARNING : gtexpmap invalid argument %s discarded'%key
                pass	
            pass
        
        if os.path.exists(gtexpmap['outfile']):
	    if overwrite==False: 
	        if chatter>0 : print 'File %s exists. User chose not to overwrite it.' % gtexpmap['outfile']
		return
	    else:
		if overwrite==True: 
		    a="Y"
	        elif overwrite=="undefined":
        	    cmd='make_expmap: %s file exists. Remove? [y/N] ' % gtexpmap['outfile']
	    	    a=raw_input(cmd)
                    pass                
                if (a.upper()=='Y'):
	            cmd='rm %s' % gtexpmap['outfile']
    	            runShellCommand(cmd)
                    if chatter>0 : print 'File %s exists. User chose to overwrite it.' % gtexpmap['outfile']
                    pass
                else:
	            print 'Skipping gtexpmap, file %s exists' % gtexpmap['outfile']
                    return
                pass
            pass
        gtexpmap.run()

    #--------------------------------
    def make_exposure(self,xmlFile,**kwargs):
        start = self.GRB.TStart
        stop  = self.GRB.TStop
        print start,stop, stop-start, self.Emin, self.Emax
        
        #1) make a LC file:
        lc_exposure=self.out_dir+'/'+self.grb_name+'_LAT_exposure.fits'
        
        gtbin = GtApp('gtbin')        
        gtbin['algorithm']='LC'
        
        gtbin['evfile']  = self.evt_file
        gtbin['scfile']  = self.FilenameFT2
        gtbin['outfile'] = lc_exposure
        
        gtbin['tbinalg']='LIN'
        
        gtbin['tstart'] = start
        gtbin['tstop']  = stop
        gtbin['dtime']  = stop-start # THIS BECAUSE MAKES ONE BIN...
        gtbin.run()        
        #2) calculate the exposure:
        gtexposure = GtApp('gtexposure')
        gtexposure['infile']=lc_exposure
        gtexposure['scfile']=self.FilenameFT2
        gtexposure['irfs']  =self._ResponseFunction
        gtexposure['srcmdl']=xmlFile
        gtexposure['target']='GRB'
        gtexposure.run()
        exposure=pyfits.open(lc_exposure)['RATE'].data.field('EXPOSURE').sum()
        return exposure

        
    # Likelihood, Upper limits, etc.:
    #--------------------------------

    def make_XmlModel(self,model='Powerlaw',ModEdit=False,**kwargs):
        if ModEdit:
            cmd = ('ModelEditor& \n')
            runShellCommand(cmd)
        else:
            xmlfile = self.out_dir+'/'+self.grb_name+'_'+model+'.xml'
            latutils.write_xmlModel(model,xmlfile,self.GRB.ra,self.GRB.dec,**kwargs)
            

    def make_Likelihood(self, model='', **kwargs):
        
        #xmlfile=self.GRB.SaveGRBModel()
        xmlfile=self.GRB.InitGRBModel()
        
        if model != '':
            xmlfile = self.out_dir+'/'+self.grb_name+'_'+model+'.xml'
            if not os.path.exists(xmlfile):
                print 'no source model file for model ' + model
                return
        print xmlfile
        xmlfile_out=xmlfile.replace('.xml','_out.xml')
        print xmlfile_out
        try:
            from GtApp import GtApp
        except:
            print "GtApp module not found. Perhaps You need to source the sane package setup file. Exiting"
            return
        try:
            like = GtApp('gtlike','Likelihood')
        except 'ParFileError':
            print "You need to have the par file in the current directory, or to set the PFILES env variable accordingly."
        like['srcmdl']=xmlfile
        like['sfile']= xmlfile_out
        like['statistic']='Unbinned'
        like['optimizer']=self.like_optimizer

        if os.path.exists(self.expCube):
            like['expcube']=self.expCube
        else:
            like['expcube']='none'

        like['evfile']=self.evt_file
        like['scfile']=self.FilenameFT2

        if os.path.exists(self.expMap):
            like['expmap']=self.expMap
        else:
            like['expmap']='none'

        if os.path.exists(self.mp_outFile):
            like['cmap']=self.mp_outFile
        else:
            like['cmap']='none'
        like['bexpmap']='none'

        like['plot']='yes'

        for key in kwargs.keys():
            if key in like.keys():
                like[key]=kwargs[key]
            else:
                print 'WARNING : like invalid argument %s discarded'%key

        like.run()
        self.xmlfile=xmlfile
        pass

    

    def pyLike(self,**kwargs):
        """
        launch a python Likelihood session. The following arguments are available:
        infile : name of the input FT1 file (default : self.evt_file)
        verbosity : verbosity of the call to the optimizer (default : 3)
        """
        
        if os.getenv('NOST') is not None:
            print 'NOST env var. is set : ScienceTools were not properly located.'
            return

        infile    = self.evt_file
        scfile    = self.FilenameFT2
        verbosity = 3
        irf       = self._ResponseFunction
        optimizer = self.like_optimizer
        expmap    = self.expMap
        expcube   = self.expCube
        fixing    = 0
        chatter   = 1
        for key in kwargs.keys():
            if key == 'infile'    : infile    = kwargs[key]
            elif key == 'verbosity' : verbosity = kwargs[key]
            elif key == 'irfs'      : irf       = kwargs[key]
            elif key == 'model'     : xmlFile   = kwargs[key]
            elif key == 'optimizer' : optimizer = kwargs[key]
            elif key == 'expmap'    : expmap    = kwargs[key]
            elif key == 'expcube'   : expcube   = kwargs[key]
            elif key == 'scfile'    : scfile    = kwargs[key]
            elif key == 'fixing'    : fixing    = kwargs[key]
            elif key == 'chatter'   : chatter   = kwargs[key]	    
	    else :print "Parameter %s not recognized!" %key
            pass
	if chatter>0: 
            print 'evtfile  =',infile
	    print 'scfile   =',scfile
    	    print 'expmap   =',expmap
    	    print 'expcube  =',expcube
	    print 'irf      =',irf
            print 'xmlFile  =',xmlFile
    	    print 'optimizer=',optimizer
	    print 'fixing   =',fixing
            print self.likeFit
        
        #my_obs =  UnbinnedAnalysis.UnbinnedObs(infile, self.FilenameFT2,  expMap=self.expMap, expCube=self.expCube, irfs=irf)
        if(os.environ.get('GUIPARAMETERS')=='yes'):
          #Use a GUI to edit the likelihood model
          #cmd='ModelEditor %s' % (xmlFile)
          #runShellCommand(cmd)
          from GTGRB.xmlModelGUI import xmlModelGUI
          app = xmlModelGUI(xmlFile)
          print("\nLoading the Likelihood model...")
          self.like = UnbinnedAnalysis.unbinnedAnalysis(evfile=infile,
                                                      scfile=scfile,
                                                      expmap=expmap,
                                                      expcube=expcube,
                                                      irfs=irf,
                                                      optimizer=optimizer,
                                                      srcmdl=xmlFile)
          print self.like.model
          #self.like.ftol=1e-10    
          fixed=0
        else:
          self.like = UnbinnedAnalysis.unbinnedAnalysis(evfile=infile,
                                                      scfile=scfile,
                                                      expmap=expmap,
                                                      expcube=expcube,
                                                      irfs=irf,
                                                      optimizer=optimizer,
                                                      srcmdl=xmlFile)
          #self.like.ftol=1e-10    
          fixed=0
          while fixing:
            print self.like.model
            a = raw_input('For fixing Parameters, input SOURCE NAME, PARAMETER NAME, VALUE. Return to skip: ')
            print a
            try:
                a=a.split(',')
                a=map(lambda x:x.strip(),a)
                if(len(a)==3):
                  #Verify the input
                  sourceName            = a[0]
                  parameterName         = a[1]
                  value                 = float(a[2])
                  if(self.like.sourceNames().count(sourceName)==0):
                    print("\n\n *************************************")
                    print("Source name %s not found! Please note that names are case-sensitive! Please retry." %(sourceName))
                    print("*************************************")
                    continue
                  else:
                    if(self.like[sourceName].funcs['Spectrum'].paramNames.count(parameterName)==0):
                      print("\n\n *************************************")
                      print("No parameter %s for source %s! Please retry." %(sourceName,parameterName))
                      print("*************************************")
                      continue
                  pass
                  self.like[sourceName].src.spectrum().parameter(parameterName).setValue(float(a[2]))
                  self.like[sourceName].src.spectrum().parameter(parameterName).setFree(not self.like[sourceName].src.spectrum().parameter(parameterName).isFree())
                else:
                  if(a[0]==''):
                    #Done! let's continue with the analysis
                    fixing = 0
                    continue
                  else:  
                    print("\n\n *************************************")
                    print("Could not understand input. Please retry.")
                    print("*************************************")
                    continue    
            except:
                if len(a)<=3:
                    fixing=0
                    pass
                pass
            pass
        
        
        return self.like
    
    def make_tsmap(self,**kwargs):
        """
        compute the tsmap
        """

        gttsmap=GtApp('gttsmap','Likelihood')
        gttsmap['evfile']=self.evt_file
        gttsmap['scfile']=self.FilenameFT2
        gttsmap['expmap']='none'
        gttsmap['expcube']='none'
        gttsmap['srcmdl']='none'
        gttsmap['outfile']=self.tsmap_outFile
        gttsmap['irfs']=self._ResponseFunction
        gttsmap['optimizer']=self.like_optimizer
        #gttsmap['ftol'] = 1e-10
        gttsmap['nxpix']=  60
        gttsmap['nypix']=  60
        gttsmap['binsz']= 0.1
        gttsmap['coordsys']='CEL'
        gttsmap['xref']=self.GRB.ra
        gttsmap['yref']=self.GRB.dec
        gttsmap['proj']='TAN' # ?
        gttsmap['cmap']=self.mp_outFile  
        gttsmap['bexpmap']=self.mp_outFile  
        
        
        
        for key in kwargs.keys():
            if key in gttsmap.keys():
                gttsmap[key]=kwargs[key]
            else:
                print 'WARNING : like invalid argument %s discarded'%key
                pass
            pass
        for key in gttsmap.keys(): print key,gttsmap[key]
        gttsmap.run()
        pass
    
    def plot_tsmap(self,filename=""):
        """ Plot the tsmap using root """
        if filename=="":
    	    filename=self.tsmap_outFile
            pass
        return plotter.PlotTS(filename)
    
    def gtfindsrc(self,**kwargs):
        """
        compute gtfindsrc
        """
        #self.GRB.MakeXMLFileLikelihood()
        expmap                = 'none'
        expcube               = 'none'
        srcmdl                = 'none'
        #for key in kwargs.keys():
        #  if   key.lower()=="expmap":               expmap    = kwargs[key]
        #  elif key.lower()=="expcube":              expcube   = kwargs[key]
        #  elif key.lower()=="srcmdl":               srcmdl    = kwargs[key]
        #pass
          
        gtfindsrc=GtApp('gtfindsrc')
        gtfindsrc['evfile']=self.evt_file
        gtfindsrc['scfile']=self.FilenameFT2
        gtfindsrc['expmap']=expmap
        gtfindsrc['expcube']=expcube
        gtfindsrc['srcmdl']=srcmdl
        gtfindsrc['outfile']=self.findsrc_outFile
        gtfindsrc['irfs']=self._ResponseFunction
        gtfindsrc['optimizer']=self.like_optimizer
        gtfindsrc['target']='GRB'
        #gtfindsrc['ftol']=1e-10
        #gtfindsrc['atol']=0.003
        gtfindsrc['reopt']='yes'
        gtfindsrc['coordsys']='CEL'
        gtfindsrc['ra']=self.GRB.ra
        gtfindsrc['dec']=self.GRB.dec
        
        for key in kwargs.keys():
            if key in gtfindsrc.keys():
                gtfindsrc[key]=kwargs[key]
            else:
                print 'WARNING : like invalid argument %s discarded'%key
                pass
            pass
        gtfindsrc['mode']='ql'
        gtfindsrc.run()

    def make_DiffuseXML(self):
        
        xml='''<?xml version="1.0" ?>
        <source_library title="source library">
          <source name="Extragal_diffuse" type="DiffuseSource">
            <spectrum type="PowerLaw">
              <parameter free="1" max="100.0" min="1e-05" name="Prefactor" scale="1e-07" value="1.6"/>
              <parameter free="0" max="-1.0" min="-3.5" name="Index" scale="1.0" value="-2.1"/>
              <parameter free="0" max="200.0" min="50.0" name="Scale" scale="1.0" value="100.0"/>
            </spectrum>
            <spatialModel type="ConstantValue">
              <parameter free="0" max="10.0" min="0.0" name="Value" scale="1.0" value="1.0"/>
            </spatialModel>
          </source>
     
          <source name="BIGRUN_GALPROP_diffuse" type="DiffuseSource">
           <!-- diffuse source units are cm^-2 s^-1 MeV^-1 sr^-1 -->
           <spectrum type="ConstantValue">
             <parameter free="0" max="10.0" min="0.0" name="Value" scale="1.0" value="1.0"/>
           </spectrum>
           <spatialModel file="$(EXTFILESSYS)/galdiffuse/GP_gamma.fits" type="MapCubeFunction">
             <parameter free="1" max="1000.0" min="0.001" name="Normalization" scale="1.0" value="1.0"/>
           </spatialModel>
          </source>
        </source_library>'''
        xmlFileName =str(self.out_dir+'/diffuse_model.xml')
        xmlFile     = open(xmlFileName,'w')
        xmlFile.write(xml)
        return xmlFileName
        
    def make_gtdiffrsp(self,**kwargs):
        
        gtdiffrsp=GtApp('gtdiffrsp','Likelihood')
        gtdiffrsp['evfile']=self.evt_file
        gtdiffrsp['scfile']=self.FilenameFT2
        #gtdiffrsp['srcmdl']=filePath
        gtdiffrsp['irfs']=self._ResponseFunction
        gtdiffrsp['convert']='yes' # Convert to the new header format
        gtdiffrsp['clobber']='yes' # This overwrite the diffuse columns
        for key in kwargs.keys():
            if key in gtdiffrsp.keys():
                gtdiffrsp[key]=kwargs[key]
            else:
                print 'WARNING : like invalid argument %s discarded'%key
                pass
            pass
        gtdiffrsp.run()
        
        pass

    def ComputeUpperLimit(self,index,**kwargs):
        
        if(not os.path.exists(self.expMap)):
            print 'run LAT.make_expMap()'
            return
        if(not os.path.exists(self.expCube)):
            print 'run LAT.make_expCube()'
            return
        
           
        import UpperLimits as UL
        my_obs = UnbinnedAnalysis.UnbinnedObs(self.evt_file,self.FilenameFT2, expMap=self.expMap, expCube=self.expCube,
                                              irfs=self._ResponseFunction)
        
        like = UnbinnedAnalysis.UnbinnedAnalysis(my_obs, self.GRB.xml_file_name,**kwargs)
        if(index is not None):
            like.model[5]=index
            like.model[5].setFree(0)
        like.fit()
        print like.model

        like.writeCountsSpectra(self.likeFit)
        
        print 'TS (GRB)=', like.Ts('GRB')
        #like = unbinnedAnalysis(mode='h')
        ul = UL.UpperLimits(like)
        flux=ul['GRB'].compute()
        print ul['GRB'].results
        return like,flux
    
        #analysis.plot()
        #analysis.print()
        #analysis.fit()
        
        #analysis.plot()
        #Ts=analysis.Ts('grb')
        #print Ts
        
        #analysis.Ts('grb', reoptimize=True)
    	#from computeUpperLimit import UpperLimits
        #ul=UpperLimits(analysis)
        #flux=ul['grb'].compute()
        #print 'Flux (100 MeV-300 GeV), 95%% CL = %.2e ph/cm^2/s' % float(flux)
        #return analysis
    
    
    def confreg_pyLike(self,nsig=3,**kwargs):

        infile=self.evt_file
        verbosity=3
        irf = 'P5_v0_transient'

        for key in kwargs.keys():
            if key == 'infile' : infile = kwargs[key]
            if key == 'verbosity' : verbosity = kwargs[key]
            if key == 'irfs' : irf = kwargs[key]
       
        like,obs = self.pyLike(infile=infile,verbosity=verbosity,irfs=irf)

        par = like.model.params
        cov = like.covariance
        if len(par) != 3:
            print 'confidence region only for simple Powerlaw spectrum so far...\n'
        elif cov is None:
            print 'no covariance matrix : can"t provide a confidence region\n'
        else:
            #self.GetEMaxMin()
            e1 = self.Emin
            e2 = self.Emax
            
            e0 = par[2].value()*par[2].getScale() # MeV
            norm = par[0].value()*par[0].getScale() # ph/cm2/s/keV
            gamma = par[1].value()*par[1].getScale()
            
            
            Vnn = cov[0][0]*par[0].getScale()*par[0].getScale()
            Vng = cov[0][1]*par[0].getScale()*par[1].getScale()
            Vgg = cov[1][1]*par[1].getScale()*par[1].getScale()
            
            plotter.plot_confreg(self,e1,e2,e0,norm,gamma,Vnn,Vgg,Vng,nsig)

    # Various plots:
    #---------------

    def plotCMAP(self,**kwargs):
        c0 = plotter.plotCMAP(self,size=self.radius,**kwargs)
        self.GRB.WriteToROOTFile(c0)
        pass
    
    def plotCMAP_PYLAB(self):
        plotter.plotCMAP_PYLAB(self,map=self.mp_outFile, center=[self.GRB.ra, self.GRB.dec])
        pass
    
    def plotSpectrum_PYLAB(self):
        plotter.plotSpectrum_PYLAB(self.likeFit)
        pass

    def plotSpectrum_ROOT(self):
        plotter.plotSpectrum_ROOT(self.likeFit)
        pass

    def plotAngSeparation(self,BEFORE=10000,AFTER=10000):
        print '-- Plotting angular separation between %s and %s'%(BEFORE,AFTER)
        png_filename='%s/%s_%i_%i_pointing.png' % (self.out_dir,self.grb_name,BEFORE,AFTER)
        MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0 = \
            latutils.AngSeparation(self.GRB.ra,self.GRB.dec,self.GRB.Ttrigger,self.FilenameFT2,BEFORE,AFTER)
        #c1 = plotter.plotAngSeparation_ROOT(self.GRB.Ttrigger, MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0)
        earth_ang = self.zmax-self.radius
        fov_ang   = 75
        plotter.plotAngSeparation_PYLAB(self.GRB.Ttrigger,MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0,outfile=png_filename,earth_ang=earth_ang,fov_ang=fov_ang)
        #png_filename='%s/%s_%i_%i_pointing.png' % (self.out_dir,self.grb_name,BEFORE,AFTER)
        #c1.Print(png_filename)
        #self.GRB.WriteToROOTFile(c1)
        pass

    def getGRBTheta(self):
        if self.theta<0: self.theta=float(latutils.GetTheta(self.GRB.ra,self.GRB.dec,self.GRB.Ttrigger,self.FilenameFT2))
        return self.theta

    def getGRBZenith(self):
        if self.zenith<0: self.zenith=float(latutils.GetZenith(self.GRB.ra,self.GRB.dec,self.GRB.Ttrigger,self.FilenameFT2,self.chatter))
        return self.zenith
    
    def getMcIlWain(self):
        (McIlWain_L,McIlWain_B) = latutils.GetMcIlWain(self.GRB.Ttrigger,
                                                       self.FilenameFT2,
                                                       self.chatter)
        return (McIlWain_L,McIlWain_B)
    
    # XSPEC:
    #-------

    def fit_XSPEC(self,model='pow',local_model_name = 'mymodels',local_model_path='',Epiv=1e3):
        #def fit_XSPEC(self,model='pow',local_model_name = 'mymodels',local_model_path='',Epiv=1e3):
        #make_LAT_XSPEC2.LAT_SPECTRUM_XSPEC(self,model,local_model_path,local_model_name,Epiv)

        if local_model_path == '':
            try:
                if os.getenv('MODELS') is not None:
                    try:
                        if os.path.exists(os.environ['MODELS']):
                            local_model_path = os.environ['MODELS']
                    except AttributeError:
                        print os.environ['MODELS'] + ' : directory does not exist\n'
            except AttributeError:
                print '$MODELS environment variable not defined\n'
                
                
        scriptname = self.GRB.out_dir+'/LAT_fit_'+model+'.xcm'
        outputfile = self.GRB.out_dir+'/LAT_fit_'+model+'.dat'
        specfile = self.GRB.out_dir+'/LAT_fit_'+model+'.ps'
        
        Detectors=[]
        PHAfiles={}
        RSPfiles={}
        BAKfiles={}
        
        Detectors=['LAT']
        PHAfiles['LAT'] = self.sp_outFile
        RSPfiles['LAT'] = self.rsp_File
        BAKfiles['LAT'] = ''
        
        Epiv = Epiv * 1000 # MeV to keV
        XSPEC.MakeScript(PHAfiles,
                         RSPfiles,
                         BAKfiles,
                         Detectors,
                         area = False,
                         model = model,
                         local_model_name = local_model_name,
                         local_model_path = local_model_path,
                         statistics = 'cstat',
                         script = scriptname,
                         outfile = outputfile,
                         CalcFlux = True,
                         parameters = [str(Epiv)],
                         SpectrumFileName = specfile,
                         deltafit=1.)
        
        # perform the fit
        XSPEC.Fit(scriptname)
        
    def confreg_XSPEC(self,model='normPL'):
        plotter.plot_confreg_xs(self,model)
        pass

    def gtsrcprob(self,**kwargs):
        ''' Basic interface to gtsrcprob.
        
        'tstart_offset', 'tstop_offset', and 'like_model' arguments to let the code create the UnbinnedLikelihood object itself.
        Default like_model="GRB+ISO+GAL"
	'''
        _gtsrcprob = GtApp('gtsrcprob')
        for key in kwargs.keys(): _gtsrcprob[key] = kwargs[key]
	_gtsrcprob.run()
	return _gtsrcprob['outfile']    
    

        
    
    def gt_run_gtsrcprob(self,**kwargs):
	'''Run gtsrcprob. The user can either pass an existing UnbinnedLikelihood object using a
        'like' argument or a set of 
        'tstart_offset', 'tstop_offset', and 'like_model' arguments to let the code create the UnbinnedLikelihood object itself.
        Default like_model="GRB+ISO+GAL"
	'''
	chatter=2
	for key in kwargs.keys():
	    if key.lower()=="chatter":  chatter=int(kwargs[key])
            pass    
        
	#first search if the user is passing an UnbinnedLikelihood analysis object for us to use. 
	like=""
	for key in kwargs.keys():
	    if kwargs[key].__class__.__name__=="UnbinnedAnalysis":  
		like=kwargs[key]
		if chatter>2: gt_print("Using passed likelihood object",chatter=chatter)
                pass
            pass
	
	if like=="": #no UnbinnedLikelihood object was passed. Create one.
	    tstart_offset=""
	    tstop_offset=""
	    like_model="GRB+ISO+GAL"
    	    for key in kwargs.keys():
		if   key.lower()=="tstart_offset":  tstart_offset=float(kwargs[key])
		elif key.lower()=="tstop_offset":   tstop_offset=float(kwargs[key])
		elif key.lower()=="like_model":    like_model=kwargs[key]
                pass
	    if tstart_offset=="" or tstop_offset=="":
		gt_print("Please pass both an tstart_offset and an tstop_offset argument to the function",chatter=chatter)
		return
            
            if chatter>2: gt_print("Creating new UnbinnedLikelihood object")
            try:
                like,files=LikelihoodFit.gt_Create_UnbinnedLikelihood(self,like_model=like_model,tstart_offset=tstart_offset,tstop_offset=tstop_offset,KeepFiles=True,chatter=chatter,Fit=True,ResultsDirPrefix="gtsrcprob")
            except:	
                return
	    pass
        
        src_xml = like.srcModel.replace('.xml','_srcprob.xml')
        like.writeXml(xmlFile = src_xml) # This make sure that the like model is saved into the XML file, without overwritting anything...
        
        return self.gtsrcprob(evfile  = like.observation.eventFiles[0],
                              scfile  = like.observation.scFiles[0],
                              outfile = "%s/%s_srcprobs.fits" %(self.out_dir,self.grb_name),
                              srcmdl  = src_xml,
                              irfs    = like.observation.irfs,
                              chatter = chatter)
    
    def plotLC_PSFCUT_AllClass(self,dt,t1_offset=0,t2_offset=9999999999,energyMin=0,FT1_File="",Containment=0.95):
       ''' Draw a set of lightcurves, each one for a different minimum event class using a 95% PSF cut '''
       
       h=[]
       import sys
       c=ROOT.TCanvas("cLC","Lightcurves %.2f containment" %Containment);ROOT.SetOwnership(c,False)
       tl=ROOT.TLegend(0.7,0.7,0.9,0.9);ROOT.SetOwnership(tl,False)
       for evtcls_min in range(0,3): 
           h.append(self.plotLC_PSFCUT(dt=dt,t1_offset=t1_offset,t2_offset=t2_offset,evtcls=evtcls_min,energyMin=energyMin,FT1_File=FT1_File,Draw=False,Containment=Containment))
           h[-1].SetLineColor(evtcls_min+1)
           h[-1].SetLineStyle(2)
           h[-1].SetLineWidth(2)
           if evtcls_min==0:  h[-1].Draw()
           else:              h[-1].Draw("SAME")
           
           tl.AddEntry(h[-1],"evtcls>%d" %evtcls_min,"l")
       pass
       tl.SetFillColor(0)
       tl.Draw("SAME")
       c.Update()
       return c
    
    def plotLC_PSFCUT(self,dt,t1_offset=0,t2_offset=9999999999,evtcls=0,energyMin=0,FT1_File="",Draw=True,Containment=0.95):
       ''' Draw a lightcurve using a PSF cut '''
       events=self.countEVT(t1_offset=t1_offset,t2_offset=t2_offset,evtcls=evtcls,energyMin=energyMin,show=False,ApplyPSFCut=True,ReturnEventList=True,FT1_File=FT1_File,Containment=Containment)
       if t1_offset==0:  start=events[0][0] 
       else           :  start=self.GRB.Ttrigger+t1_offset
       
       stop =events[-1][0]
       nbins = int((stop-start)/dt)
       title = 'GRB %s %s lightcurve (evtcls>%d)' %(self.GRB.Name,self.detector_name,evtcls)
       h=ROOT.TH1F(title,title,nbins,t1_offset,t2_offset)

       for i in range(len(events)):
          h.Fill(events[i][0]-self.GRB.Ttrigger)

       h.SetXTitle('TIME - MET ' + str(self.GRB.Ttrigger))
       h.SetYTitle('COUNTS/' + str(dt)+ 'SEC')
       h.GetXaxis().CenterTitle()
       ROOT.SetOwnership(h,False)
       
       if (Draw):
          c0 = ROOT.TCanvas ('c0', 'lightcurve %.2f containment' %(Containment), 0, 0, 500, 300)
          ROOT.SetOwnership(c0,False)
          h.Draw()
          c0.Update()
      
       return h
       
       
