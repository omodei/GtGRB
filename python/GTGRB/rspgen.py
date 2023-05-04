#! /usr/bin/env python

  #############################################################################
  ##  python script rspgen.py  -v5r5
  ##  create .pha and .rsp files for XSPEC
  ##  with energy dependent ROI.
  ##
  ##   Please let us know
  ##     if you have any commnets/suggestions or bug reports.  
  ##   Thank you!
  ##                                       written by Takashi Shimokawabe
  ##                                   email: shimokawabe@hp.phys.titech.ac.jp
  ##                                       developed by Takaaki Tanaka
  ##                                   email: ttanaka@slac.stanford.edu
  ##                                       developed by Masaaki Hayashida
  ##                                   email: mahaya@slac.stanford.edu
  ##                                                   date:  Sep. 2008
  ###########################################################################*/

  ###########################################################################
  ##
  ## This version has been modified to create pha2 files fitting with rmfit
  ##
  ## gtbindef and pha2rmfits modules added by Sylvain Guiriec
  ##                                   email: sylvain.guiriec@lpta.in2p3.fr
  ##                                                   date:  Oct. 2008
  ##
  ###########################################################################

  ###########################################################################
  ##
  ## This version has been updated to perform an automatic computation of the
  ## PSF using an energy dependent ROI as done by Aurelien Bouvier
  ##                                   email: bouvier@stanford.edu
  ##                                                   date:  Nov. 2008
  ##
  ## Implementation done by Sylvain Guiriec
  ##                                   email: sylvain.guiriec@lpta.in2p3.fr
  ##                                                   date:  Nov. 2008
  ##
  ###########################################################################

import os, os.path, sys, getopt
import math
import astropy.io.fits as pyfits
import shlex
from GtApp import GtApp
import pyIrfLoader
import ROOT
from genutils import runShellCommand
import numpy

def GenerateLogList(xmin,xmax,Nx):
    fact=10**((math.log10(xmax)-math.log10(xmin))/(Nx-1))
    List=[0 for i in range(Nx)]
    val=xmin
    for k in range(Nx):
        List[k]=val
        val*=fact
    return List

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

class PsfHandler(object):
    """
    access class to the LAT IRFs
    """
    def __init__(self, irfsname):
        #import pyIrfLoader
        pyIrfLoader.Loader_go ()
        #irfs = pyIrfLoader.IrfsFactory.instance()
        self.psf= pyIrfLoader.IrfsFactory.instance().create(irfsname).psf()
    
class AeffHandler(object):
    """
    access class to the LAT IRFs
    """
    def __init__(self, irfsname):
        #import ROOT
        #ROOT.gSystem.Load("librootIrfLoader")
        #self.psf=ROOT.rootIrfLoader.Psf(irfsname)
        pyIrfLoader.Loader_go ()
        self.aeff = pyIrfLoader.IrfsFactory.instance().create(irfsname).aeff()

    
class RspGen():
    
    def __init__(self, FT1_file, FT2_file, basename,
                 ra, dec, radius, Tstart, Tstop, Emin, Emax, Ebins,
                 TbinFile, nbTimeBins,ResponseFunction, evtclass=None, PHAtype='PHA1'):        
        self.energybinalg = 'LOG'
        self.respalg = 'PS'
        self.FT1_file = FT1_file
        self.FT2_file = FT2_file
        self.evt_file = '%s_ROI.fits' % basename
        self.pha1_file = '%s.pha' % basename
        self.pha2_file = '%s.pha2' % basename
        self.rsp_file = '%s.rsp' % basename
        self.ra = ra
        self.dec = dec
        self.radius = radius
        self.Tstart = Tstart
        self.Tstop = Tstop
        self.Emin = Emin
        self.Emax = Emax
        self.Ebins = Ebins
        self.TbinFile = TbinFile #'tbin.fit'
        self.ResponseFunction = ResponseFunction
        self.nbTimeBins = nbTimeBins
        self.dTime=(self.Tstop-self.Tstart)/self.nbTimeBins
        print 'RspGen - Tstop-Tstart: %.3f '% (self.Tstop-self.Tstart)
        print 'RspGen - nbTimeBins: %d ' % self.nbTimeBins
        print 'RspGen - dTime: %.3f ' % self.dTime
        print 'RspGen -  Emin: %.1f ' % self.Emin
        print 'RspGen -  Emax: %.1f ' % self.Emax
        print 'RspGen - Ebins: %.1f ' % self.Ebins

        if evtclass=='FRONT':
            self.evtclass=0
        elif evtclass=='BACK':
            self.evtclass=1
        else:
            self.evtclass=-1
        self.PHAtype=PHAtype
        
    def make_select(self):
        gtselect = GtApp('gtselect')
        gtselect['infile']=self.FT1_file
        gtselect['outfile']=self.evt_file
        gtselect['ra']  = self.ra
        gtselect['dec'] = self.dec
        gtselect['rad']  = self.radius
        gtselect['tmin'] = self.Tstart
        gtselect['tmax'] = self.Tstop    
        gtselect['emin'] = self.Emin
        gtselect['emax'] = self.Emax
        gtselect['convtype'] = self.evtclass
        
        gtselect.run()

        ft1 = pyfits.open(gtselect['outfile'])
        hea = ft1['EVENTS'].header
        nevents=hea.get('NAXIS2')
        ft1.close()
        print 'rspgen::make_select(): gtselect: selected : %i Events...' % (nevents)
        return nevents
    
    def make_pha1(self):
        gtbin = GtApp('gtbin')
        gtbin['algorithm']='PHA1'
        gtbin['evfile'] = self.evt_file
        gtbin['scfile'] = self.FT2_file
        gtbin['outfile'] = self.pha1_file
        gtbin['ebinalg'] = self.energybinalg
        gtbin['emin'] = self.Emin
        gtbin['emax'] = self.Emax
        gtbin['enumbins'] = self.Ebins
        gtbin.run()        

    def make_pha2(self):
        gtbin = GtApp('gtbin')
        gtbin['algorithm']='PHA2'
        gtbin['evfile'] = self.evt_file
        gtbin['scfile'] = self.FT2_file
        gtbin['outfile'] = self.pha2_file
        gtbin['ebinalg'] = self.energybinalg
        gtbin['emin'] = self.Emin
        gtbin['emax'] = self.Emax
        gtbin['enumbins'] = self.Ebins
        gtbin['tbinalg'] = 'FILE'
        gtbin['tbinfile'] = self.TbinFile
        #gtbin['tbinalg'] = 'LIN'
        gtbin['tstart'] = self.Tstart
        gtbin['tstop'] = self.Tstop    
        #gtbin['dtime']   = self.dTime
        #gtbin['tbinfile'] = "NONE" #self.TbinFile


        gtbin.run()        

    def make_rsp(self):
        # compute E_true_min and E_true_max to be included in the response file:
        dE_rsp=10**((math.log10(self.Emax)-math.log10(self.Emin))/(10.0*self.Ebins))
        Emin_rsp=self.Emin
        Emax_rsp=self.Emax
        Ebins_rsp=self.Ebins
        while Emin_rsp>self.Emin*(1-3*0.2) and Emin_rsp>20:
            Emin_rsp=Emin_rsp/dE_rsp
            Ebins_rsp+=1            
        while Emax_rsp<self.Emax*(1+3*0.2) and Emax_rsp<500000:
            Emax_rsp=Emax_rsp*dE_rsp
            Ebins_rsp+=1
            pass
        #        print Emin_rsp,self.Emin,self.Emax,Emax_rsp
        #        print self.Ebins,Ebins_rsp
        
        
        gtrspgen = GtApp('gtrspgen')
        gtrspgen['respalg']= self.respalg
        gtrspgen['specfile']=self.pha1_file # set to be the same as pha2_file so no need to change it for pha2 production
        gtrspgen['scfile']=self.FT2_file
        gtrspgen['outfile']=self.rsp_file
        gtrspgen['irfs']=self.ResponseFunction        
        #gtrspgen['time']=(self.Tstart+self.Tstop)/2.
        gtrspgen['ebinalg'] = self.energybinalg
        gtrspgen['emin']    = 50 #Emin_rsp
        gtrspgen['emax']    = 300000 #Emax_rsp
        gtrspgen['enumbins']= 100 #Ebins_rsp
        # NO
        gtrspgen['thetacut']=70.0
        gtrspgen['dcostheta']=0.05
        #
        gtrspgen.run()

    def run(self):
        self.make_select();
        if self.PHAtype=='PHA1':
            self.make_pha1();
        elif self.PHAtype=='PHA2':
            self.make_pha1();
            self.make_pha2();
        if self.PHAtype=='PHA1' or self.PHAtype=='PHA2':
            self.make_rsp();

class MultiRspGen():

    def __init__(self, paramfile):    
        
        # Output files
        self.FIT = '' 
        self.PHA = '' 
        self.RSP = ''

        # Input files and parameters
        self.FT1 = ''
        self.FT2 = ''
        self.Tstart = 0.0
        self.Tstop = 0.0
        self.Ttrig = 0.0
        self.Emin = 0.0
        self.Emax = 0.0
        self.RA=0.0
        self.DEC=0.0
        self.THETA=0.0
        self.PHI=0.0
        self.ERROR_RADIUS=0.0
        self.EMIN = 0.
        self.EMAX = 0.
        self.Ebins = 0
        # self.TbinFile = 'tbin.fit'
        self.dTime = ''
        self.ResponseFunction = ''
        self.evtclass=''
        self.PHAtype=''
        
        self.enROIs = []

        self.paramfile = paramfile

        self.nbTimeBins=0
        self.tbInputFile=''

    def read_conf(self):
        params = {'FIT'    : 'str',
                  'PHA'    : 'str',
                  'RSP'    : 'str',
                  'FT1'    : 'str',
                  'FT2'    : 'str',
                  'Tstart' : 'float',
                  'Tstop'  : 'float',
                  'Ttrig': 'float',
                  'RA'  : 'float',
                  'DEC'  : 'float',
                  'ERROR_RADIUS'  : 'float',
                  'THETA'  : 'float',                  
                  'PHI'  : 'float',                  
                  'EMIN'  : 'float',
                  'EMAX'  : 'float',
                  'Ebins'  : 'int',
                  'dTime'  : 'float',
                  'tbInputFile' : 'str',
                  'ResponseFunction' : 'str',
                  'PHAtype' : 'str'}
        f = open(self.paramfile)
        lex = shlex.shlex(f,posix=True)
        lex.whitespace += "="
        lex.whitespace_split = True
        flag = True
        while flag:
            t = lex.get_token()
            if params.has_key(t) :
                exec("self.%s = %s('%s')" % (t, params[t], lex.get_token()))
                pass
            if t==lex.eof:
                flag = False
                break
            pass
        # put the TStart / Tstop in MET time
        self.Tstart=self.Ttrig+self.Tstart
        self.Tstop=self.Ttrig+self.Tstop
        self.nbTimeBins=(self.Tstop-self.Tstart)/self.dTime
        #print '-- self.nbTimeBins=(self.Tstop-self.Tstart)/self.dTime = %s' % self.nbTimeBins
        #
        #self.TbinFile = 'tbin.fit'
        self.TbinFile  = self.FIT.replace('.fits','_tbin.fits')
        tbInputFile    = ''
        #
        if self.tbInputFile == '':
            self.tbInputFile=self.FIT.replace('.fits','_timebinsAutomaticGeneration.txt')
            print "The time step will be ",self.dTime," s"
        else:
            pass
        print "The time bins will be read from ",self.tbInputFile
        if self.ResponseFunction.split('::')[-1]=='FRONT':
            self.evtclass='FRONT'
        elif self.ResponseFunction.split('::')[-1]=='BACK':
            self.evtclass='BACK'
        else:
            self.evtclass=None
            
        # compute theta for the particular time bins if PHAtype=='PHA1':
        if self.THETA==0.0 and self.PHAtype=='PHA1': 
            fft2=pyfits.open(self.FT2)
            START=fft2['SC_DATA'].data.field('START')
            STOP=fft2['SC_DATA'].data.field('STOP')
            ra_scz=fft2['SC_DATA'].data.field('RA_SCZ')
            dec_scz=fft2['SC_DATA'].data.field('DEC_SCZ')

            Tav=(START+STOP)/2.
            difTav=abs(Tav-(self.Tstart+self.Tstop)/2.)
            ind=0
            while difTav[ind]!=min(difTav): ind+=1
            (phi,theta)=getNativeCoordinate((self.RA,self.DEC),(ra_scz[ind],dec_scz[ind]))
            self.THETA=math.degrees(getAngle(phi,theta))
            pass
        Energybins=GenerateLogList(self.EMIN,self.EMAX,self.Ebins+1)
        Emin=Energybins[:-1]
        Emax=Energybins[1:]

        if self.evtclass=='FRONT' or self.evtclass=='BACK':
            psf=PsfHandler(self.ResponseFunction)
        else:
            psf_f=PsfHandler(self.ResponseFunction+'::FRONT')
            psf_b=PsfHandler(self.ResponseFunction+'::BACK')
            pass
        dang=0.001
        PSF95=[]

        if self.evtclass!='FRONT' and self.evtclass!='BACK':
            #ROOT.gSystem.Load("librootIrfLoader")
            aeff_f = AeffHandler(self.ResponseFunction+"::FRONT").aeff#ROOT.rootIrfLoader.Aeff( self.ResponseFunction+"::FRONT")
            aeff_b = AeffHandler(self.ResponseFunction+"::BACK").aeff #ROOT.rootIrfLoader.Aeff( self.ResponseFunction+"::BACK")
            pass
        for emin,emax in zip(Emin,Emax):
            eav=math.sqrt(emin*emax)
            rad=0
            _integral_psf=0
            while _integral_psf<0.95 and rad < 20:
                rad          += dang
                if self.evtclass=='FRONT' or self.evtclass=='BACK':
                    _integral_psf = psf.psf.angularIntegral(eav,self.THETA,self.PHI,rad)
                else: # use averaged PSF for back+front selection
                    denominator = (aeff_f.value(eav,self.THETA,self.PHI)+aeff_b.value(eav,self.THETA,self.PHI))
                    numerator   = (aeff_f.value(eav,self.THETA,self.PHI)*psf_f.psf.angularIntegral(eav,self.THETA,self.PHI,rad)+aeff_b.value(eav,self.THETA,self.PHI)*psf_b.psf.angularIntegral(eav,self.THETA,self.PHI,rad))
                    if denominator > 0:  _integral_psf = (numerator/denominator)
                    else:                _integral_psf = 0
                    tt00=psf_f.psf.angularIntegral(500,0,0,2) # to have psf_f work 
                    tt11=psf_b.psf.angularIntegral(500,0,0,2) # to have psf_b work
                    pass
                pass
            PSF95.append(rad)
            pass
        for i in range(len(PSF95)):
            if Emin[i]>=self.EMIN:
                roi=[]
                roi.append(Emin[i])
                roi.append(Emax[i])
                roi.append(self.RA)
                roi.append(self.DEC)
                rad=math.sqrt(PSF95[i]**2+self.ERROR_RADIUS**2)
                if self.evtclass=='FRONT':
                    roi.append(min(rad,12))
                    pass
                else:
                    roi.append(min(rad,12))
                    pass
                self.enROIs.append(roi)
                pass
            pass
        # if you want to store the PSF values:
        
        ROI_File=self.FIT.replace('.fits','rspgen.txt')
        print "creating %s..." % ROI_File
        ff=open(ROI_File,'w')
        ff.write('Emin\tEmax\tROI=sqrt(PSF95+ERROR_RADIUS)\n')
        for pp in self.enROIs:
            for val in [pp[0],pp[1],pp[-1]]:
                ff.write(str(val)+'\t')
            ff.write('\n')
        ff.close

        f.close()

        for p in params.keys():
            print '%s =  %s' % (p,eval('self.%s' % p))
            if eval('self.%s' % p) == '' :
                print >> sys.stderr, "Parameter '%s' is not found in '%s'." % \
                      (p,self.paramfile)
#                sys.exit(1)

#        for roi in self.enROIs:
#            print roi

        self.set_emin_emax()

    def make_gtbindef(self):
        
        if self.tbInputFile == self.FIT.replace('.fits','_timebinsAutomaticGeneration.txt'):
            self.nbTimeBins=(self.Tstop-self.Tstart)/self.dTime
            outFile=open(self.tbInputFile,'w')
            for i in range(0,int(self.nbTimeBins)):
                start = self.Tstart+i*self.dTime
                end   = self.Tstart+(i+1)*self.dTime
                outFile.write(str(start))
                outFile.write(" ")
                outFile.write(str(end))
                outFile.write("\n")
            outFile.close()
            binfile=self.tbInputFile
        else:
            inFile=open(self.tbInputFile)
            tempo=self.tbInputFile.split('.')
            tempo.pop()
            tempo[-1]+='_MET.txt'
            binfile='.'.join(tempo)
            outFile=open(binfile,'w')
            outlines=inFile.readlines()
            for ll in outlines:
                if ll!='':
                    self.nbTimeBins+=1
            for i in range(0,len(outlines)):
                j=0
                while outlines[i].split(' ')[j]=='':
                    j+=1
                start = str(float(outlines[i].split(' ')[j])+self.Ttrig)
                outFile.write(str(start))
                j+=1
                try:
                    while outlines[i].split(' ')[j]=='':
                        j+=1
                    end   = outlines[i].split(' ')[j]
                    if end[-1:]=='\n': 
                        end=str(float(end[:-1])+self.Ttrig)+'\n'
                    else: 
                        end=str(float(end)+self.Ttrig)+'\n' # in case there is a space before the change of line
                    outFile.write(" ")
                    outFile.write(str(end))
                except IndexError:
                    pass
            outFile.close()
            pass
        gtbindef = GtApp('gtbindef')
        gtbindef['bintype']='T'
        gtbindef['binfile']=binfile
        gtbindef['outfile']=self.TbinFile

        gtbindef.run()

        runShellCommand('rm '+binfile)
        pass
        
    def set_emin_emax(self):
        emin = self.enROIs[0][0]
        emax = self.enROIs[0][1]
        for roi in self.enROIs:
            if emin > roi[0] :
                emin = roi[0]
            if emax < roi[1] :
                emax = roi[1]
        self.Emin = emin
        self.Emax = emax
                
    def mk_ebound(self):        
        src = pyfits.open(self.rspID2file(0,'rsp'))        
        ebounds = [src[2].data.field('E_MIN')[0]]
        for i in range(0,self.Ebins):
            ebounds.append(src[2].data.field('E_MAX')[i])
        for (i,e) in enumerate(ebounds):
            print i,e/1000.0
        return ebounds

    def enROIs2chROIs(self):
        ebounds = self.mk_ebound()
        chROIs = []
        for roi in self.enROIs:
            chroi = [0,0,roi[2],roi[3],roi[4]]
            for i in range(0,self.Ebins):
                if abs(ebounds[i]-roi[0]*1000.0)<0.5 :
                    chroi[0] = i
                    pass
                elif ebounds[i] < roi[0]*1000.0-0.5 and \
                         ebounds[i+1] > roi[0]*1000.0+0.5:
                    chroi[0] = i
                    pass
                if abs(ebounds[i+1] - roi[1]*1000.0)<0.5 :                    
                    chroi[1] = i
                    if chroi[1] < 0 :
                        chroi[1] = 0
                        pass
                    pass
                elif ebounds[i] < roi[1]*1000.0-0.5 and \
                         ebounds[i+1] > roi[1]*1000.0+0.5:
                    chroi[1] = i - 1
                    pass
                pass
            chROIs.append(chroi)            
            #        for roi in self.enROIs:
            #            print roi
            #        for roi in chROIs:
            #            print roi
            pass
        return chROIs
    
    def make_roi_files(self):
        self.read_conf()
        print '(make_roi_files: dTime      = %s)' % self.dTime
        print '(make_roi_files: nbTimeBins = %s)' % self.nbTimeBins


        for (i,roi) in enumerate(self.enROIs):
            basename = '%s_%s-%s' % (self.rspID2basename(i),roi[0],roi[1])
            rspgen = RspGen(self.FT1, self.FT2,basename,
                            roi[2],roi[3],roi[4],self.Tstart,self.Tstop,
                            roi[0], roi[1], 0,
                            self.TbinFile,
                            self.nbTimeBins,
                            '')
            rspgen.make_select()
        
    def run(self):
        self.read_conf()
        print '(run: dTime = %s)' % self.dTime
        if self.PHAtype=='PHA2':  self.make_gtbindef()
        #self.TbinFile=None
        
        Amin,Amax=[],[]
        for (i,roi) in enumerate(self.enROIs):
            Amin.append(self.Emin)
            Amax.append(self.Emax)
            if self.PHAtype=='FITS' or self.PHAtype=='FIT':
                Emi=roi[0]; Ema=roi[1]
            else:
                Emi=self.Emin
                Ema=self.Emax
                pass
            rspgen = RspGen(self.FT1, self.FT2,self.rspID2basename(i),
                            roi[2],roi[3],roi[4],self.Tstart,self.Tstop,
                            Emi, Ema, self.Ebins,
                            self.TbinFile,
                            self.nbTimeBins,
                            self.ResponseFunction, self.evtclass, self.PHAtype)
            rspgen.run()
        
        if self.PHAtype=='FITS' or self.PHAtype=='FIT':
            self.combineFITS()
        elif self.PHAtype=='PHA1':
            chROIs = self.enROIs2chROIs()
            self.combine(chROIs, 'rsp')
            self.combine(chROIs, 'pha')
        elif self.PHAtype=='PHA2':
            chROIs = self.enROIs2chROIs()
            self.combine(chROIs, 'rsp')
            self.combine(chROIs, 'pha2')
            
        if self.PHAtype=='PHA2':
            import gtrmfit
            gtrmfit.pha2rmfit(self.PHA,self.Ttrig)


        for (i,roi) in  enumerate(self.enROIs):
            command='rm -f '+self.rspID2basename(i)+'*'
            runShellCommand(command)

        #command='rm -f '+ self.tbInputFile
        #runShellCommand(command)
        command='rm -f '+ self.TbinFile
        runShellCommand(command)

    def combineFITS(self):
        FITSnames  = self.FIT.replace('.fits','rspgen_FITSnames.txt')
        fitsname   = open(FITSnames,'w')
        for i in range(self.Ebins):
            fitsname.write(self.rspID2basename(i)+'_ROI.fits'+'\n')
            pass
        fitsname.close()
        
        ColumnList = self.FIT.replace('.fits','rspgen_ColumnList.txt')
        columnlist = open(ColumnList,'w')

        h0=pyfits.open(self.rspID2basename(0)+'_ROI.fits')
        columnlist.write('\n'.join(h0['EVENTS'].columns.names)+'\n')
        columnlist.close()
        runShellCommand('rm -rf '+self.FIT+' >& /dev/null') #This make the code crashing
        cmd='fmerge @'+FITSnames+' '+self.FIT+' @'+ColumnList
        print cmd
        runShellCommand(cmd)
        hdu=pyfits.open(self.FIT,mode='update')
        hdu.append(h0['GTI'])
        hdu.close()
        h0.close()

        runShellCommand('rm '+ColumnList)
        runShellCommand('rm '+FITSnames)

    def combine(self, chROIs, extension):
        print 'combine extension %s' % extension
        dest = pyfits.open(self.rspID2file(0,extension))
        
        if(extension=='rsp'):
           destF = fixMatrixHDU(dest['MATRIX'])

        for (i,roi) in enumerate(chROIs):
            if roi[0] > roi[1]:
                continue
            for ch in range(roi[0],roi[1]+1):
                src = pyfits.open(self.rspID2file(i,extension))
                if extension == 'rsp' :
                    srcF = fixMatrixHDU(src['MATRIX'])                    
                    self.cp_rsp_dat(srcF,destF,ch)
                elif extension == 'pha':
                    self.cp_pha_dat(src,dest,ch)
                elif extension == 'pha2':
                    self.cp_pha_dat(src,dest,ch)
                    pass
                src.close()

        if extension == 'rsp' :            
            output = self.RSP
            primary = dest[0].copy()
            ebounds = dest['EBOUNDS'].copy()
            dest.close()
            dest = pyfits.HDUList([primary,ebounds,destF])
        elif extension == 'pha':
            output = self.PHA
            dest[1].header['RESPFILE'] = self.RSP
        elif extension == 'pha2':
            output = self.PHA
            dest[1].header['RESPFILE'] = self.RSP
            pass
        dest[0].header['FILENAME'] = output
        
        if os.path.exists(output):
            os.unlink(output)        
        dest.writeto(output)
        os.unlink(output)
        dest.writeto(output)
        dest.close()
        #if extension == 'pha':
        #    from latutils import setPoissonPHAError
        #    setPoissonPHAError(output)
        #    pass
        pass
    
    def cp_rsp_dat(self, src, dest, channel):
        tb = 1
        for ebin in range(0,self.Ebins):
            try:
                dest.data.field('MATRIX')[ebin][channel] = src.data.field('MATRIX')[ebin][channel]
            except IndexError:
                pass
            pass
        pass
    
    def cp_pha_dat(self, src, dest, channel):
        tb = 1
        if self.PHAtype=='PHA1':
            dest[tb].data.field('COUNTS')[channel] = src[tb].data.field('COUNTS')[channel]
            dest[tb].data.field('STAT_ERR')[channel] = src[tb].data.field('STAT_ERR')[channel]
        elif self.PHAtype=='PHA2':
            print 'ggg', self.nbTimeBins
            for i in range(int(self.nbTimeBins)):
                print 'ggg',i,self.nbTimeBins
                dest[tb].data.field('COUNTS')[i][channel] = src[tb].data.field('COUNTS')[i][channel]
                dest[tb].data.field('STAT_ERR')[i][channel] = src[tb].data.field('STAT_ERR')[i][channel]
                pass
            pass
        pass
    
    def rspID2basename(self,i):
        if self.PHAtype=='FIT':
            return '%s_%03d' % (os.path.splitext(self.FIT)[0],i)
        else:
            return '%s_%03d' % (os.path.splitext(self.RSP)[0],i)

    def rspID2file(self,i,extension):
        return '%s.%s' % (self.rspID2basename(i),extension)

    def make_conf_template(self):
        conf = """#
# Parameter file
#

### Output files ###
PHA = output/combine.pha
RSP = output/combine.rsp

### Input parameters ###
FT1 = ./gll_ph_r0258240640_v002.fit
FT2 = ./gll_pt_r0258240640_v001.fit
Tstart = 258244221.0
Tstop  = 258244296.0
Ebins = 20
ResponseFunction = PASS5_v0_TRANSIENT

### Don't delete 'ROIs' keyword ###
ROIs

### ROIs Table ###
# Emin[MeV]\tEmax[MeV]\tR.A.[deg.]\tDec.[deg.]\tradius[deg.]
20.0\t\t5000.0\t\t210.8\t\t-51.0\t\t10.0
5000.0\t\t50000.0\t\t210.8\t\t-51.0\t\t10.0
50000.0\t\t100000.0\t210.8\t\t-51.0\t\t10.0
"""
        if os.path.exists(self.paramfile):
            a = raw_input("Overwrite '%s'? [y/N] " % self.paramfile)
            if a.lower() != 'y' :
                return 
        f = open(self.paramfile,'w')
        print >> f, conf
        f.close()
        


if __name__ == '__main__':    

    def usage():
        print >> sys.stderr, 'Usage : rspgen.py    <param file>'
        print >> sys.stderr, '        rspgen.py -r <param file>'
        print >> sys.stderr, '        rspgen.py -g <template param file>'
        print >> sys.stderr, 'Options :'
        print >> sys.stderr, '        [no opt] : Reading <param file>, make combined RSP and PHA files'
        print >> sys.stderr, '        -r       : Reading <param file>, make energy-dependent ROI files'
        print >> sys.stderr, '        -g       : Make <template param file>'
                

    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "gr")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    mode = 0
    
    for o, a in opts:
        if o == "-g":
            mode = 1
        if o == "-r":
            mode = 2
    if len(args) != 1 :
        usage()
        sys.exit(2)

    mrspgen = MultiRspGen(args[0])
    if mode == 0:
        mrspgen.run()
    elif mode == 1:
        mrspgen.make_conf_template()
    elif mode == 2:
        mrspgen.make_roi_files()

#Added by G.Vianello (giacomov@slac.stanford.edu)

def fixMatrixHDU(matrixHDU):
  #This creates a copy of the input matrix with all variable-length arrays converted to fixed length,
  #of the smallest possible size.
  #This is needed because pyfits makes all sort of fuckups with variable-length arrays

  newcols = []
  
  for col in matrixHDU.columns:
    if(col.format.find("P")==0):
      #Variable-length
      newMatrix               = variableToMatrix(matrixHDU.data.field(col.name))
      length                  = len(newMatrix[0])
      coltype                 = col.format.split("(")[0].replace("P","")
      newFormat               = '%s%s' %(length,coltype)
      newcols.append(pyfits.Column(col.name,newFormat,col.unit,col.null,col.bscale,col.bzero,col.disp,
                                 col.start,col.dim,newMatrix))
    else:
      newcols.append(pyfits.Column(col.name,col.format,col.unit,col.null,col.bscale,col.bzero,col.disp,
                                 col.start,col.dim,matrixHDU.data.field(col.name)))
  pass

  newtable                    = pyfits.new_table(newcols,header=matrixHDU.header)
  return newtable
pass

def variableToMatrix(variableLengthMatrix):
  '''This take a variable length array and return it in a properly formed constant length array'''
  nrows                          = len(variableLengthMatrix)
  ncolumns                       = max([len(elem) for elem in variableLengthMatrix])
  matrix                         = numpy.zeros([nrows,ncolumns])
  for i in range(nrows):
    for j in range(ncolumns):
      try:
        matrix[i,j]                = variableLengthMatrix[i][j]
      except:
        pass
  return matrix
pass
